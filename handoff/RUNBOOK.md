# RUNBOOK – Photobook Backend

## 起動手順
1. PowerShellを開く
2. `scripts/build_backend.ps1` を実行（安全再生成）
3. `scripts/start_server.ps1` を実行（ログ採取しつつ起動）
4. ブラウザで `http://127.0.0.1:8000/static/index.html` を開く
5. セクションAでCSV生成 → セクションBでCSV選択＆画像複数選択 → 「PDF生成」

## 期待結果
- 表紙1ページ
- 以降：各ページに「画像 + キャプション（同ページ内）」で整列

## トラブル対応
- 画像が出ない／キャプションが出ない：
  - `scripts/collect_diagnostics.ps1` を実行し、出力を共有
  - `outputs/uvicorn_latest.log` を確認
  - `outputs/*.csv` の内容（caption列）を確認

## 主要ファイル
- `src/backend/main.py` … FastAPIエンドポイント群（/csv, /list_csv, /pdf, /preview）
- `src/static/index.html` … UI（CSV作成、CSV選択、画像複数選択、PDF生成）
- `outputs/` … 生成物（*.csv, *.pdf, ログ）