# smart_video_concat v3 用 ドラッグ＆ドロップ専用ラッパ
# 使い方:
#   - エクスプローラーで mp4 を複数選択して、この ps1 のショートカットに D&D
#   - またはコマンドラインから:
#       pwsh .\apps\smart_video_concat\run_smart_concat_v3_dragdrop.ps1 `
#         "D:\clips\test\0 (6).mp4" `
#         "D:\clips\test\0 (54).mp4" `
#         "D:\clips\test\013245.mp4"

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Analyzer  = Join-Path $ScriptDir "analyze_and_concat_v3.py"

if (-not (Test-Path $Analyzer)) {
    Write-Error "analyze_and_concat_v3.py が見つかりません: $Analyzer"
    exit 1
}

if (-not $args -or $args.Count -lt 1) {
    Write-Error "入力ファイルを 1 本以上指定してください（D&D またはコマンドライン引数）。"
    exit 1
}

# 引数で渡されたファイルパスを解決
$files = @()
foreach ($a in $args) {
    try {
        $resolved = Resolve-Path $a -ErrorAction Stop
        $files += $resolved.ProviderPath
    }
    catch {
        Write-Error "入力ファイルが見つかりません: $a"
        exit 1
    }
}

# 出力: 先頭ファイルと同じフォルダに smart_concat_v3.mp4
$firstDir = Split-Path -Parent $files[0]
$output   = Join-Path $firstDir "smart_concat_v3.mp4"

# 固定パラメータ（必要になったらここを編集）
$crf    = 20
$preset = "veryfast"
$width  = 1920
$height = 1080

$python = "python"

$argsList = @($Analyzer)
foreach ($f in $files) {
    $argsList += $f
}
$argsList += @(
    "--output", $output,
    "--crf",    $crf,
    "--preset", $preset,
    "--width",  $width,
    "--height", $height
)

Write-Host "Running smart_video_concat v3 (drag & drop mode)..." -ForegroundColor Cyan
Write-Host $python $($argsList -join " ")

$proc = Start-Process -FilePath $python -ArgumentList $argsList -NoNewWindow -PassThru -Wait

if ($proc.ExitCode -ne 0) {
    Write-Error "analyze_and_concat_v3.py がエラー終了しました (exit code=$($proc.ExitCode))"
    exit $proc.ExitCode
}

Write-Host "出力ファイル: $output" -ForegroundColor Green
