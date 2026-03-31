param()

$ErrorActionPreference = 'Stop'

$appRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent $appRoot

if (-not $env:PROMAT_RUNTIME_ROOT) {
	$env:PROMAT_RUNTIME_ROOT = $workspaceRoot
}
if (-not $env:PROMAT_PUBLIC_ROOT) {
	$env:PROMAT_PUBLIC_ROOT = Join-Path $workspaceRoot 'public'
}
if (-not $env:AUTH_DATABASE_URL) {
	$env:AUTH_DATABASE_URL = 'postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:54321/promat_auth'
}
if (-not $env:FLASK_ENV) {
	$env:FLASK_ENV = 'development'
}
if (-not $env:FLASK_SECRET_KEY) {
	$env:FLASK_SECRET_KEY = 'dev-secret-change-me'
}
if (-not $env:JWT_SECRET_KEY) {
	$env:JWT_SECRET_KEY = 'dev-jwt-secret-change-me'
}

$workspacePython = Join-Path $workspaceRoot '.venv\Scripts\python.exe'
if (Test-Path $workspacePython) {
	$pythonSource = $workspacePython
}
else {
	$python = Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1
	if (-not $python) {
		throw 'Python wurde nicht gefunden. Bitte eine Python-Umgebung aktivieren.'
	}
	$pythonSource = $python.Source
}

Set-Location $appRoot
& $pythonSource -m src.app.main
exit $LASTEXITCODE