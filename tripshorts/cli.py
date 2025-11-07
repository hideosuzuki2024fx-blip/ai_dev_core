"""TripShorts command line interface."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from zipfile import ZipFile, ZIP_DEFLATED

from .pipeline.analyze import detect_shots, pick_segments
from .pipeline.edit import assemble_video, render_thumbnail
from .pipeline.ingest import ingest
from .pipeline.publish import publish_x, publish_youtube
from .pipeline.seo import build_metadata, save_metadata, transcribe
from .pipeline.storyboard import build_storyboard
from .utils.io import ensure_dir

RUNS_ROOT = Path("tripshorts/outputs")
DEFAULT_DURATION = 60
DEFAULT_FPS = 30


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser("TripShorts")
    sub = parser.add_subparsers(dest="command")

    make_cmd = sub.add_parser("make", help="Generate a short-form video from media inputs")
    make_cmd.add_argument("--input", required=True, help="Input directory or zip file")
    make_cmd.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    make_cmd.add_argument("--bgm", help="Optional background music path")
    make_cmd.add_argument("--lang", default="ja", help="Transcription language code")
    make_cmd.add_argument("--fps", type=int, default=DEFAULT_FPS)

    publish_cmd = sub.add_parser("publish", help="Publish generated outputs to a platform")
    publish_cmd.add_argument("platform", choices=["youtube", "x"])
    publish_cmd.add_argument("--run", required=True, help="Run directory produced by make command")

    pack_cmd = sub.add_parser("pack", help="Zip generated outputs for manual upload")
    pack_cmd.add_argument("--run", required=True)

    return parser.parse_args(argv)


def _resolve_run_directory() -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = RUNS_ROOT / timestamp
    ensure_dir(run_dir)
    return run_dir


def _command_make(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    run_dir = _resolve_run_directory()
    ingest_result = ingest(input_path=input_path, working_dir=run_dir)

    shots = []
    for video_path in ingest_result.media.videos:
        shots.extend(detect_shots(video_path))

    segments = pick_segments(shots, desired_segments=6)
    plans = build_storyboard(segments, target_duration=float(args.duration))

    video_path = run_dir / "video.mp4"
    thumbnail_path = run_dir / "thumbnail.jpg"
    metadata_path = run_dir / "metadata.json"

    duration = assemble_video(
        plans=plans,
        images=ingest_result.media.images,
        bgm_path=Path(args.bgm) if args.bgm else None,
        output_video=video_path,
        fps=int(args.fps),
    )

    render_thumbnail(ingest_result.media.videos, ingest_result.media.images, thumbnail_path)

    transcript = ""
    if ingest_result.media.videos:
        transcript = transcribe(ingest_result.media.videos[0], language=args.lang)

    metadata = build_metadata(run_dir.name, transcript)
    save_metadata(metadata, metadata_path)

    print(json.dumps({
        "run_dir": str(run_dir),
        "video": str(video_path),
        "thumbnail": str(thumbnail_path),
        "metadata": str(metadata_path),
        "duration": duration,
    }, ensure_ascii=False, indent=2))


def _command_publish(args: argparse.Namespace) -> None:
    run_dir = Path(args.run)
    if args.platform == "youtube":
        publish_youtube(run_dir)
    elif args.platform == "x":
        publish_x(run_dir)


def _command_pack(args: argparse.Namespace) -> None:
    run_dir = Path(args.run)
    if not run_dir.exists():
        raise FileNotFoundError(run_dir)
    zip_path = run_dir.with_suffix(".zip")
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for item in run_dir.rglob("*"):
            archive.write(item, arcname=str(item.relative_to(run_dir)))
    print(f"Packed -> {zip_path}")


def main(argv: Optional[list[str]] = None) -> None:
    args = _parse_args(argv)
    if args.command == "make":
        _command_make(args)
    elif args.command == "publish":
        _command_publish(args)
    elif args.command == "pack":
        _command_pack(args)
    else:
        print("No command specified", file=sys.stderr)


if __name__ == "__main__":
    main()
