FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY frontend/sonar-sentry-main/sonar-sentry-main/backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY frontend/sonar-sentry-main/sonar-sentry-main/backend .
COPY frontend/sonar-sentry-main/sonar-sentry-main/model /app/model

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
