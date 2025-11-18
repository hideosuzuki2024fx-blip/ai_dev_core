import argparse
import os
import sys
import subprocess

import numpy as np
import cv2

# v1 の特徴抽出・並べ替えロジックを再利用
import analyze_and_concat as v1


def extract_features(path, num_samples=5):
    return v1.extract_features(path, num_samples=num_samples)


def build_order(features):
    return v1.build_order(features)


def run_ffmpeg_concat_reencode(files, output, workdir, crf=20, preset="veryfast"):
    """
    ffmpeg の concat demuxer を使い、libx264 で再エンコードして連結する版。
    -c copy ではなく再エンコードすることで、タイムスタンプやコンテナの違いに起因する
    再生互換性の問題を減らすことを狙います。
    """
    list_path = os.path.join(workdir, "concat_list_v2.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for p in files:
            escaped = p.replace("'", "''")
            # ここを修正: \n を文字列としてではなく「改行」として書き込む
            f.write(f"file '{escaped}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-vf", "format=yuv420p",
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-c:a", "copy",
        output,
    ]
    print("Running ffmpeg (reencode):", " ".join(cmd))
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed with exit code {proc.returncode}")


def main():
    parser = argparse.ArgumentParser(
        description="動画の冒頭・終端を解析して順序を決定し、libx264 で再エンコードしながら連結する v2 版です。"
    )
    parser.add_argument("inputs", nargs="*", help="入力動画ファイル（省略時は --input-dir と --pattern を使用）。")
    parser.add_argument("--input-dir", default=".", help="動画を探索するディレクトリ（デフォルト: カレントディレクトリ）。")
    parser.add_argument("--pattern", default="*.mp4", help="入力動画の簡易パターン（拡張子にマッチ、例: *.mp4）。")
    parser.add_argument("--recursive", action="store_true", help="input-dir 以下を再帰的に探索します。")
    parser.add_argument("--output", default="smart_concat_v2.mp4", help="出力動画パス。")
    parser.add_argument("--dry-run", action="store_true", help="並び順の表示のみ行い、ffmpeg は実行しません。")
    parser.add_argument("--crf", type=int, default=20, help="libx264 の CRF 値（画質・サイズのバランス、デフォルト: 20）。")
    parser.add_argument("--preset", default="veryfast", help="libx264 の preset（デフォルト: veryfast）。")

    args = parser.parse_args()

    # 入力動画の収集（v1 と同様のロジック）
    files = []
    if args.inputs:
        files = args.inputs
    else:
        suffix = args.pattern.replace("*", "").lower()
        if args.recursive:
            for root, dirs, fnames in os.walk(args.input_dir):
                for name in fnames:
                    if suffix and not name.lower().endswith(suffix):
                        continue
                    path = os.path.join(root, name)
                    if os.path.isfile(path):
                        files.append(path)
        else:
            for name in os.listdir(args.input_dir):
                path = os.path.join(args.input_dir, name)
                if not os.path.isfile(path):
                    continue
                if suffix and not name.lower().endswith(suffix):
                    continue
                files.append(path)

    files = sorted(set(os.path.abspath(p) for p in files))
    if not files:
        print("入力動画が見つかりませんでした。", file=sys.stderr)
        sys.exit(1)

    print("検出された動画ファイル:")
    for p in files:
        print(" -", p)

    # 特徴抽出
    features = []
    for p in files:
        print(f"\n特徴抽出中 (v2): {p}")
        start_feat, end_feat = extract_features(p)
        features.append({"path": p, "start": start_feat, "end": end_feat})

    # 順序決定
    order = build_order(features)
    ordered_files = [features[i]["path"] for i in order]

    print("\n推定された連結順 (先頭 -> 末尾) [v2]:")
    for i, p in enumerate(ordered_files):
        print(f"{i+1:2d}. {p}")

    if args.dry_run:
        print("\n--dry-run 指定のため、ffmpeg による連結は行いません。")
        return

    out_path = os.path.abspath(args.output)
    workdir = os.path.dirname(out_path) or "."
    os.makedirs(workdir, exist_ok=True)
    run_ffmpeg_concat_reencode(ordered_files, out_path, workdir, crf=args.crf, preset=args.preset)
    print("\n出力ファイル (v2):", out_path)


if __name__ == "__main__":
    main()
