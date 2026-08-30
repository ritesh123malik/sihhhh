Set-Location "$PSScriptRoot\frontend\sonar-sentry-main\sonar-sentry-main\backend"
python -m uvicorn app.main:app --reload --port 8000
