# ==============================================
# ✅ check_integrity.ps1 : manifest-aware version
# ==============================================
Set-Location "E:\ai_dev_core"
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "`n🧩 Manifest-aware Integrity Check Starting..."
$base = "E:\ai_dev_core"
$manifestPath = Join-Path $base "SYSTEM_MANIFEST.yaml"
if (-not (Test-Path $manifestPath)) {
    throw "❌ SYSTEM_MANIFEST.yaml not found."
}

# --- SYSTEM_MANIFEST を読む ---
$manifest = Get-Content -Raw -Path $manifestPath
$patternCode = Select-String -InputObject $manifest -Pattern "kind:\s*code" -AllMatches
$patternDoc  = Select-String -InputObject $manifest -Pattern "kind:\s*document" -AllMatches

# --- チェック対象ファイル ---
$targets = @()
if ($patternCode) {
    $targets += Get-ChildItem -Recurse -Include *.py,*.ps1 | Where-Object { -not ($_.FullName -match 'venv|node_modules') }
}
if ($patternDoc) {
    $targets += Get-ChildItem -Recurse -Include *.md,*.yaml | Where-Object { -not ($_.FullName -match 'logs|backup') }
}

$issues = @()
foreach ($f in $targets) {
    $text = Get-Content -Raw -Path $f.FullName
    if ($text -match '(省略|略(?!称)|中略)') {
        # 文脈判定
        if ($f.Extension -in @(".py",".ps1")) {
            $issues += $f.FullName
        }
    }
}

if ($issues.Count -gt 0) {
    Write-Host "`n❌ 分断・省略コード検出:`n"
    $issues | ForEach-Object { Write-Host " - $_" }
    exit 1
} else {
    Write-Host "`n✅ Integrity check completed successfully."
    exit 0
}
