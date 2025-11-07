"""Metadata generation utilities."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from rake_nltk import Rake

try:  # pragma: no cover - optional dependency bootstrap
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except Exception:  # noqa: BLE001
    HAS_WHISPER = False


@dataclass
class Metadata:
    title: str
    description: str
    tags: List[str]
    transcript: str
    run_id: str


DEFAULT_TITLE = "TripShorts"
MAX_DESCRIPTION_LENGTH = 800


def transcribe(video_path: Path, language: str = "ja") -> str:
    if not HAS_WHISPER:
        return ""
    model = WhisperModel("small", device="cpu")
    segments, _ = model.transcribe(str(video_path), language=language)
    text = " ".join(segment.text.strip() for segment in segments)
    return text


def extract_tags(text: str, top_k: int = 10) -> List[str]:
    if not text.strip():
        return ["travel", "trip", "vacation"]
    try:
        rake = Rake()
        rake.extract_keywords_from_text(text)
        ranked = rake.get_ranked_phrases()[:top_k]
        if ranked:
            return ranked
    except LookupError:
        pass

    words = [w.strip(".,!?:\"'") for w in text.split() if len(w) >= 3]
    freq: dict[str, int] = {}
    for word in words:
        if not word:
            continue
        lower = word.lower()
        freq[lower] = freq.get(lower, 0) + 1
    ranked_words = sorted(freq.items(), key=lambda item: item[1], reverse=True)
    return [word for word, _ in ranked_words[:top_k]] or ["travel", "trip", "vacation"]


def build_metadata(run_id: str, transcript: str) -> Metadata:
    title = f"TripShorts {run_id}"
    description = transcript[:MAX_DESCRIPTION_LENGTH]
    tags = extract_tags(transcript)
    return Metadata(title=title, description=description, tags=tags, transcript=transcript, run_id=run_id)


def save_metadata(metadata: Metadata, output_path: Path) -> None:
    payload = {
        "title": metadata.title,
        "description": metadata.description,
        "tags": metadata.tags,
        "transcript": metadata.transcript,
        "run_id": metadata.run_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
