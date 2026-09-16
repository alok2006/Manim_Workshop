"""The notebook is generated from ``scenes/`` — these tests prove it stayed that way.

A workshop notebook is the artefact students actually open. If it drifts from the
scene modules, the repository has two sources of truth and the notebook rots
first (it is the one nobody runs in CI). So the notebook here is *generated* by
``scripts/build_notebook.py``, and the tests below check the generation is
current and that every cell is coherent.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys

import pytest

from manim_workshop.catalog import all_scenes
from manim_workshop.paths import REPO_ROOT

NOTEBOOK = REPO_ROOT / "notebooks" / "workshop.ipynb"
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build_notebook.py"

MAGIC_RE = re.compile(r"^%%manim\s+(?P<flags>.*?)\s+(?P<scene>\w+)\s*$", re.MULTILINE)


@pytest.fixture(scope="module")
def notebook() -> dict:
    assert NOTEBOOK.exists(), "notebooks/workshop.ipynb is missing"
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))


def code_cells(notebook: dict) -> list[str]:
    """Code cell sources as strings.

    nbformat serialises ``source`` as a list of lines; joining them keeps the
    assertions below readable.
    """
    sources = []
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = cell["source"]
        sources.append("".join(source) if isinstance(source, list) else source)
    return sources


def test_notebook_is_valid_json_with_cells(notebook):
    assert notebook["nbformat"] == 4
    assert len(notebook["cells"]) > 20, "the notebook looks truncated"


def test_notebook_is_up_to_date_with_the_scenes(notebook):
    """Regenerating must be a no-op — otherwise the notebook has been hand-edited."""
    completed = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--check"],
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, (
        f"{completed.stdout}{completed.stderr}\n"
        "Run `python scripts/build_notebook.py` (or `make notebook`) to regenerate."
    )


def test_every_code_cell_parses(notebook):
    for index, source in enumerate(code_cells(notebook)):
        body = "\n".join(line for line in source.splitlines() if not line.startswith("%%"))
        try:
            ast.parse(body)
        except SyntaxError as exc:  # pragma: no cover - failure path
            pytest.fail(f"code cell {index} does not parse: {exc}")


def test_manim_cells_cover_every_scene(notebook):
    found = {
        match.group("scene")
        for source in code_cells(notebook)
        for match in MAGIC_RE.finditer(source)
    }
    expected = {scene.name for scene in all_scenes()}
    assert found == expected, (
        f"missing from the notebook: {sorted(expected - found)}; "
        f"unknown in the notebook: {sorted(found - expected)}"
    )


def test_manim_cell_source_matches_the_scene_module(notebook):
    """The class body in the notebook must be the class body on disk."""
    by_name = {scene.name: scene for scene in all_scenes()}

    for source in code_cells(notebook):
        match = MAGIC_RE.search(source)
        if not match:
            continue
        scene_name = match.group("scene")
        cell_body = "\n".join(line for line in source.splitlines() if not line.startswith("%%"))

        module_source = by_name[scene_name].path.read_text(encoding="utf-8")
        module_tree = ast.parse(module_source)
        module_class = next(
            node
            for node in module_tree.body
            if isinstance(node, ast.ClassDef) and node.name == scene_name
        )
        module_body = "\n".join(
            module_source.splitlines()[module_class.lineno - 1 : module_class.end_lineno]
        )

        assert cell_body.strip() == module_body.strip(), (
            f"{scene_name}: the notebook cell and {by_name[scene_name].relative_path} differ. "
            "Regenerate the notebook instead of editing it."
        )


def test_every_manim_cell_uses_low_quality(notebook):
    for source in code_cells(notebook):
        match = MAGIC_RE.search(source)
        if match:
            assert "-ql" in match.group("flags"), (
                f"{match.group('scene')} is not rendered at low quality in the notebook; "
                "the workshop develops at -ql"
            )


def test_notebook_imports_are_self_contained(notebook):
    """The first code cell must set up everything the later cells assume."""
    first = code_cells(notebook)[0]
    assert "from manim import *" in first
    assert "import numpy as np" in first

    # `--dry_run`-style magic must not be smuggled in: the notebook is meant to
    # produce real videos when a student runs it.
    assert "--dry_run" not in NOTEBOOK.read_text(encoding="utf-8")


def test_notebook_documents_the_fourier_helper(notebook):
    text = NOTEBOOK.read_text(encoding="utf-8")
    assert "from manim_workshop.fourier import get_fourier_coefficients" in text
    assert "docs/concepts/07-fourier-epicycles.md" in text
