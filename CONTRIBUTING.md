# Contributing

Thanks for helping. This repository is teaching material, so the bar for a change
is not only "does it work" but "does it still teach clearly".

## Quick start for contributors

```bash
git clone https://github.com/alok2006/Manim_Workshop.git
cd Manim_Workshop
uv venv --python 3.13 && source .venv/bin/activate
uv pip install -r requirements-dev.txt
uv pip install -e .
python scripts/check_scenes.py --dry-run   # everything should pass before you start
```

Full details, including non-`uv` recipes: [docs/01-getting-started.md](docs/01-getting-started.md).

## The three gates

Every change must pass all three, cheapest first:

```bash
python scripts/check_scenes.py            # static: names, docstrings, no dupes   (<1 s)
python scripts/check_scenes.py --dry-run  # every scene executes, writes nothing (~20 s)
pytest                                    # catalogue, docs, maths, one real render
```

Then, if your change alters what is on screen, refresh the committed artefacts:

```bash
python scripts/check_scenes.py --render --quality l --publish videos
python scripts/make_gallery.py
```

CI runs the same commands, so if they pass locally they pass there.

## The rules

| Rule | Why |
|:--|:--|
| **Nothing is deleted.** `make clean` *moves* render output to `.trash/` | renders take minutes to produce; a mistaken `rm` should never cost someone a morning |
| **Use proper file tools** for source edits — no heredoc string surgery | shell-based edits silently corrupted a tool registration in a sibling project |
| **One scene, one idea.** A scene that teaches two things teaches neither | it is the whole structure of the workshop |
| **Every scene needs a docstring** on the class *and* the module | the docs and the catalog are checked against them |
| **Scenes are loaded by path** (`manim render scenes/01_basics.py HelloCircle`) | the numbered file names are not importable identifiers; see below |
| **Keep `from manim import *`** in `scenes/` | it is Manim's own documented style, and the notes assume it |
| **Names carry meaning.** Fix a typo rather than living with it | `Sqaure` survived years because nobody wanted to touch it — the old→new table is in [docs/03](docs/03-scene-catalog.md#renamed-scenes-migration-table) |

## Adding a scene

1. Put it in the right stage file under `scenes/` (or add `NN_name.py` if it
   starts a new stage), with a module docstring and a class docstring.
2. Write it in the same style: a `ValueTracker` for anything parametric, no
   `Tex`/`MathTex` (this workshop is LaTeX-free on purpose), and a comment
   wherever a beginner would ask "why?".
3. Add it to [docs/03-scene-catalog.md](docs/03-scene-catalog.md) — including a
   `manim render …` line for it. `pytest` fails if you forget.
4. Update `EXPECTED_SCENE_COUNT` in `tests/test_scene_catalog.py`.
5. If you renamed an existing scene, add it to
   `manim_workshop.catalog.LEGACY_SCENE_NAMES` (the map is tested for
   completeness and injectivity).
6. Run the three gates, then regenerate `videos/` and `docs/gallery/`.

## Adding documentation

* Put prose in `docs/`, numbered when it belongs to the reading order.
* Link relatively (`concepts/04-groups-and-rotation.md`) — `tests/test_docs.py`
  checks that every relative link resolves.
* Prefer tables and runnable commands over adjectives.
* Every claim about Manim's behaviour should be **checked against the pinned
  version** (`manim --version`), not recalled. If you cannot check it, mark it
  as unverified in the PR description instead of asserting it.

## Why are the scenes not type-checked?

`pyrightconfig.json` excludes `scenes/`. Manim's bundled type stubs are
imprecise in ways that fire on every idiomatic scene:

| Idiom | Stub says | Reality |
|:--|:--|:--|
| `Rotate(mob, about_point=ORIGIN)` | `about_point: Sequence[float] \| None` | `ORIGIN` *is* a `Vector3D` (ndarray) and works |
| `Rotate(mob, about_point=mob.get_center())` | same | returns `Point3D`, works |
| `Dot([x, y, 0])` | `point: Point3DLike` | lists are accepted and converted |
| `TracedPath(dot.get_center, stroke_color=[a, b])` | `stroke_color: ParsableManimColor` | a list means "gradient stroke" and works |
| `VGroup().add(always_redraw(…))` | `add(vmobjects: VMobject \| Iterable[VMobject])` | `always_redraw` returns a `Mobject` *typed* as `Mobject` |

Rather than litter teaching code with `# type: ignore`, the scenes are excluded
from the *type checker* but not from the *gates*: they are parsed, executed
(`--dry_run`), rendered, and analysed for geometry by the Manim MCP server during
review. The library code in `manim_workshop/`, `scripts/` and `tests/` **is**
type-checked.

## Commit conventions

Short, imperative, and specific about *why*:

```
fix(flowers): use TracedPath(dot.get_center) not dot.get_center() in RotatingFlower
docs(catalog): document the doraemon polarity requirement
test(fourier): assert a full coefficient set reconstructs the contour exactly
```

Prefixes in use: `feat`, `fix`, `docs`, `test`, `chore`, `ci`. If a change fixes
something that could regress, name the regression in the test you add.

## Pull requests

* One topic per PR; a rename plus a rewrite in the same PR cannot be reviewed.
* Describe **how you verified**: the commands you ran and what they printed.
* If you changed a scene, include the before/after still (`-s` renders one PNG).
* Expect questions about clarity, not just correctness — that is the product.
