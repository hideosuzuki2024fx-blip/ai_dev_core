param(
    [Parameter(Mandatory = $false)]
    [string]$InputDir = ".",

    [Parameter(Mandatory = $false)]
    [string]$Pattern = "*.mp4",

    [Parameter(Mandatory = $false)]
    [string]$Output = "smart_concat_v2.mp4",

    [Parameter(Mandatory = $false)]
    [switch]$Recursive,

    [Parameter(Mandatory = $false)]
    [switch]$DryRun,

    [Parameter(Mandatory = $false)]
    [int]$Crf = 20,

    [Parameter(Mandatory = $false)]
    [string]$Preset = "veryfast",

    [Parameter(Mandatory = $false)]
    [string]$Python = "python"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript = Join-Path $scriptDir "analyze_and_concat_v2.py"

if (-not (Test-Path $pyScript)) {
    Write-Error "analyze_and_concat_v2.py が見つかりませんでした: $pyScript"
    exit 1
}

$argsList = @($pyScript)

if ($InputDir) {
    $argsList += @("--input-dir", $InputDir)
}
if ($Pattern) {
    $argsList += @("--pattern", $Pattern)
}
if ($Output) {
    $argsList += @("--output", $Output)
}
if ($Recursive.IsPresent) {
    $argsList += "--recursive"
}
if ($DryRun.IsPresent) {
    $argsList += "--dry-run"
}
if ($Crf) {
    $argsList += @("--crf", $Crf)
}
if ($Preset) {
    $argsList += @("--preset", $Preset)
}

Write-Host "=== Smart Video Concat v2 (reencode) ===" -ForegroundColor Cyan
Write-Host "Python: $Python"
Write-Host "Script: $pyScript"
Write-Host "Args  : $($argsList -join ' ' )"
Write-Host ""

& $Python @argsList
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Error "Smart Video Concat v2 実行中にエラーが発生しました。exit code = $exitCode"
    exit $exitCode
}
