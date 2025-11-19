@echo off
REM smart_video_concat v3 drag & drop launcher (.cmd wrapper)

setlocal

REM この cmd と同じフォルダにある ps1 を指す
set SCRIPT_DIR=%~dp0
set PS1_PATH=%SCRIPT_DIR%run_smart_concat_v3_dragdrop.ps1

REM PowerShell 7 (pwsh) で ps1 を実行し、D&D した引数(%*)をそのまま渡す
REM 終了後に Enter 待ちして、ウィンドウが即閉じしないようにする
pwsh -NoLogo -ExecutionPolicy Bypass -Command ^
  "& '%PS1_PATH%' @args; Write-Host ''; Write-Host '--- done ---'; Read-Host 'Press Enter to close window'" ^
  %*

endlocal
