# Photobook Demo Bootstrap

このディレクトリは、既存のFastAPIバックエンドを使って**即時に成果物を得るためのデモスクリプト**を提供します。

## できること
- `outputs/` 配下にサンプルのキャプションCSVとデモ画像を自動生成
- バックエンドの `/csv` `/pdf` エンドポイントを直接呼び出してPDFを作成
- 生成結果を `Demo Photobook.pdf` として保存

## 使い方
```bash
python apps/photobook_demo/bootstrap.py
```

実行すると `outputs/` に PDF が生成され、パスが標準出力に表示されます。そのまま既存の `uvicorn src.backend.main:app --reload` を起動すれば、`http://127.0.0.1:8000/static/` から同じPDFを閲覧できます。

## 前提条件
- `pip install -r requirements.txt` が完了していること
- WeasyPrint がバックエンド同様にインストールされていること（Linux/WSLを推奨）

デモ生成により、成果物が無い状態でもすぐにPDFとサンプル画像を確認できます。
