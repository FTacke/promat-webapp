function Get-LocalDevPostgresHost {
	return '127.0.0.1'
}

function Get-DefaultLocalDevPostgresPort {
	return 54321
}

function Get-FallbackLocalDevPostgresPorts {
	return @(55432, 55433, 55434)
}

function Get-LocalDevPostgresDatabaseUrl {
	param(
		[int]$Port
	)

	return "postgresql+psycopg2://promat_auth:promat_auth@$(Get-LocalDevPostgresHost):$Port/promat_auth"
}

function Get-LocalDevPostgresPortFromUrl {
	param(
		[string]$DatabaseUrl
	)

	if ($null -eq $DatabaseUrl) {
		$normalized = ''
	}
	else {
		$normalized = $DatabaseUrl.Trim()
	}
	if (-not $normalized) {
		return $null
	}

	$match = [regex]::Match(
		$normalized,
		'^postgresql(?:\+psycopg2|\+psycopg)?://[^@]+@(127\.0\.0\.1|localhost):(?<port>\d+)/promat_auth(?:\?.*)?$'
	)
	if (-not $match.Success) {
		return $null
	}

	return [int]$match.Groups['port'].Value
}

function Test-LocalDevPostgresUrl {
	param(
		[string]$DatabaseUrl,
		[int]$Port
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

	if ($normalized -eq (Get-LocalDevPostgresDatabaseUrl -Port $Port)) {
		return $true
	}

	return $normalized -match "^postgresql(\+psycopg2|\+psycopg)?://[^@]+@(127\.0\.0\.1|localhost):$Port/promat_auth(?:\?.*)?$"
}

function Set-LocalDevPostgresEnvironment {
	param(
		[string]$HostName,
		[int]$Port,
		[switch]$UpdateAuthDatabaseUrl,
		[switch]$MarkAsAuto
	)

	$env:PROMAT_DEV_DB_PORT = "$Port"
	if ($MarkAsAuto) {
		$env:PROMAT_DEV_DB_PORT_AUTO = '1'
	}
	elseif (Test-Path Env:PROMAT_DEV_DB_PORT_AUTO) {
		Remove-Item Env:PROMAT_DEV_DB_PORT_AUTO
	}
	if ($UpdateAuthDatabaseUrl) {
		$env:AUTH_DATABASE_URL = Get-LocalDevPostgresDatabaseUrl -Port $Port
	}
}

function Initialize-LocalDevPostgresEnvironment {
	param(
		[string]$DefaultDatabaseUrl
	)

	if ($null -eq $env:AUTH_DATABASE_URL) {
		$currentAuthDatabaseUrl = ''
	}
	else {
		$currentAuthDatabaseUrl = $env:AUTH_DATABASE_URL.Trim()
	}
	$portFromUrl = Get-LocalDevPostgresPortFromUrl -DatabaseUrl $currentAuthDatabaseUrl
	$autoManagedPort = $env:PROMAT_DEV_DB_PORT_AUTO -eq '1'
	$updateAuthDatabaseUrl = (-not $currentAuthDatabaseUrl) -or ($currentAuthDatabaseUrl -eq $DefaultDatabaseUrl)
	$allowPortFallback = $false

	if ($env:PROMAT_DEV_DB_PORT) {
		$resolvedPort = [int]$env:PROMAT_DEV_DB_PORT
		if ($autoManagedPort -and ((-not $currentAuthDatabaseUrl) -or (Test-LocalDevPostgresUrl -DatabaseUrl $currentAuthDatabaseUrl -Port $resolvedPort))) {
			$allowPortFallback = $true
			$updateAuthDatabaseUrl = $true
		}
		elseif (($resolvedPort -eq (Get-DefaultLocalDevPostgresPort)) -and ((-not $currentAuthDatabaseUrl) -or ($currentAuthDatabaseUrl -eq $DefaultDatabaseUrl))) {
			$allowPortFallback = $true
			$updateAuthDatabaseUrl = $true
		}
	}
	elseif ($portFromUrl) {
		$resolvedPort = $portFromUrl
		$allowPortFallback = $currentAuthDatabaseUrl -eq $DefaultDatabaseUrl
	}
	else {
		$resolvedPort = Get-DefaultLocalDevPostgresPort
		$allowPortFallback = $true
	}

	Set-LocalDevPostgresEnvironment -HostName (Get-LocalDevPostgresHost) -Port $resolvedPort -UpdateAuthDatabaseUrl:$updateAuthDatabaseUrl -MarkAsAuto:$updateAuthDatabaseUrl

	return [pscustomobject]@{
		Host = Get-LocalDevPostgresHost
		Port = $resolvedPort
		AllowPortFallback = $allowPortFallback
		UpdateAuthDatabaseUrl = $updateAuthDatabaseUrl
	}
}

function Test-TcpPortBindable {
	param(
		[int]$Port
	)

	$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
	try {
		$listener.Start()
		return $true
	}
	catch {
		return $false
	}
	finally {
		try {
			$listener.Stop()
		}
		catch {
		}
	}
}

function Test-TcpPortReachable {
	param(
		[string]$HostName,
		[int]$Port,
		[int]$TimeoutMilliseconds = 1000
	)

	$client = New-Object System.Net.Sockets.TcpClient
	try {
		$asyncResult = $client.BeginConnect($HostName, $Port, $null, $null)
		if (-not $asyncResult.AsyncWaitHandle.WaitOne($TimeoutMilliseconds, $false)) {
			return $false
		}

		$client.EndConnect($asyncResult)
		return $true
	}
	catch {
		return $false
	}
	finally {
		$client.Dispose()
	}
}

function Wait-ForLocalDevPostgres {
	param(
		[string]$ComposeFilePath,
		[string]$DockerExecutable,
		[string]$HostName,
		[int]$Port
	)

	for ($attempt = 1; $attempt -le 30; $attempt++) {
		& $DockerExecutable compose -f $ComposeFilePath exec -T promat_auth_db pg_isready -U promat_auth -d promat_auth *> $null
		if (($LASTEXITCODE -eq 0) -and (Test-TcpPortReachable -HostName $HostName -Port $Port)) {
			return $true
		}
		Start-Sleep -Seconds 1
	}

	return $false
}

function Get-FallbackLocalDevPostgresPort {
	param(
		[int]$CurrentPort
	)

	foreach ($candidatePort in (Get-FallbackLocalDevPostgresPorts)) {
		if ($candidatePort -eq $CurrentPort) {
			continue
		}
		if (Test-TcpPortBindable -Port $candidatePort) {
			return $candidatePort
		}
	}

	return $null
}

function Start-LocalDevPostgresContainer {
	param(
		[string]$ComposeFilePath,
		[string]$DockerExecutable,
		[switch]$ForceRecreate
	)

	$args = @('compose', '-f', $ComposeFilePath, 'up', '-d')
	if ($ForceRecreate) {
		$args += '--force-recreate'
	}
	$args += 'promat_auth_db'

	& $DockerExecutable @args
	return $LASTEXITCODE
}

function Remove-LocalDevPostgresContainer {
	param(
		[string]$ComposeFilePath,
		[string]$DockerExecutable
	)

	$previousErrorActionPreference = $ErrorActionPreference
	$ErrorActionPreference = 'Continue'
	try {
		& $DockerExecutable compose -f $ComposeFilePath rm -sf promat_auth_db *> $null
		return $LASTEXITCODE
	}
	finally {
		$ErrorActionPreference = $previousErrorActionPreference
	}
}

function Ensure-LocalDevPostgres {
	param(
		[string]$ComposeFilePath,
		[string]$DockerExecutable,
		[int]$Port,
		[switch]$AllowPortFallback,
		[switch]$UpdateAuthDatabaseUrl
	)

	$hostName = Get-LocalDevPostgresHost
	Set-LocalDevPostgresEnvironment -HostName $hostName -Port $Port -UpdateAuthDatabaseUrl:$UpdateAuthDatabaseUrl -MarkAsAuto:$UpdateAuthDatabaseUrl

	$startExitCode = Start-LocalDevPostgresContainer -ComposeFilePath $ComposeFilePath -DockerExecutable $DockerExecutable
	if (($startExitCode -eq 0) -and (Wait-ForLocalDevPostgres -ComposeFilePath $ComposeFilePath -DockerExecutable $DockerExecutable -HostName $hostName -Port $Port)) {
		return $Port
	}

	if (-not $AllowPortFallback) {
		if ($startExitCode -ne 0) {
			throw "Lokale promat_auth_db konnte auf $hostName`:$Port nicht gestartet werden."
		}
		throw "Lokale PostgreSQL-Dev-Datenbank antwortet im Container, aber $hostName`:$Port ist vom Host nicht erreichbar. Bitte Docker Desktop und die Port-Veroeffentlichung pruefen."
	}

	$fallbackPort = Get-FallbackLocalDevPostgresPort -CurrentPort $Port
	if ($null -eq $fallbackPort) {
		if ($startExitCode -ne 0) {
			throw "Lokale promat_auth_db konnte auf $hostName`:$Port nicht gestartet werden, und es wurde kein freier Fallback-Port gefunden."
		}
		throw "Lokale PostgreSQL-Dev-Datenbank antwortet im Container, aber weder $hostName`:$Port noch ein freier Fallback-Port sind verfuegbar."
	}

	Write-Host "Lokaler Dev-Port $Port ist auf diesem Host nicht verfuegbar. PostgreSQL wird stattdessen auf $hostName`:$fallbackPort veroeffentlicht."
	Remove-LocalDevPostgresContainer -ComposeFilePath $ComposeFilePath -DockerExecutable $DockerExecutable | Out-Null
	Set-LocalDevPostgresEnvironment -HostName $hostName -Port $fallbackPort -UpdateAuthDatabaseUrl:$UpdateAuthDatabaseUrl -MarkAsAuto:$UpdateAuthDatabaseUrl

	$startExitCode = Start-LocalDevPostgresContainer -ComposeFilePath $ComposeFilePath -DockerExecutable $DockerExecutable -ForceRecreate
	if ($startExitCode -ne 0) {
		throw "Lokale promat_auth_db konnte auch auf dem Fallback-Port $hostName`:$fallbackPort nicht gestartet werden."
	}

	if (Wait-ForLocalDevPostgres -ComposeFilePath $ComposeFilePath -DockerExecutable $DockerExecutable -HostName $hostName -Port $fallbackPort) {
		return $fallbackPort
	}

	throw "Lokale PostgreSQL-Dev-Datenbank wurde intern bereit, aber der Fallback-Port $hostName`:$fallbackPort bleibt vom Host aus unerreichbar. Bitte Docker Desktop und die Port-Veroeffentlichung pruefen."
}