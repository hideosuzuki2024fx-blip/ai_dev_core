# ops/scripts/check_integrity.ps1
# 分断・省略検出（コメント・コードブロック除外版）
$ErrorActionPreference = "Stop"
$Root = Resolve-Path "$PSScriptRoot/../../"
$Targets = Get-ChildItem -Path $Root -Recurse -File -Include *.ps1,*.py,*.md,*.yml
$Patterns = @("中略","省略","略(?!称)","\.\.\.","…")
$Violations = @()

foreach ($File in $Targets) {
    $Content = Get-Content -Raw -Encoding UTF8 -LiteralPath $File.FullName

    # === 除外ロジック追加 ===
    # コードブロック内 (``` ～ ```) と コメント行 (# で始まる行) を除外
    $Filtered = $Content -split "`n" | Where-Object {
        ($_ -notmatch '^\s*#') -and
        ($_ -notmatch '^\s*```')
    } | Out-String

    foreach ($Pattern in $Patterns) {
        if ($Filtered -match $Pattern) {
            $Violations += "$($File.FullName)（検出: $Pattern）"
        }
    }
}

if ($Violations.Count -gt 0) {
    Write-Host "`n🧩 Integrity check under: $Root`n" -ForegroundColor Yellow
    Write-Host "❌ 分断・省略コード検出:" -ForegroundColor Red
    $Violations | ForEach-Object { Write-Host " - $_" }
    exit 1
} else {
    Write-Host "`n✅ 整合性OK — 分断なし" -ForegroundColor Green
}