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
if (($env:FLASK_ENV -eq 'development') -and (-not $env:FLASK_DEBUG)) {
	$env:FLASK_DEBUG = '1'
}
if (-not $env:FLASK_SECRET_KEY) {
	$env:FLASK_SECRET_KEY = 'dev-secret-change-me'
}
if (-not $env:JWT_SECRET_KEY) {
	$env:JWT_SECRET_KEY = 'dev-jwt-secret-change-me'
}

function Get-PromatDevServerProcesses {
	param(
		[string]$WorkspaceRoot
	)

	$resolvedWorkspaceRoot = (Resolve-Path $WorkspaceRoot).Path
	return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
		$commandLine = $_.CommandLine
		$processName = $_.Name
		($processName -ieq 'python.exe' -or $processName -ieq 'pythonw.exe') -and
		$commandLine -and
		(
			(
				($commandLine -match [regex]::Escape($resolvedWorkspaceRoot)) -and
				(
					($commandLine -match 'src\.app\.main') -or
					($commandLine -match 'run_local_server\.py') -or
					($commandLine -match 'run_app_\d+\.py')
				)
			) -or
			($commandLine -match '(^|\s)-m\s+src\.app\.main(?:\s|$)')
		)
	})
}

function Get-ListeningProcessIdsForPort {
	param(
		[int]$Port
	)

	return @(
		Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
			Select-Object -ExpandProperty OwningProcess -Unique
	)
}

function Get-ProcessSummary {
	param(
		[int]$ProcessId
	)

	$process = Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId" -ErrorAction SilentlyContinue
	if ($null -eq $process) {
		return "PID $ProcessId"
	}

	if ($process.CommandLine) {
		return "PID $ProcessId :: $($process.CommandLine)"
	}

	return "PID $ProcessId :: $($process.Name)"
}

function Stop-StalePromatDevServers {
	param(
		[string]$WorkspaceRoot,
		[int]$Port = 8000
	)

	$promatProcesses = @(Get-PromatDevServerProcesses -WorkspaceRoot $WorkspaceRoot)
	$promatProcessIds = @($promatProcesses | Select-Object -ExpandProperty ProcessId -Unique)
	if ($promatProcessIds.Count -eq 0) {
		return
	}

	$listenerProcessIds = @(Get-ListeningProcessIdsForPort -Port $Port)
	$foreignListeners = @($listenerProcessIds | Where-Object { $promatProcessIds -notcontains $_ })
	if ($foreignListeners.Count -gt 0) {
		$details = ($foreignListeners | ForEach-Object { Get-ProcessSummary -ProcessId $_ }) -join "`n"
		throw "Port ${Port} ist bereits durch einen fremden Prozess belegt:`n$details"
	}

	$stopCandidates = @($promatProcesses | Where-Object { $_.ProcessId -ne $PID })
	if ($stopCandidates.Count -eq 0) {
		return
	}

	$details = ($stopCandidates | ForEach-Object { Get-ProcessSummary -ProcessId $_.ProcessId }) -join "`n"
	Write-Host "Beende bestehende PROMAT-Dev-Prozesse vor dem Neustart auf Port ${Port}:`n$details" -ForegroundColor Yellow
	foreach ($process in $stopCandidates) {
		Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
	}
	foreach ($process in $stopCandidates) {
		Wait-Process -Id $process.ProcessId -Timeout 10 -ErrorAction SilentlyContinue
	}

	$remainingListeners = @(Get-ListeningProcessIdsForPort -Port $Port)
	if ($remainingListeners.Count -gt 0) {
		$remainingDetails = ($remainingListeners | ForEach-Object { Get-ProcessSummary -ProcessId $_ }) -join "`n"
		throw "Port ${Port} bleibt nach dem Bereinigen belegt:`n$remainingDetails"
	}
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
		throw 'Auth-/Research-Set-Migration fehlgeschlagen (engine=postgres). Siehe die vorherige Fehlermeldung aus scripts/apply_auth_migration.py fuer die betroffene Migration.'
	}
}

if ($shouldSeedDefaultAdmin -and $StartAdminPassword) {
	& $pythonSource (Join-Path $appRoot 'scripts\create_initial_admin.py') --username $StartAdminUsername --email $StartAdminEmail --display-name $StartAdminDisplayName --password $StartAdminPassword
	if ($LASTEXITCODE -ne 0) {
		throw 'Standard-Dev-Admin konnte nicht angelegt oder aktualisiert werden.'
	}
}

Stop-StalePromatDevServers -WorkspaceRoot $workspaceRoot -Port 8000

Set-Location $appRoot
& $pythonSource -m src.app.main
exit $LASTEXITCODE