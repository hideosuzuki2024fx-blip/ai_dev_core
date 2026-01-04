<#
.SYNOPSIS
GitHub Actions + Vercel で Yoshio 発酵自動化環境をセットアップ
#>

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$base = "E:\ai_dev_core"
Set-Location $base

New-Item -ItemType Directory -Force -Path ".github\workflows" | Out-Null
New-Item -ItemType Directory -Force -Path "scripts" | Out-Null

Write-Host "☁️ Cloud 発酵自動化セットアップを開始します# CODE_TRUNCATED"

@"
name: Yoshio Auto-Ferment

on:
  schedule:
    - cron: "0 3 * * *"
  workflow_dispatch:

jobs:
  ferment:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-powershell@v2
      - name: Run Ferment Pipeline
        run: pwsh ./scripts/FermentPipeline.ps1
      - name: Update Manifest
        run: pwsh ./scripts/update_manifest_with_latest_log.ps1
      - name: Commit & Push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add -A
          git commit -m "ci: auto-ferment \$(date +'%Y%m%d_%H%M%S')" || echo "No changes"
          git push
"@ | Set-Content -Path ".github\workflows\ferment.yml" -Encoding utf8NoBOM

@"
{
  "version": 2,
  "builds": [
    { "src": "NoteMD/3_article/**/*", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "/NoteMD/3_article/$1" }
  ]
}
"@ | Set-Content -Path "vercel.json" -Encoding utf8NoBOM

# PowerShell 側では独自タイムスタンプを使う
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

git add .github/workflows/ferment.yml vercel.json
git commit -m "ci: add auto-ferment workflow and vercel.json ($timestamp)" || Write-Host "No changes to commit"
git push

Write-Host "🎉 セットアップ完了！"
Write-Host "🚀 次のステップ："
Write-Host "1. GitHub Actions を有効化"
Write-Host "2. Vercel にリポジトリをリンク"
Write-Host "3. 初回トリガー: https://github.com/hideosuzuki2024fx-blip/ai_dev_core/actions"
