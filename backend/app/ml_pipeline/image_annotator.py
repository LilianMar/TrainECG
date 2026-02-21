"""
Image annotation module for ECG images.
Handles drawing bounding boxes and creating annotated images.
"""

import cv2
import numpy as np
import base64
from typing import List, Tuple
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ImageAnnotator:
    """Handles ECG image annotation with bounding boxes."""

    @staticmethod
    def draw_arrhythmia_windows(
        image_path: str,
        affected_windows: List[Tuple[int, int, int, int, float]],
        output_path: str = None,
    ) -> str:
        """
        Draw bounding boxes on ECG image for affected windows.

        Args:
            image_path: Path to original image
            affected_windows: List of (x, y, width, height, confidence) tuples
            output_path: Optional output path for annotated image

        Returns:
            Path to annotated image (or output_path if provided)
        """
        try:
            # Load original image in color
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")

            # Create a copy for annotation
            annotated = image.copy()

            # Color for arrhythmia detection (red)
            color = (0, 0, 255)  # BGR format
            thickness = 2

            # Draw rectangles for each affected window
            for x, y, width, height, confidence in affected_windows:
                # Draw rectangle
                cv2.rectangle(
                    annotated,
                    (x, y),
                    (x + width, y + height),
                    color,
                    thickness
                )

                # Add confidence label
                label = f"{confidence*100:.0f}%"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                
                # Background for text
                cv2.rectangle(
                    annotated,
                    (x, y - label_size[1] - 4),
                    (x + label_size[0], y),
                    color,
                    -1
                )
                
                # Text
                cv2.putText(
                    annotated,
                    label,
                    (x, y - 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )

            # Save annotated image
            if output_path is None:
                path = Path(image_path)
                output_path = str(path.parent / f"{path.stem}_annotated{path.suffix}")

            cv2.imwrite(output_path, annotated)
            logger.info(f"Annotated image saved to: {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Error annotating image: {str(e)}")
            raise

    @staticmethod
    def image_to_base64(image_path: str) -> str:
        """
        Convert image to base64 string for frontend display.

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded image string with data URI prefix
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            
            # Detect image format from extension
            ext = Path(image_path).suffix.lower()
            mime_type = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
            }.get(ext, "image/jpeg")
            
            return f"data:{mime_type};base64,{encoded_string}"

        except Exception as e:
            logger.error(f"Error converting image to base64: {str(e)}")
            raise

    @staticmethod
    def create_annotated_image_base64(
        image_path: str,
        affected_windows: List[Tuple[int, int, int, int, float]],
    ) -> Tuple[str, str]:
        """
        Create annotated image and return as base64 string.

        Args:
            image_path: Path to original image
            affected_windows: List of (x, y, width, height, confidence) tuples

        Returns:
            Tuple of (annotated_image_path, base64_string)
        """
        try:
            # Create annotated image
            annotated_path = ImageAnnotator.draw_arrhythmia_windows(
                image_path, affected_windows
            )
            
            # Convert to base64
            base64_image = ImageAnnotator.image_to_base64(annotated_path)
            
            return annotated_path, base64_image

        except Exception as e:
            logger.error(f"Error creating annotated base64 image: {str(e)}")
            raise


def get_image_annotator() -> ImageAnnotator:
    """Get ImageAnnotator instance."""
    return ImageAnnotator()
