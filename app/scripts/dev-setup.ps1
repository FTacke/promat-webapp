param(
	[switch]$SkipInstall,
	[switch]$SkipDevServer,
	[switch]$ResetAuth,
	[string]$StartAdminUsername = 'admin_dev',
	[string]$StartAdminEmail = 'felix.tacke@uni-marburg.de',
	[string]$StartAdminDisplayName = 'Felix Tacke',
	[string]$StartAdminPassword = 'change-me'
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

$localDevPostgres = Initialize-LocalDevPostgresEnvironment -DefaultDatabaseUrl $defaultAuthDatabaseUrl
$localDevPostgresPort = $localDevPostgres.Port

if (Get-Command docker -ErrorAction SilentlyContinue) {
	$docker = (Get-Command docker -ErrorAction SilentlyContinue | Select-Object -First 1).Source
	$localDevPostgresPort = Ensure-LocalDevPostgres -ComposeFilePath $composeFile -DockerExecutable $docker -Port $localDevPostgresPort -AllowPortFallback:$localDevPostgres.AllowPortFallback -UpdateAuthDatabaseUrl:$localDevPostgres.UpdateAuthDatabaseUrl
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
	& $pythonSource (Join-Path $appRoot 'scripts\create_initial_admin.py') --username $StartAdminUsername --email $StartAdminEmail --display-name $StartAdminDisplayName --password $StartAdminPassword
	if ($LASTEXITCODE -ne 0) {
		throw 'Initialer Admin konnte nicht angelegt werden.'
	}
}

if (-not $SkipDevServer) {
	& $PSScriptRoot\dev-start.ps1 -SkipBootstrap
}