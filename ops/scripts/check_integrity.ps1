# ops/scripts/check_integrity.ps1
# --- コード完全性・分断防止 自動検証スクリプト ---
$ErrorActionPreference = "Stop"
$root = "$PSScriptRoot/../../"
Write-Host "`n🧩 Integrity check under: $root" -ForegroundColor Cyan

# 対象ファイル
$targets = Get-ChildItem -Path $root -Recurse -Include *.ps1,*.py,*.md,*.yml
$patterns = "ここに本文","省略","中略","略","..."

$violations = @()
foreach ($f in $targets) {
    $c = Get-Content -Raw -Encoding UTF8 $f
    foreach ($p in $patterns) {
        if ($c -match $p) {
            $violations += "$($f.FullName)（検出: $p）"
        }
    }
}

if ($violations.Count -gt 0) {
    Write-Host "`n❌ 分断・省略コード検出:" -ForegroundColor Red
    $violations | ForEach-Object { Write-Host " - $_" }
    exit 1
} else {
    Write-Host "`n✅ 全ファイル整合性チェック完了。分断・省略なし。" -ForegroundColor Green
}