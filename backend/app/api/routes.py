import uuid

from fastapi import APIRouter, File, Request, UploadFile

from app.api.exceptions import (
    FileTooLargeError,
    InferenceFailedError,
    InvalidFileTypeError,
    ModelUnavailableError,
    NoFileError,
    PreprocessingFailedError,
)
from app.config import get_settings
from app.schemas.response import (
    HealthResponse,
    ModelInfo,
    PredictionData,
    PredictionResponse,
)
from app.services.inference_service import InferenceService

router = APIRouter(tags=["health"])

_JPEG_MAGIC = b"\xff\xd8\xff"
_PNG_MAGIC = b"\x89PNG"
_ALLOWED_MIMES = {"image/jpeg", "image/png"}


@router.get("/health", response_model=HealthResponse)
def health_check(request: Request) -> HealthResponse:
    inference_service: InferenceService = request.app.state.inference_service
    return HealthResponse(
        status="ok",
        model_loaded=inference_service.is_model_loaded,
    )


@router.post("/api/predict", response_model=PredictionResponse)
async def predict(
    request: Request, file: UploadFile | None = File(default=None)
) -> PredictionResponse:
    inference_service: InferenceService = request.app.state.inference_service
    settings = get_settings()

    if file is None:
        raise NoFileError()

    content_type = (file.content_type or "").lower()
    if content_type not in _ALLOWED_MIMES:
        raise InvalidFileTypeError()

    contents = await file.read()
    if len(contents) == 0:
        raise NoFileError()

    if len(contents) > settings.max_file_size_mb * 1024 * 1024:
        raise FileTooLargeError()

    if not _has_valid_signature(contents, content_type):
        raise InvalidFileTypeError()

    if not inference_service.is_model_loaded:
        raise ModelUnavailableError()

    try:
        prediction_result = inference_service.predict(contents)
    except Exception:
        raise InferenceFailedError()

    model_meta = inference_service.metadata()

    return PredictionResponse(
        prediction=PredictionData(
            label=prediction_result.label,
            confidence=prediction_result.confidence,
            raw_scores=prediction_result.raw_scores,
        ),
        model=ModelInfo(
            name=model_meta.name,
            version=model_meta.version,
            provider=model_meta.provider,
        ),
        request_id=str(uuid.uuid4()),
    )


def _has_valid_signature(data: bytes, content_type: str) -> bool:
    """Validate magic bytes against the declared MIME type."""
    if content_type == "image/jpeg":
        return data[:3] == _JPEG_MAGIC
    if content_type == "image/png":
        return data[:4] == _PNG_MAGIC
    return False
