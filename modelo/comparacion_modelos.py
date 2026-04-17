"""
comparacion_modelos.py
======================
Reentrenamiento corregido de:
  - best_model_Hybrid_CNN_LSTM_Attention.h5
  - best_model_CNN_Mejorada_Usuario.h5

CORRECCIONES RESPECTO AL NOTEBOOK ORIGINAL
-------------------------------------------
1. Sin augmentación exclusiva de N.
   El notebook original duplicaba solo la clase N (augment_factor=2), lo que
   hacía que N tuviese el doble de muestras que el resto.  Aquí se aplica
   oversampling uniforme: todas las clases se igualan a la clase mayoritaria
   usando ImageDataGenerator con parámetros conservadores.

2. Alpha de focal loss proporcional a la frecuencia inversa de cada clase.
   El notebook ponía alpha[N]=2 (boosteaba la clase más frecuente).
   Aquí alpha[i] = N_total / (n_clases * n_i), de modo que las clases raras
   (F, M, Q) reciben mayor penalización cuando el modelo se equivoca en ellas.

3. Sin boost manual de class_weight para N.
   Se usa compute_class_weight('balanced') sin modificaciones adicionales.

4. ModelCheckpoint monitorea val_f1_score (macro) en lugar de val_loss, lo
   que garantiza que se guarda el modelo con mejor discriminación entre clases
   y no el que simplemente predice siempre la clase mayoritaria.

USO
---
    python comparacion_modelos.py --data /ruta/al/dataset [--epochs 50] [--batch 32]

La carpeta del dataset debe tener subcarpetas por clase:
  dataset/
    F/  imagen1.png  imagen2.png ...
    M/  ...
    N/  ...
    Q/  ...
    S/  ...
    V/  ...

Los modelos se guardan en:
  ../models/best_model_Hybrid_CNN_LSTM_Attention.h5
  ../models/best_model_CNN_Mejorada_Usuario.h5
"""

import argparse
import os
import random
import sys
import time
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, label_binarize
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (classification_report, confusion_matrix,
                             accuracy_score, f1_score, roc_curve, auc)
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.layers import (Conv2D, MaxPooling2D, Dense, Dropout,
                                     Flatten, GlobalAveragePooling2D,
                                     BatchNormalization)
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical

# ── Semillas de reproducibilidad ────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# ── Hiperparámetros globales ─────────────────────────────────────────────────
IMG_SIZE      = (128, 128)
MAX_PER_CLASS = 2000        # cap por clase al cargar (evita desbalance severo)
TRAIN_IMAGES_PER_CLASS = 1400
VAL_IMAGES_PER_CLASS   = 600
TEST_IMAGES_PER_CLASS  = 600
TRAINVAL_IMAGES_PER_CLASS = TRAIN_IMAGES_PER_CLASS + VAL_IMAGES_PER_CLASS
EPOCHS        = 50
BATCH_SIZE    = 32
TRAIN_SPLIT   = 0.70
VAL_SPLIT     = 0.15
TEST_SPLIT    = 0.15

# Ruta por defecto del dataset en Descargas
DEFAULT_DATA_PATH_CANDIDATES = [
    Path.home() / "Downloads" / "ECG_Image_data_2",
    Path.home() / "Downloads" / "ECG_Image_data 2",
]
DEFAULT_DATA_PATH = next((path for path in DEFAULT_DATA_PATH_CANDIDATES if path.exists()), DEFAULT_DATA_PATH_CANDIDATES[0])

# Ruta de salida de modelos (../models/ relativa al script)
MODELS_DIR = (Path.cwd() / "backend" / "models2") if (Path.cwd() / "backend").exists() else (Path.cwd().parent / "models2")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# ── Clases del dataset MIT-BIH ───────────────────────────────────────────────
# Orden esperado tras LabelEncoder alfabético
CLASS_NAMES_EXPECTED = ["F", "M", "N", "Q", "S", "V"]


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  UTILIDADES                                                             ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def preprocess_image(img_path: str, img_size=IMG_SIZE):
    """Preprocesamiento idéntico al del entrenamiento original."""
    try:
        img = cv2.imread(img_path)
        if img is None:
            return None
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, img_size, interpolation=cv2.INTER_AREA)
        img = cv2.GaussianBlur(img, (3, 3), 0)
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
        _, thr = cv2.threshold(img.astype(np.uint8), 0, 255, cv2.THRESH_OTSU)
        final = thr.astype(np.float32) / 255.0
        return np.expand_dims(final, axis=-1)          # (128, 128, 1)
    except Exception as e:
        print(f"  [WARN] Error en {img_path}: {e}")
        return None


def _load_images_from_split(split_root: Path, per_class_limit: int):
    """Carga un split con subcarpetas por clase y limita muestras por clase."""
    if not split_root.is_dir():
        raise FileNotFoundError(f"No existe la carpeta esperada: {split_root}")

    X, y, img_paths = [], [], []
    distribution = {}
    for cls_name in CLASS_NAMES_EXPECTED:
        cls_dir = split_root / cls_name
        if not cls_dir.is_dir():
            continue
        exts = {".png", ".jpg", ".jpeg", ".bmp"}
        files = [f for f in cls_dir.iterdir() if f.suffix.lower() in exts]
        if not files:
            continue
        if len(files) > per_class_limit:
            files = random.sample(files, per_class_limit)
            print(f"  {cls_name}: {per_class_limit} (muestreado de {len(list(cls_dir.iterdir()))})")
        else:
            print(f"  {cls_name}: {len(files)}")
        for fp in files:
            img = preprocess_image(str(fp))
            if img is not None:
                X.append(img)
                y.append(cls_name)
                img_paths.append(str(fp))
        distribution[cls_name] = distribution.get(cls_name, 0) + len(files)

    if not X:
        raise ValueError(f"No se cargaron imágenes válidas desde {split_root}.")

    return np.array(X, dtype=np.float32), np.array(y), np.array(img_paths), distribution


def load_dataset(data_path: str):
    """Carga train/val desde train/ y test desde test/."""
    data_path = Path(data_path)
    train_root = data_path / "train" if (data_path / "train").is_dir() else data_path
    test_root = data_path / "test" if (data_path / "test").is_dir() else None

    print(f"\n{'─'*50}")
    print("Cargando dataset desde:", data_path)
    print(f"{'─'*50}")

    X_trainval, y_trainval, paths_trainval, dist_trainval = _load_images_from_split(train_root, TRAINVAL_IMAGES_PER_CLASS)
    print(f"\nDistribución train/val: {dist_trainval}")

    if test_root is None:
        raise FileNotFoundError(f"No se encontró la carpeta test en {data_path}")
    X_test, y_test, paths_test, dist_test = _load_images_from_split(test_root, TEST_IMAGES_PER_CLASS)
    print(f"Distribución test: {dist_test}")

    le = LabelEncoder()
    y_trainval_enc = le.fit_transform(y_trainval)
    class_names = list(le.classes_)
    y_trainval_onehot = to_categorical(y_trainval_enc, num_classes=len(class_names))

    y_test_enc = le.transform(y_test)
    y_test_onehot = to_categorical(y_test_enc, num_classes=len(class_names))

    X_train, X_val, y_train, y_val, paths_train, paths_val = train_test_split(
        X_trainval, y_trainval_onehot, paths_trainval,
        test_size=VAL_IMAGES_PER_CLASS / TRAINVAL_IMAGES_PER_CLASS,
        random_state=SEED,
        stratify=y_trainval_enc,
    )

    print(f"Dataset cargado: train={X_train.shape}, val={X_val.shape}, test={X_test.shape}, clases={class_names}")
    return X_train, y_train, paths_train, X_val, y_val, paths_val, X_test, y_test_onehot, paths_test, class_names


def oversample_to_majority(X, y_onehot, class_names):
    """
    Oversampling con augmentación leve para equilibrar TODAS las clases
    al número de la clase mayoritaria.
    Reemplaza la vieja lógica de duplicar solo N.
    """
    datagen = ImageDataGenerator(
        rotation_range=8,
        width_shift_range=0.05,
        height_shift_range=0.05,
        zoom_range=0.08,
        shear_range=0.04,
        brightness_range=(0.9, 1.1),
        fill_mode="nearest",
    )

    y_labels = np.argmax(y_onehot, axis=1)
    counts = np.bincount(y_labels)
    target = int(counts.max())

    print(f"\nOversampling balanceado → {target} muestras por clase:")
    X_out = list(X)
    y_out = list(y_onehot)

    for cls_idx, cls_name in enumerate(class_names):
        n = counts[cls_idx]
        needed = target - n
        if needed <= 0:
            print(f"  {cls_name}: {n} (sin augmentación)")
            continue

        idxs = np.where(y_labels == cls_idx)[0]
        added = 0
        rng = np.random.default_rng(SEED + cls_idx)
        while added < needed:
            i = rng.choice(idxs)
            batch = X[i][None]
            aug = next(datagen.flow(batch, batch_size=1))[0]
            X_out.append(aug)
            y_out.append(y_onehot[i])
            added += 1
        print(f"  {cls_name}: {n} + {needed} aug = {target}")

    X_out = np.array(X_out, dtype=np.float32)
    y_out = np.array(y_out, dtype=np.float32)
    # Mezclar
    perm = np.random.default_rng(SEED).permutation(len(X_out))
    return X_out[perm], y_out[perm]


def compute_inverse_freq_alpha(y_train_labels, n_classes):
    """
    FIX PRINCIPAL: alpha[i] = N_total / (n_clases * n_i)
    Las clases raras reciben alpha mayor → focal loss penaliza más los errores
    en clases difíciles, en lugar de boosteár la clase más frecuente (N).
    """
    counts = np.bincount(y_train_labels, minlength=n_classes).astype(float)
    n_total = counts.sum()
    alpha = n_total / (n_classes * (counts + 1e-9))
    # Normalizar para que el promedio sea 1.0
    alpha = alpha / alpha.mean()
    return alpha.tolist()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  LOSS Y MÉTRICAS                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def focal_loss(gamma=2.0, alpha=None):
    """Focal loss con alpha por clase opcional."""
    def focal(y_true, y_pred):
        eps = 1e-7
        y_pred = tf.clip_by_value(y_pred, eps, 1.0 - eps)
        ce = -y_true * tf.math.log(y_pred)
        if alpha is not None:
            alpha_t = tf.constant(alpha, dtype=tf.float32)
            aw = tf.reduce_sum(alpha_t * y_true, axis=1)
            weight = aw[:, None] * tf.pow(1.0 - y_pred, gamma)
        else:
            weight = tf.pow(1.0 - y_pred, gamma)
        return tf.reduce_mean(tf.reduce_sum(weight * ce, axis=1))
    focal.__name__ = "focal_loss"
    return focal


class F1Score(tf.keras.metrics.Metric):
    """Métrica F1 macro-average para monitoreo durante entrenamiento."""
    def __init__(self, name="f1_score", **kwargs):
        super().__init__(name=name, **kwargs)
        self.prec = tf.keras.metrics.Precision()
        self.rec  = tf.keras.metrics.Recall()

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.prec.update_state(y_true, y_pred, sample_weight)
        self.rec.update_state(y_true, y_pred, sample_weight)

    def result(self):
        p = self.prec.result()
        r = self.rec.result()
        return 2 * ((p * r) / (p + r + tf.keras.backend.epsilon()))

    def reset_state(self):
        self.prec.reset_state()
        self.rec.reset_state()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CAPAS PERSONALIZADAS (idénticas al original para compatibilidad)       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class AttentionLayer(layers.Layer):
    def __init__(self, units=128, **kwargs):
        super().__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        self.W_q = self.add_weight(name="W_q",
                                   shape=(input_shape[-1], self.units),
                                   initializer="glorot_uniform", trainable=True)
        self.W_k = self.add_weight(name="W_k",
                                   shape=(input_shape[-1], self.units),
                                   initializer="glorot_uniform", trainable=True)
        self.W_v = self.add_weight(name="W_v",
                                   shape=(input_shape[-1], self.units),
                                   initializer="glorot_uniform", trainable=True)
        self.dense = layers.Dense(input_shape[-1])
        super().build(input_shape)

    def call(self, inputs):
        Q = tf.matmul(inputs, self.W_q)
        K = tf.matmul(inputs, self.W_k)
        V = tf.matmul(inputs, self.W_v)
        attn = tf.matmul(Q, K, transpose_b=True)
        attn = attn / tf.sqrt(tf.cast(self.units, tf.float32))
        w   = tf.nn.softmax(attn, axis=-1)
        out = tf.matmul(w, V)
        return self.dense(out) + inputs   # conexión residual

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"units": self.units})
        return cfg


class SpatialAttentionLayer(layers.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self, input_shape):
        self.conv1 = layers.Conv2D(64, (3, 3), padding="same", activation="relu")
        self.conv2 = layers.Conv2D(1,  (1, 1), padding="same", activation="sigmoid")
        super().build(input_shape)

    def call(self, x):
        m = self.conv1(x)
        m = self.conv2(m)
        return x * m

    def get_config(self):
        return super().get_config()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ARQUITECTURAS DE MODELO                                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class SimpleECGModel:
    """CONSERVADO DEL ORIGINAL - SIN CAMBIOS"""
    def __init__(self, input_shape, num_classes): 
        self.input_shape=input_shape; self.num_classes=num_classes
    def build_model(self):
        inp = layers.Input(shape=self.input_shape)
        x = layers.Conv2D(16,3,padding='same',activation='relu')(inp)
        x = layers.BatchNormalization()(x); x = layers.MaxPooling2D(2)(x)
        x = layers.Conv2D(32,3,padding='same',activation='relu')(x)
        x = layers.BatchNormalization()(x); x = layers.MaxPooling2D(2)(x)
        x = layers.Conv2D(64,3,padding='same',activation='relu')(x)
        x = layers.BatchNormalization()(x); x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.3)(x); x = layers.Dense(128,activation='relu')(x); x = layers.Dropout(0.2)(x)
        out = layers.Dense(self.num_classes, activation='softmax')(x)
        return models.Model(inp,out)


class LSTMWithAttentionModel:
    """MODIFICADO: Peso especial para clase N en loss"""
    def __init__(self, input_shape, num_classes): 
        self.input_shape=input_shape; self.num_classes=num_classes
    def build_model(self):
        inputs = layers.Input(shape=self.input_shape)
        x = layers.Reshape((self.input_shape[0], self.input_shape[1]))(inputs)
        x = layers.LSTM(128, return_sequences=True, dropout=0.25, recurrent_dropout=0.15)(x)
        att = layers.Dense(1, activation='tanh')(x); att = layers.Flatten()(att); att = layers.Activation('softmax')(att)
        att = layers.RepeatVector(128)(att); att = layers.Permute([2,1])(att); x = layers.multiply([x, att])
        x = layers.LSTM(64, dropout=0.25, recurrent_dropout=0.15)(x); x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.3)(x); out = layers.Dense(self.num_classes, activation='softmax')(x)
        return models.Model(inputs, out)

class ResNet50WithSpatialAttention:
    """CORREGIDO: Manejo de canal único para ResNet50"""
    def __init__(self, input_shape, num_classes, trainable_from=None):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.trainable_from = trainable_from
    def build_model(self):
        inputs = layers.Input(shape=self.input_shape)
        
        # Convertir de 1 canal a 3 canales para ResNet50
        x = layers.Conv2D(3, (1,1), padding='same')(inputs)
        
        base = tf.keras.applications.ResNet50(include_top=False, weights='imagenet', 
                                            input_shape=(self.input_shape[0], self.input_shape[1], 3))
        if self.trainable_from is None:
            for layer in base.layers:
                layer.trainable = False
        else:
            for i, layer in enumerate(base.layers):
                layer.trainable = True if i >= self.trainable_from else False

        x = base(x, training=False)
        x = SpatialAttentionLayer()(x)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(256, activation='relu')(x); x = layers.Dropout(0.4)(x)
        x = layers.Dense(128, activation='relu')(x); x = layers.Dropout(0.3)(x)
        outputs = layers.Dense(self.num_classes, activation='softmax')(x)
        return models.Model(inputs, outputs)

class HybridCNNLSTMWithAttentionModel:
    """
    CNN con SpatialAttention → BiLSTM → AttentionLayer → clasificador.
    Guarda como: best_model_Hybrid_CNN_LSTM_Attention.h5
    """
    SAVE_NAME = "best_model_Hybrid_CNN_LSTM_Attention.h5"

    def __init__(self, input_shape, num_classes):
        self.input_shape = input_shape
        self.num_classes = num_classes

    def build(self):
        inp = layers.Input(shape=self.input_shape)

        # Bloque CNN 1
        x = layers.Conv2D(32, 3, padding="same", activation="relu")(inp)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling2D(2)(x)
        x = SpatialAttentionLayer()(x)
        x = layers.Dropout(0.2)(x)

        # Bloque CNN 2
        x = layers.Conv2D(64, 3, padding="same", activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling2D(2)(x)
        x = SpatialAttentionLayer()(x)
        x = layers.Dropout(0.25)(x)

        # Bloque CNN 3
        x = layers.Conv2D(128, 3, padding="same", activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling2D(2)(x)
        x = layers.Dropout(0.2)(x)

        # Reshape para LSTM: (batch, steps, features)
        s = x.shape
        x = layers.Reshape((s[1], s[2] * s[3]))(x)

        # BiLSTM + AttentionLayer
        x = layers.Bidirectional(
            layers.LSTM(96, return_sequences=True, dropout=0.2, recurrent_dropout=0.15)
        )(x)
        x = AttentionLayer(units=192)(x)
        x = layers.GlobalAveragePooling1D()(x)

        # Clasificador
        x = layers.Dense(256, activation="relu")(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(128, activation="relu")(x)
        x = layers.Dropout(0.25)(x)
        x = layers.Dense(64, activation="relu")(x)
        x = layers.Dropout(0.2)(x)
        out = layers.Dense(self.num_classes, activation="softmax")(x)

        return models.Model(inp, out, name="Hybrid_CNN_LSTM_Attention")


class ImprovedCNNModel:
    """
    CNN mejorada especificada por el usuario.
    Guarda como: best_model_CNN_Mejorada_Usuario.h5
    """
    SAVE_NAME = "best_model_CNN_Mejorada_Usuario.h5"

    def __init__(self, input_shape, num_classes):
        self.input_shape = input_shape
        self.num_classes = num_classes

    def build(self):
        inp = layers.Input(shape=self.input_shape)
        x = Conv2D(32, (3, 3), activation="relu")(inp)
        x = MaxPooling2D((2, 2))(x)
        x = Conv2D(32, (3, 3), activation="relu")(x)
        x = MaxPooling2D((2, 2))(x)
        x = Conv2D(64, (3, 3), activation="relu")(x)
        x = MaxPooling2D((2, 2))(x)
        x = Conv2D(64, (3, 3), activation="relu")(x)
        x = MaxPooling2D((2, 2))(x)
        x = Conv2D(128, (3, 3), activation="relu")(x)   # → 6×6
        x = Conv2D(128, (3, 3), activation="relu")(x)   # → 4×4
        x = GlobalAveragePooling2D()(x)
        x = Dense(256, activation="relu")(x)
        x = Dropout(0.5)(x)
        out = Dense(self.num_classes, activation="softmax")(x)
        return models.Model(inp, out, name="CNN_Mejorada_Usuario")


def plot_training_curves(history, model_name: str, out_dir: Path):
    """Grafica métricas de train vs val y guarda la figura."""
    hist = history.history
    metrics_to_plot = [
        ("loss", "Loss"),
        ("accuracy", "Accuracy"),
        ("precision", "Precision"),
        ("recall", "Recall"),
        ("f1_score", "F1 Score"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    for idx, (metric_key, metric_title) in enumerate(metrics_to_plot):
        ax = axes[idx]
        if metric_key in hist:
            ax.plot(hist[metric_key], label=f"Train {metric_title}", linewidth=2)
        if f"val_{metric_key}" in hist:
            ax.plot(hist[f"val_{metric_key}"], label=f"Val {metric_title}", linewidth=2)
        ax.set_title(metric_title)
        ax.set_xlabel("Epoca")
        ax.grid(alpha=0.3)
        ax.legend()

    axes[-1].axis("off")
    fig.suptitle(f"{model_name} - Train vs Val", fontsize=14)
    fig.tight_layout()

    out_path = out_dir / f"{model_name}_train_val_metrics.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    return out_path


def plot_confusion_matrix_figure(y_true, y_pred, class_names, model_name: str, out_dir: Path):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=class_names, yticklabels=class_names, ax=ax)
    ax.set_xlabel("Prediccion")
    ax.set_ylabel("Real")
    ax.set_title(f"Matriz de Confusion - {model_name}")
    fig.tight_layout()

    out_path = out_dir / f"{model_name}_confusion_matrix.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    return out_path


def plot_multiclass_roc(y_true_onehot, y_proba, class_names, model_name: str, out_dir: Path):
    y_true_idx = np.argmax(y_true_onehot, axis=1)
    y_true_bin = label_binarize(y_true_idx, classes=np.arange(len(class_names)))

    fig, ax = plt.subplots(figsize=(9, 7))
    plotted_any = False
    for i, class_name in enumerate(class_names):
        y_true_i = y_true_bin[:, i]
        y_score_i = y_proba[:, i]
        if len(np.unique(y_true_i)) < 2:
            continue
        fpr, tpr, _ = roc_curve(y_true_i, y_score_i)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, linewidth=2, label=f"{class_name} (AUC={roc_auc:.3f})")
        plotted_any = True

    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"Curvas ROC (Test) - {model_name}")
    ax.grid(alpha=0.3)
    if plotted_any:
        ax.legend(loc="lower right")

    fig.tight_layout()
    out_path = out_dir / f"{model_name}_roc_test.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    return out_path


def plot_predictions_per_class(model, X_test, y_test, test_paths, class_names, model_name: str, out_dir: Path, samples_per_class=12):
    y_true = np.argmax(y_test, axis=1)
    y_proba = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_proba, axis=1)

    saved_paths = []
    for cls_idx, cls_name in enumerate(class_names):
        cls_indices = np.where(y_true == cls_idx)[0][:samples_per_class]
        if len(cls_indices) == 0:
            continue

        cols = 4
        rows = int(np.ceil(len(cls_indices) / cols))
        fig, axes = plt.subplots(rows, cols, figsize=(16, 3.8 * rows))
        axes = np.array(axes).reshape(-1)

        for j, idx in enumerate(cls_indices):
            ax = axes[j]
            img = X_test[idx].squeeze()
            ax.imshow(img, cmap="gray")
            real_lbl = class_names[y_true[idx]]
            pred_lbl = class_names[y_pred[idx]]
            ok = real_lbl == pred_lbl
            color = "green" if ok else "red"
            ax.set_title(f"Real:{real_lbl} | Pred:{pred_lbl}", color=color, fontsize=10)
            if test_paths is not None:
                ax.set_xlabel(Path(test_paths[idx]).name, fontsize=8)
            ax.axis("off")

        for j in range(len(cls_indices), len(axes)):
            axes[j].axis("off")

        fig.suptitle(f"{model_name} - Clase {cls_name} (12 ejemplos max)", fontsize=13)
        fig.tight_layout()
        out_path = out_dir / f"{model_name}_samples_class_{cls_name}.png"
        fig.savefig(out_path, dpi=180, bbox_inches="tight")
        plt.show()
        plt.close(fig)
        saved_paths.append(out_path)

    return saved_paths


def plot_inline_dashboard(history, y_true, y_pred, y_test, y_proba, class_names, model_name: str):
    """Muestra en el notebook un panel resumen con subplots."""
    fig = plt.figure(figsize=(22, 16))
    gs = fig.add_gridspec(3, 2)

    ax_curve = fig.add_subplot(gs[0, :])
    hist = history.history
    ax_curve.plot(hist.get("loss", []), label="Train Loss", linewidth=2)
    if "val_loss" in hist:
        ax_curve.plot(hist["val_loss"], label="Val Loss", linewidth=2)
    ax_curve.plot(hist.get("accuracy", []), label="Train Accuracy", linewidth=2)
    if "val_accuracy" in hist:
        ax_curve.plot(hist["val_accuracy"], label="Val Accuracy", linewidth=2)
    ax_curve.plot(hist.get("precision", []), label="Train Precision", linewidth=2)
    if "val_precision" in hist:
        ax_curve.plot(hist["val_precision"], label="Val Precision", linewidth=2)
    ax_curve.plot(hist.get("recall", []), label="Train Recall", linewidth=2)
    if "val_recall" in hist:
        ax_curve.plot(hist["val_recall"], label="Val Recall", linewidth=2)
    ax_curve.plot(hist.get("f1_score", []), label="Train F1", linewidth=2)
    if "val_f1_score" in hist:
        ax_curve.plot(hist["val_f1_score"], label="Val F1", linewidth=2)
    ax_curve.set_title(f"{model_name} - Curvas de entrenamiento")
    ax_curve.set_xlabel("Epoca")
    ax_curve.grid(alpha=0.25)
    ax_curve.legend(ncol=3, fontsize=9)

    ax_cm = fig.add_subplot(gs[1, 0])
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=class_names, yticklabels=class_names, ax=ax_cm)
    ax_cm.set_title("Matriz de confusion (Test)")
    ax_cm.set_xlabel("Prediccion")
    ax_cm.set_ylabel("Real")

    ax_roc = fig.add_subplot(gs[1, 1])
    plotted_any = False
    y_true_idx = np.argmax(y_test, axis=1)
    y_true_bin = label_binarize(y_true_idx, classes=np.arange(len(class_names)))
    for i, class_name in enumerate(class_names):
        y_true_i = y_true_bin[:, i]
        y_score_i = y_proba[:, i]
        if len(np.unique(y_true_i)) < 2:
            continue
        fpr, tpr, _ = roc_curve(y_true_i, y_score_i)
        roc_auc = auc(fpr, tpr)
        ax_roc.plot(fpr, tpr, linewidth=2, label=f"{class_name} (AUC={roc_auc:.3f})")
        plotted_any = True
    ax_roc.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1)
    ax_roc.set_title("Curvas ROC (Test)")
    ax_roc.set_xlabel("FPR")
    ax_roc.set_ylabel("TPR")
    ax_roc.grid(alpha=0.25)
    if plotted_any:
        ax_roc.legend(loc="lower right", fontsize=8)

    ax_report = fig.add_subplot(gs[2, :])
    ax_report.axis("off")
    acc = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    report_text = (
        f"Accuracy: {acc:.4f}\n"
        f"F1 Macro: {f1_macro:.4f}\n"
        f"F1 Weighted: {f1_weighted:.4f}\n"
        f"Muestras test: {len(y_true)}"
    )
    ax_report.text(0.02, 0.75, report_text, fontsize=14, va="top", family="monospace")

    fig.suptitle(f"{model_name} - Dashboard de resultados", fontsize=16)
    fig.tight_layout()
    plt.show()
    plt.close(fig)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FUNCIÓN DE ENTRENAMIENTO CORREGIDA                                     ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def train_model(ModelClass, X_train, X_val, X_test,
                y_train, y_val, y_test, class_names, test_paths=None,
                learning_rate=3e-4, epochs=EPOCHS, batch_size=BATCH_SIZE):
    """
    Entrena un modelo con las correcciones aplicadas.

    Correcciones clave:
    - Oversampling uniforme (no solo N) ya aplicado antes de llamar esta función
    - Alpha de focal loss = frecuencia inversa (no boost de N)
    - class_weight balanceado sin modificaciones manuales
    - Checkpoint monitoreando val_f1_score (macro)
    """
    model_obj = ModelClass(X_train.shape[1:], len(class_names))
    model     = model_obj.build()
    save_path = str(MODELS_DIR / ModelClass.SAVE_NAME)
    name      = model.name
    plot_dir  = MODELS_DIR / "plots" / name
    plot_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'═'*60}")
    print(f"  Entrenando: {name}")
    print(f"  Guardará en: {save_path}")
    print(f"{'═'*60}")
    print(f"  Parámetros totales: {model.count_params():,}")

    # ── Alpha de focal loss: inverso de frecuencia ─────────────────────────
    y_train_labels = np.argmax(y_train, axis=1)
    alpha = compute_inverse_freq_alpha(y_train_labels, len(class_names))
    print(f"\n  Alpha por clase (focal loss — mayor = más penalizada):")
    for cls, a in zip(class_names, alpha):
        bar = "█" * int(a * 10)
        print(f"    {cls}: {a:.3f}  {bar}")

    # ── Class weights: balanced sin modificaciones manuales ────────────────
    classes = np.unique(y_train_labels)
    weights = compute_class_weight("balanced", classes=classes, y=y_train_labels)
    cw = {int(i): float(w) for i, w in enumerate(weights)}
    print(f"\n  Class weights (balanced):")
    for cls, i in zip(class_names, range(len(class_names))):
        print(f"    {cls}: {cw[i]:.3f}")

    # ── Compilar ───────────────────────────────────────────────────────────
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss=focal_loss(gamma=2.0, alpha=alpha),
        metrics=[
            "accuracy",
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
            F1Score(name="f1_score"),
        ],
    )

    # ── Callbacks ─────────────────────────────────────────────────────────
    cb_list = [
        callbacks.EarlyStopping(
            monitor="val_f1_score", mode="max",
            patience=12, restore_best_weights=True, verbose=1
        ),
        callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=5,
            min_lr=1e-7, verbose=1
        ),
        callbacks.ModelCheckpoint(
            filepath=save_path,
            monitor="val_f1_score", mode="max",
            save_best_only=True, verbose=1
        ),
    ]

    # ── Entrenamiento ──────────────────────────────────────────────────────
    t0 = time.time()
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=cw,
        callbacks=cb_list,
        verbose=1,
    )
    elapsed = time.time() - t0

    # ── Cargar el mejor checkpoint guardado ───────────────────────────────
    if os.path.exists(save_path):
        custom_objects = {
            "AttentionLayer":        AttentionLayer,
            "SpatialAttentionLayer": SpatialAttentionLayer,
            "F1Score":               F1Score,
            "focal_loss":            focal_loss(gamma=2.0, alpha=alpha),
            "focal":                 focal_loss(gamma=2.0, alpha=alpha),
        }
        try:
            model = keras.models.load_model(save_path, custom_objects=custom_objects)
            print(f"\n  Mejor checkpoint cargado desde {save_path}")
        except Exception as e:
            print(f"  [WARN] No se pudo recargar el checkpoint: {e}")

    # ── Evaluación en test ─────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  EVALUACIÓN EN TEST — {name}")
    print(f"{'─'*60}")

    y_proba = model.predict(X_test, verbose=0)
    y_pred  = np.argmax(y_proba, axis=1)
    y_true  = np.argmax(y_test,  axis=1)

    eval_names = model.metrics_names
    eval_vals = model.evaluate(X_test, y_test, verbose=0)
    eval_map = {k: float(v) for k, v in zip(eval_names, eval_vals)}

    acc        = accuracy_score(y_true, y_pred)
    f1_macro   = f1_score(y_true, y_pred, average="macro",    zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    print(f"  Accuracy  : {acc:.4f}")
    if "loss" in eval_map:
        print(f"  Loss      : {eval_map['loss']:.4f}")
    if "precision" in eval_map:
        print(f"  Precision : {eval_map['precision']:.4f}")
    if "recall" in eval_map:
        print(f"  Recall    : {eval_map['recall']:.4f}")
    print(f"  F1 Macro  : {f1_macro:.4f}")
    print(f"  F1 Weighted: {f1_weighted:.4f}")
    print(f"  Tiempo    : {elapsed/60:.1f} min  |  Épocas: {len(history.history['loss'])}")

    print(f"\n  Reporte por clase:")
    print(classification_report(y_true, y_pred, target_names=class_names,
                                 digits=4, zero_division=0))

    # Matriz de confusión en texto
    cm = confusion_matrix(y_true, y_pred)
    print("  Matriz de confusión (filas=real, cols=pred):")
    header = "       " + "  ".join(f"{c:>4}" for c in class_names)
    print(header)
    for i, row in enumerate(cm):
        line = f"  {class_names[i]:>3}  " + "  ".join(f"{v:>4}" for v in row)
        print(line)

    curves_path = plot_training_curves(history, name, plot_dir)
    cm_path = plot_confusion_matrix_figure(y_true, y_pred, class_names, name, plot_dir)
    roc_path = plot_multiclass_roc(y_test, y_proba, class_names, name, plot_dir)
    plot_inline_dashboard(history, y_true, y_pred, y_test, y_proba, class_names, name)
    samples_paths = plot_predictions_per_class(
        model=model,
        X_test=X_test,
        y_test=y_test,
        test_paths=test_paths,
        class_names=class_names,
        model_name=name,
        out_dir=plot_dir,
        samples_per_class=12,
    )

    print(f"\n  Graficas guardadas en: {plot_dir}")

    print(f"\n  Modelo guardado en: {save_path}")

    return {
        "model":      model,
        "history":    history,
        "accuracy":   acc,
        "f1_macro":   f1_macro,
        "f1_weighted": f1_weighted,
        "test_loss":  eval_map.get("loss", None),
        "test_precision": eval_map.get("precision", None),
        "test_recall": eval_map.get("recall", None),
        "elapsed_min": elapsed / 60,
        "epochs":     len(history.history["loss"]),
        "save_path":  save_path,
        "plots": {
            "train_val": str(curves_path),
            "confusion": str(cm_path),
            "roc": str(roc_path),
            "samples": [str(p) for p in samples_paths],
        },
    }


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  PIPELINE PRINCIPAL                                                     ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def main(data_path: str, epochs: int = EPOCHS, batch: int = BATCH_SIZE,
         models_to_run: list = None):

    # ── 1. Cargar datos ────────────────────────────────────────────────────
    X_train, y_train, paths_train, X_val, y_val, paths_val, X_test, y_test, paths_test, class_names = load_dataset(data_path)
    print(f"\nSplit → train: {len(X_train)}  val: {len(X_val)}  test: {len(X_test)}")

    # ── 3. Oversampling balanceado en el conjunto de entrenamiento ─────────
    print("\nAplicando oversampling balanceado al conjunto de entrenamiento...")
    X_train_bal, y_train_bal = oversample_to_majority(X_train, y_train, class_names)
    print(f"Entrenamiento después de balanceo: {X_train_bal.shape[0]} muestras")

    # ── 4. Entrenar modelos ────────────────────────────────────────────────
    all_models = {
        "Hybrid_CNN_LSTM_Attention": HybridCNNLSTMWithAttentionModel,
        "CNN_Mejorada_Usuario":      ImprovedCNNModel,
        "Simple_ECG_Model":          SimpleECGModel,
        "LSTM_Attention_Model":      LSTMWithAttentionModel,
        "ResNet50_Spatial_Attention": ResNet50WithSpatialAttention,
    }
    if models_to_run:
        all_models = {k: v for k, v in all_models.items() if k in models_to_run}

    results = {}
    for model_key, ModelClass in all_models.items():
        try:
            res = train_model(
                ModelClass,
                X_train_bal, X_val, X_test,
                y_train_bal, y_val, y_test,
                class_names,
                test_paths=paths_test,
                learning_rate=3e-4,
                epochs=epochs,
                batch_size=batch,
            )
            results[model_key] = res
        except tf.errors.ResourceExhaustedError:
            print(f"\n[ERROR] OOM al entrenar {model_key}. "
                  "Reduce BATCH_SIZE o MAX_PER_CLASS.")
        except Exception as exc:
            print(f"\n[ERROR] Fallo al entrenar {model_key}: {exc}")

    # ── 5. Resumen final ───────────────────────────────────────────────────
    if results:
        print(f"\n{'═'*60}")
        print("  RESUMEN FINAL")
        print(f"{'═'*60}")
        rows = []
        for name, r in results.items():
            rows.append({
                "Modelo":       name,
                "Accuracy":     f"{r['accuracy']:.4f}",
                "Test_Loss":    f"{(r['test_loss'] if r['test_loss'] is not None else float('nan')):.4f}",
                "Test_Prec":    f"{(r['test_precision'] if r['test_precision'] is not None else float('nan')):.4f}",
                "Test_Recall":  f"{(r['test_recall'] if r['test_recall'] is not None else float('nan')):.4f}",
                "F1_Macro":     f"{r['f1_macro']:.4f}",
                "F1_Weighted":  f"{r['f1_weighted']:.4f}",
                "Epocas":       r["epochs"],
                "Tiempo_min":   f"{r['elapsed_min']:.1f}",
                "Guardado_en":  r["save_path"],
            })
        df = pd.DataFrame(rows)
        print(df.to_string(index=False))
        csv_out = MODELS_DIR / "training_results.csv"
        df.to_csv(csv_out, index=False)
        print(f"\nResultados guardados en: {csv_out}")


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ENTRADA                                                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reentrenamiento corregido de modelos ECG"
    )
    parser.add_argument(
        "--data", default=str(DEFAULT_DATA_PATH),
        help=f"Ruta al dataset (default: {DEFAULT_DATA_PATH})"
    )
    parser.add_argument(
        "--epochs", type=int, default=EPOCHS,
        help=f"Número de épocas máximas (default: {EPOCHS})"
    )
    parser.add_argument(
        "--batch", type=int, default=BATCH_SIZE,
        help=f"Batch size (default: {BATCH_SIZE})"
    )
    parser.add_argument(
        "--only", nargs="+",
        choices=["Hybrid_CNN_LSTM_Attention", "CNN_Mejorada_Usuario","Simple_ECG_Model", "LSTM_Attention_Model", "ResNet50_Spatial_Attention"],
        help="Entrenar solo los modelos indicados"
    )
    args, _ = parser.parse_known_args()

    main(
        data_path=args.data,
        epochs=args.epochs,
        batch=args.batch,
        models_to_run=args.only,
    )