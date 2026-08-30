# Sonar Image Web Application

Web application for ML-based sonar image analysis:
**React frontend → FastAPI backend → preprocessing → model service → prediction → frontend**.

> **Status: Phase 1 scaffolding only.**
> The sonar ML model is still **under development**, separately in Google Colab.
> The backend does **not** contain the real model — a mock provider is wired in
> its place, and only `GET /health` is implemented.

## Architecture

```
project/
├── frontend/    React + Vite app (placeholder UI, proves it runs)
├── backend/
│   ├── app/api/             HTTP routes (currently /health only)
│   ├── app/preprocessing/   preprocessing interface (to be implemented)
│   ├── app/schemas/         Pydantic request/response schemas
│   ├── app/services/        ModelService abstraction + mock provider
│   └── tests/               pytest suite
└── model/       reserved for future model artifacts
```

The backend talks to models exclusively through the `ModelService` interface
(`load()`, `predict()`, `metadata()`), so the real sonar model can be plugged
in later without changing the API contract or the frontend.

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows (source .venv/bin/activate on Linux/macOS)
pip install -r requirements.txt
copy .env.example .env        # optional; sane defaults are built in
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000  ·  Docs: http://127.0.0.1:8000/docs
- Tests: `pytest`
- Docker: `docker build -t sonar-backend . && docker run -p 8000:8000 sonar-backend`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## Configuration

Environment variables (see `backend/.env.example`):

| Variable           | Default       | Purpose                        |
| ------------------ | ------------- | ------------------------------ |
| `MODEL_PROVIDER`   | `mock`        | Which model service to use     |
| `MODEL_PATH`       | _(empty)_     | Path to future model artifacts |
| `MODEL_VERSION`    | `development` | Reported model version         |
| `MAX_FILE_SIZE_MB` | `10`          | Future upload size limit       |
