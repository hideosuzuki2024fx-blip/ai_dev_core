# ======================================
# Yoshio Code Integrity Checker (v3)
# 構文感知型：省略・中略等の誤検出を根絶
# ======================================
Set-Location "E:\ai_dev_core"
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "🧩 Integrity check under: $(Get-Location)"

$targets = Get-ChildItem -Recurse -Include *.ps1,*.py,*.md,*.yaml,*.yml | Where-Object {
    $_.FullName -notmatch "node_modules|venv|.git"
}

$detected = @()

foreach ($file in $targets) {
    $lines = Get-Content -Path $file.FullName
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i].Trim()

        # コメント行・docstring・空行・YAMLコメントはスキップ
        if ($line -match '^(#|//|<!--|"""|```|\'\'\'|--|%|!|$)') { continue }

        # 文中でなくコードとして「省略」等が含まれる場合のみ検出
        if ($line -match '(?<!#|//|<!--)\b(省略|中略|略(?!称))\b') {
            $detected += [PSCustomObject]@{
                Path  = $file.FullName
                Line  = $i + 1
                Text  = $line
            }
        }
    }
}

if ($detected.Count -gt 0) {
    Write-Host "❌ 分断・省略コード検出:"
    $detected | ForEach-Object {
        Write-Host " - $($_.Path) (L$($_.Line)): $($_.Text)"
    }
    Write-Host "⚠️ 注意: コメントやMarkdown内の『省略』は無視されました。"
    exit 1
} else {
    Write-Host "✅ Integrity check passed: No truncated or placeholder code found."
    exit 0
}
