param(
    [Parameter(Mandatory = $false)]
    [string]$Python = "python"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$guiScript = Join-Path $scriptDir "gui.py"

if (-not (Test-Path $guiScript)) {
    Write-Error "gui.py が見つかりませんでした: $guiScript"
    exit 1
}

Write-Host "=== Smart Video Concat GUI ===" -ForegroundColor Cyan
Write-Host "Python: $Python"
Write-Host "Script: $guiScript"
Write-Host ""

& $Python $guiScript
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Error "Smart Video Concat GUI 実行中にエラーが発生しました。exit code = $exitCode"
    exit $exitCode
}
