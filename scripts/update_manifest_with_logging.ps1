Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$base = "E:\ai_dev_core"
Set-Location $base

$manifest = "SYSTEM_MANIFEST.yaml"
if (-not (Test-Path $manifest)) {
    throw "❌ SYSTEM_MANIFEST.yaml が存在しません。"
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup = "SYSTEM_MANIFEST_backup_${timestamp}.yaml"
Copy-Item $manifest $backup -Force
Write-Host "🧾 バックアップ作成: $backup"

$content = Get-Content -Raw -Path $manifest -Encoding UTF8

$appendBlock = @"
process:
  stages: [Draft, Review, Final]
  note_pipeline: "0_raw → 1_mash → 2_ferment → 3_article"
  scripts:
    ferment_pipeline: "scripts/FermentPipeline.ps1"

logging:
  critique: "logs/critique/"
  error: "logs/error/"
  policy: >
    各発酵サイクルごとに自動生成。成功はcritiqueログ、例外はerrorログに記録。
    ファイル名は ferment_YYYYMMDD_HHMMSS.log。
"@

if ($content -match "(?s)process:.*?logging:") {
    Write-Host "🧩 既存セクション検出 → 差し替え"
    $content = $content -replace "(?s)process:.*?logging:", $appendBlock
} else {
    Write-Host "➕ 新規追加"
    $content = $content.TrimEnd() + "`n`n" + $appendBlock
}

Set-Content -Path $manifest -Value $content -Encoding utf8NoBOM
Write-Host "✅ SYSTEM_MANIFEST.yaml を更新しました。"

git add SYSTEM_MANIFEST.yaml
git commit -m "chore: update SYSTEM_MANIFEST with FermentPipeline and logging structure"
git push

Write-Host "🎉 反映完了: SYSTEM_MANIFEST.yaml に発酵ログ構造を統合しました。"
