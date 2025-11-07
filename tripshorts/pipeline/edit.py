"""Video assembly and thumbnail helpers."""
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence

from moviepy.editor import concatenate_videoclips, ImageClip, VideoFileClip

from ..utils.audio import load_bgm
from ..utils.vision import best_frame, resize_image
from ..utils.io import ensure_dir
from .analyze import Shot
from .storyboard import ClipPlan

TARGET_SIZE = (1080, 1920)


def _clip_from_shot(shot: Shot, duration: float) -> VideoFileClip:
    clip = VideoFileClip(str(shot.source)).subclip(shot.start, min(shot.end, shot.start + duration))
    return clip.resize(newsize=TARGET_SIZE)


def _clip_from_image(image_path: Path, duration: float) -> ImageClip:
    clip = ImageClip(str(image_path)).set_duration(max(1.5, duration))
    return clip.resize(newsize=TARGET_SIZE)


def assemble_video(
    plans: Sequence[ClipPlan],
    images: Sequence[Path],
    bgm_path: Path | None,
    output_video: Path,
    fps: int,
) -> float:
    clips: List = []
    image_iter = iter(images)
    for plan in plans:
        clips.append(_clip_from_shot(plan.source, plan.target_duration))

    # If we do not have enough video shots, fill with images
    while len(clips) < len(plans):
        try:
            image_path = next(image_iter)
        except StopIteration:
            break
        clips.append(_clip_from_image(image_path, plans[len(clips)].target_duration))

    if not clips:
        for image_path in images:
            clips.append(_clip_from_image(image_path, 3.0))
        if not clips:
            raise RuntimeError("No clips or images available for assembly")

    final = concatenate_videoclips(clips, method="compose")

    bgm = load_bgm(bgm_path if bgm_path else None)
    if bgm is not None:
        final = final.set_audio(bgm.volumex(0.2).set_duration(final.duration))

    ensure_dir(output_video.parent)
    final.write_videofile(str(output_video), fps=fps, codec="libx264", audio_codec="aac")
    duration = final.duration
    final.close()
    if bgm is not None:
        bgm.close()  # type: ignore[attr-defined]
    return duration


def render_thumbnail(videos: Sequence[Path], images: Sequence[Path], output_path: Path) -> None:
    if videos:
        thumbnail = best_frame(videos[0])
    elif images:
        thumbnail = resize_image(images[0], TARGET_SIZE)
    else:
        raise RuntimeError("No media available for thumbnail")

    thumbnail.save(output_path, quality=95)
