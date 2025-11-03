# ops/scripts/check_integrity.ps1
# コードのみ分断検査（Markdownは対象外） / UTF-8 No BOM
$ErrorActionPreference = "Stop"

$Root   = Resolve-Path "$PSScriptRoot/../../"
$Globs  = @("*.ps1","*.psm1","*.psd1","*.py","*.ts","*.tsx","*.js","*.jsx","*.json","*.yml","*.yaml","*.sh","*.bat","*.cmd","*.cs","*.go","*.rs","*.java","*.c","*.cpp")

# 分断検出パターン（コードで使うべきでない表現）
$Patterns = @(
  "中略",
  "省略",
  "略(?!称)",   # 「略称」は許可
  "\.\.\.",     # ドット3個
  "…"
)

$Files = @()
foreach($g in $Globs){
  $Files += Get-ChildItem -Path $Root -Recurse -File -Include $g -ErrorAction SilentlyContinue
}

$Viol = @()
foreach($F in $Files){
  $Txt = Get-Content -Raw -Encoding UTF8 -LiteralPath $F.FullName

  foreach($P in $Patterns){
    if($Txt -match $P){
      $Viol += "$($F.FullName)（検出: $P）"
    }
  }
}

Write-Host "`n🧩 Integrity check under: $Root`n" -ForegroundColor Yellow
if($Viol.Count -gt 0){
  Write-Host "❌ 分断・省略コード検出:" -ForegroundColor Red
  $Viol | ForEach-Object { Write-Host " - $_" }
  exit 1
}else{
  Write-Host "✅ 整合性OK — コードに分断なし" -ForegroundColor Green
}