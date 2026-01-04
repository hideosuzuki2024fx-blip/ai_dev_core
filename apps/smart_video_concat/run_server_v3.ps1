param(
    [string]$ListenHost = "127.0.0.1",
    [int]$Port = 5005,
    [switch]$Debug
)

Set-Location "C:\Users\MaoGon\ai_dev_core"

# プロジェクト直下を PYTHONPATH に追加
$env:PYTHONPATH = "$PWD"

$pythonArgs = @(
    ".\apps\smart_video_concat\server_v3.py",
    "--host", $ListenHost,
    "--port", $Port
)

if ($Debug) {
    $pythonArgs += "--debug"
}

Write-Host "Starting smart_video_concat v3 server on http://$ListenHost`:$Port # CODE_TRUNCATED" -ForegroundColor Cyan
Write-Host "Ctrl+C でサーバを停止できます。" -ForegroundColor Yellow

python @pythonArgs
