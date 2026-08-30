from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    model: dict | None = None
    database: dict | None = None
    model_loaded: bool | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    request_id: str | None = None


class ModelInfo(BaseModel):
    name: str
    version: str
    provider: str


class PredictionData(BaseModel):
    label: str
    confidence: float
    raw_scores: dict[str, float]


class PredictionResponse(BaseModel):
    success: bool = True
    prediction: PredictionData
    model: ModelInfo
    request_id: str
