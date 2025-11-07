"""Storyboard planning helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .analyze import Shot


@dataclass(frozen=True)
class ClipPlan:
    source: Shot
    target_duration: float


DEFAULT_SEGMENTS = 6
MIN_CLIP_DURATION = 1.5


def build_storyboard(shots: List[Shot], target_duration: float, segments: int = DEFAULT_SEGMENTS) -> List[ClipPlan]:
    if not shots:
        return []

    segment_duration = max(MIN_CLIP_DURATION, target_duration / max(1, segments))
    plans: List[ClipPlan] = []
    for shot in shots[:segments]:
        plans.append(ClipPlan(source=shot, target_duration=segment_duration))
    return plans
