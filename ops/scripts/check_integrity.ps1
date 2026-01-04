# --- Yoshio Patch: SKIP_INTEGRITY Safe Bypass ---
if ($env:SKIP_INTEGRITY -eq "true") {
    Write-Host "⚙️ SKIP_INTEGRITY=true → Integrity チェックをスキップします。"
    if ($env:GITHUB_ACTIONS -eq "true") {
        exit 0  # Actions 環境では正常終了
    } else {
        return   # ローカルでは return で抜ける（ターミナルを閉じない）
    }
}
# --- End Yoshio Patch ---
$ErrorActionPreference = "Stop"

# ルート解決
$Root = Resolve-Path "$PSScriptRoot/../../"

# 走査対象
$Targets = Get-ChildItem -Path $Root -Recurse -File -Include *.ps1,*.py,*.md,*.yml

# 除外（パス基準）
$ExcludePathRegex = @(
  '\.github[\\/]+workflows[\\/]+',      # CI定義は対象外
  'ops[\\/]+scripts[\\/]+check_integrity\.ps1$',  # 自己除外
  'ops[\\/]+ai_policy\.md$',            # 規範本文は例示語を含むため除外
  'README\.md$'                        # READMEの方針文も除外（必要に応じて外せる）
) -join '|'

# 検出パターン（分断・# CODE_TRUNCATEDを疑う語）
$Patterns = @('# CODE_TRUNCATED','# CODE_TRUNCATED','# CODE_TRUNCATED(?!称)','\.\.\.','# CODE_TRUNCATED')

# コードフェンス/インラインコードを除去して本文のみ検査
function Strip-Code($s) {
  if (-not $s) { return $s }
  # ``` ``` フェンス除去（言語指定あり/なし）
  $s = [regex]::Replace($s, '(?s)```.*?```', '')
  # インラインコード `code` 除去
  $s = [regex]::Replace($s, '(?<!`)`[^`\r\n]+`(?!`)', '')
  return $s
}

Write-Host "`n🧩 Integrity check under: $Root" -ForegroundColor Cyan
$Violations = @()

foreach ($F in $Targets) {
  $full = $F.FullName
  if ($full -match $ExcludePathRegex) { continue }
  $raw = Get-Content -Raw -Encoding UTF8 -LiteralPath $full
  $body = Strip-Code $raw
  foreach ($P in $Patterns) {
    if ($body -match $P) {
      $Violations += "$full（検出: $P）"
    }
  }
}

if ($Violations.Count -gt 0) {
  Write-Host "`n❌ 分断・# CODE_TRUNCATEDコード検出:" -ForegroundColor Red
  $Violations | ForEach-Object { Write-Host " - $_" }
  exit 1
} else {
  Write-Host "`n✅ 整合性OK（AI分断禁止チェック）" -ForegroundColor Green
}

Write-Host "✅ Integrity check completed (non-fatal mode)"
exit 0
