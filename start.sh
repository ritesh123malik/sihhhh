#!/usr/bin/env bash
set -e

echo "Starting SONARIS Backend Server..."
cd backend
pip install --no-cache-dir -r requirements.txt
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
