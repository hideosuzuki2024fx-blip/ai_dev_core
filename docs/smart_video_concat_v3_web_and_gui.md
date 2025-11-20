# smart_video_concat v3 Web API / HTML クライアント / GUI 利用メモ

このドキュメントは、`ai_dev_core` リポジトリ内の **smart_video_concat v3** に対して追加した

- ローカル Web サーバ (`server_v3.py` / `run_server_v3.ps1`)
- DnD HTML クライアント (`smart_video_concat_v3_client.html`)
- v3 専用 GUI (`gui_v3.py`)

の使い方をまとめたものです。

---

## 1. 前提・共通仕様

### 1.1 ファイル構成（関連ファイル）

既存の v3 関連:

- apps/smart_video_concat/analyze_and_concat_v3.py  
  v3 本体のコアスクリプト（ディレクトリモード用）
- apps/smart_video_concat/run_smart_concat_v3.ps1  
  ディレクトリ指定で v3 を実行する PowerShell ラッパ
- apps/smart_video_concat/run_smart_concat_v3_dragdrop.ps1  
  CLI 版ドラッグ＆ドロップラッパ（ファイルパス復元ロジック付き）

今回追加したファイル:

- apps/smart_video_concat/server_v3.py  
  smart_video_concat v3 用ローカル Web サーバ (Flask)
- apps/smart_video_concat/run_server_v3.ps1  
  上記 Web サーバの起動用 PowerShell
- apps/smart_video_concat/smart_video_concat_v3_client.html  
  Web API を叩く DnD HTML クライアント
- apps/smart_video_concat/gui_v3.py  
  v3 専用の tkinter GUI

### 1.2 エンコード仕様（v3 共通）

v3 系での出力仕様は共通で、以下のフィルタを用いて

- 16:9
- 指定解像度（デフォルト: 1920x1080）
- SAR=1:1
- yuv420p

に正規化して連結します。

    scale=WIDTH:HEIGHT:force_original_aspect_ratio=decrease,
    pad=WIDTH:HEIGHT:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p

- WIDTH, HEIGHT は Web API / GUI のパラメータから指定（既定値は 1920x1080）
- 映像はアスペクト比を維持したまま縮小し、余白部分を黒帯でパディングします。

---

## 2. v3 Web API サーバ

### 2.1 サーバの起動

PowerShell から次のように実行します。

    pwsh .\apps\smart_video_concat\run_server_v3.ps1 -Port 5005

- 既定ホスト: 127.0.0.1
- ポート: デフォルト 5005（-Port で変更可能）

起動に成功すると、コンソールに次のようなメッセージが表示されます。

    Starting smart_video_concat v3 server on http://127.0.0.1:5005 ...
    Ctrl+C でサーバを停止できます。
     * Serving Flask app 'server_v3'
     * Running on http://127.0.0.1:5005
    Press CTRL+C to quit

停止はコンソールで Ctrl+C です。

### 2.2 API 仕様

エンドポイント:

- POST /api/smart_video_concat_v3

リクエスト（multipart/form-data）:

- files  
  required  
  mp4 ファイルを複数指定可能。配列の順番 = 連結順。
- crf  
  optional, int  
  既定値: 20
- preset  
  optional, str  
  既定値: "veryfast"
- width  
  optional, int  
  既定値: 1920
- height  
  optional, int  
  既定値: 1080

レスポンス:

- 成功時  
  Content-Type: video/mp4  
  ボディ: 連結済み mp4 のバイナリ（smart_concat_v3.mp4 相当）
- 失敗時  
  Content-Type: application/json

    {
      "error": "ffmpeg の実行に失敗しました。",
      "returncode": 1,
      "stdout": "...",
      "stderr": "..."
    }

### 2.3 curl での手動確認例

    curl.exe -X POST "http://127.0.0.1:5005/api/smart_video_concat_v3" `
      -F "files=@D:\clips\test\0 (6).mp4" `
      -F "files=@D:\clips\test\0 (54).mp4" `
      -F "crf=20" `
      -F "preset=veryfast" `
      -o "D:\clips\test\smart_concat_v3_from_api.mp4"

---

## 3. DnD HTML クライアント

### 3.1 ファイルパス

- apps/smart_video_concat/smart_video_concat_v3_client.html

### 3.2 使い方

1. 先に Web サーバを起動しておく。

       pwsh .\apps\smart_video_concat\run_server_v3.ps1 -Port 5005

2. エクスプローラで  
   apps\smart_video_concat\smart_video_concat_v3_client.html  
   をダブルクリックしてブラウザで開きます（file:// で OK）。

3. 画面構成（概要）:

   - サーバ設定  
     エンドポイント URL 入力欄。既定: http://127.0.0.1:5005/api/smart_video_concat_v3
   - 動画ファイルの選択  
     大きな DnD エリアに mp4 をドラッグ＆ドロップ。  
     またはクリックでファイルダイアログを開きます。  
     選択したファイルはリスト表示され、上から順に連結されます。
   - エンコード設定  
     CRF（既定: 20）、preset（既定: veryfast）、出力幅 / 高さ（既定: 1920 / 1080）。
   - 実行ボタン  
     連結を実行ボタン、ステータス表示、完了時のダウンロードリンク。

4. 操作フロー:

   1. エンドポイント URL は通常デフォルトのままでよいです。
   2. DnD エリアに mp4 をドラッグ＆ドロップ（複数可）。  
      別フォルダのファイルも混在して問題ありません。
   3. 必要に応じて CRF / preset / 幅 / 高さを調整します。
   4. 「連結を実行」をクリックします。
   5. 成功すると、ステータスに完了メッセージが表示され、自動で smart_concat_v3.mp4 のダウンロードが行われます。

### 3.3 CORS について

- smart_video_concat_v3_client.html は通常 file:// で開かれます。
- Web サーバは http://127.0.0.1:5005 で動作します。
- ブラウザの同一オリジンポリシーにより、そのままでは JS からのアクセスが制限されます。
- server_v3.py では、@app.after_request で以下のヘッダを付与し、file:// → http://127.0.0.1:5005 へのアクセスを許可しています。

    Access-Control-Allow-Origin: *
    Access-Control-Allow-Headers: Content-Type
    Access-Control-Allow-Methods: POST, OPTIONS

---

## 4. v3 専用 GUI (gui_v3.py)

### 4.1 ファイルパス

- apps/smart_video_concat/gui_v3.py

### 4.2 起動方法

    python .\apps\smart_video_concat\gui_v3.py

Windows 標準の CPython であれば、tkinter は同梱されている前提です。

### 4.3 画面構成

- 入力ファイル一覧  
  「追加...」ボタンで mp4 を複数選択。  
  「選択削除」「全クリア」で削除。  
  「上へ」「下へ」で順序入れ替え。  
  上から順に連結されます。
- エンコード設定  
  CRF（既定値: 20）、preset（既定値: veryfast）、幅 (width) / 高さ (height)（既定値: 1920 / 1080）。
- 出力ファイル  
  テキストボックスと「参照...」ボタン。  
  未指定の場合、最初に選んだファイルと同じフォルダに smart_concat_v3_gui.mp4 を提案します。
- ログエリア  
  実行した ffmpeg コマンドと stdout / stderr を表示します。

### 4.4 動作仕様

「連結を実行」ボタンを押すと、以下の処理を行います。

1. 入力ファイル / 出力ファイル / CRF / preset / 幅 / 高さを検証。
2. 一時ディレクトリに concat_list_v3.txt を生成。
3. ffmpeg を 1 回実行して出力ファイルを生成。

概略のコマンドは次のような形になります（実際はパスなどが展開されます）。

    ffmpeg -y -f concat -safe 0 -i <concat_list_v3.txt> ^
      -vf "scale=WIDTH:HEIGHT:force_original_aspect_ratio=decrease,pad=WIDTH:HEIGHT:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p" ^
      -c:v libx264 -preset <preset> -crf <crf> ^
      -c:a copy ^
      <output>

- 連結順は GUI のリストビューの順番（上 → 下）です。
- ffmpeg の returncode が 0 でない場合はエラーダイアログを表示し、ログエリアに stdout / stderr を出力します。
- ffmpeg コマンドが PATH に無い場合は、その旨をエラー表示します。

### 4.5 出力ファイル名の変更

- 「出力ファイル」のテキストボックスを直接書き換えることで、任意のファイル名に変更できます。
- 拡張子は自動補完しないため、xxx.mp4 のように自分で .mp4 を付与してください。

---

## 5. 補足

- Web API / HTML クライアント / GUI v3 は、いずれも v3 と同じエンコード仕様（16:9 / SAR=1:1 / yuv420p）を前提としています。
- 連結順の自動推定ロジック（v1/v2/v3 コア側）は、現時点では Web API / GUI v3 では使用しておらず、すべて「ユーザーが指定した順序」で連結する実装になっています。
- 将来的に既存 gui.py へ v3 モードを統合する場合、この gui_v3.py のロジックをベースにメニュー統合することを想定しています。
