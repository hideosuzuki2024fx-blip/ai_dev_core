$Root    = Join-Path $HOME "Projects/ai_dev_core"
$Backend = Join-Path $Root "src/backend"
$Static  = Join-Path $Root "src/static"
$Outputs = Join-Path $Root "outputs"
$LogFile = Join-Path $Outputs "uvicorn_latest.log"

Write-Host "`n=== 🔎 Diagnostics ===" -ForegroundColor Cyan
Write-Host "[CWD] $PWD"
Write-Host "[Root] $Root"

Write-Host "`n--- Folders ---"
Get-ChildItem $Root | Select-Object Name, LastWriteTime

Write-Host "`n--- Outputs (csv/pdf/images) ---"
Get-ChildItem $Outputs | Select-Object Name, Length, LastWriteTime

if (Test-Path $LogFile) {
  Write-Host "`n--- Tail Log ---"
  Get-Content $LogFile -Tail 200
} else {
  Write-Host "`n(ログなし: $LogFile)"
}

Write-Host "`n--- Latest CSV Content ---"
$LatestCsv = Get-ChildItem $Outputs -Filter *.csv | Sort-Object LastWriteTime -Desc | Select-Object -First 1
if ($LatestCsv) { Get-Content $LatestCsv.FullName } else { Write-Host "(CSVなし)" }

Write-Host "`n--- main.py Snippet (pdf) ---"
$MainPy = Join-Path $Backend "main.py"
if (Test-Path $MainPy) {
  (Select-String -Path $MainPy -Pattern "@app.post(`"/pdf`")" -Context 0,80) | ForEach-Object { $_.Context.PostContext }
} else { Write-Host "(main.pyなし)" }

Write-Host "`n✅ Diagnostics 完了" -ForegroundColor Green