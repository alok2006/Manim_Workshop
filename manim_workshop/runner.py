"""Invoking the Manim CLI, from Python, portably.

``scenes/`` is loaded **by path** (``manim render scenes/01_basics.py``), so the
tooling here only ever shells out — it never imports a scene module. That keeps
checks fast and side-effect free, and means a syntax error in a scene is
reported as a failed subprocess instead of an import traceback.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from .catalog import SceneInfo
from .paths import REPO_ROOT

__all__ = [
    "MANIM_QUALITIES",
    "DEFAULT_MEDIA_DIR",
    "DEFAULT_TIMEOUT",
    "ManimNotFoundError",
    "manim_command",
    "SceneRun",
    "run_scene",
    "find_rendered_video",
]

MANIM_QUALITIES = ("l", "m", "h", "p", "k")
"""``-ql`` 854x480@15, ``-qm`` 1280x720@30, ``-qh`` 1920x1080@60, ``-qp`` 2560x1440@60, ``-qk`` 3840x2160@60."""

RESOLUTION_PREFIX = {"l": "480", "m": "720", "h": "1080", "p": "1440", "k": "2160"}
"""Manim names its output folders after the vertical resolution (``480p15``)."""

DEFAULT_MEDIA_DIR = REPO_ROOT / "media"
"""Where Manim writes by default, relative to the repository root."""

DEFAULT_TIMEOUT = 900
"""Seconds before a single scene is considered hung."""


class ManimNotFoundError(RuntimeError):
    """Raised when no usable ``manim`` executable can be located."""


@dataclass
class SceneRun:
    """The outcome of one ``manim render`` invocation."""

    scene: SceneInfo
    dry_run: bool
    returncode: int
    output: str
    duration: float = 0.0
    """Wall-clock seconds spent in the subprocess."""

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def status(self) -> str:
        return "ok" if self.ok else "FAIL"


def manim_command() -> list[str]:
    """Return a command prefix that runs Manim, best candidate first.

    Order matters: inside a virtual environment the console script sitting next
    to :data:`sys.executable` is the one that belongs to *this* interpreter, so
    it wins over whatever ``manim`` happens to be on ``PATH``.
    """
    candidates = [
        Path(sys.executable).parent / "manim",
        Path(sys.executable).parent / "manimce",
    ]
    for candidate in candidates:
        if candidate.exists():
            return [str(candidate)]

    on_path = shutil.which("manim") or shutil.which("manimce")
    if on_path:
        return [on_path]

    # Last resort: the module entry point, if manim is importable at all.
    try:
        import manim  # noqa: F401
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise ManimNotFoundError(
            "Could not find the `manim` command. Activate your virtual "
            "environment (or install the requirements) first; see "
            "docs/01-getting-started.md."
        ) from exc
    return [sys.executable, "-m", "manim"]


def run_scene(
    scene: SceneInfo,
    *,
    quality: str = "l",
    dry_run: bool = False,
    media_dir: Path | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> SceneRun:
    """Execute one scene, returning a :class:`SceneRun` instead of raising.

    ``dry_run=True`` passes ``--dry_run``: Manim builds every frame but writes no
    video, which is the fastest honest answer to "does this script compile and
    run?".

    Raises
    ------
    ValueError
        If ``quality`` is not one of :data:`MANIM_QUALITIES`.
    """
    if quality not in MANIM_QUALITIES:
        raise ValueError(f"quality must be one of {MANIM_QUALITIES}, got {quality!r}")

    command = [
        *manim_command(),
        "render",
        f"-q{quality}",
        str(scene.path),
        scene.name,
    ]
    if dry_run:
        command.append("--dry_run")
    if media_dir is not None:
        command += ["--media_dir", str(media_dir)]

    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(scene.path.parent.parent),  # repository root: keep media/ together
        )
        return SceneRun(
            scene=scene,
            dry_run=dry_run,
            returncode=completed.returncode,
            output=completed.stdout + completed.stderr,
            duration=time.monotonic() - started,
        )
    except subprocess.TimeoutExpired as exc:
        # On timeout Python may hand back either str or bytes depending on when
        # the child was killed mid-write, so normalise both streams.
        return SceneRun(
            scene=scene,
            dry_run=dry_run,
            returncode=124,
            output=f"TIMEOUT after {timeout}s\n{_as_text(exc.stdout)}{_as_text(exc.stderr)}",
            duration=time.monotonic() - started,
        )


def _as_text(value: str | bytes | None) -> str:
    """Decode a captured stream to ``str`` without ever raising."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def find_rendered_video(
    scene: SceneInfo,
    *,
    quality: str = "l",
    media_dir: Path | None = None,
) -> Path | None:
    """Return the newest rendered video for ``scene``, or ``None``.

    Manim's layout is ``media/videos/<stage>/<quality>/<Scene>.mp4``; globbing
    the two middle levels keeps this working if Manim reorganises its output.
    When several qualities exist, the one matching ``quality`` wins.
    """
    root = Path(media_dir) if media_dir is not None else DEFAULT_MEDIA_DIR
    if not root.exists():
        return None

    candidates = sorted(
        root.glob(f"videos/*/*/{scene.name}.mp4"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return None

    prefix = RESOLUTION_PREFIX.get(quality)
    matching = [path for path in candidates if prefix and path.parent.name.startswith(prefix)]
    return (matching or candidates)[0]
