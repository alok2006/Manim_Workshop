# 05 — Troubleshooting

Error message → what it means → what to do. The first column is the text you
actually see; search for it.

## Install-time problems

| Message | Cause | Fix |
|:--|:--|:--|
| `ModuleNotFoundError: No module named 'manim'` | the virtual environment is not active, or Manim is not installed *in it* | `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`), then `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'manim_workshop'` | the repository's helper package was not installed | `pip install -e .` — or set `PYTHONPATH=$PWD` instead |
| `ModuleNotFoundError: No module named 'cv2'` | OpenCV is missing (only the finale needs it) | `pip install -r requirements.txt`, or `pip install opencv-python` |
| `manim: command not found` / `'manim' is not recognized` | same as above — the venv is not active | activate it, or call the binary directly: `.venv/bin/manim` (Windows: `.venv\Scripts\manim.exe`) |
| `OSError: libcairo.so.2: cannot open shared object file` | Cairo is missing at the system level | `sudo apt install libcairo2-dev` (Debian/Ubuntu) |
| `OSError: libpango-1.0.so.0: cannot open shared object file` | Pango is missing | `sudo apt install libpango1.0-dev` |
| `Failed building wheel for pycairo` | no C compiler / Cairo headers | `sudo apt install build-essential python3-dev libcairo2-dev pkg-config` |
| `Failed building wheel for ManimPango` | missing Pango headers | `sudo apt install libpango1.0-dev pkg-config` (Fedora: `pango-devel`) |
| `error: Microsoft Visual C++ 14.0 or greater is required` (Windows) | no compiler for a source build | use Python 3.13/3.14 where wheels exist, or use the conda recipe — no compiler needed |
| `No matching distribution found for manim==0.21.0` | Python too old for the pinned NumPy | install Python 3.12+ (`uv python install 3.13`) and recreate the environment |
| `error: externally-managed-environment` | `pip` is trying to write into the system Python | you skipped the virtual environment — go back to [Step 3](01-getting-started.md#step-3-create-the-virtual-environment) |

## Environment-health questions

**`manim checkhealth` says `latex … FAILED` and `dvisvgm … FAILED`.**
Expected here, and harmless: none of the 17 scenes use `Tex`/`MathTex`, so no
LaTeX distribution is required. Manim itself still reports "no problems detected".

**`manim checkhealth` says `manim is not on your PATH`.**
The environment is not active in this shell. Either activate it, or run
`python -m manim checkhealth` (which works but prints a harmless
`RuntimeWarning: 'manim.__main__' found in sys.modules`).

**`ffmpeg: command not found`.**
Manim 0.21 encodes through the bundled PyAV library and does **not** need the
`ffmpeg` binary — this was verified by rendering with an empty `PATH`. Only
`scripts/make_gallery.py` shells out to `ffmpeg`/`ffprobe`; install the binary
(`sudo apt install ffmpeg`, `brew install ffmpeg`) if you want to regenerate the
documentation stills.

## Notebook problems

| Symptom | Cause | Fix |
|:--|:--|:--|
| `UsageError: Cell magic %%manim not found` | the imports cell has not been run in this kernel | run the `from manim import *` cell first — that import registers the magic |
| the kernel cannot import manim | the notebook is running on a *different* Python than your venv | `pip install ipykernel`, then `python -m ipykernel install --user --name manim-workshop --display-name "Python (manim-workshop)"`, then pick that kernel |
| the cell renders but no video appears | the magic writes files next to the notebook | look for `media/` beside the notebook, or pass `--media_dir` |

## Run-time problems

| Message | Cause | Fix |
|:--|:--|:--|
| `FileNotFoundError: Asset 'doraemon.jpg' not found. Tried: …` | running from a directory where neither `assets/` nor the file exists | run commands from the repository root, or `pip install -e .` so the package knows where the repo is |
| `ValueError: … the subject is lighter than its background` | `assets/`-style silhouette with inverted polarity | use a dark drawing on a light background, or invert your image first — the [catalog](03-scene-catalog.md#fourierepicycle) explains why this is an error rather than a wrong picture |
| `ValueError: No contour found …; is the background uniform?` | the image has no dark region to trace | check the image; a pure white canvas has no contour |
| `FileNotFoundError: OpenCV could not read an image at …` | the path exists but is not a readable image (wrong extension, corrupt file) | re-export the image as PNG/JPG |
| `NameError: name 'rate_functions' is not defined` | *not* a real Manim error — but some third-party Manim linters report it. `from manim import *` does export `rate_functions` | ignore, or import it explicitly: `from manim import rate_functions` |
| the render hangs with no output | a very long scene, or a stuck wait | press `Ctrl-C`, render with `-n 0,3` to find the slow animation |
| the video is missing but the render "worked" | it went to a different `--media_dir` | read the `File ready at …` line from the terminal |
| changes do not appear in the output | you rendered the same scene at a different quality, or the cache is stale | check the path; then `--flush_cache` |

## Performance

**Rendering feels slow.**
Use `-ql` (see the quality table in the [rendering guide](04-rendering-guide.md)).
`FourierEpicycle` is inherently the heaviest scene: it rebuilds 123 mobjects per
frame. Reduce `num_coeffs` while iterating:

```python
coeffs = get_fourier_coefficients(num_coeffs=16)   # instead of 60
```

**The repository checker takes a while.**
`--dry-run` starts a Manim process per scene (~1.5 s of interpreter startup
each). Run it with `--jobs 6` and restrict with `--only` when you are iterating.

## When to ask for help

If something fails here that this page does not cover, [open an issue](../../issues)
with:

1. the exact command you ran,
2. the complete error output,
3. the result of `manim --version`, `python --version`, and `python -c "import manim_workshop; print(manim_workshop.__version__)"`,
4. your operating system.
