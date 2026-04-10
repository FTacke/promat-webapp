param(
	[switch]$SkipInstall,
	[switch]$SkipDevServer,
	[switch]$ResetAuth,
	[string]$StartAdminPassword = 'change-me'
)

$ErrorActionPreference = 'Stop'

$appRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent $appRoot
$composeFile = Join-Path $workspaceRoot 'docker-compose.dev-postgres.yml'

function Wait-ForLocalDevPostgres {
	param(
		[string]$ComposeFilePath,
		[string]$DockerExecutable
	)

	for ($attempt = 1; $attempt -le 30; $attempt++) {
		& $DockerExecutable compose -f $ComposeFilePath exec -T promat_auth_db pg_isready -U promat_auth -d promat_auth *> $null
		if ($LASTEXITCODE -eq 0) {
			return
		}
		Start-Sleep -Seconds 1
	}

	throw 'Lokale PostgreSQL-Dev-Datenbank wurde nicht rechtzeitig bereit. Bitte Docker-Status prüfen.'
}

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

$dirs = @(
	(Join-Path $workspaceRoot 'data\config'),
	(Join-Path $workspaceRoot 'data\sessions'),
	(Join-Path $workspaceRoot 'data\db\postgres_dev'),
	(Join-Path $workspaceRoot 'logs'),
	(Join-Path $workspaceRoot 'public'),
	(Join-Path $workspaceRoot 'secure')
)
foreach ($dir in $dirs) {
	if (-not (Test-Path $dir)) {
		New-Item -ItemType Directory -Path $dir -Force | Out-Null
	}
}

if (Get-Command docker -ErrorAction SilentlyContinue) {
	$docker = (Get-Command docker -ErrorAction SilentlyContinue | Select-Object -First 1).Source
	& $docker compose -f $composeFile up -d promat_auth_db
	if ($LASTEXITCODE -ne 0) {
		throw 'Failed to start promat_auth_db via docker compose.'
	}
	Wait-ForLocalDevPostgres -ComposeFilePath $composeFile -DockerExecutable $docker
}

if (-not $SkipInstall) {
	Write-Host 'Hinweis: Python-Abhaengigkeiten bitte in der aktiven Umgebung mit requirements.txt installieren.' -ForegroundColor Yellow
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

& $pythonSource (Join-Path $appRoot 'scripts\apply_auth_migration.py') --engine postgres $(if ($ResetAuth) { '--reset' })
if ($LASTEXITCODE -ne 0) {
	throw 'Auth-Migration fehlgeschlagen.'
}

if ($StartAdminPassword) {
	& $pythonSource (Join-Path $appRoot 'scripts\create_initial_admin.py') --password $StartAdminPassword
	if ($LASTEXITCODE -ne 0) {
		throw 'Initialer Admin konnte nicht angelegt werden.'
	}
}

if (-not $SkipDevServer) {
	& $PSScriptRoot\dev-start.ps1 -SkipBootstrap
}