# TripShorts CLI

TripShorts は旅行素材から 30〜60 秒のショート動画を自動生成し、メタデータ・サムネイル・公開準備ファイルをまとめて出力する CLI ツールです。MVP では素材フォルダを指定するだけで、動画生成・SEO メタ生成・公開準備 ZIP の作成までを完結できます。

## はじめての方向けセットアップ（超丁寧版）

1. **TripShorts フォルダを開く**  
   ダウンロードしたリポジトリの中にある `tripshorts` フォルダをエクスプローラー（Windows）や Finder（macOS）で開きます。

2. **フォルダ内でターミナルを開く**  
   - Windows: フォルダの何もないところで `Shift + 右クリック` → **「PowerShell ウィンドウをここで開く」** を選びます。  
   - macOS: Finder で `tripshorts` フォルダを開いた状態で、画面上部メニューの **「表示 ▸ ターミナルでフォルダを開く」** を選ぶか、Spotlight で「ターミナル」と入力して開いた後、ターミナルに `cd ` と入力してから `tripshorts` フォルダをドラッグ＆ドロップします。

   これでターミナルの現在地（カレントディレクトリ）が自動的に `tripshorts` になります。手入力で長いパスを打つ必要はありません。

3. **Python 仮想環境を作る**  
   ターミナルで次のコマンドを一行ずつ実行します。

   ```bash
   python -m venv .venv
   ```

4. **仮想環境を起動する**  
   - Windows:  
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - macOS/Linux:  
     ```bash
     source .venv/bin/activate
     ```

   コマンド入力後、ターミナルの先頭に `(.venv)` の表示が追加されれば成功です。

5. **必要なライブラリを入れる**  
   仮想環境が有効なまま、次を実行します。

   ```bash
   pip install -r requirements.txt
   ```

   これで TripShorts が動くためのソフトがすべて揃います。

## 基本コマンド

```bash
# 旅行素材からショート動画を作る
python -m tripshorts.cli make --input ./tripshorts/input_sample --duration 45 --bgm ./tripshorts/assets/bgm_sample.mp3

# 出来上がった成果物を公開（API キーを設定したら）
python -m tripshorts.cli publish youtube --run tripshorts/outputs/2025-11-07_120101

# 成果物を ZIP にまとめて共有
python -m tripshorts.cli pack --run tripshorts/outputs/2025-11-07_120101
```

- `make`: 入力素材からショート動画、サムネイル、metadata.json を生成します。
- `publish`: API キーが設定されていれば YouTube / X に公開します（MVP ではスタブ出力）。
- `pack`: 生成物一式を ZIP にまとめます。

## ディレクトリ構成

```
tripshorts/
  assets/             # サンプルBGMやテンプレート素材を配置
  input_sample/       # テスト素材を配置（同梱の placeholder を削除して使用）
  outputs/            # 実行時に生成される成果物
  requirements.txt
  setup.cfg
  cli.py              # CLI エントリーポイント
  pipeline/           # 解析・編集・公開ステップ
  utils/              # 共通ユーティリティ
```

## 注意事項
- MoviePy が内部で FFmpeg を呼び出すため、システムに FFmpeg がインストールされている必要があります。わからない場合は「ffmpeg インストール Windows（または Mac）」で検索すると公式手順が見つかります。
- `faster-whisper` は任意機能（音声文字起こし）で、GPU がない環境では CPU モードで実行されます。
- API 連携はスタブ実装です。公開処理を実行する場合は `.env` に認証情報を設定し、`tripshorts/pipeline/publish.py` を拡張してください。
- うまくいかないときは、ターミナルを閉じて開き直し、もう一度手順 2 からやり直すと多くの問題が解決します。
