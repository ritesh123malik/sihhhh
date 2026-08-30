Set-Location "$PSScriptRoot\frontend\sonar-sentry-main\sonar-sentry-main\frontend"
if (-not (Test-Path node_modules)) { npm install }
npm run dev
