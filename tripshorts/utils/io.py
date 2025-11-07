"""Utility helpers for filesystem I/O."""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


MEDIA_EXTENSIONS = {
    "video": (".mp4", ".mov", ".m4v"),
    "image": (".jpg", ".jpeg", ".png"),
}


@dataclass(frozen=True)
class MediaCollection:
    """Represents sorted media assets used for a single run."""

    videos: Tuple[Path, ...]
    images: Tuple[Path, ...]

    def all(self) -> Tuple[Path, ...]:
        return self.videos + self.images


class ExtractedArchive:
    """Context manager that extracts archives to a temp directory."""

    def __init__(self, source: Path):
        self._source = source
        self._tmpdir: tempfile.TemporaryDirectory[str] | None = None

    def __enter__(self) -> Path:
        self._tmpdir = tempfile.TemporaryDirectory()
        extract_to = Path(self._tmpdir.name)
        with zipfile.ZipFile(self._source, "r") as archive:
            archive.extractall(extract_to)
        return extract_to

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._tmpdir is not None:
            self._tmpdir.cleanup()


def ensure_dir(path: Path) -> None:
    """Create directory if it does not exist."""

    path.mkdir(parents=True, exist_ok=True)


def find_media(input_path: Path) -> MediaCollection:
    """Discover supported media files sorted by modification time."""

    if not input_path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")

    if input_path.is_file() and input_path.suffix.lower() == ".zip":
        with ExtractedArchive(input_path) as extracted:
            return _scan_directory(extracted)

    if input_path.is_dir():
        return _scan_directory(input_path)

    raise ValueError(f"Unsupported input: {input_path}")


def _scan_directory(directory: Path | str) -> MediaCollection:
    directory = Path(directory)
    videos: List[Path] = []
    images: List[Path] = []
    for ext in MEDIA_EXTENSIONS["video"]:
        videos.extend(sorted(directory.rglob(f"*{ext}"), key=_sort_key))
    for ext in MEDIA_EXTENSIONS["image"]:
        images.extend(sorted(directory.rglob(f"*{ext}"), key=_sort_key))

    if not videos and not images:
        raise FileNotFoundError(f"No supported media found under {directory}")

    return MediaCollection(tuple(videos), tuple(images))


def _sort_key(path: Path) -> Tuple[float, str]:
    try:
        stat = path.stat()
        return (stat.st_mtime, str(path))
    except FileNotFoundError:
        return (0.0, str(path))


def copy_tree(src: Path, dst: Path) -> None:
    """Copy directory tree contents."""

    if not src.exists():
        raise FileNotFoundError(src)

    ensure_dir(dst)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
