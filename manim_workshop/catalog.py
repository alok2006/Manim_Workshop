"""Discovery of the scenes in ``scenes/`` — by parsing, never by importing.

Why AST instead of ``import``:

* scene modules are loaded **by path** (``manim render scenes/01_basics.py``),
  and their file names start with digits, so ``import scenes.01_basics`` is not
  even valid Python syntax;
* importing a scene module executes manim's startup cost, which is exactly what
  a fast pre-flight check is trying to avoid;
* parsing cannot have side effects, so this is safe to call from tests, CI and
  editors.

The functions here are the single source of truth for "what scenes exist",
used by ``scripts/check_scenes.py``, the test-suite and the documentation check.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from .paths import REPO_ROOT, SCENES_DIR

__all__ = [
    "SCENE_FILE_PATTERN",
    "LEGACY_SCENE_NAMES",
    "SceneInfo",
    "scene_files",
    "module_docstring",
    "is_scene_class",
    "scenes_in_file",
    "all_scenes",
    "find_scene",
]

SCENE_FILE_PATTERN = "[0-9][0-9]_*.py"
"""Workshop stages are numbered so they sort in teaching order."""

LEGACY_SCENE_NAMES: dict[str, str] = {
    # name in the original notebook  ->  name in scenes/
    "aCircle": "HelloCircle",
    "aFilledCircle": "FilledCircle",
    "ConvertSqtoCircle": "SquareToCircle",
    "CircleAndSqaure": "CircleAndSquare",
    "CircleAndSqaureRotating": "CircleAndSquareRotating",
    "CircleAndSqaureRotatingWithTracing": "CircleAndSquareRotatingWithTracing",
    "CircleAndCircleRotatingAndMoved": "CircleAndCircleRotating",
    "CircleAndCircleMoving": "CircleAndCircleMoving",
    "CircleAndDotRotatingMovingANDTracing": "CircleAndDotRotatingAndTracing",
    "Snake": "SineSnake",
    "EpiCycloids": "Epicycloid",
    "LissajousFigures": "LissajousFigures",
    "MyRose": "RoseCurve",
    "MyFlowerWIthColors": "FlowerWithColors",
    "MyRotatingFlower": "RotatingFlower",
    "MyFlowerWithGradientEffect": "FlowerWithGradient",
    "MyFourierEpicyle": "FourierEpicycle",
}
"""Renames applied when the notebook was split into modules.

The original names are misspelled (``Sqaure``, ``cirlce``, ``Epicyle``) and were
kept in the notebook for years, so anyone arriving with old slides needs a way
to find the new name. ``docs/03-scene-catalog.md`` renders this mapping as a
table, and the test-suite asserts that it stays complete and bijective."""


@dataclass(frozen=True)
class SceneInfo:
    """One ``Scene`` subclass found on disk."""

    name: str
    """The class name, e.g. ``FourierEpicycle``."""

    path: Path
    """Absolute path of the module that defines it."""

    lineno: int
    """Line of the ``class`` statement."""

    docstring: str | None
    """First line of the class docstring, if it has one."""

    @property
    def relative_path(self) -> str:
        """Path relative to the repository root, POSIX separators."""
        return self.path.relative_to(REPO_ROOT).as_posix()

    @property
    def stage(self) -> str:
        """The stage the scene belongs to, e.g. ``01_basics``."""
        return self.path.stem

    def render_command(self, quality: str = "l") -> str:
        """A copy-pasteable command that renders this scene."""
        return f"manim render -q{quality} {self.relative_path} {self.name}"


def scene_files(directory: Path | None = None) -> list[Path]:
    """Return the scene modules, in teaching order (``01_…``, ``02_…``, …)."""
    root = Path(directory) if directory is not None else SCENES_DIR
    return sorted(root.glob(SCENE_FILE_PATTERN))


def module_docstring(path: Path) -> str | None:
    """Return the module-level docstring of ``path``, or ``None``."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return ast.get_docstring(tree, clean=True)


def is_scene_class(node: ast.ClassDef) -> bool:
    """True if ``node`` subclasses something whose name ends in ``Scene``.

    Covers ``Scene`` and any of manim's variants (``ThreeDScene``,
    ``MovingCameraScene``, …) without importing manim.
    """
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id.endswith("Scene"):
            return True
        if isinstance(base, ast.Attribute) and base.attr.endswith("Scene"):
            return True
    return False


def scenes_in_file(path: Path) -> list[SceneInfo]:
    """Return every ``Scene`` subclass defined in ``path``."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    infos = []
    for node in tree.body:  # top level only: scenes are public API
        if isinstance(node, ast.ClassDef) and is_scene_class(node):
            infos.append(
                SceneInfo(
                    name=node.name,
                    path=Path(path).resolve(),
                    lineno=node.lineno,
                    docstring=ast.get_docstring(node, clean=True),
                )
            )
    return infos


def all_scenes(directory: Path | None = None) -> list[SceneInfo]:
    """Every scene in the repository, grouped by module and then by line."""
    infos: list[SceneInfo] = []
    for path in scene_files(directory):
        infos.extend(scenes_in_file(path))
    return infos


def find_scene(name: str, directory: Path | None = None) -> SceneInfo | None:
    """Return the scene called ``name``, or ``None`` if it does not exist."""
    for info in all_scenes(directory):
        if info.name == name:
            return info
    return None
