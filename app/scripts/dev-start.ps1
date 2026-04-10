param(
	[switch]$SkipBootstrap
)

$ErrorActionPreference = 'Stop'

$appRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent $appRoot
$composeFile = Join-Path $workspaceRoot 'docker-compose.dev-postgres.yml'
$defaultAuthDatabaseUrl = 'postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:54321/promat_auth'

if (-not $env:PROMAT_RUNTIME_ROOT) {
	$env:PROMAT_RUNTIME_ROOT = $workspaceRoot
}
if (-not $env:PROMAT_PUBLIC_ROOT) {
	$env:PROMAT_PUBLIC_ROOT = Join-Path $workspaceRoot 'public'
}
if (-not $env:AUTH_DATABASE_URL) {
	$env:AUTH_DATABASE_URL = $defaultAuthDatabaseUrl
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

function Test-LocalDevPostgresUrl {
	param(
		[string]$DatabaseUrl,
		[string]$DefaultDatabaseUrl
	)

	if ($null -eq $DatabaseUrl) {
		$normalized = ''
	}
	else {
		$normalized = $DatabaseUrl.Trim()
	}
	if (-not $normalized) {
		return $false
	}

	if ($normalized -eq $DefaultDatabaseUrl) {
		return $true
	}

	return $normalized -match '^postgresql(\+psycopg2|\+psycopg)?://[^@]+@(127\.0\.0\.1|localhost):54321/promat_auth(?:\?.*)?$'
}

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

$shouldBootstrapLocalPostgres = (-not $SkipBootstrap) -and ($env:FLASK_ENV -eq 'development') -and (Test-LocalDevPostgresUrl -DatabaseUrl $env:AUTH_DATABASE_URL -DefaultDatabaseUrl $defaultAuthDatabaseUrl)

if ($shouldBootstrapLocalPostgres) {
	$docker = Get-Command docker -ErrorAction SilentlyContinue | Select-Object -First 1
	if ($docker -and (Test-Path $composeFile)) {
		& $docker.Source compose -f $composeFile up -d promat_auth_db
		if ($LASTEXITCODE -ne 0) {
			throw 'Lokale promat_auth_db konnte nicht per docker compose gestartet werden.'
		}
		Wait-ForLocalDevPostgres -ComposeFilePath $composeFile -DockerExecutable $docker.Source
	}

	& $pythonSource (Join-Path $appRoot 'scripts\apply_auth_migration.py') --engine postgres
	if ($LASTEXITCODE -ne 0) {
		throw 'Auth-/Research-Set-Migration fehlgeschlagen.'
	}
}

Set-Location $appRoot
& $pythonSource -m src.app.main
exit $LASTEXITCODE