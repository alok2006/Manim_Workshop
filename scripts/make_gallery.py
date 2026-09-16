#!/usr/bin/env python3
"""Regenerate the stills in ``docs/gallery/`` from rendered videos.

The gallery in ``docs/03-scene-catalog.md`` is generated, not hand-painted:
this script grabs one frame from each scene's rendered video so the
documentation shows what the code actually draws.

Workflow::

    python scripts/check_scenes.py --render --quality l   # or: make render
    python scripts/make_gallery.py                        # or: make gallery

Frames are sampled at ~80% of each video's timeline: far enough in that the
curve is fully drawn, early enough to avoid the final ``FadeOut`` in scenes
that clear the screen at the end.

Requires ``ffmpeg``/``ffprobe`` on ``PATH``. Frames are written to
``docs/gallery/<SceneName>.png``.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim_workshop.catalog import all_scenes  # noqa: E402
from manim_workshop.paths import DOCS_DIR, REPO_ROOT  # noqa: E402
from manim_workshop.runner import find_rendered_video  # noqa: E402

GALLERY_DIR = DOCS_DIR / "gallery"
FRAME_POSITION = 0.8
"""Fraction of the timeline to sample (see module docstring)."""


def require(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        raise SystemExit(
            f"{tool} not found on PATH. Install ffmpeg (see docs/01-getting-started.md) "
            "and run this script again."
        )
    return path


def video_duration(ffprobe: str, video: Path) -> float:
    completed = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(json.loads(completed.stdout)["format"]["duration"])


def extract_frame(ffmpeg: str, video: Path, destination: Path, timestamp: float) -> None:
    subprocess.run(
        [
            ffmpeg,
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{timestamp:.3f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            str(destination),
        ],
        check=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--quality", default="l", help="quality subdirectory to prefer (default: l)"
    )
    parser.add_argument(
        "--media-dir", default=str(REPO_ROOT / "media"), help="Manim media directory"
    )
    parser.add_argument("--output-dir", default=str(GALLERY_DIR), help="where to write the PNGs")
    parser.add_argument("--only", default="", help="comma-separated scene names")
    args = parser.parse_args(argv)

    ffmpeg = require("ffmpeg")
    ffprobe = require("ffprobe")

    media_dir = Path(args.media_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scenes = all_scenes()
    if args.only:
        wanted = {name.strip() for name in args.only.split(",") if name.strip()}
        scenes = [scene for scene in scenes if scene.name in wanted]

    missing: list[str] = []
    written = 0

    for scene in scenes:
        video = find_rendered_video(scene, quality=args.quality, media_dir=media_dir)
        if video is None:
            missing.append(scene.name)
            continue
        duration = video_duration(ffprobe, video)
        timestamp = max(0.0, duration * FRAME_POSITION)
        destination = output_dir / f"{scene.name}.png"
        extract_frame(ffmpeg, video, destination, timestamp)
        written += 1
        print(
            f"  {scene.name:<38} {video.name:<28} t={timestamp:5.1f}s -> {destination.relative_to(REPO_ROOT)}"
        )

    print(f"\n{written}/{len(scenes)} stills written to {output_dir}")
    if missing:
        print(
            "no rendered video for: "
            + ", ".join(missing)
            + "\nRun `python scripts/check_scenes.py --render` (or `make render`) first.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
