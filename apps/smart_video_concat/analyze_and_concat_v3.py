import argparse
import os
import sys
import subprocess

import numpy as np
import cv2

# v1 の特徴抽出・並べ替えロジックを再利用
import analyze_and_concat as v1


def extract_features(path, num_samples=5):
    """
    v1 と同じ特徴抽出。
    """
    return v1.extract_features(path, num_samples=num_samples)


def build_order(features):
    """
    v1 と同じ順序決定ロジック。
    """
    return v1.build_order(features)


def run_ffmpeg_concat_reencode_normalized(
    files,
    output,
    workdir,
    crf=20,
    preset="veryfast",
    width=1920,
    height=1080,
):
    """
    ffmpeg の concat demuxer を使い、libx264 で再エンコードしながら、
    出力を指定の解像度 (width x height) / SAR=1:1 に正規化して連結する版。
    """
    list_path = os.path.join(workdir, "concat_list_v3.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for p in files:
            escaped = p.replace("'", "''")
            f.write(f"file '{escaped}'n")

    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
        "setsar=1,"
        "format=yuv420p"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-c:a", "copy",
        output,
    ]
    print("Running ffmpeg (reencode + aspect normalize):")
    print(" ".join(cmd))

    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed with exit code {proc.returncode}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "動画の冒頭・終端を解析して順序を決定し、"
            "libx264 で再エンコードしながら "
            "16:9 (デフォルト 1920x1080, SAR=1:1) に正規化して連結する v3 版です。"
        )
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="入力動画ファイル（省略時は --input-dir と --pattern を使用）。",
    )
    parser.add_argument(
        "--input-dir",
        default=".",
        help="動画を探索するディレクトリ（デフォルト: カレントディレクトリ）。",
    )
    parser.add_argument(
        "--pattern",
        default="*.mp4",
        help="入力動画の簡易パターン（拡張子にマッチ、例: *.mp4）。",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="input-dir 以下を再帰的に探索します。",
    )
    parser.add_argument(
        "--output",
        default="smart_concat_v3.mp4",
        help="出力動画パス。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="並び順の表示のみ行い、ffmpeg は実行しません。",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=20,
        help="libx264 の CRF 値（デフォルト: 20）。",
    )
    parser.add_argument(
        "--preset",
        default="veryfast",
        help="libx264 の preset（デフォルト: veryfast）。",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="出力動画の幅（デフォルト: 1920）。",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="出力動画の高さ（デフォルト: 1080）。",
    )

    args = parser.parse_args()

    # 入力動画の収集（v1/v2 と同様のロジック）
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

    print("検出された動画ファイル (v3):")
    for p in files:
        print(" -", p)

    # 特徴抽出
    features = []
    for p in files:
        print(f"n特徴抽出中 (v3): {p}")
        start_feat, end_feat = extract_features(p)
        features.append({"path": p, "start": start_feat, "end": end_feat})

    # 順序決定
    order = build_order(features)
    ordered_files = [features[i]["path"] for i in order]

    print("n推定された連結順 (先頭 -> 末尾) [v3]:")
    for i, p in enumerate(ordered_files):
        print(f"{i+1:2d}. {p}")

    if args.dry_run:
        print("n--dry-run 指定のため、ffmpeg による連結は行いません。")
        return

    out_path = os.path.abspath(args.output)
    workdir = os.path.dirname(out_path) or "."
    os.makedirs(workdir, exist_ok=True)

    run_ffmpeg_concat_reencode_normalized(
        ordered_files,
        out_path,
        workdir,
        crf=args.crf,
        preset=args.preset,
        width=args.width,
        height=args.height,
    )
    print("n出力ファイル (v3):", out_path)


if __name__ == "__main__":
    main()

