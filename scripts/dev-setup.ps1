 $implementation = Join-Path $PSScriptRoot "..\app\scripts\dev-setup.ps1"
if (-not (Test-Path $implementation)) {
	throw "Could not resolve dev-setup implementation: $implementation"
}

& $implementation @args
exit $LASTEXITCODE