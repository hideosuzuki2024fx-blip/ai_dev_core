import argparse
import os
import sys
import subprocess

import cv2
import numpy as np


def extract_features(path, num_samples=5):
    """
    各動画について、冒頭側と終端側からそれぞれ num_samples 枚のフレームをサンプリングし、
    HSV 色空間の 3 次元ヒストグラムを平均して特徴ベクトルにします。
    """
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {path}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count <= 0:
        raise RuntimeError(f"Video has no frames: {path}")

    # 冒頭側・終端側からサンプリングするフレームインデックス
    indices_start = np.linspace(0, max(frame_count - 1, 0), num=num_samples, endpoint=False, dtype=int)
    indices_end = np.linspace(max(frame_count - num_samples, 0), max(frame_count - 1, 0), num=num_samples, dtype=int)

    def sample_hist(idxs):
        hists = []
        for idx in idxs:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ok, frame = cap.read()
            if not ok or frame is None:
                continue
            # 解像度を落として計算コスト削減
            frame = cv2.resize(frame, (160, 90))
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # HSV の 3D ヒストグラム (8x8x4 bin)
            hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 8, 4], [0, 180, 0, 256, 0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            hists.append(hist)
        if not hists:
            # フレームが取れなかった場合はゼロベクトルで埋める
            return np.zeros((8 * 8 * 4,), dtype=np.float32)
        return np.mean(hists, axis=0)

    start_feat = sample_hist(indices_start)
    end_feat = sample_hist(indices_end)
    cap.release()
    return start_feat, end_feat


def build_order(features):
    """
    各動画 i の「終端特徴」と各動画 j の「冒頭特徴」の距離に基づいて、
    全体の遷移コストが小さくなるような順序を貪欲法で構成します。
    """
    n = len(features)
    if n <= 1:
        return list(range(n))

    # cost[i][j] = 動画 i の終端 -> 動画 j の冒頭 の距離
    cost = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                cost[i][j] = float("inf")
            else:
                end_i = features[i]["end"]
                start_j = features[j]["start"]
                diff = end_i - start_j
                cost[i][j] = float(np.linalg.norm(diff))

    best_path = None
    best_score = float("inf")

    # すべての動画を始点候補として、貪欲に経路を伸ばす
    for start in range(n):
        used = {start}
        path = [start]
        total = 0.0
        current = start
        while len(path) < n:
            next_idx = None
            next_cost = float("inf")
            for j in range(n):
                if j in used:
                    continue
                c = cost[current][j]
                if c < next_cost:
                    next_cost = c
                    next_idx = j
            if next_idx is None:
                break
            used.add(next_idx)
            path.append(next_idx)
            if len(path) > 1:
                total += next_cost
            current = next_idx
        if len(path) == n and total < best_score:
            best_score = total
            best_path = path

    if best_path is None:
        return list(range(n))
    return best_path


def run_ffmpeg_concat(files, output, workdir):
    """
    ffmpeg の concat demuxer を使って、files に並んだ順に連結します。
    """
    list_path = os.path.join(workdir, "concat_list.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for p in files:
            escaped = p.replace("'", "''")
            f.write(f"file '{escaped}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        output,
    ]
    print("Running ffmpeg:", " ".join(cmd))
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed with exit code {proc.returncode}")


def main():
    parser = argparse.ArgumentParser(
        description="動画の冒頭・終端を解析して、つながりが滑らかになる順に並び替えて連結します。"
    )
    parser.add_argument("inputs", nargs="*", help="入力動画ファイル（省略時は --input-dir と --pattern を使用）。")
    parser.add_argument("--input-dir", default=".", help="動画を探索するディレクトリ（デフォルト: カレントディレクトリ）。")
    parser.add_argument("--pattern", default="*.mp4", help="入力動画の簡易パターン（拡張子にマッチ、例: *.mp4）。")
    parser.add_argument("--recursive", action="store_true", help="input-dir 以下を再帰的に探索します。")
    parser.add_argument("--output", default="smart_concat.mp4", help="出力動画パス。")
    parser.add_argument("--dry-run", action="store_true", help="並び順の表示のみ行い、ffmpeg は実行しません。")
    args = parser.parse_args()

    # 入力動画の収集
    files = []
    if args.inputs:
        files = args.inputs
    else:
        # 簡易な suffix マッチで pattern を解釈
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
        print(f"\n特徴抽出中: {p}")
        start_feat, end_feat = extract_features(p)
        features.append({"path": p, "start": start_feat, "end": end_feat})

    # 順序決定
    order = build_order(features)
    ordered_files = [features[i]["path"] for i in order]

    print("\n推定された連結順 (先頭 -> 末尾):")
    for i, p in enumerate(ordered_files):
        print(f"{i+1:2d}. {p}")

    if args.dry_run:
        print("\n--dry-run 指定のため、ffmpeg による連結は行いません。")
        return

    # ffmpeg 連結
    out_path = os.path.abspath(args.output)
    workdir = os.path.dirname(out_path) or "."
    os.makedirs(workdir, exist_ok=True)
    run_ffmpeg_concat(ordered_files, out_path, workdir)
    print("\n出力ファイル:", out_path)


if __name__ == "__main__":
    main()
