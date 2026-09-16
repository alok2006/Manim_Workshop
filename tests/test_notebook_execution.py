"""Execute the notebook in a real Jupyter kernel.

The other notebook tests are static. This one starts a kernel, runs every cell in
order and fails if any of them raises — which is the only way to know that the
notebook a student opens actually works: the imports, the ``%%manim`` magic (which
only registers when ``from manim import *`` runs) and the package import in the
finale section.

The cells are patched to pass ``--dry_run``, so the kernel compiles all 17 scenes
without encoding 3 minutes of video. Marked ``slow``.
"""

from __future__ import annotations

import shutil

import pytest

from manim_workshop.paths import REPO_ROOT

NOTEBOOK = REPO_ROOT / "notebooks" / "workshop.ipynb"

pytestmark = pytest.mark.slow


def _require_nbclient():
    pytest.importorskip("nbclient", reason="nbclient is needed to execute the notebook")
    pytest.importorskip("nbformat")
    pytest.importorskip("ipykernel")


@pytest.mark.skipif(shutil.which("python3") is None, reason="no python3 executable")
def test_notebook_runs_end_to_end(tmp_path):
    _require_nbclient()
    import nbformat
    from nbclient import NotebookClient

    notebook = nbformat.read(NOTEBOOK, as_version=4)

    magic_cells = 0
    for cell in notebook.cells:
        if cell.cell_type == "code" and cell.source.lstrip().startswith("%%manim"):
            cell.source = cell.source.replace("-ql ", "-ql --dry_run ", 1)
            magic_cells += 1

    assert magic_cells == 17, f"expected 17 scene cells, found {magic_cells}"

    # Use the kernel of the running interpreter, so the test exercises *this*
    # virtual environment (its manim, its numpy, its manim_workshop).
    notebook.metadata["kernelspec"] = {
        "name": "python3",
        "display_name": "Python 3",
        "language": "python",
    }

    client = NotebookClient(
        notebook,
        timeout=900,
        kernel_name="python3",
        allow_errors=False,
        resources={"metadata": {"path": str(tmp_path)}},
    )
    client.execute()

    # Every scene cell must have actually run a scene. The `%%manim` magic
    # captures Manim's log, so the visible proof is its progress bar.
    stream_text = "\n".join(
        "".join(output.get("text", ""))
        for cell in notebook.cells
        if cell.cell_type == "code"
        for output in cell.get("outputs", [])
        if output.get("output_type") == "stream"
    )
    assert "Animation" in stream_text, (
        f"no scene progress bar in the notebook output; the magic may not have run: {stream_text[:500]!r}"
    )

    # And `--dry_run` really means "write nothing", even from inside a kernel.
    stray_videos = list(tmp_path.rglob("*.mp4"))
    assert not stray_videos, f"dry-run cells wrote video: {stray_videos}"
