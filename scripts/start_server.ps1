$Root    = Join-Path $HOME "Projects/ai_dev_core"
$Backend = Join-Path $Root "src/backend"
$Outputs = Join-Path $Root "outputs"
$PyExe   = "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python310\python.exe"
$LogFile = Join-Path $Outputs "uvicorn_latest.log"

New-Item -ItemType Directory -Path $Outputs -ErrorAction SilentlyContinue | Out-Null
Remove-Item $LogFile -ErrorAction SilentlyContinue

Set-Location $Backend
Write-Host "✅ CWD = $Backend" -ForegroundColor Green
Write-Host "✅ Uvicorn 起動（ログ保存）..." -ForegroundColor Green
& $PyExe -m uvicorn main:app --reload *>&1 | Tee-Object -FilePath $LogFile