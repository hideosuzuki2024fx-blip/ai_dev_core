Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$base = "E:\ai_dev_core"
Set-Location $base

Write-Host "🔁 発酵ループ起動中# CODE_TRUNCATED"

$dirs = @("NoteMD\0_raw","NoteMD\1_mash","NoteMD\2_ferment","NoteMD\3_article")
foreach ($d in $dirs) { if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null } }

function Format-Markdown($path) {
  $text = Get-Content -Raw -Path $path
  $text = ($text -split "`r?`n") | ForEach-Object { $_.TrimEnd() } | Where-Object { $_ -ne "" } | Out-String
  Set-Content -Path $path -Value $text -Encoding utf8
}

$rawFiles = Get-ChildItem "NoteMD\0_raw" -Filter *.md
foreach ($f in $rawFiles) {
  $mash = "NoteMD\1_mash\$($f.BaseName)_mash.md"
  Copy-Item $f.FullName $mash -Force
  Format-Markdown $mash
  Write-Host "🥣 整形: $($f.Name)"
}

$mashFiles = Get-ChildItem "NoteMD\1_mash" -Filter *.md
foreach ($f in $mashFiles) {
  $fer = "NoteMD\2_ferment\$($f.BaseName)_ferment.md"
  Copy-Item $f.FullName $fer -Force
  Add-Content $fer "`n---`n# Critique Stage`n- [ ] 構成`n- [ ] 論理`n- [ ] 発酵度"
  Write-Host "🧪 発酵: $($f.Name)"
}

$fermentFiles = Get-ChildItem "NoteMD\2_ferment" -Filter *.md
foreach ($f in $fermentFiles) {
  $final = "NoteMD\3_article\$($f.BaseName)_final.md"
  Copy-Item $f.FullName $final -Force
  Add-Content $final "`n---`n*Finalized $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')*"
  Write-Host "🍶 Final化: $($f.Name)"
}

git add NoteMD
git commit -m "chore: run ferment pipeline $(Get-Date -Format 'yyyyMMdd_HHmmss')"
git push

Write-Host "🎉 発酵ループ完了！"
