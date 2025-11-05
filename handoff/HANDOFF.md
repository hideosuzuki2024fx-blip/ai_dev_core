---
type: handoff
date: 2025-11-06
owner: MaoGon
version: 0.3
status: ready
paths:
  root: ~/Projects/ai_dev_core
  backend: ~/Projects/ai_dev_core/src/backend
  static:  ~/Projects/ai_dev_core/src/static
  outputs: ~/Projects/ai_dev_core/outputs
runtime:
  python: C:\Users\MaoGon\AppData\Local\Programs\Python\Python310\python.exe
  server: uvicorn main:app --reload
endpoints:
  csv_create: POST /csv  (title, captions: CSV rows "caption,text")
  csv_list:   GET  /list_csv
  pdf_build:  POST /pdf (title, csv_name, files[])
  preview:    GET  /preview?file=<pdf_name>
  static:     GET  /static/index.html
notes:
  - CSVは outputs/*.csv に保存されます
  - PDFは outputs/<title>.pdf に保存・配信されます
  - 画像URIは file:/// 経由でWeasyPrintへ渡します（Path.as_uri()）
checklist:
  - [ ] scripts/build_backend.ps1 実行（main.py / index.html 再生成）
  - [ ] scripts/start_server.ps1 実行（uvicorn起動＆ログ採取）
  - [ ] /static/index.html を開き、A→Bの順に操作してPDFをプレビュー
  - [ ] 不具合時は scripts/collect_diagnostics.ps1 でログ収集