from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from flask import Flask, jsonify, request, send_file
from werkzeug.utils import secure_filename

import analyze_and_concat_v3 as v3

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
TMP_ROOT = BASE_DIR / "tmp"
TMP_ROOT.mkdir(parents=True, exist_ok=True)


@app.after_request
def add_cors_headers(response):
    """
    シンプルな CORS ヘッダ付与。
    - file:// で開いた HTML から http://127.0.0.1:5005 へアクセスする用途を想定。
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


def run_ffmpeg_concat(
    input_files,
    output_path: Path,
    crf: int = 20,
    preset: str = "veryfast",
    width: int = 1920,
    height: int = 1080,
) -> Tuple[int, str, str]:
    """
    アップロードされた FileStorage 群を一時ディレクトリに保存し、
    v3 コア (analyze_and_concat_v3) と同じ特徴抽出・順序決定ロジックで
    連結順を推定したうえで、ffmpeg で 1 本の MP4 に連結します。

    - 特徴抽出: v3.extract_features (中身は v1 のロジックを再利用)
    - 順序決定: v3.build_order
    """
    work_dir = Path(
        tempfile.mkdtemp(prefix="svc_v3_", dir=str(TMP_ROOT))
    )

    saved_paths: List[Path] = []

    # 1) 一時ディレクトリに保存
    for idx, file_storage in enumerate(input_files, start=1):
        orig_name = file_storage.filename or f"input_{idx}.mp4"
        filename = secure_filename(orig_name) or f"input_{idx}.mp4"

        # 拡張子が mp4 でない場合も、最低限 mp4 で保存して ffmpeg に渡す
        if not filename.lower().endswith(".mp4"):
            filename = filename + ".mp4"

        dest = work_dir / f"{idx:04d}_{filename}"
        file_storage.save(dest)
        saved_paths.append(dest)

    if not saved_paths:
        return 1, "", "有効な mp4 入力が 1 件もありません。"

    # 2) v3 と同じ特徴抽出・順序推定ロジックを適用
    features = []
    for p in saved_paths:
        app.logger.info(f"特徴抽出 (API v3): {p}")
        start_feat, end_feat = v3.extract_features(str(p))
        features.append({"path": str(p), "start": start_feat, "end": end_feat})

    order = v3.build_order(features)
    ordered_paths = [features[i]["path"] for i in order]

    app.logger.info("推定された連結順 (先頭 -> 末尾) [API v3]:")
    for idx, path in enumerate(ordered_paths, start=1):
        app.logger.info("%2d. %s", idx, path)

    # 3) concat list を作成
    concat_path = work_dir / "concat_list_v3.txt"
    with concat_path.open("w", encoding="utf-8") as f:
        for p in ordered_paths:
            # Windows でも ffmpeg には POSIX 形式で渡す & ' をエスケープ
            posix = Path(p).as_posix().replace("'", "''")
            f.write(f"file '{posix}'\n")

    # 4) v3 と同じフィルタ構成で 16:9 / SAR=1:1 / yuv420p に正規化
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_path),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        str(crf),
        "-c:a",
        "copy",
        str(output_path),
    ]

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return proc.returncode, proc.stdout, proc.stderr


def _to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@app.route("/api/smart_video_concat_v3", methods=["POST", "OPTIONS"])
def smart_video_concat_v3():
    """
    POST /api/smart_video_concat_v3

    フィールド:
      - files: mp4 ファイルを複数指定（multipart/form-data）
      - crf:   任意 (int, 既定 20)
      - preset: 任意 (str, 既定 "veryfast")
      - width:  任意 (int, 既定 1920)
      - height: 任意 (int, 既定 1080)

    レスポンス:
      - 成功時: smart_concat_v3.mp4 をバイナリで返す (Content-Type: video/mp4)
      - 失敗時: JSON エラーと 4xx/5xx
    """
    if request.method == "OPTIONS":
        # CORS プリフライト
        return ("", 204)

    if "files" not in request.files:
        return jsonify(
            {"error": "multipart/form-data の files フィールドに mp4 を指定してください。"}
        ), 400

    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "files フィールドが空です。"}), 400

    crf = _to_int(request.form.get("crf"), 20)
    width = _to_int(request.form.get("width"), 1920)
    height = _to_int(request.form.get("height"), 1080)
    preset = request.form.get("preset") or "veryfast"

    output_dir = Path(
        tempfile.mkdtemp(prefix="svc_v3_out_", dir=str(TMP_ROOT))
    )
    output_path = output_dir / "smart_concat_v3.mp4"

    code, out, err = run_ffmpeg_concat(
        files,
        output_path=output_path,
        crf=crf,
        preset=preset,
        width=width,
        height=height,
    )

    if code != 0 or not output_path.exists():
        return (
            jsonify(
                {
                    "error": "ffmpeg の実行に失敗しました。",
                    "returncode": code,
                    "stdout": out,
                    "stderr": err,
                }
            ),
            500,
        )

    return send_file(
        output_path,
        mimetype="video/mp4",
        as_attachment=True,
        download_name="smart_concat_v3.mp4",
    )


def create_app() -> Flask:
    """将来的に WSGI サーバ等から使う場合のファクトリ。"""
    return app


def main() -> None:
    parser = argparse.ArgumentParser(
        description="smart_video_concat v3 用ローカル Web サーバ"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Flask の debug モードを有効化します。",
    )
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
