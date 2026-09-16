"""``manim_workshop`` — shared helpers for the workshop notebook and scenes.

The package deliberately keeps *no* heavy imports at the top level: ``import
manim_workshop`` only exposes paths, so it stays usable from any script.

Submodules
----------
``manim_workshop.fourier``
    OpenCV + NumPy behind :class:`scenes.07_fourier_epicycle.FourierEpicycle`
    (the DFT of an image outline). Import it explicitly — it pulls in ``cv2``.
``manim_workshop.catalog``
    AST-only discovery of the ``Scene`` classes in ``scenes/``.
``manim_workshop.paths``
    ``REPO_ROOT``, ``ASSETS_DIR``, … and :func:`resolve_asset`.
"""

from __future__ import annotations

from .paths import ASSETS_DIR, DOCS_DIR, REPO_ROOT, SCENES_DIR, resolve_asset

__version__ = "1.0.0"

__all__ = [
    "ASSETS_DIR",
    "DOCS_DIR",
    "REPO_ROOT",
    "SCENES_DIR",
    "resolve_asset",
    "__version__",
]
