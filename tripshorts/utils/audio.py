"""Audio helpers for TripShorts."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from moviepy.audio.io.AudioFileClip import AudioFileClip


def load_bgm(path: Optional[Path]) -> Optional[AudioFileClip]:
    """Load background music if the file exists."""

    if path is None:
        return None
    if not path.exists():
        raise FileNotFoundError(path)
    clip = AudioFileClip(str(path))
    return clip
