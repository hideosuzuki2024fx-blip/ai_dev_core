param(
    [string]$InputDir = ".",
    [string]$Pattern = "*.mp4",
    [string]$Output = "out\smart_concat_v3.mp4",
    [switch]$Recursive,
    [switch]$DryRun,
    [int]$Crf = 20,
    [string]$Preset = "veryfast",
    [int]$Width = 1920,
    [int]$Height = 1080
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Analyzer = Join-Path $ScriptDir "analyze_and_concat_v3.py"

if (-not (Test-Path $Analyzer)) {
    Write-Error "analyze_and_concat_v3.py が見つかりません: $Analyzer"
    exit 1
}

$python = "python"

$argsList = @(
    $Analyzer,
    "--input-dir", $InputDir,
    "--pattern", $Pattern,
    "--output", $Output,
    "--crf", $Crf,
    "--preset", $Preset,
    "--width", $Width,
    "--height", $Height
)

if ($Recursive.IsPresent) {
    $argsList += "--recursive"
}
if ($DryRun.IsPresent) {
    $argsList += "--dry-run"
}

Write-Host "Running smart_video_concat v3 (dir/pattern mode)..." -ForegroundColor Cyan
Write-Host $python $($argsList -join " ")

$proc = Start-Process -FilePath $python -ArgumentList $argsList -NoNewWindow -PassThru -Wait

if ($proc.ExitCode -ne 0) {
    Write-Error "analyze_and_concat_v3.py がエラー終了しました (exit code=$($proc.ExitCode))"
    exit $proc.ExitCode
}
