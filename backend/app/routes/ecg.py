"""
ECG classification routes.
"""

from collections import Counter
from pathlib import Path
import shutil
import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database import get_db
from app.ml_pipeline import get_gradcam, get_model_manager, get_preprocessor, get_image_annotator
from app.models.user import User
from app.routes.users import get_current_user
from app.schemas.ecg import ECGClassificationResponse, WindowCoordinate
from app.services.ecg_service import ECGService
from app.services.achievement_service import AchievementService
from app.services.progress_service import ProgressService
from app.services.llm_service import LLMService
from app.utils import (
    get_file_size_mb,
    get_logger,
    is_file_extension_allowed,
    sanitize_filename,
)

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/ecg", tags=["ECG Classification"])


def _ensure_upload_path(filename: str) -> Path:
    sanitized_filename = sanitize_filename(filename)
    upload_path = Path(settings.UPLOAD_DIR) / sanitized_filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    return upload_path


@router.post("/classify", response_model=ECGClassificationResponse)
async def classify_ecg(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Classify an ECG image.
    """
    start_time = time.perf_counter()

    try:
        if not is_file_extension_allowed(file.filename, settings.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Allowed: jpg, jpeg, png",
            )

        upload_path = _ensure_upload_path(file.filename)

        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = get_file_size_mb(str(upload_path))
        if file_size > settings.MAX_UPLOAD_SIZE_MB:
            upload_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max: {settings.MAX_UPLOAD_SIZE_MB}MB",
            )

        preprocessor = get_preprocessor()
        windows, coordinates, original_image = preprocessor.preprocess_pipeline(str(upload_path))
        if not windows:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid windows extracted from image",
            )
        
        # Get image dimensions
        img_height, img_width = original_image.shape[:2]
        
        # Window width is calculated inside preprocessor
        window_width = min(150, img_width // 4)

        model_manager = get_model_manager()
        predictions: list[tuple[str, float, int]] = []
        affected_windows: list[tuple[int, float]] = []

        for i, window in enumerate(windows):
            predicted_class, confidence = model_manager.predict(window)
            predictions.append((predicted_class, confidence, i))
            if confidence > 0.9:
                affected_windows.append((i, confidence))

        # Get most common class from HIGH-CONFIDENCE predictions only
        if affected_windows:
            high_conf_predictions = [predictions[i] for i, _ in affected_windows]
            classes = [p[0] for p in high_conf_predictions]
            main_class = Counter(classes).most_common(1)[0][0]
            main_confidence = (
                sum(p[1] for p in high_conf_predictions if p[0] == main_class) / len(high_conf_predictions)
            )
        else:
            # Fallback: no high-confidence predictions found
            classes = [p[0] for p in predictions]
            main_class = Counter(classes).most_common(1)[0][0]
            main_confidence = max(p[1] for p in predictions if p[0] == main_class)

        model = model_manager.get_model()
        grad_cam = get_gradcam(model)

        gradcam_windows: list[WindowCoordinate] = []
        affected_windows_data: list[tuple[int, int, int, int, float]] = []  # For annotation
        
        for window_idx, conf in affected_windows:
            x, y_center, region_height = coordinates[window_idx]
            
            # Calculate rectangle boundaries in original image space
            y_start = max(0, y_center - region_height // 2)
            y_end = min(img_height, y_center + region_height // 2)
            rect_height = y_end - y_start
            
            # heatmap = grad_cam.compute_gradcam(windows[window_idx])
            gradcam_windows.append(
                WindowCoordinate(
                    x=x,
                    y=y_start,
                    width=window_width,
                    height=rect_height,
                    confidence=float(conf),
                )
            )
            # Add to annotation data (x, y, width, height, confidence)
            affected_windows_data.append((x, y_start, window_width, rect_height, conf))

        # Create annotated image with bounding boxes on the ORIGINAL image
        annotated_image_base64 = None
        if affected_windows_data:
            try:
                image_annotator = get_image_annotator()
                _, annotated_image_base64 = image_annotator.create_annotated_image_base64(
                    str(upload_path), affected_windows_data
                )
            except Exception as e:
                logger.warning(f"Failed to create annotated image: {str(e)}")
                # Continue without annotated image

        # Generate LLM explanation for the classification
        llm_explanation = LLMService.generate_ecg_explanation(
            predicted_class=main_class,
            confidence=float(main_confidence),
            affected_windows=len(affected_windows),
            user_skill_level=current_user.skill_level or 2,
        )
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        classification = ECGService.create_classification(
            db=db,
            user_id=current_user.id,
            image_filename=upload_path.name,
            image_path=str(upload_path),
            predicted_class=main_class,
            confidence=float(main_confidence),
            windows_analyzed=len(windows),
            affected_windows=len(affected_windows),
            gradcam_windows=gradcam_windows,
            llm_explanation=llm_explanation,
            processing_time_ms=processing_time_ms,
        )

        # Check and unlock achievements
        newly_unlocked = AchievementService.check_and_unlock_badges(
            db=db,
            user_id=current_user.id,
            test_attempt_id=classification.id
        )

        # Update progress - increment ECGs analyzed
        ProgressService.update_progress(
            db=db,
            user_id=current_user.id,
            ecgs_analyzed=1
        )

        logger.info(
            "Classification created: %s for user %s",
            classification.id,
            current_user.id,
        )
        
        # Build response with annotated image
        response = ECGClassificationResponse(
            id=classification.id,
            predicted_class=classification.predicted_class,
            confidence=classification.confidence,
            windows_analyzed=classification.windows_analyzed,
            affected_windows=classification.affected_windows,
            gradcam_windows=gradcam_windows,
            annotated_image=annotated_image_base64,
            llm_explanation=classification.llm_explanation,
            processing_time_ms=classification.processing_time_ms,
            created_at=classification.created_at,
        )
        
        return response
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Classification error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Classification failed",
        ) from exc


@router.get("/history")
async def get_classification_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's classification history."""
    classifications = ECGService.get_user_classifications(db, current_user.id, limit)
    return {
        "total": len(classifications),
        "items": classifications,
    }
