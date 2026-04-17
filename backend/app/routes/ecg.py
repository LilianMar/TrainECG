"""
ECG classification routes.
"""

import base64
from pathlib import Path
import shutil
import time

import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database import get_db
from app.ml_pipeline import get_model_manager, get_preprocessor
from app.ml_pipeline.grad_cam import get_gradcam
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

        # Read file content with size limit to prevent disk-filling DoS
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        content = await file.read(max_bytes + 1)
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max: {settings.MAX_UPLOAD_SIZE_MB}MB",
            )

        with open(upload_path, "wb") as buffer:
            buffer.write(content)

        preprocess_start = time.perf_counter()
        preprocessor = get_preprocessor()

        # 1. CLASIFICACIÓN — imagen completa preprocesada (Blur+Normalize+Otsu, 128×128)
        # Diagnóstico confirma: imagen completa → confianza 1.0 correcta.
        # Ventanas parciales → Otsu colapsa contenido a binario plano → votación incorrecta.
        full_arr, original_image = preprocessor.preprocess_for_classification(str(upload_path))
        img_height, img_width = original_image.shape[:2]

        # Coordenadas de bandas ECG para trazabilidad en respuesta/BD.
        _, coordinates, _ = preprocessor.preprocess_pipeline(str(upload_path))
        preprocess_time_ms = int((time.perf_counter() - preprocess_start) * 1000)

        # 2. INFERENCIA sobre imagen completa
        inference_start = time.perf_counter()
        model_manager = get_model_manager()
        main_class, main_confidence = model_manager.predict(full_arr)
        inference_time_ms = int((time.perf_counter() - inference_start) * 1000)

        # Bandas afectadas para explicación: marcar todas si confianza > 0.7
        affected_windows: list[tuple[int, float]] = [
            (i, main_confidence)
            for i in range(len(coordinates))
            if main_confidence > 0.7
        ]

        # 3. GRAD-CAM sobre imagen completa (mapa de calor sobre el trazo)
        gradcam_start = time.perf_counter()
        gradcam_image_base64: str | None = None
        try:
            gradcam = get_gradcam(model_manager.get_model())
            full_arr_4d = np.asarray(full_arr, dtype=np.float32)
            if full_arr_4d.ndim == 2:
                full_arr_4d = np.expand_dims(full_arr_4d, axis=0)
                full_arr_4d = np.expand_dims(full_arr_4d, axis=-1)
            elif full_arr_4d.ndim == 3:
                if full_arr_4d.shape[-1] == 1:
                    full_arr_4d = np.expand_dims(full_arr_4d, axis=0)
                else:
                    full_arr_4d = np.expand_dims(full_arr_4d, axis=-1)

            heatmap = gradcam.compute_gradcam(full_arr_4d)

            # Alinear Grad-CAM al trazo: usar la máscara binaria del mismo input
            # que ve el modelo (fondo blanco=1, trazo negro=0).
            trace_mask = 1.0 - full_arr_4d[0, :, :, 0]
            trace_mask = cv2.resize(
                trace_mask,
                (heatmap.shape[1], heatmap.shape[0]),
                interpolation=cv2.INTER_AREA,
            )
            heatmap = heatmap * trace_mask
            max_value = float(heatmap.max())
            if max_value > 0:
                heatmap = heatmap / max_value

            # Usar la misma imagen del preprocesador evita diferencias geométricas
            # con respecto al tensor de entrada del modelo.
            overlay_base = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
            overlay = gradcam.overlay_heatmap(overlay_base, heatmap, alpha=0.4)
            success, buffer = cv2.imencode(".png", overlay)
            if success:
                gradcam_image_base64 = (
                    "data:image/png;base64," + base64.b64encode(buffer).decode()
                )
        except Exception as e:
            logger.warning(f"Failed to compute Grad-CAM: {str(e)}")

        # Mantener coordenadas en respuesta/BD para trazabilidad histórica,
        # pero sin generar overlay de recuadros en la imagen final.
        gradcam_windows: list[WindowCoordinate] = []
        window_width = max(min(img_height, img_width), 64)

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
        gradcam_time_ms = int((time.perf_counter() - gradcam_start) * 1000)

        # 4. Método antiguo deshabilitado: no generar imagen con recuadros.
        annotate_start = time.perf_counter()
        annotated_image_base64 = None
        annotate_time_ms = int((time.perf_counter() - annotate_start) * 1000)

        # 5. GENERACIÓN LLM (OpenAI)
        llm_start = time.perf_counter()
        llm_explanation = LLMService.generate_ecg_explanation(
            predicted_class=main_class,
            confidence=float(main_confidence),
            affected_windows=len(affected_windows),
            user_skill_level=current_user.skill_level or 2,
        )
        llm_time_ms = int((time.perf_counter() - llm_start) * 1000)
        
        # Tiempo total
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)
        
        # Log tiempos por componente
        logger.info(
            "Pipeline timing: preprocess=%dms, inference=%dms, gradcam=%dms, annotate=%dms, llm=%dms, total=%dms",
            preprocess_time_ms, inference_time_ms, gradcam_time_ms, annotate_time_ms, llm_time_ms, processing_time_ms
        )

        classification = ECGService.create_classification(
            db=db,
            user_id=current_user.id,
            image_filename=upload_path.name,
            image_path=str(upload_path),
            predicted_class=main_class,
            confidence=float(main_confidence),
            windows_analyzed=len(coordinates),
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
            gradcam_image=gradcam_image_base64,
            llm_explanation=classification.llm_explanation,
            processing_time_ms=classification.processing_time_ms,
            is_fallback=model_manager.is_fallback_mode(),
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
