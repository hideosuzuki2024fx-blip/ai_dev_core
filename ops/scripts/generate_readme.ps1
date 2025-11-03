# PowerShell Script: generate_readme.ps1
# 実行すると README.md が完全生成されます（分断・欠落ゼロ）

\C:\Users\MaoGon\Projects\ai_dev_core = Join-Path \C:\Users\MaoGon 'Projects/ai_dev_core'
\ = Join-Path \C:\Users\MaoGon\Projects\ai_dev_core 'README.md'
\System.Text.UTF8Encoding = New-Object System.Text.UTF8Encoding \False

\ = @'
<ここにREADME全文を貼り付け>
'@

[System.IO.File]::WriteAllText(\, \, \System.Text.UTF8Encoding)
Write-Host "✅ README.md を完全生成しました。" -ForegroundColor Green