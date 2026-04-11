"""
test_classification_pipeline.py
================================
Simula exactamente el pipeline de clasificacion ECG de la app con
trazabilidad completa en cada paso para diagnosticar clasificaciones incorrectas.

Uso:
    python backend/scripts/test_classification_pipeline.py
    python backend/scripts/test_classification_pipeline.py --image /ruta/a/imagen.png
    python backend/scripts/test_classification_pipeline.py --class V --n 3

Ejecutar desde la raiz del proyecto (TrainECG_app/).
"""

import argparse
import os
import sys
import glob
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]          # TrainECG_app/
BACKEND = Path(__file__).resolve().parents[1]        # backend/
MODEL_PATH = BACKEND / "models" / "best_model_Hybrid_CNN_LSTM_Attention.h5"
DATASET_PATH = Path.home() / "Downloads" / "ECG_Image_data_2" / "train"
OUT_DIR = BACKEND / "scripts" / "test_output"
OUT_DIR.mkdir(exist_ok=True)

# Clases reales del modelo (LabelEncoder alfabetico: F M N Q S V)
CLASS_NAMES = ["fusion", "paced", "normal", "unknown",
               "supraventricular_ectopic", "ventricular_ectopic"]
FOLDER_NAMES = ["F", "M", "N", "Q", "S", "V"]

# ---------------------------------------------------------------------------
# Cargar TensorFlow y modelo
# ---------------------------------------------------------------------------
import tensorflow as tf
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

print("=" * 70)
print("  CARGANDO MODELO")
print("=" * 70)


class AttentionLayer(tf.keras.layers.Layer):
    def __init__(self, units=128, **kwargs):
        super().__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        self.W_q = self.add_weight(name="W_q", shape=(input_shape[-1], self.units),
                                   initializer="glorot_uniform", trainable=True)
        self.W_k = self.add_weight(name="W_k", shape=(input_shape[-1], self.units),
                                   initializer="glorot_uniform", trainable=True)
        self.W_v = self.add_weight(name="W_v", shape=(input_shape[-1], self.units),
                                   initializer="glorot_uniform", trainable=True)
        self.dense = tf.keras.layers.Dense(input_shape[-1])
        super().build(input_shape)

    def call(self, inputs):
        Q = tf.matmul(inputs, self.W_q)
        K = tf.matmul(inputs, self.W_k)
        V = tf.matmul(inputs, self.W_v)
        attn = tf.matmul(Q, K, transpose_b=True) / tf.sqrt(tf.cast(self.units, tf.float32))
        return self.dense(tf.matmul(tf.nn.softmax(attn, -1), V)) + inputs

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"units": self.units})
        return cfg


class SpatialAttentionLayer(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self, input_shape):
        self.conv1 = tf.keras.layers.Conv2D(64, (3, 3), padding="same", activation="relu")
        self.conv2 = tf.keras.layers.Conv2D(1, (1, 1), padding="same", activation="sigmoid")
        super().build(input_shape)

    def call(self, x):
        return x * self.conv2(self.conv1(x))

    def get_config(self):
        return super().get_config()


def focal_loss(gamma=2.0, alpha=None):
    def focal(y_true, y_pred):
        eps = 1e-7
        y_pred = tf.clip_by_value(y_pred, eps, 1 - eps)
        ce = -y_true * tf.math.log(y_pred)
        w = tf.pow(1 - y_pred, gamma)
        return tf.reduce_mean(tf.reduce_sum(w * ce, axis=1))
    return focal


if not MODEL_PATH.exists():
    print(f"[ERROR] Modelo no encontrado: {MODEL_PATH}")
    sys.exit(1)

model = tf.keras.models.load_model(
    str(MODEL_PATH),
    custom_objects={
        "AttentionLayer": AttentionLayer,
        "SpatialAttentionLayer": SpatialAttentionLayer,
        "focal_loss": focal_loss(),
        "focal": focal_loss(),
    },
    compile=False,
)
print(f"  Modelo cargado: {MODEL_PATH.name}")
print(f"  Input shape : {model.input_shape}")
print(f"  Output shape: {model.output_shape}")
print(f"  Num clases  : {model.output_shape[-1]}")


# ---------------------------------------------------------------------------
# Funciones de preprocesamiento — replica exacta del app
# ---------------------------------------------------------------------------

def load_image(path: str) -> np.ndarray:
    """Replica ImagePreprocessor.load_image()"""
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"No se pudo cargar: {path}")
    return img


def detect_ecg_region(image: np.ndarray):
    """Replica ImagePreprocessor.detect_ecg_region()"""
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0, image.shape[0]
    all_points = np.vstack(contours)
    _, y, _, h = cv2.boundingRect(all_points)
    padding = 10
    return max(0, y - padding), min(image.shape[0], y + h + padding)


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Replica ImagePreprocessor.normalize_image()"""
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    normalized = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX)
    _, thresholded = cv2.threshold(normalized.astype(np.uint8), 0, 255, cv2.THRESH_OTSU)
    return thresholded.astype(np.float32) / 255.0


def create_sliding_windows(image: np.ndarray, y_start: int, y_end: int,
                            window_size: int = 128):
    """Replica ImagePreprocessor.create_sliding_windows() con ventanas cuadradas."""
    height, width = image.shape[:2]
    ecg_region = image[y_start:y_end, :]
    region_height = y_end - y_start

    window_width = max(min(region_height, width), 64)
    step_size = max(window_width // 2, 30)

    windows, coordinates = [], []
    x = 0
    while x + window_width <= width:
        window = ecg_region[:, x:x + window_width]
        if window.std() > 10:
            window_resized = cv2.resize(window, (window_size, window_size),
                                        interpolation=cv2.INTER_AREA)
            windows.append(window_resized)
            y_center = y_start + region_height // 2
            coordinates.append((x, y_center, region_height))
        x += step_size

    return windows, coordinates, region_height, window_width, step_size


def preprocess_for_classification(path: str, window_size: int = 128):
    """Replica ImagePreprocessor.preprocess_for_classification() (fallback)."""
    img = load_image(path)
    resized = cv2.resize(img, (window_size, window_size), interpolation=cv2.INTER_AREA)
    return normalize_image(resized), img


def predict_single(arr: np.ndarray) -> tuple:
    """Replica ModelManager.predict() con salida completa de probabilidades."""
    if len(arr.shape) == 2:
        tensor = arr[None, :, :, None]
    elif len(arr.shape) == 3:
        tensor = arr[None, ...]
    else:
        tensor = arr

    probs = model.predict(tensor, verbose=0)[0]
    idx = int(np.argmax(probs))
    return CLASS_NAMES[idx], float(probs[idx]), probs


# ---------------------------------------------------------------------------
# Pipeline de diagnostico completo para una imagen
# ---------------------------------------------------------------------------

def diagnose_image(image_path: str, true_class: str = None, save_fig: bool = True):
    print("\n" + "=" * 70)
    print(f"  IMAGEN: {Path(image_path).name}")
    if true_class:
        print(f"  Clase real: {true_class}")
    print("=" * 70)

    # --- PASO 1: Carga ---
    print("\n[1] CARGA")
    raw = load_image(image_path)
    print(f"    Shape original : {raw.shape}  dtype={raw.dtype}")
    print(f"    Rango valores  : [{raw.min()}, {raw.max()}]")
    print(f"    Media / Std    : {raw.mean():.1f} / {raw.std():.1f}")

    # --- PASO 2: Deteccion de region ECG ---
    print("\n[2] DETECCION REGION ECG")
    y_start, y_end = detect_ecg_region(raw)
    region_height = y_end - y_start
    print(f"    y_start={y_start}, y_end={y_end}, region_height={region_height}px")
    print(f"    Region como % de la imagen: {region_height / raw.shape[0] * 100:.1f}%")

    # --- PASO 3: Ventanas deslizantes ---
    print("\n[3] VENTANAS DESLIZANTES")
    windows, coords, region_h, win_w, step = create_sliding_windows(raw, y_start, y_end)
    print(f"    window_width  = {win_w}px  (region_height={region_h}, img_width={raw.shape[1]})")
    print(f"    step_size     = {step}px")
    print(f"    Ventanas generadas: {len(windows)}")
    if not windows:
        print("    [ADVERTENCIA] No se generaron ventanas — se usara fallback imagen completa")

    # --- PASO 4: Normalizacion de ventanas ---
    print("\n[4] NORMALIZACION (Blur + Normalize + Otsu)")
    normalized_windows = []
    for i, w in enumerate(windows):
        normed = normalize_image(w)
        normalized_windows.append(normed)
        unique_vals = np.unique(normed)
        print(f"    Ventana {i:02d}: shape={normed.shape}  "
              f"unique_vals={len(unique_vals)}  "
              f"mean={normed.mean():.3f}  std={normed.std():.3f}  "
              f"min={normed.min():.2f}  max={normed.max():.2f}")
        if len(unique_vals) <= 2:
            print(f"             [ALERTA] Solo {len(unique_vals)} valores unicos — "
                  f"Otsu puede haber colapsado la imagen a binario plano")

    # --- PASO 5: Prediccion por ventana ---
    print("\n[5] PREDICCION POR VENTANA")
    print(f"    {'Win':>3}  {'Clase':>25}  {'Conf':>6}  Probabilidades [F    M    N    Q    S    V]")
    print(f"    {'-'*75}")

    per_window_results = []
    if normalized_windows:
        for i, normed in enumerate(normalized_windows):
            pred_class, conf, probs = predict_single(normed)
            per_window_results.append((pred_class, conf, probs))
            prob_str = "  ".join(f"{p:.2f}" for p in probs)
            marker = " <-- BAJA CONF" if conf < 0.7 else ""
            print(f"    {i:3d}  {pred_class:>25}  {conf:6.3f}  [{prob_str}]{marker}")
    else:
        print("    (sin ventanas — usando fallback imagen completa)")

    # --- PASO 6: Fallback imagen completa ---
    print("\n[6] PREDICCION IMAGEN COMPLETA (fallback / referencia)")
    full_arr, _ = preprocess_for_classification(image_path)
    full_class, full_conf, full_probs = predict_single(full_arr)
    prob_str = "  ".join(f"{p:.2f}" for p in full_probs)
    print(f"    Clase={full_class}  Conf={full_conf:.3f}  [{prob_str}]")

    # --- PASO 7: Resultado final (replica ecg.py actual) ---
    # ecg.py usa imagen completa como clasificacion principal.
    # Las ventanas solo se usan para anotacion visual (rectangulos sobre la imagen).
    print("\n[7] RESULTADO FINAL (replica ecg.py — imagen completa)")
    main_class = full_class
    main_conf = full_conf
    print(f"    Fuente: preprocess_for_classification → imagen completa 128x128")
    if per_window_results:
        from collections import Counter
        win_classes = [r[0] for r in per_window_results]
        print(f"    (Info ventanas — solo anotacion, no afectan resultado)")
        print(f"    Clases de ventanas: {dict(Counter(win_classes))}")
        high = [(c, cf) for c, cf, _ in per_window_results if cf > 0.7]
        print(f"    Ventanas conf>0.7 que se mostrarian en anotacion: {len(high)}")

    print(f"\n    >>> RESULTADO FINAL: {main_class}  (confianza={main_conf:.3f})")

    if true_class:
        expected = CLASS_NAMES[FOLDER_NAMES.index(true_class)]
        ok = "CORRECTO" if main_class == expected else "INCORRECTO"
        print(f"    >>> Esperado        : {expected}")
        print(f"    >>> {ok}")

    # --- PASO 8: Figura de diagnostico ---
    if save_fig:
        _save_diagnostic_figure(
            image_path, raw, y_start, y_end, win_w, step,
            windows, normalized_windows, per_window_results,
            full_arr, full_class, full_conf, full_probs,
            main_class, main_conf, true_class
        )

    return main_class, main_conf


def _save_diagnostic_figure(image_path, raw, y_start, y_end, win_w, step,
                              windows, normalized_windows, per_window_results,
                              full_arr, full_class, full_conf, full_probs,
                              main_class, main_conf, true_class):
    """Guarda figura con imagen original + ventanas + probabilidades."""
    n_windows = min(len(windows), 6)
    cols = max(n_windows + 2, 4)
    fig, axes = plt.subplots(3, cols, figsize=(cols * 2.5, 8))

    # Fila 0: imagen original con rectángulos de ventanas
    ax_orig = axes[0, 0]
    ax_orig.imshow(raw, cmap="gray", vmin=0, vmax=255)
    ax_orig.axhline(y_start, color="cyan", linewidth=1, linestyle="--")
    ax_orig.axhline(y_end, color="cyan", linewidth=1, linestyle="--")
    for i, (x, y_center, rh) in enumerate(
        [(x, yc, rh) for (x, yc, rh) in
         [c for _, c in zip(windows, [(x, yc, rh) for (x, yc, rh) in
          [(x, y_start + (y_end - y_start) // 2, y_end - y_start)
           for x in range(0, raw.shape[1] - win_w + 1, step)]])][:n_windows]]
    ):
        rect = patches.Rectangle(
            (x, y_center - rh // 2), win_w, rh,
            linewidth=1.5, edgecolor=f"C{i}", facecolor="none"
        )
        ax_orig.add_patch(rect)
        ax_orig.text(x + 2, y_center - rh // 2 - 3, str(i), color=f"C{i}", fontsize=8)
    ax_orig.set_title(f"Original\n{raw.shape[1]}x{raw.shape[0]}", fontsize=8)
    ax_orig.axis("off")

    # Imagen completa preprocesada (fallback)
    ax_full = axes[0, 1]
    ax_full.imshow(full_arr, cmap="gray", vmin=0, vmax=1)
    ax_full.set_title(f"Full preproc\n→ {full_class}\n{full_conf:.2f}", fontsize=8)
    ax_full.axis("off")

    # Filas 1-2: ventanas raw y normalizadas
    for i in range(cols):
        for row in range(3):
            if i >= 2 or row == 0:
                ax = axes[row, i] if i < cols else None
                if ax and row > 0:
                    ax.axis("off")

    for i in range(n_windows):
        col = i + 2
        if col < cols:
            # Fila 1: ventana raw
            axes[1, col].imshow(windows[i], cmap="gray", vmin=0, vmax=255)
            pred_c, conf, _ = per_window_results[i] if i < len(per_window_results) else ("?", 0, None)
            axes[1, col].set_title(f"Win {i} raw\n{windows[i].shape}", fontsize=7)
            axes[1, col].axis("off")

            # Fila 2: ventana normalizada + prediccion
            if i < len(normalized_windows):
                axes[2, col].imshow(normalized_windows[i], cmap="gray", vmin=0, vmax=1)
                color = "green" if conf > 0.7 else "red"
                axes[2, col].set_title(f"→ {pred_c}\n{conf:.2f}", fontsize=7, color=color)
                axes[2, col].axis("off")

    # Fila 2, col 0-1: barras de probabilidad
    ax_bar = axes[2, 0]
    if per_window_results:
        avg_probs = np.mean([r[2] for r in per_window_results], axis=0)
    else:
        avg_probs = full_probs
    bars = ax_bar.bar(FOLDER_NAMES, avg_probs, color=["green" if v == avg_probs.max() else "steelblue" for v in avg_probs])
    ax_bar.set_ylim(0, 1)
    ax_bar.set_title("Prob promedio\nventanas", fontsize=8)
    ax_bar.tick_params(axis='both', labelsize=7)
    for bar, val in zip(bars, avg_probs):
        ax_bar.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f"{val:.2f}", ha="center", va="bottom", fontsize=6)

    ax_bar2 = axes[1, 0]
    bars2 = ax_bar2.bar(FOLDER_NAMES, full_probs,
                        color=["green" if v == full_probs.max() else "steelblue" for v in full_probs])
    ax_bar2.set_ylim(0, 1)
    ax_bar2.set_title("Prob img completa\n(fallback)", fontsize=8)
    ax_bar2.tick_params(axis='both', labelsize=7)

    axes[1, 1].axis("off")
    axes[2, 1].axis("off")

    true_str = f"  (real={true_class})" if true_class else ""
    ok_str = ""
    if true_class:
        expected = CLASS_NAMES[FOLDER_NAMES.index(true_class)]
        ok_str = " ✓" if main_class == expected else " ✗"
    fig.suptitle(
        f"{Path(image_path).name}{true_str}\n"
        f"Resultado: {main_class} ({main_conf:.2f}){ok_str}",
        fontsize=10, fontweight="bold"
    )
    plt.tight_layout()
    out_name = OUT_DIR / f"diag_{Path(image_path).stem}.png"
    plt.savefig(out_name, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"\n    [FIGURA] Guardada en: {out_name}")


# ---------------------------------------------------------------------------
# Reporte de resumen multi-imagen
# ---------------------------------------------------------------------------

def run_batch(images_by_class: dict, save_figs: bool = True):
    """Clasifica múltiples imágenes y muestra resumen de aciertos por clase."""
    print("\n" + "=" * 70)
    print("  RESUMEN POR CLASE")
    print("=" * 70)

    results = {}
    for true_folder, paths in images_by_class.items():
        true_class_name = CLASS_NAMES[FOLDER_NAMES.index(true_folder)]
        correct = 0
        for path in paths:
            pred, conf = diagnose_image(path, true_class=true_folder, save_fig=save_figs)
            if pred == true_class_name:
                correct += 1
        results[true_folder] = (correct, len(paths))

    print("\n" + "=" * 70)
    print("  TABLA DE ACIERTOS")
    print("=" * 70)
    print(f"  {'Clase':>5}  {'Nombre app':>25}  {'Aciertos':>10}")
    print(f"  {'-'*50}")
    for folder, (correct, total) in results.items():
        name = CLASS_NAMES[FOLDER_NAMES.index(folder)]
        pct = correct / total * 100 if total else 0
        print(f"  {folder:>5}  {name:>25}  {correct}/{total} ({pct:.0f}%)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Test pipeline de clasificacion ECG")
    parser.add_argument("--image", type=str, default=None,
                        help="Ruta a imagen especifica para diagnosticar")
    parser.add_argument("--class", dest="ecg_class", type=str, default=None,
                        help="Clase a testear del dataset (F/M/N/Q/S/V)")
    parser.add_argument("--n", type=int, default=2,
                        help="Numero de imagenes por clase a testear (default=2)")
    parser.add_argument("--all-classes", action="store_true",
                        help="Testear N imagenes de TODAS las clases")
    parser.add_argument("--no-figs", action="store_true",
                        help="No guardar figuras de diagnostico")
    args = parser.parse_args()

    save_figs = not args.no_figs

    if args.image:
        # Imagen especifica
        true_class = None
        for folder in FOLDER_NAMES:
            if f"/{folder}/" in args.image or f"/{folder}0" in Path(args.image).name:
                true_class = folder
                break
        diagnose_image(args.image, true_class=true_class, save_fig=save_figs)

    elif args.all_classes:
        # Todas las clases
        images_by_class = {}
        for folder in FOLDER_NAMES:
            folder_path = DATASET_PATH / folder
            if not folder_path.exists():
                continue
            imgs = sorted(folder_path.glob("*.png"))[:args.n] + \
                   sorted(folder_path.glob("*.jpg"))[:args.n]
            imgs = imgs[:args.n]
            if imgs:
                images_by_class[folder] = [str(p) for p in imgs]
        run_batch(images_by_class, save_figs=save_figs)

    elif args.ecg_class:
        # Clase especifica
        folder = args.ecg_class.upper()
        if folder not in FOLDER_NAMES:
            print(f"[ERROR] Clase invalida: {folder}. Opciones: {FOLDER_NAMES}")
            sys.exit(1)
        folder_path = DATASET_PATH / folder
        imgs = sorted(folder_path.glob("*.png"))[:args.n] + \
               sorted(folder_path.glob("*.jpg"))[:args.n]
        imgs = [str(p) for p in imgs[:args.n]]
        run_batch({folder: imgs}, save_figs=save_figs)

    else:
        # Default: 2 imagenes de cada clase critica (N, V, S)
        print("\n[INFO] Modo default: 2 imagenes de clases N, V, S")
        print("[INFO] Usa --all-classes para todas las clases")
        images_by_class = {}
        for folder in ["N", "V", "S", "F"]:
            folder_path = DATASET_PATH / folder
            if not folder_path.exists():
                continue
            imgs = sorted(folder_path.glob("*.png"))[:2]
            if imgs:
                images_by_class[folder] = [str(p) for p in imgs]
        run_batch(images_by_class, save_figs=save_figs)

    print(f"\n[INFO] Figuras guardadas en: {OUT_DIR}/")


if __name__ == "__main__":
    main()
