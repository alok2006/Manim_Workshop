"""File-system anchors for the workshop repository.

Every path in this project is derived from one place — this module — so that a
scene, a script, a test or the notebook can find the assets no matter which
directory it was launched from.
"""

from __future__ import annotations

from pathlib import Path

__all__ = [
    "PACKAGE_DIR",
    "REPO_ROOT",
    "ASSETS_DIR",
    "SCENES_DIR",
    "DOCS_DIR",
    "DEFAULT_IMAGE",
    "resolve_asset",
]

PACKAGE_DIR: Path = Path(__file__).resolve().parent
"""``<repo>/manim_workshop``"""

REPO_ROOT: Path = PACKAGE_DIR.parent
"""``<repo>`` — the root of a cloned copy of the repository."""

ASSETS_DIR: Path = REPO_ROOT / "assets"
"""Images and other media consumed by scenes."""

SCENES_DIR: Path = REPO_ROOT / "scenes"
"""One module per workshop stage; each holds one or more ``Scene`` classes."""

DOCS_DIR: Path = REPO_ROOT / "docs"
"""The written workshop notes."""

DEFAULT_IMAGE: Path = ASSETS_DIR / "doraemon.jpg"
"""The silhouette traced by :class:`scenes.07_fourier_epicycle.FourierEpicycle`."""


def resolve_asset(name: str | Path | None = None) -> Path:
    """Return an absolute path to an asset, or explain why it cannot be found.

    Resolution order for a relative ``name``:

    1. relative to the **current working directory** — an explicit user choice
       wins, so ``get_fourier_coefficients("my_photo.jpg")`` works from wherever
       that file happens to live;
    2. relative to the repository's ``assets/`` directory — so the images that
       ship with the workshop work from any directory.

    Parameters
    ----------
    name
        File name or path. ``None`` means :data:`DEFAULT_IMAGE`.

    Raises
    ------
    FileNotFoundError
        If none of the candidate locations exist. The message lists every
        location that was tried, which is the fastest way to fix a typo.

    Examples
    --------
    >>> resolve_asset().name            # doctest: +SKIP
    'doraemon.jpg'
    >>> resolve_asset("doraemon.jpg")   # doctest: +SKIP
    PosixPath('/.../assets/doraemon.jpg')
    """
    if name is None:
        if DEFAULT_IMAGE.exists():
            return DEFAULT_IMAGE
        candidates = [DEFAULT_IMAGE]
    else:
        path = Path(name).expanduser()
        candidates = (
            [path] if path.is_absolute() else [Path.cwd() / path, ASSETS_DIR / path]
        )

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    tried = "\n  ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(
        f"Asset {name!r} not found. Tried:\n  {tried}\n"
        f"Drop the file into {ASSETS_DIR} or pass an explicit path."
    )
