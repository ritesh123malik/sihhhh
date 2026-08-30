# Sonar Sentry — local product

This workspace is a complete local app: React UI, FastAPI backend, and the
wired model service. Nothing here depends on a GitHub remote.

## Run it

Terminal 1 (API):

```powershell
cd C:\SIH_FINAL_PROJECT\frontend\sonar-sentry-main\sonar-sentry-main\backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Terminal 2 (UI):

```powershell
cd C:\SIH_FINAL_PROJECT\frontend\sonar-sentry-main\sonar-sentry-main\frontend
npm install
npm run dev
```

Open http://localhost:5173

- UI talks to the API through the Vite `/api` proxy
- `POST /api/detect` runs preprocessing → model → detections → report
- `GET /api/runs` and `/api/reports` power My Uploads and Reports
- `GET /api/anomalies` also serves `backend/anomaly_report.csv` from this folder
- The live model provider is `mock` until a trained weights file is placed in `model/`

## Layout

- `frontend/sonar-sentry-main/sonar-sentry-main/frontend` — React app
- `frontend/sonar-sentry-main/sonar-sentry-main/backend` — FastAPI + SQLite
- `frontend/sonar-sentry-main/sonar-sentry-main/model` — model artifacts (optional)
- `backend/` — extra anomaly CSV/JSON used by `/api/anomalies`
