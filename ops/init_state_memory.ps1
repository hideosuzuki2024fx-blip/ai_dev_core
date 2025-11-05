$ErrorActionPreference = "Stop"

# スクリプト基準でリポジトリルートを解決
$Here     = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $Here "..")
$StateDir = Join-Path $RepoRoot "docs\state"
$StateYml = Join-Path $StateDir "phase.yml"

# ディレクトリ生成
if (!(Test-Path $StateDir)) {
  New-Item -ItemType Directory -Path $StateDir | Out-Null
  Write-Host "📁 Created: $StateDir"
}

# 既存を壊さない：存在しなければ初期化、あれば日付のみ更新
$nowIso = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
if (!(Test-Path $StateYml)) {
  $Initial = @"
current_phase: "market_research"
objective: "市場カテゴリと競合アプリの分析"
next_phase: "アプリ設計仕様書作成"
responsible: "GPT（PM/マーケター）"
last_update: "$nowIso"
"@
  Set-Content -Path $StateYml -Value $Initial -Encoding UTF8
  Write-Host "✅ Initialized: $StateYml"
} else {
  # last_update を置換（他の項目は温存）
  $text = Get-Content -Raw -Encoding UTF8 $StateYml
  if ($text -match 'last_update:\s*".*?"') {
    $text = [regex]::Replace($text, 'last_update:\s*".*?"', ('last_update: "' + $nowIso + '"'))
  } else {
    $text = ($text.TrimEnd() + "`nlast_update: `"$nowIso`"`n")
  }
  Set-Content -Path $StateYml -Value $text -Encoding UTF8
  Write-Host "📝 Updated: last_update in $StateYml"
}

# 検証出力
Write-Host "`n📄 現在の状態ファイル:" -ForegroundColor Cyan
Get-Content $StateYml | ForEach-Object { "   $_" }

Write-Host "`n🎯 構造初期化/更新 完了: docs/state/phase.yml を管理対象に設定しました。" -ForegroundColor Green