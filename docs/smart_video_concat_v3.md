# smart_video_concat v3 ドキュメント

このドキュメントは、smart_video_concat の v3 実装についてまとめたものです。  
v1 / v2 の仕様は既存ファイル（analyze_and_concat.py / analyze_and_concat_v2.py）を参照してください。

## v3 の概要

- 入力動画の冒頭・終端フレームを解析して「つながりの良さ」を元に並び替えるロジックは v1 ベース
- v2 と同様に ffmpeg + libx264 で再エンコードする
- v3 ではさらに **出力を 16:9 (デフォルト: 1920x1080, SAR=1:1) に正規化** する
    - scale=width:height:force_original_aspect_ratio=decrease
    - pad=width:height:(ow-iw)/2:(oh-ih)/2
    - setsar=1, format=yuv420p
- smart_concat_* で始まるファイル名（既存の連結結果）は自動的にスキップする

## 実装ファイル

- 本体: `apps/smart_video_concat/analyze_and_concat_v3.py`
- ディレクトリ＋パターン用ラッパ:
    - `apps/smart_video_concat/run_smart_concat_v3.ps1`
- ドラッグ＆ドロップ専用ラッパ:
    - `apps/smart_video_concat/run_smart_concat_v3_dragdrop.ps1`

## ディレクトリ＋パターンでの利用 (run_smart_video_concat_v3.ps1)

典型的な使い方:

    pwsh .\apps\smart_video_concat\run_smart_concat_v3.ps1 `
      -InputDir "D:\clips\test" `
      -Pattern "*.mp4" `
      -Output "D:\clips\test\smart_concat_v3_dirmode.mp4"

オプション:

- `-InputDir` : 探索するディレクトリ（デフォルト: カレント）
- `-Pattern`  : 拡張子パターン（例: `"*.mp4"`）
- `-Recursive`: サブフォルダも含めて探索する場合に指定
- `-Output`   : 出力ファイルパス
- `-Crf`      : libx264 の CRF（デフォルト: 20）
- `-Preset`   : libx264 の preset（デフォルト: veryfast）
- `-Width`    : 出力幅（デフォルト: 1920）
- `-Height`   : 出力高さ（デフォルト: 1080）
- `-DryRun`   : 並び順の計算とログ表示のみ行い、ffmpeg は実行しない

v3 本体側では、`-Pattern` にマッチしたファイルのうち:

- 出力ファイル自身（`-Output` で指定したパスと同じもの）
- `smart_concat_` で始まるファイル名

は自動的にスキップしてから特徴抽出と並び替えを行います。

## ドラッグ＆ドロップでの利用 (run_smart_video_concat_v3_dragdrop.ps1)

D&D 用ラッパ: `apps/smart_video_concat/run_smart_concat_v3_dragdrop.ps1`

### 使い方（エクスプローラーから）

1. `run_smart_concat_v3_dragdrop.ps1` のショートカットを作成し、デスクトップなど分かりやすい場所に置く
2. 連結したい mp4 ファイルをエクスプローラーで複数選択する
3. そのままショートカットにドラッグ＆ドロップする
4. **最初のファイルと同じフォルダ** に `smart_concat_v3.mp4` が出力される

### 使い方（コマンドラインから）

    pwsh .\apps\smart_video_concat\run_smart_concat_v3_dragdrop.ps1 `
      "D:\clips\test\0 (6).mp4" `
      "D:\clips\test\0 (54).mp4" `
      "D:\clips\test\013245.mp4"

- 引数として渡したファイルパスが、そのまま v3 本体の `inputs` に渡される
- 出力ファイル名は `smart_concat_v3.mp4`（先頭ファイルと同じディレクトリ）に固定

## 出力の仕様

- 出力解像度: デフォルト 1920x1080（Width / Height 引数で変更可）
- 画面比率: 常に 16:9
- SAR (Sample Aspect Ratio): 1:1 に正規化
- ピクセルフォーマット: yuv420p
- エンコード: libx264, CRF=20, preset=veryfast（引数で変更可）

縦長・横長が混在する素材の場合は、拡大ではなく「最大でも 1920x1080 に収まるよう縮小」した上で、足りない部分に黒帯を追加する（レターボックス／ピラーボックス）方式で統一しています。

## 注意事項・既知の仕様

- 明らかに壊れた mp4 ファイルは v1 と同様、OpenCV (cv2.VideoCapture) が開けない場合に例外となります。
- v3 の順序決定ロジックは v1 ベースなので、「どのクリップを素材にするか」は事前にディレクトリ構成や Pattern で制御してください。
- smart_concat_* 系のファイルは自動スキップされますが、誤って別名で出力した場合は対象に含まれます。
