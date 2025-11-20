param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 5005,
    [switch]$Debug
)

Set-Location "C:\Users\MaoGon\ai_dev_core"

# プロジェクト直下を PYTHONPATH に追加しておく（必要に応じて利用）
$env:PYTHONPATH = "$PWD"

$pythonArgs = @(
    ".\apps\smart_video_concat\server_v3.py",
    "--host", $Host,
    "--port", $Port
)

if ($Debug) {
    $pythonArgs += "--debug"
}

Write-Host "Starting smart_video_concat v3 server on http://$Host`:$Port ..." -ForegroundColor Cyan
Write-Host "Ctrl+C でサーバを停止できます。" -ForegroundColor Yellow

python @pythonArgs
