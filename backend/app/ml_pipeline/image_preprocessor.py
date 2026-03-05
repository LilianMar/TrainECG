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

    def detect_ecg_region(self, image: np.ndarray) -> Tuple[int, int]:
        """
        Automatically detect the vertical region where ECG signal is located.
        
        Args:
            image: Input image array (grayscale)
            
        Returns:
            Tuple of (y_start, y_end) for the ECG signal region
        """
        try:
            # Binarize to find signal
            _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                # If no contours found, use full height
                return 0, image.shape[0]
            
            # Get bounding rectangle of all contours
            all_points = np.vstack(contours)
            x, y, w, h = cv2.boundingRect(all_points)
            
            # Add padding
            padding = 10
            y_start = max(0, y - padding)
            y_end = min(image.shape[0], y + h + padding)
            
            logger.info(f"ECG region detected: y={y_start}-{y_end}")
            return y_start, y_end
            
        except Exception as e:
            logger.error(f"Error detecting ECG region: {str(e)}")
            return 0, image.shape[0]

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
        Normalize image to 0-1 range with preprocessing matching training.
        Applies GaussianBlur, normalization, and Otsu threshold.

        Args:
            image: Input image array

        Returns:
            Normalized and preprocessed image
        """
        try:
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(image, (3, 3), 0)
            
            # Normalize to 0-255 range
            normalized = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX)
            
            # Apply Otsu's thresholding
            _, thresholded = cv2.threshold(normalized.astype(np.uint8), 0, 255, cv2.THRESH_OTSU)
            
            # Scale to [0, 1] range
            return thresholded.astype(np.float32) / 255.0
        except Exception as e:
            logger.error(f"Error in normalize_image: {str(e)}")
            # Fallback to simple normalization
            return image.astype(np.float32) / 255.0

    def create_sliding_windows(
        self, image: np.ndarray, y_start: int, y_end: int
    ) -> Tuple[List[np.ndarray], List[Tuple[int, int, int]]]:
        """
        Create sliding windows from image.
        Creates horizontal sliding windows in the ECG signal region.

        Args:
            image: Input image array (original size)
            y_start: Starting y coordinate of ECG region
            y_end: Ending y coordinate of ECG region

        Returns:
            Tuple of (list of windows resized to model size, 
                     list of (x, y_center, region_height) coordinates in original image)
        """
        windows = []
        coordinates = []

        height, width = image.shape[:2]
        
        # Extract the ECG region (full height of signal area)
        ecg_region = image[y_start:y_end, :]
        region_height = y_end - y_start
        
        # Use fixed window width similar to original pipeline (150px or adaptive)
        window_width = min(150, width // 4)  # Horizontal window width
        step_size = max(30, window_width // 3)  # Horizontal step (creates overlap)
        
        logger.info(f"Window settings: width={window_width}, step={step_size}, region_height={region_height}")

        # Slide horizontally across the image
        x = 0
        while x + window_width <= width:
            # Extract window from ECG region (vertical = full ECG height, horizontal = sliding window)
            window = ecg_region[:, x:x + window_width]
            
            # Only keep windows with enough signal variation
            if window.std() > 10:
                # Resize window to model input size (128x128)
                window_resized = cv2.resize(
                    window,
                    (self.window_size, self.window_size),
                    interpolation=cv2.INTER_AREA
                )
                
                windows.append(window_resized)
                # Store coordinates in original image space
                # x is horizontal position, y is the center of the ECG region
                y_center = y_start + region_height // 2
                coordinates.append((x, y_center, region_height))
            
            x += step_size

        return windows, coordinates

    def preprocess_pipeline(
        self, image_path: str
    ) -> Tuple[List[np.ndarray], List[Tuple[int, int, int]], np.ndarray]:
        """
        Complete preprocessing pipeline.
        
        Steps:
        1. Load original image (no resizing)
        2. Detect ECG signal region (vertical bounds)
        3. Create sliding windows horizontally in that region
        4. Normalize each window
        
        Coordinates returned are in original image space:
        (x_start, y_center, height) where height is the ECG region height

        Args:
            image_path: Path to ECG image

        Returns:
            Tuple of (preprocessed windows, coordinates in original space, original image)
        """
        try:
            # Load image
            image = self.load_image(image_path)
            original_image = image.copy()

            # Detect ECG signal region (vertical bounds)
            y_start, y_end = self.detect_ecg_region(image)

            # Create sliding windows on original size image
            # Windows are created horizontally in the ECG region
            windows_raw, coordinates = self.create_sliding_windows(image, y_start, y_end)

            # Normalize each window
            windows_normalized = []
            for window in windows_raw:
                normalized = self.normalize_image(window)
                windows_normalized.append(normalized)

            return windows_normalized, coordinates, original_image
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

