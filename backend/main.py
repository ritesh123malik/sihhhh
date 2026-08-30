from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# Allow cross-origin requests from your future React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/get_anomalies")
def get_anomalies():
    # Serve the actionable, localized data formatted as structured JSON
    if os.path.exists("anomaly_report.csv"):
        df = pd.read_csv("anomaly_report.csv")
        return {"status": "success", "data": df.to_dict(orient="records")}
    return {"status": "error", "message": "Report not found."}