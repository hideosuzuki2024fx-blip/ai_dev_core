[CmdletBinding(PositionalBinding = $false)]
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

# 位置引数（D&D / ファイル直指定）は $args にそのまま入ってくる前提
$filesFromArgs = @()
if ($args -and $args.Count -gt 0) {
    foreach ($a in $args) {
        try {
            $resolved = Resolve-Path $a -ErrorAction Stop
            $filesFromArgs += $resolved.ProviderPath
        }
        catch {
            Write-Error "入力ファイルが見つかりません: $a"
            exit 1
        }
    }
}

if ($filesFromArgs.Count -gt 0) {
    # ファイル直指定モード（ドラッグ＆ドロップ含む）
    if (-not $PSBoundParameters.ContainsKey("Output")) {
        $firstDir = Split-Path -Parent $filesFromArgs[0]
        $Output = Join-Path $firstDir "smart_concat_v3.mp4"
    }

    $argsList = @($Analyzer)

    foreach ($f in $filesFromArgs) {
        $argsList += $f
    }

    $argsList += @(
        "--output", $Output,
        "--crf", $Crf,
        "--preset", $Preset,
        "--width", $Width,
        "--height", $Height
    )

    if ($DryRun.IsPresent) {
        $argsList += "--dry-run"
    }
}
else {
    # 従来どおり、ディレクトリ + パターンで探索
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
}

Write-Host "Running smart_video_concat v3..." -ForegroundColor Cyan
Write-Host $python $($argsList -join " ")

$proc = Start-Process -FilePath $python -ArgumentList $argsList -NoNewWindow -PassThru -Wait

if ($proc.ExitCode -ne 0) {
    Write-Error "analyze_and_concat_v3.py がエラー終了しました (exit code=$($proc.ExitCode))"
    exit $proc.ExitCode
}
