"""The end-to-end proof: a scene really renders to a video file.

Everything else in the suite is static or geometry-level. This file buys the one
piece of evidence the others cannot: Manim, ffmpeg (via PyAV), the filesystem and
the scene all working together to produce a playable file.

It is marked ``slow`` because it costs a few seconds:

    pytest -m "not slow"    # skip it while iterating
"""

from __future__ import annotations

import pytest

from manim_workshop.catalog import find_scene
from manim_workshop.runner import find_rendered_video, run_scene

CHEAPEST_SCENE = "HelloCircle"
"""30 frames at -ql: the fastest real render in the repository."""


@pytest.mark.slow
def test_cheapest_scene_renders_a_playable_file(tmp_path):
    scene = find_scene(CHEAPEST_SCENE)
    assert scene is not None, f"{CHEAPEST_SCENE} disappeared from scenes/"

    result = run_scene(scene, quality="l", dry_run=False, media_dir=tmp_path, timeout=300)
    assert result.ok, f"render failed:\n{result.output[-2000:]}"

    video = find_rendered_video(scene, quality="l", media_dir=tmp_path)
    assert video is not None, f"no mp4 produced under {tmp_path}"
    assert video.stat().st_size > 1024, f"{video} looks empty"
    assert "File ready at" in result.output, "Manim did not report an output file"


@pytest.mark.slow
def test_dry_run_writes_nothing(tmp_path):
    """``--dry_run`` must be side-effect free — CI relies on it."""
    scene = find_scene(CHEAPEST_SCENE)
    assert scene is not None

    result = run_scene(scene, quality="l", dry_run=True, media_dir=tmp_path, timeout=300)
    assert result.ok, result.output[-2000:]
    assert not list(tmp_path.glob("videos/**/*.mp4")), "dry run wrote a video"
