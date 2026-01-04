# ✅ check_integrity.ps1（FINAL）
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if ($env:GITHUB_WORKSPACE) {
    Set-Location $env:GITHUB_WORKSPACE; $base=$env:GITHUB_WORKSPACE; $isCI=$true
} elseif (Test-Path "E:\ai_dev_core") {
    Set-Location "E:\ai_dev_core"; $base="E:\ai_dev_core"; $isCI=$false
} else {
    $base=(Get-Location).Path; $isCI=$false
}

Write-Host "`n🧩 Manifest-aware Integrity Check Starting..."
$manifestPath = Join-Path $base "SYSTEM_MANIFEST.yaml"
if (-not (Test-Path $manifestPath)) { throw "❌ SYSTEM_MANIFEST.yaml not found in $base" }

$manifest = Get-Content -Raw -Path $manifestPath -Encoding UTF8
$codeKinds=[regex]::Matches($manifest,'kind:\s*code','IgnoreCase').Count
$docKinds=[regex]::Matches($manifest,'kind:\s*document','IgnoreCase').Count
$allowTerms=@('仕様','説明','参照','例','context','manifest')

$targets=@()
if ($codeKinds -gt 0){$targets+=Get-ChildItem -Recurse -Include *.py,*.ps1 |?{$_ -notmatch 'venv|node_modules'}}
if ($docKinds -gt 0){$targets+=Get-ChildItem -Recurse -Include *.md,*.yaml |?{$_ -notmatch 'logs|backup'}}

$scriptPath = $MyInvocation.PSCommandPath
if (-not $scriptPath){$scriptPath=Join-Path $base "ops/scripts/check_integrity.ps1"}
$targets=$targets|?{$_.FullName -ne $scriptPath}

$issues=@()
foreach($f in $targets){
  $lines=@((Get-Content -Path $f.FullName -Encoding UTF8))
  for($i=0;$i -lt $lines.Count;$i++){
    $line=$lines[$i]
    if($line -match '(省略|略(?!称)|中略)'){
      $ctx=($lines[([Math]::Max(0,$i-2))..([Math]::Min($i+2,$lines.Count-1))]-join' ')
      $isContextual=$false
      foreach($term in $allowTerms){if($ctx -match $term){$isContextual=$true;break}}
      if(-not $isContextual -and ($f.Extension -in @('.py','.ps1'))){$issues+=$f.FullName;break}
    }
  }
}

if($issues.Count -gt 0){
  Write-Host "`n❌ 分断・省略コード検出:`n"
  $issues|sort -u|%{Write-Host " - $_"}
  if($isCI){exit 1}else{Write-Host "`n⚠ ローカルモード: 発酵継続可（エラーは記録のみ）";return}
}else{
  Write-Host "`n✅ Integrity check completed successfully."
  if($isCI){exit 0}else{return}
}
