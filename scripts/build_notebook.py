#!/usr/bin/env python3
"""Generate ``notebooks/workshop.ipynb`` *from* the scene modules.

The workshop learns from a notebook, but the repository's source of truth is
``scenes/``. Rather than maintaining both by hand (and watching them drift), this
script builds the notebook: one markdown cell of context per scene, followed by a
code cell containing that scene's real source, wrapped in the ``%%manim`` magic.

    python scripts/build_notebook.py            # write the notebook
    python scripts/build_notebook.py --check    # fail if it is out of date

``make notebook`` runs the first form, and CI runs the second, so the notebook
cannot silently disagree with the code.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import nbformat  # noqa: E402

from manim_workshop.catalog import SCENES_DIR, all_scenes  # noqa: E402
from manim_workshop.paths import REPO_ROOT  # noqa: E402

NOTEBOOK = REPO_ROOT / "notebooks" / "workshop.ipynb"
NOTEBOOK_DIR = NOTEBOOK.parent

PREAMBLE = """\
# Manim Workshop

From one circle to Fourier epicycles tracing a photograph.

This notebook is **generated** from `scenes/` by `scripts/build_notebook.py` —
the code in every cell below is the same code the repository ships, so you can
copy any cell into a `.py` file and run it with the `manim` CLI instead.

## Before you start

```bash
uv venv --python 3.13 && source .venv/bin/activate
uv pip install -r requirements.txt && uv pip install -e .
pip install -r requirements-dev.txt        # JupyterLab + ipykernel
python -m ipykernel install --user --name manim-workshop --display-name "Python (manim-workshop)"
```

Then choose **Kernel → Change Kernel → Python (manim-workshop)**. The
`pip install -e .` line is what makes `manim_workshop` importable in the last
section. Full details: `docs/01-getting-started.md`.
"""

IMPORTS = """\
from manim import *
import numpy as np

config.max_files_cached = 200
"""

FOURIER_INTRO = """\
## The finale: Fourier epicycles

Everything so far has been shapes. This last one is the trick from 3Blue1Brown's
*"But what is a Fourier series?"*: a chain of rotating circles, whose radii and
phases come from a Fourier transform, draws any closed outline you give it.

The maths now lives in the package rather than in this notebook (one
implementation, used by both the notebook and `scenes/07_fourier_epicycle.py`).
The annotated walk-through is in `docs/concepts/07-fourier-epicycles.md`.
"""

FOURIER_IMPORT = """\
from manim_workshop.fourier import get_fourier_coefficients

# The bundled silhouette: a dark subject on a light background.
coeffs = get_fourier_coefficients()
print(f"{len(coeffs)} circles; the biggest has radius {coeffs[0]['radius']:.3f}")
"""

OUTRO = """\
## Where next

* `docs/03-scene-catalog.md` — every scene, with the API it teaches and a run command.
* `docs/concepts/` — seven notes, including the DFT derivation behind the finale.
* Exercises are at the bottom of each concept note and in
  `docs/02-workshop-outline.md`.

Point the finale at your own drawing: put a dark shape on a light background into
`assets/`, then call `get_fourier_coefficients("my_drawing.png")`.
"""

# (markdown before the cell, scene name) in workshop order.
SCENE_ORDER: list[tuple[str, str]] = [
    (
        "## Make a circle\n\nA **mobject** is any mathematical object. `Create` draws it, and `rate_func` "
        "controls *how* it is drawn.",
        "HelloCircle",
    ),
    (
        "## Fill it\n\n`.animate` interpolates any property you can set. A fill needs an `opacity`.",
        "FilledCircle",
    ),
    (
        "## A square becomes a circle\n\n`Transform(a, b)` morphs `a` into `b` and leaves `a` on screen — keep "
        "animating `a` afterwards.",
        "SquareToCircle",
    ),
    (
        "## Put two shapes together\n\n`next_to` positions one mobject relative to another; `buff=0` makes them touch.",
        "CircleAndSquare",
    ),
    (
        "## Groups and rotation\n\nA `VGroup` animates several mobjects as one. `about_point` chooses the pivot.",
        "CircleAndSquareRotating",
    ),
    (
        "## Leave a trail\n\n`TracedPath` records where a point has been. Add it first so it draws behind.",
        "CircleAndSquareRotatingWithTracing",
    ),
    (
        "## An orbit\n\nThe pivot is one of the circles, so the pair revolves instead of spinning in place.",
        "CircleAndCircleRotating",
    ),
    ("## Moving\n\n`.animate.move_to` is absolute; `shift` is relative.", "CircleAndCircleMoving"),
    (
        "## Spin *and* move\n\n`add_updater` runs code every frame, so rotation and translation can overlap — "
        "and the trace compounds into a cycloid.",
        "CircleAndDotRotatingAndTracing",
    ),
    (
        "## Projects: the sine function\n\nA `ValueTracker` is an abstract time axis; `always_redraw` rebuilds the "
        "dot from it each frame.",
        "SineSnake",
    ),
    (
        "## Epicycloid\n\nTwo rotations nest here: the small wheel orbits, the pen spins.",
        "Epicycloid",
    ),
    (
        "## Lissajous figures\n\nTwo sines, one per axis. Rational ratios close the curve; irrational ones never do.",
        "LissajousFigures",
    ),
    (
        "## A rose\n\nThe polar equation `r = sin(k·θ)`, written out in Cartesian coordinates.",
        "RoseCurve",
    ),
    (
        "## Flowers: colour per petal\n\nEach petal gets its own `TracedPath`, so each stroke has its own colour. "
        "`time_period` is what makes the petals meet cleanly.",
        "FlowerWithColors",
    ),
    (
        "## Rotating flower\n\nThe traced petals are copied into one `VMobject` with no updaters "
        "attached, then rotated.",
        "RotatingFlower",
    ),
    (
        "## Gradient flower\n\n`stroke_color` accepts a *list* of colours and interpolates along the stroke.",
        "FlowerWithGradient",
    ),
]

CELL_METADATA = {"tags": ["manim-generated"]}


def cell_for_scene(scene_name: str) -> str:
    """Return ``%%manim`` cell source for the named scene, taken verbatim from disk."""
    scene = next((s for s in all_scenes() if s.name == scene_name), None)
    if scene is None:
        raise SystemExit(f"scene {scene_name!r} does not exist in {SCENES_DIR}")

    source = scene.path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    class_node = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == scene_name)
    lines = source.splitlines()
    body = "\n".join(lines[class_node.lineno - 1 : class_node.end_lineno])
    return f"%%manim -ql {scene_name}\n{body}"


def build_notebook() -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()
    cells: list[nbformat.NotebookNode] = []

    cells.append(nbformat.v4.new_markdown_cell(PREAMBLE))
    cells.append(nbformat.v4.new_code_cell(IMPORTS, metadata=dict(CELL_METADATA)))

    for markdown, scene_name in SCENE_ORDER:
        cells.append(nbformat.v4.new_markdown_cell(markdown))
        cells.append(nbformat.v4.new_code_cell(cell_for_scene(scene_name), metadata=dict(CELL_METADATA)))

    cells.append(nbformat.v4.new_markdown_cell(FOURIER_INTRO))
    cells.append(nbformat.v4.new_code_cell(FOURIER_IMPORT, metadata=dict(CELL_METADATA)))
    cells.append(nbformat.v4.new_code_cell(cell_for_scene("FourierEpicycle"), metadata=dict(CELL_METADATA)))
    cells.append(nbformat.v4.new_markdown_cell(OUTRO))

    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python (manim-workshop)",
            "language": "python",
            "name": "manim-workshop",
        },
        "language_info": {"name": "python", "file_extension": ".py", "mimetype": "text/x-python"},
    }
    # nbformat 4.5 requires a unique id per cell and would otherwise invent a
    # random uuid, making the generated file different on every run (and
    # `--check` impossible). Stable, positional ids keep the notebook a pure
    # function of the scenes.
    for index, cell in enumerate(nb["cells"]):
        cell["id"] = f"cell-{index:02d}"
    return nb


def render(nb: nbformat.NotebookNode) -> str:
    return nbformat.writes(nb, version=4) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the notebook is up to date instead of writing it",
    )
    parser.add_argument("--output", default=str(NOTEBOOK), help=f"where to write (default: {NOTEBOOK})")
    args = parser.parse_args(argv)

    target = Path(args.output)
    generated = render(build_notebook())

    if args.check:
        if not target.exists():
            print(f"MISSING: {target}", file=sys.stderr)
            return 1
        if target.read_text(encoding="utf-8") != generated:
            print(
                f"OUT OF DATE: {target}\nRegenerate with: python scripts/build_notebook.py",
                file=sys.stderr,
            )
            return 1
        print(f"up to date: {target}")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(generated, encoding="utf-8")
    nb = build_notebook()
    scenes = sum(1 for cell in nb["cells"] if cell["cell_type"] == "code" and "%%manim" in cell["source"])
    print(f"wrote {target} ({len(nb['cells'])} cells, {scenes} manim scenes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
