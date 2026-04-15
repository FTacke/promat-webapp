param(
	[switch]$SkipBootstrap,
	[string]$StartAdminUsername = 'admin_dev',
	[string]$StartAdminEmail = 'felix.tacke@uni-marburg.de',
	[string]$StartAdminDisplayName = 'Felix Tacke',
	[string]$StartAdminPassword = 'Admin0000!'
)

$ErrorActionPreference = 'Stop'

$appRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent $appRoot
$composeFile = Join-Path $workspaceRoot 'docker-compose.dev-postgres.yml'
$devPostgresHelpers = Join-Path $PSScriptRoot 'dev-postgres.ps1'
if (-not (Test-Path $devPostgresHelpers)) {
	throw "Could not resolve dev-postgres helpers: $devPostgresHelpers"
}

. $devPostgresHelpers

$defaultAuthDatabaseUrl = Get-LocalDevPostgresDatabaseUrl -Port (Get-DefaultLocalDevPostgresPort)

if (-not $env:PROMAT_RUNTIME_ROOT) {
	$env:PROMAT_RUNTIME_ROOT = $workspaceRoot
}
if (-not $env:PROMAT_PUBLIC_ROOT) {
	$env:PROMAT_PUBLIC_ROOT = Join-Path $workspaceRoot 'public'
}
if (-not $env:AUTH_ACCESS_REQUEST_EMAIL) {
	$env:AUTH_ACCESS_REQUEST_EMAIL = 'felix.tacke@uni-marburg.de'
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

$localDevPostgres = Initialize-LocalDevPostgresEnvironment -DefaultDatabaseUrl $defaultAuthDatabaseUrl
$localDevPostgresPort = $localDevPostgres.Port

$shouldBootstrapLocalPostgres = (-not $SkipBootstrap) -and ($env:FLASK_ENV -eq 'development') -and (Test-LocalDevPostgresUrl -DatabaseUrl $env:AUTH_DATABASE_URL -Port $localDevPostgresPort)
$shouldSeedDefaultAdmin = ($env:FLASK_ENV -eq 'development') -and (Test-LocalDevPostgresUrl -DatabaseUrl $env:AUTH_DATABASE_URL -Port $localDevPostgresPort)

if ($shouldBootstrapLocalPostgres) {
	$docker = Get-Command docker -ErrorAction SilentlyContinue | Select-Object -First 1
	if ($docker -and (Test-Path $composeFile)) {
		$localDevPostgresPort = Ensure-LocalDevPostgres -ComposeFilePath $composeFile -DockerExecutable $docker.Source -Port $localDevPostgresPort -AllowPortFallback:$localDevPostgres.AllowPortFallback -UpdateAuthDatabaseUrl:$localDevPostgres.UpdateAuthDatabaseUrl
	}

	& $pythonSource (Join-Path $appRoot 'scripts\apply_auth_migration.py') --engine postgres
	if ($LASTEXITCODE -ne 0) {
		throw 'Auth-/Research-Set-Migration fehlgeschlagen.'
	}
}

if ($shouldSeedDefaultAdmin -and $StartAdminPassword) {
	& $pythonSource (Join-Path $appRoot 'scripts\create_initial_admin.py') --username $StartAdminUsername --email $StartAdminEmail --display-name $StartAdminDisplayName --password $StartAdminPassword
	if ($LASTEXITCODE -ne 0) {
		throw 'Standard-Dev-Admin konnte nicht angelegt oder aktualisiert werden.'
	}
}

Set-Location $appRoot
& $pythonSource -m src.app.main
exit $LASTEXITCODE