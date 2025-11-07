"""Shot detection utilities for TripShorts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import cv2


@dataclass(frozen=True)
class Shot:
    source: Path
    start: float
    end: float


def detect_shots(video_path: Path, min_length: float = 1.0) -> List[Shot]:
    """Naive HSV histogram based shot detection."""

    capture = cv2.VideoCapture(str(video_path))
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if frame_count == 0:
        capture.release()
        return []

    prev_hist = None
    threshold = 0.65
    shots: List[Shot] = []
    start_frame = 0
    frame_index = 0

    try:
        while True:
            success, frame = capture.read()
            if not success:
                break
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [16, 16], [0, 180, 0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            if prev_hist is not None:
                distance = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)
                if distance > threshold:
                    end_time = frame_index / fps
                    start_time = start_frame / fps
                    if end_time - start_time >= min_length:
                        shots.append(Shot(source=video_path, start=start_time, end=end_time))
                    start_frame = frame_index
            prev_hist = hist
            frame_index += 1
    finally:
        capture.release()

    final_time = frame_index / fps
    start_time = start_frame / fps
    if final_time - start_time >= min_length:
        shots.append(Shot(source=video_path, start=start_time, end=final_time))

    return shots


def pick_segments(shots: List[Shot], desired_segments: int) -> List[Shot]:
    if not shots:
        return []
    if len(shots) <= desired_segments:
        return shots

    step = len(shots) / desired_segments
    result: List[Shot] = []
    index = 0.0
    for _ in range(desired_segments):
        result.append(shots[int(index)])
        index += step
    return result
