 $implementation = Join-Path $PSScriptRoot "..\app\scripts\dev-start.ps1"
if (-not (Test-Path $implementation)) {
	throw "Could not resolve dev-start implementation: $implementation"
}

& $implementation @args
exit $LASTEXITCODE