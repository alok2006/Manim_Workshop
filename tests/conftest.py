"""Shared pytest fixtures.

Two of these exist because the scene modules are loaded **by path** and cannot
be imported as packages (``scenes/01_basics.py`` is not a legal module name in
an ``import`` statement): ``scene_source`` hands a test the file's text, and
``repo_root`` locates the checkout.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from manim_workshop.catalog import all_scenes, scene_files
from manim_workshop.paths import REPO_ROOT


@dataclass(frozen=True)
class SceneSource:
    """A scene module's text plus its path, for AST-level assertions."""

    path: Path
    text: str

    @property
    def name(self) -> str:
        return self.path.name


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(params=scene_files(), ids=lambda path: path.name)
def scene_source(request) -> SceneSource:
    """Every scene module, one parametrised case each."""
    path: Path = request.param
    return SceneSource(path=path, text=path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def scene_names() -> list[str]:
    return [scene.name for scene in all_scenes()]
