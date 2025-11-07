"""Input ingestion logic."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from ..utils.io import MediaCollection, ensure_dir, find_media


@dataclass(frozen=True)
class IngestResult:
    media: MediaCollection
    working_dir: Path


def ingest(input_path: Path, working_dir: Path) -> IngestResult:
    """Prepare media assets for further processing."""

    ensure_dir(working_dir)
    media = find_media(input_path)
    return IngestResult(media=media, working_dir=working_dir)
