# Meta: NoteOps token auth fix

- Date: 2026-01-04
- Problem:
  - token無しでも書き込みが通る（NOTEOPS_TOKEN がサーバ側で空扱い）
- Fix:
  - NOTEOPS_TOKEN を import時に固定せず、リクエスト毎に os.getenv から読む
  - /debug/repo に tokenEnabled を追加
  - run-noteops.ps1 に -Token 引数を追加し、起動時に確実に env へ注入
- Next TODO:
  - 運用モードでは local-dev bypass を無効化するフラグを追加
