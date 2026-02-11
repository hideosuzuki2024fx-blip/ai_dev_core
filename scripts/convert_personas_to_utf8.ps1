param([string]$Dir = ".\knowledge\personas")
$time = Get-Date -Format "yyyyMMddHHmmss"
$backup = "encoding-backup-$time.zip"
Compress-Archive -Path $Dir -DestinationPath $backup
Get-ChildItem -Path $Dir -Filter *.md -Recurse | ForEach-Object {
    $path = $_.FullName
    $text = Get-Content -Raw -Path $path -Encoding Default
    Set-Content -Path $path -Value $text -Encoding utf8
    Write-Host "→ UTF-8変換: $path"
}
Write-Host "✅ 完了: $backup にバックアップを保存しました。"
