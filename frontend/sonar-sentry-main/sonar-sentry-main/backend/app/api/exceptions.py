from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class PredictError(Exception):
    """Base for prediction-specific errors.

    Subclasses carry an HTTP status code and an error code/message pair
    that will be serialised into the standardised JSON error contract.
    """

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(self) -> None:
        super().__init__(self.message)


class NoFileError(PredictError):
    status_code = 400
    error_code = "NO_FILE"
    message = "No image file was provided."


class InvalidFileTypeError(PredictError):
    status_code = 400
    error_code = "INVALID_FILE_TYPE"
    message = "Only JPEG, PNG, and TIFF images are supported."


class FileTooLargeError(PredictError):
    status_code = 400
    error_code = "FILE_TOO_LARGE"
    message = "The uploaded file exceeds the maximum allowed size."


class PreprocessingFailedError(PredictError):
    status_code = 500
    error_code = "PREPROCESSING_FAILED"
    message = "Unable to preprocess the image."


class ModelUnavailableError(PredictError):
    status_code = 503
    error_code = "MODEL_UNAVAILABLE"
    message = "The prediction service is currently unavailable."


class InferenceFailedError(PredictError):
    status_code = 500
    error_code = "INFERENCE_FAILED"
    message = "Unable to analyze the image."


class InvalidMetadataError(PredictError):
    status_code = 400
    error_code = "INVALID_METADATA"
    message = "The provided metadata is invalid."

    def __init__(self, detail: str | None = None) -> None:
        if detail:
            self.message = detail
        super().__init__()


class RunNotFoundError(PredictError):
    status_code = 404
    error_code = "RUN_NOT_FOUND"
    message = "The requested run was not found."


class ReportNotFoundError(PredictError):
    status_code = 404
    error_code = "REPORT_NOT_FOUND"
    message = "The requested report was not found."


class DatabaseError(PredictError):
    status_code = 500
    error_code = "DATABASE_ERROR"
    message = "A database error occurred."


def register_exception_handler(application: FastAPI) -> None:
    """Attach a handler that converts ``PredictError`` into JSON responses."""

    @application.exception_handler(PredictError)
    async def _handle_predict_error(
        request: Request, exc: PredictError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {"code": exc.error_code, "message": exc.message},
            },
        )
