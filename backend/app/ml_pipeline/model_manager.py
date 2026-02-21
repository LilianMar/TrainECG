"""
ML Model loading and inference manager.
Handles loading Keras/TensorFlow model and predictions.
"""

import numpy as np
from typing import Optional
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


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
        """Load Keras model from file."""
        try:
            import tensorflow as tf
            # Load with compile=False to avoid compatibility issues
            self._model = tf.keras.models.load_model(
                settings.MODEL_PATH,
                compile=False
            )
            logger.info(f"Model loaded successfully from {settings.MODEL_PATH}")
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

            # Map index to class name (6 classes based on model output)
            class_names = [
                "normal",
                "atrial_fibrillation",
                "ventricular_tachycardia",
                "av_block",
                "atrial_flutter",
                "sinus_bradycardia",  # 6th class
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
