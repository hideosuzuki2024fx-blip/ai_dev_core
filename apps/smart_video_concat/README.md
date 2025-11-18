# Smart Video Concat (visual smoothness)

動画ファイルの冒頭と終端を簡易解析し、つながりが滑らかになりやすい順番に並べ替えて ffmpeg で連結するツールです。

コマンドライン版と GUI 版があり、さらに以下の 2 系統があります。

- v1: ffmpeg の -c copy を使って高速に連結する版（再エンコードなし）
- v2: libx264 で再エンコードしながら連結する版（互換性重視）

## ファイル構成

- analyze_and_concat.py  
  v1 の本体スクリプト。HSV 色ヒストグラムに基づいて順序を決定し、ffmpeg の concat demuxer + -c copy で連結します。

- run_smart_concat.ps1  
  analyze_and_concat.py を呼び出す v1 用 PowerShell ラッパーです。

- gui.py  
  v1 を呼び出す Tkinter ベースの簡易 GUI です。

- run_smart_concat_gui.ps1  
  gui.py を起動するための PowerShell ラッパーです。

- analyze_and_concat_v2.py  
  v1 と同じ特徴量・順序決定ロジックを利用しつつ、ffmpeg で libx264 による再エンコードを行う v2 本体です。

- run_smart_concat_v2.ps1  
  analyze_and_concat_v2.py を呼び出す v2 用 PowerShell ラッパーです。

## 前提条件

- Python 3.10 以降
- Python パッケージ: opencv-python, numpy
- ffmpeg がインストールされており、PATH から ffmpeg として実行できること
- GUI 利用時は、Python に Tkinter がインストールされていること（通常の Windows 向け Python であれば同梱されています）

## v1 の使い方（高速・再エンコードなし）

リポジトリ直下 (ai_dev_core) から PowerShell で実行します。

カレントディレクトリ直下の *.mp4 を対象に、自動順序で連結する例:

pwsh .\apps\smart_video_concat\run_smart_concat.ps1

特定ディレクトリを対象にする場合:

pwsh .\apps\smart_video_concat\run_smart_concat.ps1 -InputDir "D:\clips" -Pattern "*.mp4" -Output "out\smart_concat.mp4"

再帰的に探索したい場合:

pwsh .\apps\smart_video_concat\run_smart_concat.ps1 -InputDir "D:\clips" -Pattern "*.mp4" -Recursive

並び順だけ確認したい場合 (ffmpeg 実行なし):

pwsh .\apps\smart_video_concat\run_smart_concat.ps1 -InputDir "D:\clips" -DryRun

## v2 の使い方（再エンコードあり・互換性重視）

v2 では、順序決定ロジックは v1 と同じですが、出力時に libx264 で再エンコードします。  
異なるソースを混ぜたときのタイムスタンプや再生互換性を重視したい場合はこちらを使います。

基本的な呼び出し:

pwsh .\apps\smart_video_concat\run_smart_concat_v2.ps1 -InputDir "D:\clips" -Pattern "*.mp4" -Output "out\smart_concat_v2.mp4"

CRF や preset を調整する例:

pwsh .\apps\smart_video_concat\run_smart_concat_v2.ps1 -InputDir "D:\clips" -Crf 18 -Preset "slow"

並び順だけ確認したい場合 (ffmpeg 実行なし):

pwsh .\apps\smart_video_concat\run_smart_concat_v2.ps1 -InputDir "D:\clips" -DryRun

## GUI からの利用（v1）

1. リポジトリ直下 (ai_dev_core) から、次のコマンドで GUI を起動します。

   pwsh .\apps\smart_video_concat\run_smart_concat_gui.ps1

2. 表示されたウィンドウで以下を指定します。
   - 入力ディレクトリ: 連結したい mp4 ファイルが入っているフォルダ
   - ファイルパターン: デフォルトは *.mp4
   - 出力ファイル: 連結結果を書き出す mp4 のパス
   - 必要に応じて recursive / Dry run

3. 「実行」ボタンを押すと、ウィンドウ下部のログ欄に処理内容と実行ログが表示されます。

デスクトップからすぐ起動したい場合は、この run_smart_concat_gui.ps1 へのショートカットを作成し、デスクトップに配置してください。

## 動作概要（共通）

1. 対象となる動画ファイルを列挙します。
2. 各動画について、冒頭側・終端側からそれぞれ数枚のフレームをサンプリングし、HSV 色空間で 3D ヒストグラムを計算・正規化して特徴ベクトルとします。
3. 各動画ペア (i, j) について、「i の終端特徴」と「j の冒頭特徴」の距離 (L2 ノルム) をコストとみなします。
4. すべての動画を始点候補として、貪欲法で「毎回コストが最小の次動画」をつないでいく経路を構成し、総コストが最小のものを採用します。
5. 決定された順序で ffmpeg の concat demuxer を用いて連結し、出力動画を生成します。
   - v1: -c copy による高速連結
   - v2: libx264 による再エンコード連結

## 注意・制限

- ここでの「滑らかさ」は、色ヒストグラムの類似度に基づく簡易な指標です。
- 実際のカット編集としての自然さや意味的なつながりまでは考慮していません。
- すべての動画が同じ解像度・フレームレート・コーデックであることが望ましいです。
- 音声の解析は行っていません。
