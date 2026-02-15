"""
Grad-CAM (Gradient-weighted Class Activation Mapping) for model interpretability.
Generates visualization of regions that influenced the model's prediction.
"""

import numpy as np
import cv2
from typing import Tuple
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GradCAM:
    """Grad-CAM implementation for model explainability."""

    def __init__(self, model, layer_name: str = None):
        """
        Initialize Grad-CAM.

        Args:
            model: Keras model
            layer_name: Name of layer to use for Grad-CAM (last conv layer by default)
        """
        self.model = model
        self.layer_name = layer_name or self._get_last_conv_layer()

    def _get_last_conv_layer(self) -> str:
        """Get name of last convolutional layer."""
        for layer in reversed(self.model.layers):
            if "conv" in layer.name.lower():
                return layer.name
        raise ValueError("No convolutional layer found in model")

    def compute_gradcam(
        self, image: np.ndarray, class_idx: int = None
    ) -> np.ndarray:
        """
        Compute Grad-CAM heatmap.

        Args:
            image: Input image array (batch dimension required)
            class_idx: Index of class to compute gradients for

        Returns:
            Grad-CAM heatmap
        """
        try:
            import tensorflow as tf

            # Create model with output at target layer
            grad_model = tf.keras.models.Model(
                [self.model.inputs],
                [
                    self.model.get_layer(self.layer_name).output,
                    self.model.output,
                ],
            )

            with tf.GradientTape() as tape:
                conv_outputs, predictions = grad_model(image, training=False)
                if class_idx is None:
                    class_idx = tf.argmax(predictions[0])
                class_channel = predictions[:, class_idx]

            # Compute gradients
            grads = tape.gradient(class_channel, conv_outputs)

            # Average gradients over channels
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

            # Weight each channel by its gradient
            conv_outputs = conv_outputs[0]
            heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
            heatmap = tf.squeeze(heatmap)

            # Normalize to 0-1
            heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
            heatmap = heatmap.numpy()

            return heatmap

        except Exception as e:
            logger.error(f"Error computing Grad-CAM: {str(e)}")
            raise

    @staticmethod
    def overlay_heatmap(
        image: np.ndarray, heatmap: np.ndarray, alpha: float = 0.4
    ) -> np.ndarray:
        """
        Overlay Grad-CAM heatmap on original image.

        Args:
            image: Original image
            heatmap: Grad-CAM heatmap
            alpha: Transparency of overlay

        Returns:
            Image with heatmap overlay
        """
        # Resize heatmap to match image
        heatmap_resized = cv2.resize(
            heatmap, (image.shape[1], image.shape[0])
        )

        # Convert to color
        heatmap_color = cv2.applyColorMap(
            (heatmap_resized * 255).astype(np.uint8), cv2.COLORMAP_JET
        )

        # Normalize image if needed
        if image.max() <= 1.0:
            image_display = (image * 255).astype(np.uint8)
        else:
            image_display = image.astype(np.uint8)

        # Convert grayscale to BGR
        if len(image_display.shape) == 2:
            image_display = cv2.cvtColor(image_display, cv2.COLOR_GRAY2BGR)

        # Overlay
        overlay = cv2.addWeighted(
            image_display, 1 - alpha, heatmap_color, alpha, 0
        )

        return overlay


def get_gradcam(model, layer_name: str = None) -> GradCAM:
    """Get GradCAM instance."""
    return GradCAM(model, layer_name)
