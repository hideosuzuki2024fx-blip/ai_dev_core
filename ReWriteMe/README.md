# ReWriteMe

ReWriteMe は、ユーザーが書いた文章を AI の力で複数候補にリライトし、
それぞれの修正理由と感情トーンを可視化する Web アプリケーションです。
本リポジトリにはバックエンド (`backend`) とフロントエンド (`frontend`) の
ソースコードが含まれます。開発用の環境変数を設定することで、
ローカル環境でも簡単に動作を確認できます。

## 構成

- **backend**: Python/FastAPI による API サーバー。
  - `/rewrite` でリライト案を 3 件生成
  - `/emotion` で感情分析を実行
  - `/history` で履歴の保存・取得
- **frontend**: React(TypeScript) + Vite + Tailwind CSS による SPA。
  - テキスト入力、リライト結果の表示、感情メーター、比較ビューを提供

## セットアップ

### バックエンド

1. Python 3.10 以降をインストールします。
2. `backend` ディレクトリに移動し、依存関係をインストールします。

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. 環境変数 `OPENAI_API_KEY` を設定します。設定しない場合は簡易的な
   フォールバック実装が使用されます。

4. サーバーを起動します。

   ```bash
   uvicorn main:app --reload --port 8000
   ```

### フロントエンド

1. Node.js 18 以降をインストールします。
2. `frontend` ディレクトリに移動し、依存パッケージをインストールします。

   ```bash
   cd frontend
   npm install
   ```

3. 開発サーバーを起動します。

   ```bash
   npm run dev
   ```

   `vite.config.ts` でポート 8000 のバックエンドに API プロキシが設定されているため、
   フロントエンドから `/rewrite` 等のエンドポイントへ直接アクセスできます。

## テスト

簡易的な QA テストとして、以下の確認を推奨します。

1. `/rewrite` エンドポイントに POST すると、3 件のリライト案が返るか
2. `/emotion` エンドポイントが JSON 形式の感情ラベルを返すか
3. `/history` で履歴が保存され、GET で取得できるか
4. フロントエンドを起動した際にエラーなく画面が表示されるか

## ライセンス

このプロジェクトは教育目的で作成されたサンプルです。商用利用等はご自身で
ライセンス条件を決めた上でご利用ください。