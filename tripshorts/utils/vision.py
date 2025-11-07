"""Vision helpers for thumbnails and frame metrics."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
from PIL import Image


def best_frame(video_path: Path, sample_stride: int = 15, target_size: tuple[int, int] = (1080, 1920)) -> Image.Image:
    """Pick the sharpest frame using Laplacian variance."""

    capture = cv2.VideoCapture(str(video_path))
    best_score = -1.0
    best_frame_img: Optional[Image.Image] = None
    frame_index = 0
    try:
        while True:
            success, frame = capture.read()
            if not success:
                break
            if frame_index % sample_stride == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                score = cv2.Laplacian(gray, cv2.CV_64F).var()
                if score > best_score:
                    best_score = score
                    resized = cv2.resize(frame, target_size)
                    best_frame_img = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
            frame_index += 1
    finally:
        capture.release()

    if best_frame_img is None:
        raise RuntimeError(f"No frames available in {video_path}")

    return best_frame_img


def resize_image(image_path: Path, target_size: tuple[int, int]) -> Image.Image:
    image = Image.open(image_path)
    return image.resize(target_size)
