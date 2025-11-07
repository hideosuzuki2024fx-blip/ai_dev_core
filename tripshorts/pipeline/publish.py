"""Stubs for publishing to social platforms."""
from __future__ import annotations

from pathlib import Path


def publish_youtube(run_dir: Path) -> None:
    video = run_dir / "video.mp4"
    thumbnail = run_dir / "thumbnail.jpg"
    metadata = run_dir / "metadata.json"
    print(f"[YouTube] upload -> {video} {thumbnail} {metadata}")


def publish_x(run_dir: Path) -> None:
    video = run_dir / "video.mp4"
    metadata = run_dir / "metadata.json"
    print(f"[X] upload -> {video} {metadata}")
