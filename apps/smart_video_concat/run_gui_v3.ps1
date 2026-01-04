param(
    [string]$Python = "python"
)

Set-Location "C:\Users\MaoGon\ai_dev_core"

# プロジェクト直下を PYTHONPATH に追加（必要に応じてモジュール import に利用）
$env:PYTHONPATH = "$PWD"

$scriptPath = ".\apps\smart_video_concat\gui_v3.py"

if (-not (Test-Path $scriptPath)) {
    Write-Host "$scriptPath が見つかりません。リポジトリの状態を確認してください。" -ForegroundColor Red
    exit 1
}

Write-Host "Launching smart_video_concat v3 GUI# CODE_TRUNCATED" -ForegroundColor Cyan
Write-Host "Python: $Python" -ForegroundColor Gray
Write-Host "Script: $scriptPath" -ForegroundColor Gray

& $Python $scriptPath
