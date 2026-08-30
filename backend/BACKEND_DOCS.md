# Sonar Sentry Backend — Architecture & Integration Guide

## Quick Start

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # edit if needed
uvicorn app.main:app --reload --port 8000
```

Verify: `GET http://127.0.0.1:8000/api/health`

Interactive docs: `http://127.0.0.1:8000/docs`

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app factory + lifespan
│   ├── config.py                  # Pydantic Settings (env-based)
│   ├── database.py                # SQLAlchemy engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   └── orm.py                 # Run, Detection, Report ORM models
│   ├── schemas/
│   │   ├── ml.py                  # PreprocessedInput, PredictionResult, Detection, ModelMetadata
│   │   ├── response.py            # HealthResponse, PredictionResponse, ErrorResponse
│   │   ├── detection.py           # DetectResponse, DetectionItem, RiskLevel, ProcessingStatus
│   │   ├── run.py                 # RunSummary, RunDetail, RunListResponse
│   │   ├── report.py              # ReportItem, ReportDetail, ReportListResponse
│   │   └── upload.py              # UploadMetadata, DetectionSettings
│   ├── services/
│   │   ├── model_service.py       # ABC interface for model implementations
│   │   ├── mock_model_service.py  # Mock model (deterministic, multi-detection)
│   │   ├── sonar_model_service.py # Placeholder for real model (NotImplementedError)
│   │   ├── inference_service.py   # Orchestrates preprocessing → model
│   │   ├── factory.py             # Creates InferenceService based on MODEL_PROVIDER
│   │   ├── result_normalizer.py   # Raw model output → normalized DetectionItems
│   │   ├── storage_service.py     # File upload/output management
│   │   └── report_service.py      # Report CRUD + pagination
│   ├── preprocessing/
│   │   ├── base.py                # Preprocessor ABC
│   │   └── identity_preprocessor.py  # No-op preprocessor (placeholder)
│   ├── repositories/
│   │   ├── run_repository.py      # Run DB operations
│   │   ├── detection_repository.py # Detection DB operations
│   │   └── report_repository.py   # Report DB operations (filter, search, paginate)
│   └── api/
│       ├── exceptions.py          # Exception hierarchy + handler
│       └── routes/
│           ├── health.py          # GET /api/health, GET /health
│           ├── detect.py          # POST /api/detect
│           ├── runs.py            # GET /api/runs, GET /api/runs/{id}
│           ├── reports.py         # GET /api/reports, GET /api/reports/{id}
│           └── predict.py         # POST /api/predict (legacy, kept)
├── tests/
│   ├── conftest.py                # Fresh SQLite per test
│   ├── test_health_api.py
│   ├── test_detect_api.py
│   ├── test_runs_api.py
│   ├── test_reports_api.py
│   ├── test_normalizer.py
│   ├── test_storage.py
│   ├── test_health.py             # Original tests (updated)
│   ├── test_predict.py            # Original tests (updated)
│   ├── test_model_service.py
│   ├── test_inference_service.py
│   ├── test_preprocessing.py
│   └── test_factory.py
├── requirements.txt
├── .env.example
└── Dockerfile
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PROVIDER` | `mock` | `mock` or `sonar` |
| `MODEL_PATH` | `""` | Path to model weights (for sonar provider) |
| `MODEL_VERSION` | `development` | Version reported by health endpoint |
| `MAX_FILE_SIZE_MB` | `500` | Maximum upload size |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | CORS allowed origin |
| `DATABASE_URL` | `sqlite:///./sonar_sentry.db` | Database connection string |
| `UPLOAD_DIR` | `./data/uploads` | Where sonar files are stored |
| `OUTPUT_DIR` | `./data/outputs` | Where processed outputs go |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | CORS origins list |
| `DEBUG` | `false` | Enable SQLAlchemy query logging |

---

## API Endpoints

### `GET /api/health`

Returns backend status, model readiness, and database connectivity.

```json
{
  "status": "ok",
  "model": {
    "provider": "mock",
    "loaded": true,
    "name": "sonar-model",
    "version": "development"
  },
  "database": {
    "status": "ok"
  }
}
```

### `POST /api/detect`

Primary production endpoint. Accepts multipart/form-data.

**Request fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | yes | Sonar image (JPEG, PNG, TIFF) |
| `latitude` | float | yes | -90 to 90 |
| `longitude` | float | yes | -180 to 180 |
| `sonar_type` | string | yes | `Side-Scan`, `Multibeam`, or `Synthetic Aperture` |
| `resolution` | string | yes | `0.1 m/px`, `0.5 m/px`, or `1 m/px` |
| `depth_min` | float | yes | Minimum depth in metres (>= 0) |
| `depth_max` | float | yes | Maximum depth in metres (> depth_min) |
| `confidence_threshold` | int | no | 50–95 (default 78) |
| `selected_classes` | string | no | Comma-separated (default `Debris,Shipwreck`) |
| `min_object_size` | int | no | 10–200 (default 40) |

**Response (200):**

```json
{
  "success": true,
  "run_id": "uuid",
  "mission_id": "MSN-xxxx",
  "status": "completed",
  "scan_metadata": {
    "filename": "sonar_scan.jpg",
    "file_size_bytes": 504,
    "latitude": 12.9716,
    "longitude": 80.2436,
    "sonar_type": "Side-Scan",
    "resolution": "0.5 m/px",
    "depth_min": 4.0,
    "depth_max": 38.0
  },
  "detection_summary": {
    "total": 4,
    "high_risk": 2,
    "medium_risk": 0,
    "low_risk": 2,
    "critical_risk": 1,
    "avg_confidence": 0.74
  },
  "detections": [
    {
      "detection_id": "uuid",
      "class_label": "Rock Formation",
      "confidence": 0.86,
      "risk_level": "high",
      "bbox": { "x": 111.0, "y": 177.0, "width": 151.0, "height": 111.0 },
      "depth_m": 13.1,
      "area_m2": 167.6,
      "position_info": "MOCK_POSITION_1"
    }
  ],
  "model": {
    "name": "sonar-model",
    "version": "development",
    "provider": "mock"
  },
  "timestamps": {
    "started_at": "2026-08-30T10:09:26.767450+00:00",
    "completed_at": "2026-08-30T10:09:26.795632+00:00",
    "duration_seconds": 0.028
  }
}
```

### `GET /api/runs`

List detection runs with pagination.

**Query params:** `page` (default 1), `page_size` (default 20), `status`

```json
{
  "items": [
    {
      "run_id": "uuid",
      "mission_id": "MSN-7631",
      "filename": "sonar_scan.jpg",
      "status": "completed",
      "detection_count": 4,
      "file_size_bytes": 504,
      "created_at": "2026-08-30T10:09:26.776011",
      "updated_at": "2026-08-30T10:09:26.815025"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total": 1, "total_pages": 1 }
}
```

### `GET /api/runs/{run_id}`

Full run detail with all detections.

### `GET /api/reports`

Paginated, filterable report list.

**Query params:** `page`, `page_size` (default 8), `search`, `status`, `date_from`, `date_to`, `region`, `sort`, `order`

```json
{
  "items": [
    {
      "report_id": "uuid",
      "run_id": "uuid",
      "mission_id": "MSN-7631",
      "mission_name": "Side-Scan Survey — sonar_scan.jpg",
      "filename": "sonar_scan.jpg",
      "scan_date": "30 Aug 2026",
      "anomaly_count": 4,
      "high_risk_count": 2,
      "medium_risk_count": 0,
      "low_risk_count": 2,
      "status": "completed",
      "confidence": 74.2,
      "region": null,
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "pagination": { "page": 1, "page_size": 8, "total": 1, "total_pages": 1 }
}
```

### `GET /api/reports/{report_id}`

Single report detail.

### `POST /api/predict`

Legacy endpoint kept for backward compatibility. Accepts only `file` (JPEG/PNG). Returns single-label prediction.

---

## Processing States

Defined as `ProcessingStatus` enum, used consistently across runs, detections, and reports:

| State | Description |
|-------|-------------|
| `queued` | Created, waiting to be processed |
| `processing` | Inference in progress |
| `completed` | Inference finished successfully |
| `failed` | Inference encountered an error |
| `flagged` | Completed, flagged for human review |
| `reviewed` | Human has reviewed the results |

---

## Error Responses

All errors follow a consistent structure:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "Only JPEG and PNG images are supported."
  }
}
```

| HTTP Code | Error Code | Description |
|-----------|------------|-------------|
| 400 | `NO_FILE` | No file provided |
| 400 | `INVALID_FILE_TYPE` | Unsupported file format |
| 400 | `FILE_TOO_LARGE` | Exceeds MAX_FILE_SIZE_MB |
| 400 | `INVALID_METADATA` | Invalid coordinates, depths, sonar type, or resolution |
| 500 | `PREPROCESSING_FAILED` | Image preprocessing error |
| 500 | `INFERENCE_FAILED` | Model inference error |
| 503 | `MODEL_UNAVAILABLE` | Model not loaded |
| 404 | `RUN_NOT_FOUND` | Run ID does not exist |
| 404 | `REPORT_NOT_FOUND` | Report ID does not exist |

---

## Database

SQLite by default. Three tables with foreign-key relationships:

```
Run (id, mission_id, filename, file_path, status, latitude, longitude, ...)
  ├── Detection (id, run_id FK, class_label, confidence, risk_level, bbox_*, ...)
  └── Report (id, run_id FK UNIQUE, mission_name, scan_date, anomaly_count, ...)
```

Switch to PostgreSQL by changing `DATABASE_URL`:

```
DATABASE_URL=postgresql://user:pass@localhost:5432/sonar_sentry
```

---

## Storage

| Directory | Purpose |
|-----------|---------|
| `UPLOAD_DIR` (default `./data/uploads`) | Stored sonar images |
| `OUTPUT_DIR` (default `./data/outputs`) | Processed outputs |

Files are saved with UUID-based names to prevent collisions. The `StorageService` abstracts all file operations so storage backends can be swapped.

---

## Model Provider Architecture

```
MODEL_PROVIDER=mock
    └── MockModelService (deterministic, multi-detection, for dev/testing)

MODEL_PROVIDER=sonar
    └── SonarModelService (placeholder — raises NotImplementedError)
```

Both implement the same `ModelService` ABC:

```python
class ModelService(ABC):
    def load(self) -> None: ...
    def is_loaded(self) -> bool: ...
    def predict(self, input_data: PreprocessedInput) -> PredictionResult: ...
    def metadata(self) -> ModelMetadata: ...
```

### Data Flow

```
raw sonar bytes
       ↓
Preprocessor.process()
       ↓
PreprocessedInput
       ↓
ModelService.predict()
       ↓
PredictionResult (with detections list)
       ↓
ResultNormalizer.normalize()
       ↓
list[DetectionItem] + DetectionSummary
       ↓
API response (JSON)
```

---

## Integrating the Real Sonar Model

### Step 1: Create `sonar_model_service.py`

Replace the placeholder with the real implementation:

```python
class SonarModelService(ModelService):
    def __init__(self, model_path: str = ""):
        self._model_path = model_path
        self._loaded = False

    def load(self) -> None:
        # Load your model weights from self._model_path
        self._model = torch.load(self._model_path)
        self._loaded = True

    def predict(self, input_data: PreprocessedInput) -> PredictionResult:
        # input_data.data contains raw bytes
        # Convert to tensor, run inference, return PredictionResult
        tensor = preprocess(input_data.data)
        output = self._model(tensor)
        return PredictionResult(
            label=...,
            confidence=...,
            detections=[
                Detection(
                    class_label="Shipwreck",
                    confidence=0.95,
                    bbox=BBox(x=10, y=20, width=100, height=50),
                    depth_m=25.3,
                    area_m2=5.0,
                ),
            ],
        )
```

### Step 2: Create `SonarPreprocessor` (if needed)

```python
class SonarPreprocessor(Preprocessor):
    def process(self, raw_image_bytes: bytes) -> PreprocessedInput:
        # Decode, resize, normalize, convert to tensor
        return PreprocessedInput(data=tensor)
```

### Step 3: Update Factory

Add the sonar provider to `factory.py` (already wired):

```python
elif settings.model_provider == "sonar":
    from app.services.sonar_model_service import SonarModelService
    model = SonarModelService(model_path=settings.model_path)
```

### Step 4: Set Environment

```bash
MODEL_PROVIDER=sonar
MODEL_PATH=/path/to/model/weights.pth
```

### What You Will Need From the Colab Model

1. **ML framework** — PyTorch, TensorFlow, ONNX, etc.
2. **Model artifact format** — `.pth`, `.pt`, `.onnx`, `.h5`, SavedModel, etc.
3. **Input shape** — expected dimensions (e.g., `1 x 3 x 640 x 640`)
4. **Input dtype** — float32, uint8, etc.
5. **Channel ordering** — RGB, BGR, grayscale
6. **Exact preprocessing** — resize, crop, padding, normalization values
7. **Output format** — classification logits, bounding boxes, masks, heatmaps
8. **Class labels** — ordered list of class names
9. **Confidence behaviour** — softmax, sigmoid, raw scores
10. **CPU/GPU requirements** — device placement
11. **Model file location** — path to weights

---

## Testing

```bash
cd backend
pytest -v          # run all tests
pytest tests/test_detect_api.py -v    # detect endpoint tests
pytest tests/test_reports_api.py -v   # reports tests
```

**73 tests** covering:
- Health endpoint (3)
- Detect endpoint (10)
- Runs endpoint (6)
- Reports endpoint (7)
- Result normalizer (6)
- Storage service (6)
- Model service (8)
- Inference service (5)
- Preprocessing (5)
- Factory (3)
- Original predict endpoint (11)
- Health legacy (3)

All tests use mock model. No ML dependencies required.

---

## Frontend Integration

The frontend pages map to these endpoints:

| Page | Endpoint |
|------|----------|
| Launch | `POST /api/detect` |
| My Uploads | `GET /api/runs`, `GET /api/runs/{id}` |
| Detection Results | `GET /api/runs/{id}` |
| Reports | `GET /api/reports`, `GET /api/reports/{id}` |
| Settings | Local state (no API needed yet) |

The existing frontend uses hardcoded mock data and makes no API calls yet. When ready to integrate, replace the mock data with `fetch()` calls to these endpoints. The API contract is stable and will not change when the real model is integrated.

---

## Commands

```bash
# Start backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000

# Run tests
cd backend && pytest -v

# Start frontend
cd frontend && npm install && npm run dev

# Build frontend
cd frontend && npm run build
```
