$ErrorActionPreference = "Stop"
$Root = Resolve-Path "$PSScriptRoot/../../"
Write-Host "`n🧩 Integrity check under: $Root`n"

# 監視対象はコードのみ（*.ps1, *.py, *.yml）。ドキュメント *.md は許容。
$Targets = Get-ChildItem -Path $Root -Recurse -File -Include *.ps1,*.py,*.yml |
  Where-Object {
    $_.FullName -notmatch '\\.git\\' -and
    $_.FullName -notmatch '\\.github\\workflows\\' -and
    $_.Name -notin @('check_integrity.ps1','integrity.yml')
  }

# “分断・省略”検出パターン
$Patterns = @('中略','省略','略(?!称)','\.\.\.','…')

$Violations = @()
foreach ($F in $Targets) {
  $C = Get-Content -Raw -Encoding UTF8 -LiteralPath $F.FullName
  foreach ($P in $Patterns) {
    if ($C -match $P) { $Violations += "$($F.FullName)（検出: $P）" }
  }
}

if ($Violations.Count -gt 0) {
  Write-Host "❌ 分断・省略コード検出:" -ForegroundColor Red
  $Violations | ForEach-Object { Write-Host " - $_" }
  exit 1
} else {
  Write-Host "✅ 整合性OK（.md除外・自己/Workflow除外済）" -ForegroundColor Green
}