"""
ML Model loading and inference manager.
Handles loading Keras/TensorFlow model and predictions.
"""

import numpy as np
import tensorflow as tf
from typing import Optional
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


# Custom layers for Hybrid CNN LSTM Attention model - FROM TRAINED MODEL
class AttentionLayer(tf.keras.layers.Layer):
    """Capa de atención temporal para enfoque en regiones relevantes del ECG"""
    
    def __init__(self, units=128, **kwargs):
        super().__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        self.W_q = self.add_weight(
            name='W_q',
            shape=(input_shape[-1], self.units), 
            initializer='glorot_uniform',
            trainable=True
        )
        self.W_k = self.add_weight(
            name='W_k',
            shape=(input_shape[-1], self.units), 
            initializer='glorot_uniform',
            trainable=True
        ) 
        self.W_v = self.add_weight(
            name='W_v',
            shape=(input_shape[-1], self.units), 
            initializer='glorot_uniform',
            trainable=True
        )
        self.dense = tf.keras.layers.Dense(input_shape[-1])
        super().build(input_shape)

    def call(self, inputs):
        Q = tf.matmul(inputs, self.W_q)
        K = tf.matmul(inputs, self.W_k)
        V = tf.matmul(inputs, self.W_v)
        
        attn = tf.matmul(Q, K, transpose_b=True)
        attn = attn / tf.sqrt(tf.cast(self.units, tf.float32))
        w = tf.nn.softmax(attn, axis=-1)
        out = tf.matmul(w, V)
        
        return self.dense(out) + inputs  # Residual connection

    def get_config(self):
        config = super().get_config()
        config.update({"units": self.units})
        return config


class SpatialAttentionLayer(tf.keras.layers.Layer):
    """Capa de atención espacial para enfoque en regiones de señal ECG"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def build(self, input_shape):
        self.conv1 = tf.keras.layers.Conv2D(64, (3, 3), padding='same', activation='relu')
        self.conv2 = tf.keras.layers.Conv2D(1, (1, 1), padding='same', activation='sigmoid')
        super().build(input_shape)

    def call(self, x):
        m = self.conv1(x)
        m = self.conv2(m)
        return x * m
    
    def get_config(self):
        config = super().get_config()
        return config


class F1Score(tf.keras.metrics.Metric):
    """Métrica F1 personalizada para datasets desbalanceados de ECG"""
    
    def __init__(self, name='f1_score', **kwargs):
        super().__init__(name=name, **kwargs)
        self.precision_metric = tf.keras.metrics.Precision()
        self.recall_metric = tf.keras.metrics.Recall()

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.precision_metric.update_state(y_true, y_pred, sample_weight)
        self.recall_metric.update_state(y_true, y_pred, sample_weight)

    def result(self):
        p = self.precision_metric.result()
        r = self.recall_metric.result()
        return 2 * ((p * r) / (p + r + tf.keras.backend.epsilon()))

    def reset_state(self):
        self.precision_metric.reset_state()
        self.recall_metric.reset_state()


def focal_loss(gamma=2.0, alpha=None):
    """Función de pérdida Focal Loss para clases minoritarias de arritmias"""
    def focal(y_true, y_pred):
        eps = 1e-7
        y_pred = tf.clip_by_value(y_pred, eps, 1.0 - eps)
        ce = -y_true * tf.math.log(y_pred)
        
        if alpha is not None:
            alpha_tensor = tf.constant(alpha, dtype=tf.float32)
            alpha_weight = tf.reduce_sum(alpha_tensor * y_true, axis=1)
            weight = alpha_weight[:, None] * tf.pow(1 - y_pred, gamma)
        else:
            weight = tf.pow(1 - y_pred, gamma)
            
        fl = weight * ce
        return tf.reduce_mean(tf.reduce_sum(fl, axis=1))
    
    return focal


class ModelManager:
    """Singleton class to manage ML model lifecycle."""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize model manager and load model if not already loaded."""
        if self._model is None:
            self.load_model()

    def load_model(self):
        """Load Keras model from file with custom objects."""
        try:
            # Define custom objects for the Hybrid model (matching training implementation)
            custom_objects = {
                'AttentionLayer': AttentionLayer,
                'SpatialAttentionLayer': SpatialAttentionLayer,
                'F1Score': F1Score,
                'focal_loss': focal_loss(),
                'focal': focal_loss()  # Alternative name used in some models
            }
            
            # Load with compile=False and custom objects
            self._model = tf.keras.models.load_model(
                settings.MODEL_PATH,
                custom_objects=custom_objects,
                compile=False
            )
            logger.info(f"Model loaded successfully from {settings.MODEL_PATH}")
            logger.info(f"Model input shape: {self._model.input_shape}")
            logger.info(f"Model output shape: {self._model.output_shape}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    def predict(self, image_array: np.ndarray) -> tuple[str, float]:
        """
        Predict arrhythmia class from image array.

        Args:
            image_array: Preprocessed image as numpy array (128x128)

        Returns:
            Tuple of (predicted_class, confidence)
        """
        if self._model is None:
            raise RuntimeError("Model not loaded")

        try:
            # Add batch dimension if needed
            if len(image_array.shape) == 2:
                image_array = np.expand_dims(image_array, axis=0)
                image_array = np.expand_dims(image_array, axis=-1)
            elif len(image_array.shape) == 3:
                image_array = np.expand_dims(image_array, axis=0)

            # Make prediction
            prediction = self._model.predict(image_array, verbose=0)
            
            # Get class and confidence
            class_idx = np.argmax(prediction[0])
            confidence = float(prediction[0][class_idx])

            # Map index to class name (MIT-BIH beat types)
            # Model has 6 outputs, though typically uses 5 main classes
            class_names = [
                "normal",                      # 0: Normal beat
                "supraventricular_ectopic",   # 1: Supraventricular ectopic beat
                "ventricular_ectopic",        # 2: Ventricular ectopic beat
                "fusion",                      # 3: Fusion beat
                "unknown",                     # 4: Unknown beat
                "paced",                       # 5: Paced beat (additional class)
            ]
            
            # Safety check for index
            if class_idx >= len(class_names):
                logger.warning(f"Model predicted unexpected class index {class_idx}. Using 'normal' as fallback.")
                predicted_class = "normal"
            else:
                predicted_class = class_names[class_idx]
            
            logger.info(f"Prediction: class_idx={class_idx}, class={predicted_class}, confidence={confidence:.2f}")
            
            return predicted_class, confidence
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise

    def get_model(self):
        """Get the loaded model instance."""
        return self._model


def get_model_manager() -> ModelManager:
    """Get singleton instance of ModelManager."""
    return ModelManager()
