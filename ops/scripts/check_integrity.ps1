$ErrorActionPreference="Stop"
$Root = Resolve-Path "$PSScriptRoot/../../"
$Targets = Get-ChildItem -Path $Root -Recurse -File -Include *.ps1,*.py,*.yml,*.md

# 「分断語」パターン
$Patterns = @("中略","省略","略(?!称)","\.\.\.","…")

# 除外（ポリシー/README/自身/ワークフロー等）
$ExcludeNames = @(
  "ai_policy.md",
  "README.md",
  "check_integrity.ps1",
  "integrity.yml",
  "deploy_lp.yml"
)

$Viol = @()
foreach($F in $Targets){
  if ($ExcludeNames -contains $F.Name) { continue }
  $C = Get-Content -Raw -Encoding UTF8 -LiteralPath $F.FullName
  foreach($P in $Patterns){ if($C -match $P){ $Viol += "$($F.FullName)（検出: $P）" } }
}

Write-Host "`n🧩 Integrity check under: $($Root)`n"
if($Viol.Count -gt 0){
  Write-Host "❌ 分断・省略コード検出:" -ForegroundColor Red
  $Viol | ForEach-Object { Write-Host " - $_" }
  exit 1
}else{
  Write-Host "✅ 整合性OK（README/ai_policy/自己・CI定義は除外）" -ForegroundColor Green
}