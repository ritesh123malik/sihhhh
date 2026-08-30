from fastapi import APIRouter, Request

from app.schemas.response import HealthResponse
from app.services.inference_service import InferenceService

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
@router.get("/health", response_model=HealthResponse)
def health_check(request: Request) -> HealthResponse:
    inference_service: InferenceService = request.app.state.inference_service

    db_status = "ok"
    try:
        from app.database import engine

        if engine is not None:
            with engine.connect() as conn:
                conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="ok",
        model={
            "provider": inference_service.metadata().provider,
            "loaded": inference_service.is_model_loaded,
            "name": inference_service.metadata().name,
            "version": inference_service.metadata().version,
        },
        database={"status": db_status},
    )
