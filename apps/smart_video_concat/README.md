# Smart Video Concat (visual smoothness)

動画ファイルの冒頭と終端を簡易解析し、つながりが滑らかになりやすい順番に並べ替えて ffmpeg で連結するツールです。

コマンドラインからの利用と、簡単なデスクトップ GUI からの利用の両方に対応しています。

## ファイル構成

- analyze_and_concat.py  
  各動画の冒頭・終端フレームから HSV 色ヒストグラムを抽出し、
  「ある動画の終端」と「別の動画の冒頭」の色分布の距離が小さくなるような順序を貪欲法で決定します。
  決定した順序に従って、ffmpeg の concat demuxer で連結します。

- run_smart_concat.ps1  
  リポジトリ直下から簡単にこのツールを呼び出すための PowerShell ラッパーです。

- gui.py  
  Tkinter を使った簡易 GUI ラッパーです。入力ディレクトリや出力ファイルを GUI 上で指定して実行できます。

- run_smart_concat_gui.ps1  
  gui.py を起動する PowerShell ラッパーです。ダブルクリックやショートカットから GUI を立ち上げる用途を想定しています。

## 前提条件

- Python 3.10 以降
- Python パッケージ: opencv-python, numpy
- ffmpeg がインストールされており、PATH から ffmpeg として実行できること
- GUI 利用時は、Python に Tkinter がインストールされていること（通常の Windows 向け Python であれば同梱されています）

## コマンドラインからの使い方

リポジトリ直下 (ai_dev_core) から PowerShell で実行します。

カレントディレクトリ直下の *.mp4 を対象に、自動順序で連結する例:

pwsh .\apps\smart_video_concat\run_smart_concat.ps1

特定ディレクトリを対象にする場合:

pwsh .\apps\smart_video_concat\run_smart_concat.ps1 -InputDir "D:\clips" -Pattern "*.mp4" -Output "out\smart_concat.mp4"

再帰的に探索したい場合:

pwsh .\apps\smart_video_concat\run_smart_concat.ps1 -InputDir "D:\clips" -Pattern "*.mp4" -Recursive

並び順だけ確認したい場合 (ffmpeg 実行なし):

pwsh .\apps\smart_video_concat\run_smart_concat.ps1 -InputDir "D:\clips" -DryRun

## GUI からの使い方

1. リポジトリ直下 (ai_dev_core) から、次のコマンドで GUI を起動します。

   pwsh .\apps\smart_video_concat\run_smart_concat_gui.ps1

2. 表示されたウィンドウで以下を指定します。
   - 入力ディレクトリ: 連結したい mp4 ファイルが入っているフォルダ
   - ファイルパターン: デフォルトは *.mp4
   - 出力ファイル: 連結結果を書き出す mp4 のパス

3. 必要に応じてオプションを指定します。
   - サブディレクトリも含める (recursive)
   - Dry run (連結を実行しない)

4. 「実行」ボタンを押すと、ウィンドウ下部のログ欄に処理内容と実行ログが表示されます。

デスクトップからすぐ起動したい場合は、この run_smart_concat_gui.ps1 へのショートカットを作成し、デスクトップに配置してください。

## 動作概要

1. 対象となる動画ファイルを列挙します。
2. 各動画について、冒頭側・終端側からそれぞれ数枚のフレームをサンプリングし、HSV 色空間で 3D ヒストグラムを計算・正規化して特徴ベクトルとします。
3. 各動画ペア (i, j) について、「i の終端特徴」と「j の冒頭特徴」の距離 (L2 ノルム) をコストとみなします。
4. すべての動画を始点候補として、貪欲法で「毎回コストが最小の次動画」をつないでいく経路を構成し、総コストが最小のものを採用します。
5. 決定された順序で ffmpeg の concat demuxer を用いて連結し、出力動画を生成します。

## 注意・制限

- ここでの「滑らかさ」は、色ヒストグラムの類似度に基づく簡易な指標です。
- 実際のカット編集としての自然さや意味的なつながりまでは考慮していません。
- すべての動画が同じ解像度・フレームレート・コーデックであることが望ましいです。
- 音声の解析は行っていません。
