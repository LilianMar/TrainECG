"""
Image preprocessing module for ECG images.
Handles image loading, resizing, normalization, and windowing.
"""

import cv2
import numpy as np
from typing import List, Tuple
from pathlib import Path
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ImagePreprocessor:
    """Handles ECG image preprocessing and windowing."""

    def __init__(
        self,
        image_size: int = settings.IMAGE_SIZE,
        window_size: int = settings.WINDOW_SIZE,
        overlap: float = settings.WINDOW_OVERLAP,
    ):
        """
        Initialize preprocessor.

        Args:
            image_size: Target image size
            window_size: Size of sliding windows
            overlap: Overlap ratio for sliding windows (0-1)
        """
        self.image_size = image_size
        self.window_size = window_size
        self.overlap = overlap
        self.stride = int(window_size * (1 - overlap))

    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load image from file.

        Args:
            image_path: Path to image file

        Returns:
            Loaded image as numpy array
        """
        try:
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image not found: {image_path}")

            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")

            return image
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            raise

    def resize_image(self, image: np.ndarray, size: int = None) -> np.ndarray:
        """
        Resize image to target size.

        Args:
            image: Input image array
            size: Target size (default: self.image_size)

        Returns:
            Resized image
        """
        if size is None:
            size = self.image_size

        try:
            resized = cv2.resize(image, (size, size), interpolation=cv2.INTER_CUBIC)
            return resized
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            raise

    def normalize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize image to 0-1 range.

        Args:
            image: Input image array

        Returns:
            Normalized image
        """
        return image.astype(np.float32) / 255.0

    def create_sliding_windows(
        self, image: np.ndarray
    ) -> Tuple[List[np.ndarray], List[Tuple[int, int]]]:
        """
        Create sliding windows from image.

        Args:
            image: Input image array

        Returns:
            Tuple of (list of windows, list of (x, y) coordinates)
        """
        windows = []
        coordinates = []

        height, width = image.shape[:2]

        for y in range(0, height - self.window_size + 1, self.stride):
            for x in range(0, width - self.window_size + 1, self.stride):
                window = image[
                    y : y + self.window_size, x : x + self.window_size
                ]
                windows.append(window)
                coordinates.append((x, y))

        return windows, coordinates

    def preprocess_pipeline(
        self, image_path: str
    ) -> Tuple[List[np.ndarray], List[Tuple[int, int]], np.ndarray]:
        """
        Complete preprocessing pipeline.

        Args:
            image_path: Path to ECG image

        Returns:
            Tuple of (preprocessed windows, coordinates, original resized image)
        """
        try:
            # Load image
            image = self.load_image(image_path)

            # Resize
            resized = self.resize_image(image)

            # Normalize
            normalized = self.normalize_image(resized)

            # Create sliding windows
            windows, coordinates = self.create_sliding_windows(normalized)

            return windows, coordinates, resized
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {str(e)}")
            raise


def get_preprocessor(
    image_size: int = settings.IMAGE_SIZE,
    window_size: int = settings.WINDOW_SIZE,
    overlap: float = settings.WINDOW_OVERLAP,
) -> ImagePreprocessor:
    """Get ImagePreprocessor instance."""
    return ImagePreprocessor(image_size, window_size, overlap)
