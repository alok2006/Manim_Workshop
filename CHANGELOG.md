# Changelog

All notable changes to this workshop are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the helper
package `manim_workshop`.

## [1.1.0] — first organised release

The workshop content is the same 17 scenes; everything around them changed.

### Added

* `scenes/` — the 17 scenes extracted from the notebook into seven staged
  modules, each with a module docstring and a class docstring.
* `manim_workshop/` — the shared Python package:
  * `fourier.py`: contour extraction and the DFT behind `FourierEpicycle`,
    with a `TypedDict` result and a path-resolving default asset;
  * `catalog.py`: AST-based scene discovery (never imports a scene) and the
    old→new name map;
  * `runner.py`: portable `manim render` invocation plus rendered-video lookup;
  * `paths.py`: single source of truth for repository paths and `resolve_asset()`.
* `scripts/check_scenes.py` — the three-level verifier (static / `--dry-run` /
  `--render`), with parallelism, per-scene timeouts, JSON reports and
  `--publish` to refresh `videos/`.
* `scripts/make_gallery.py` — regenerates the documentation stills with ffmpeg.
* `scripts/build_notebook.py` — generates `notebooks/workshop.ipynb` *from*
  `scenes/`, so the notebook cannot drift from the code (`--check` mode fails CI
  if it is stale).
* `tests/` — 95 tests: catalogue invariants, documentation↔code consistency,
  relative-link checking, notebook↔scene cell equality, the DFT mathematics, one
  real end-to-end render, and a full notebook execution in a Jupyter kernel.
* `docs/` — a full knowledge base: getting started (per-OS install), workshop
  outline with instructor notes, scene catalog, rendering guide,
  troubleshooting, and seven annotated concept notes.
* `videos/` — 17 low-quality previews (2.5 MB) so the workshop can be watched
  without installing anything.
* `docs/gallery/` — one still per scene, generated from real renders.
* Project plumbing: `pyproject.toml`, `requirements.txt` (pinned direct
  dependencies), `requirements-dev.txt`, `Makefile`, `.gitignore`,
  `.editorconfig`, `pyrightconfig.json`.
* CI (`.github/workflows/ci.yml`): static checks, `--dry-run` of all 17 scenes,
  the test-suite (including one real render), and a documentation-consistency
  job on Python 3.13 and 3.14.

### Changed

* Scene class names normalised (17 renames, e.g. `aCircle` → `HelloCircle`,
  `MyFourierEpicyle` → `FourierEpicycle`, `CircleAndSqaureRotating` →
  `CircleAndSquareRotating`). The mapping is in
  `manim_workshop.catalog.LEGACY_SCENE_NAMES` and documented as a table in
  [docs/03](docs/03-scene-catalog.md#renamed-scenes-migration-table).
* `requirements.txt` is now three pinned direct dependencies instead of a
  63-package `pip freeze`; the original freeze is preserved verbatim as
  `requirements-lock.txt`.
* `Notebook.ipynb` → `notebooks/workshop.ipynb`, with the same 17 scenes, the
  new names, and the DFT helper imported from the package rather than redefined
  inline.
* `doraemon.jpg` → `assets/doraemon.jpg`; the DFT helper resolves the path, so
  scenes and notebook work from any directory.
* `seq.md` → `docs/02-workshop-outline.md`, expanded into a teaching plan with
  the original brief preserved verbatim as an appendix.
* `FourierEpicycle` uses `get_fourier_coefficients()` (the bundled asset) and
  the helper's guard rails instead of a hard-coded file name.

### Fixed

* An inverted silhouette (light subject on dark background) used to be traced as
  the **image border** — a plausible-looking wrong animation. It now raises an
  error that names the cause.
* A missing or unreadable image produced a confusing numpy error; it now raises
  `FileNotFoundError` naming the path.
* `Epicycloid`'s declared `f1`/`f2` parameters are now actually wired to the
  updaters (they were hard-coded duplicates before; the visual result is
  unchanged).
* Documented that `rate_functions` *is* exported by `from manim import *`, after
  a third-party linter reported it as undefined.

### Verification

* All 17 scenes: `--dry-run` clean (17.1 s wall-clock), real `-ql` render clean
  (17.9 s wall-clock, 6 workers).
* Every scene analysed for geometry defects with the Manim MCP server: clean
  (the two flagged overlaps are the intended pen-inside-the-drawn-shape
  layering).
* The pinned requirements install and render on both Python 3.13 and 3.14.
* Rendering verified to work with an empty `PATH` (no system ffmpeg required).

## [1.0.0] — original workshop

* `Notebook.ipynb` (24 cells, 17 scenes), `doraemon.jpg`, `requirements.txt`,
  `seq.md` — the material as taught.
