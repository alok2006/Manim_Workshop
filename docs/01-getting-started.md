# 01 — Getting started

From zero to a rendered video. Follow the section for your operating system,
then pick one of the three environment recipes. Everything on this page was
executed while writing it; the expected outputs are real.

> **Short on time?** Skip to the [four-command quickstart](#four-command-quickstart).

## What you need

| Requirement | Why | Notes |
|:--|:--|:--|
| **Python 3.11 – 3.14** | Manim requires ≥ 3.11; the pinned NumPy requires ≥ 3.12 | 3.13 or 3.14 recommended — both verified with this repository |
| **Cairo + Pango development headers** | `pycairo` and `ManimPango` build against them on Linux/macOS | Not needed on Windows (wheels exist) |
| **A C compiler + Python headers** | same reason, on Linux | `build-essential` / `python3-dev` |
| **~500 MB of disk** | virtual environment + render cache | videos themselves are tiny (2.5 MB for all 17) |
| **LaTeX** | *not needed* | none of the 17 scenes typeset maths — they only draw shapes |
| **ffmpeg binary** | *not needed for rendering* — Manim 0.21 encodes through the bundled PyAV library | the `ffmpeg` **binary** is only used by `scripts/make_gallery.py`, which extracts stills for the docs |

That last row surprises people, so it was tested: rendering a scene with an
*empty* `PATH` (no `ffmpeg` anywhere) still produces a valid `.mp4`.

## Four-command quickstart

Assuming Linux/macOS with `uv` available (see [step 1](#step-1-get-the-tools)):

```bash
git clone https://github.com/alok2006/Manim_Workshop.git && cd Manim_Workshop
uv venv --python 3.13 && source .venv/bin/activate
uv pip install -r requirements.txt && uv pip install -e .
manim render -ql scenes/01_basics.py HelloCircle
```

If the last command writes `media/videos/01_basics/480p15/HelloCircle.mp4`, you
are done — jump to [Where your videos go](#where-your-videos-go).

---

## Step 1: get the tools

### Linux

Manim needs to compile two small helper libraries, so install the toolchain
first. These are Manim's own documented commands:

```bash
# Debian / Ubuntu / Mint
sudo apt update
sudo apt install build-essential python3-dev libcairo2-dev libpango1.0-dev

# Fedora / RHEL
sudo dnf install python3-devel pkg-config cairo-devel pango-devel

# Arch
sudo pacman -Syu base-devel cairo pango
```

### macOS

```bash
brew install cairo pkg-config
```

If Homebrew is not installed, get it from <https://brew.sh> first — the
installer will offer to add it to your `PATH`; accept that.

### Windows

No system packages are required: `pycairo` and `ManimPango` ship as wheels.
Use PowerShell, and prefer the `uv` recipe below (it avoids the
"which Python did that install into?" problem entirely).

### Install `uv` (recommended, optional)

Manim's own documentation [strongly recommends `uv`](https://docs.manim.community/en/stable/installation/uv.html)
because it manages both Python and the virtual environment for you.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Not a fan? Every recipe below has a `venv` + `pip` equivalent, and conda works
too.

---

## Step 2: clone the repository

```bash
git clone https://github.com/alok2006/Manim_Workshop.git
cd Manim_Workshop
```

What you should see:

```
scenes/  manim_workshop/  notebooks/  assets/  docs/  scripts/  tests/  videos/
README.md  pyproject.toml  requirements.txt  requirements-lock.txt  Makefile
```

---

## Step 3: create the virtual environment

A virtual environment keeps Manim and NumPy out of your system Python. Pick
**one** of the three recipes; all of them end with the same three packages
installed (Manim, NumPy, OpenCV) plus this repository's `manim_workshop`
helper package.

### Recipe A — `uv` (fastest, recommended)

```bash
uv venv --python 3.13          # creates .venv/ and fetches Python 3.13 if needed
source .venv/bin/activate      # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
uv pip install -e .            # makes `manim_workshop` importable
```

### Recipe B — standard `venv` + `pip`

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### Recipe C — conda

```bash
conda create -n manim-workshop python=3.13 -y
conda activate manim-workshop
pip install -r requirements.txt
pip install -e .
```

> **Why the `pip install -e .` line?** `scenes/07_fourier_epicycle.py` imports
> the shared DFT helper from the `manim_workshop` package. An *editable* install
> (`-e`) registers that package with your environment while leaving the code in
> the repository, so edits take effect immediately. If you would rather not
> install anything, `export PYTHONPATH=$PWD` (Windows: `set PYTHONPATH=%CD%`)
> achieves the same thing.

### Which files do what

| File | Install it when |
|:--|:--|
| `requirements.txt` | always — pinned **direct** dependencies (Manim, NumPy, OpenCV) at the exact versions this workshop was recorded with |
| `requirements-dev.txt` | you want to run the tests, lint, or the notebook (`-r requirements.txt` + pytest, ruff, JupyterLab) |
| `requirements-lock.txt` | you need byte-for-byte reproduction of the author's machine (the full 63-package freeze, Python 3.14) |
| `pyproject.toml` | you are installing the package itself (`pip install -e .`) — it declares floors, not pins |

---

## Step 4: verify the installation

Two checks, in increasing order of thoroughness.

```bash
manim checkhealth
```

```
Checking whether your installation of Manim Community is healthy...
- Checking whether manim is on your PATH ... PASSED
- Checking whether the executable belongs to manim ... PASSED
- Checking whether latex is available ... FAILED
- Checking whether dvisvgm is available ... FAILED

No problems detected, your installation seems healthy!
```

`latex` and `dvisvgm` failing is **expected and harmless here**: it only means
you cannot render `Tex`/`MathTex` objects, and none of these scenes use them.
Manim deliberately does not count it as a problem.

Then the repository's own check, which compiles and executes every scene without
writing any video (about 20 seconds on a laptop, most of it Manim's start-up):

```bash
python scripts/check_scenes.py --dry-run
```

```
Static checks
  scene modules : 7
  scene classes : 17
  problems      : none

Running 17 scenes (dry-run), 6 at a time
  [ 1/17] ok   HelloCircle                               1.5s
  ...
  [17/17] ok   FourierEpicycle                          13.6s

dry-run summary: 17/17 passed
all checks passed
```

If you see `17/17 passed`, your environment is complete.

---

## Step 5: render your first scene

```bash
manim render -ql scenes/01_basics.py HelloCircle
```

```
Animation 0: Create(Circle):  100%|██████████| 30/30 [00:00<00:00]
INFO     Rendered HelloCircle
File ready at /…/media/videos/01_basics/480p15/HelloCircle.mp4
```

Open that file. Then try the finale:

```bash
manim render -ql scenes/07_fourier_epicycle.py FourierEpicycle
```

`-ql` means *quality: low* (854×480, 15 fps) — always develop at `-ql`. When you
are happy, re-render the same scene with `-qh` for a 1080p60 version; nothing
else changes. See the [rendering guide](04-rendering-guide.md) for the full
quality table.

---

## Step 6: run the notebook (optional)

The notebook in `notebooks/` contains the same 17 scenes as cells, in teaching
order, plus the explanations. It needs a Jupyter kernel that can see Manim:

```bash
pip install -r requirements-dev.txt          # JupyterLab + ipykernel
python -m ipykernel install --user --name manim-workshop --display-name "Python (manim-workshop)"
jupyter lab notebooks/workshop.ipynb
```

Then choose **Kernel → Change Kernel → Python (manim-workshop)**.

`%%manim -ql HelloCircle` (the cell magic) renders the cell's scene inline.
The magic is registered by `from manim import *`, so the first cell must be run
before any scene cell.

---

## Where your videos go

Manim writes to `media/videos/<stage>/<quality>/<SceneName>.mp4`:

```
media/
└── videos/
    ├── 01_basics/
    │   └── 480p15/
    │       ├── HelloCircle.mp4          ← your video
    │       └── partial_movie_files/…    ← cache: one file per animation
    └── 07_fourier_epicycle/
        └── 480p15/
            └── FourierEpicycle.mp4
```

* `media/` is git-ignored; nothing there is precious.
* The **`videos/`** directory in the repository root is the curated set of
  17 low-quality previews, tracked on purpose — see [`videos/README.md`](../videos/README.md).
* Change the output location with `--media_dir /somewhere/else`.

---

## The Makefile

If you have `make` (Linux/macOS, or Git Bash on Windows):

```bash
make            # list every target
make install    # venv + dependencies + editable package
make check      # the dry-run check above
make render     # render all 17 scenes at low quality
make videos     # …and publish them into videos/
make gallery    # refresh the stills in docs/gallery/
make test       # run the test-suite
```

---

## Updating, uninstalling, starting over

| I want to… | Do this |
|:--|:--|
| update to the latest code | `git pull` (then `pip install -r requirements.txt` if the pins changed) |
| leave the environment | `deactivate` |
| delete the environment and start again | remove `.venv/`, then redo Step 3 |
| clear Manim's render cache | `manim render --flush_cache …` for one scene, or delete `media/` |
| see what Manim is configured to do | `manim cfg show` |
| install a different Manim version | edit `requirements.txt`, then `pip install -r requirements.txt` |

---

## Next steps

* [Workshop outline](02-workshop-outline.md) — the plan, if you are teaching this.
* [Scene catalog](03-scene-catalog.md) — what every scene does and how to run it.
* [Troubleshooting](05-troubleshooting.md) — when the above does not work:
  `libcairo` errors, `ManimPango` build failures, `ModuleNotFoundError:
  manim_workshop`, the `%%manim` magic "not found", and more.
