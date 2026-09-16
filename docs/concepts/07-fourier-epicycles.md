# Fourier epicycles

*Demonstrated by `FourierEpicycle`.* **The finale.** It is worth reading this
even if you skip every other note: the idea is genuinely surprising the first
time.

> Reference: [3Blue1Brown — *But what is a Fourier series? From heat flow to
> drawing with circles*](https://www.youtube.com/watch?v=r6sGWTCMz2k) (the video
> this scene is a homage to; there is also a [written version](https://www.3blue1brown.com/lessons/fourier-series/)).
> Grant uses 101 rotating vectors there; this workshop gets a recognisable
> Doraemon out of **61**.

## The claim

Take any closed curve — a signature, a coastline, Doraemon's silhouette. It can
be drawn, to any accuracy you like, by a chain of circles rotating at constant
speeds, each mounted on the rim of the previous one. The pen is at the tip of the
last link.

The chain's ingredients are: for each integer frequency `n`, a **radius** and a
**starting angle**. Those come from the Fourier transform of the curve.

## Step 1 — turn the picture into a list of points

```python
contour = longest_contour(doraemon.jpg)      # OpenCV: threshold + findContours
x, y = contour[:, 0], -contour[:, 1]         # flip y: image rows grow downward
x, y = centre_and_scale(x, y)                # origin in the middle, fits the frame
```

Then resample evenly *along the arc length* (not by index — image contours have
many more points on curves than on straight edges), and treat each point as a
complex number:

```python
z = x_sampled + 1j * y_sampled
```

That is the `manim_workshop.fourier.sample_contour` function. Its output is "the
drawing as a function of time": `z(t)`, closed because you return to the start.

## Step 2 — the discrete Fourier transform

```python
c_n = np.sum(z * np.exp(-1j * 2 * np.pi * n * k / N)) / N   # n = -30 … 30
```

Read that as: *multiply the drawing by `e^{-2πi·n·t}` (which spins the `n`-th
component backwards until it is standing still), then average*. Everything that
was rotating averages to zero; the one component that is now frozen survives.
That average **is** the coefficient.

The corresponding reconstruction is the sum:

```python
z(t) ≈ Σ_n  c_n · e^{+2πi·n·t}
```

Each term is a point moving on a circle of radius `|c_n|`, rotating `n` times per
unit `t`, starting at angle `arg(c_n)`. Add them tip to tail and you get a chain
of circles — the epicycles.

`manim_workshop/fourier.py` stores each term as a small dict:

```python
{"freq": int(n), "radius": float(abs(c_n)), "phase": float(np.angle(c_n))}
```

## Step 3 — draw the chain

The scene's inner function is the reconstruction, line by line:

```python
current_center = np.array([0, 0, 0])
for coeff in coeffs:
    angle = coeff["freq"] * tracker.get_value() + coeff["phase"]
    next_center = np.array([
        coeff["radius"] * np.cos(angle),
        coeff["radius"] * np.sin(angle),
        0,
    ]) + current_center                       # tip-to-tail addition
    group.add(Circle(radius=coeff["radius"]).move_to(current_center))
    group.add(Line(current_center, next_center))
    current_center = next_center              # the pen moves to the new tip
```

`always_redraw` rebuilds that group every frame; `TracedPath` records where
`current_center` has been. That traced path **is** the drawing.

## Step 4 — why 61 circles are enough

The coefficients are sorted by radius, biggest first, so the coarse shape lands
before the detail. For `assets/doraemon.jpg` they decay fast:

| Rank | Frequency `n` | Radius `|c_n|` | Contributes |
|--:|--:|--:|:--|
| 1 | 1 | 2.0174 | the head-and-body blob |
| 2 | −1 | 0.6849 | the offset that makes it egg-shaped rather than round |
| 3 | 3 | 0.6003 | the ears |
| 4 | −2 | 0.5112 | the arms |
| 5 | −6 | 0.3070 | the feet |
| 6 | 6 | 0.2971 | the other side of the feet |
| … | | | |
| 61 | 27 | 0.0010 | sub-pixel wobble you cannot see |

The first coefficient is `n = 1` and its radius is ~2.0, close to the largest
extent of the shape (the frame fit puts the widest axis at 3.0) — a nice sanity
check that the transform is oriented correctly. The phase of that dominant term
is ≈ 1.5775 ≈ π/2, i.e. the outline starts near the top of the drawing.

Two knobs matter:

| Parameter | Effect |
|:--|:--|
| `num_samples` (default 300) | how finely the outline is sampled — too low and corners round off |
| `num_coeffs` (default 60) | how many frequencies to keep — 60 gives `n = −30 … 30`, i.e. 61 circles |

Higher `num_coeffs` → sharper corners and a slower render. Try 200; the render
time roughly doubles.

## Sanity check you can run

A perfect circle has **exactly one** non-zero Fourier coefficient — `|c_1|`
equals the radius, and everything else is zero. The repository asserts this with
a drawn circle (and checks `|c_1|` lands at 3.0 after the frame fit):

```bash
pytest tests/test_fourier.py -v
```

There is also a round-trip test that reconstructs a synthetic contour from a
*complete* coefficient set to `1e-9` — that is what pins down the sign convention
in the exponent. (Get the sign wrong and the pen walks the outline backwards;
get the normalisation wrong and the picture shrinks.)

## The practical gotcha

The extractor expects a **dark subject on a light background**, because
`cv2.threshold(..., THRESH_BINARY_INV)` makes a light background white — so with
an inverted image, the largest "contour" is the picture frame, and you get a
plausible-looking animation of a *rectangle*. This was discovered by testing and
is now an error message rather than a wrong drawing:

```
ValueError: The only contour found in … is the image border, which means the
subject is lighter than its background. …
```

## Try it on your own drawing

1. Draw something solid black on white (or photograph a dark object on a plain
   light surface), save as PNG.
2. Put it in `assets/`.
3. Render:

```python
coeffs = get_fourier_coefficients("assets/my_silhouette.png", num_coeffs=120)
```

Two things make a drawing work well: a **single closed outline** (holes are
ignored — only the outer contour is traced) and a **smooth boundary** (fewer
coefficients are needed for a smooth shape than for a jagged one).

## Exercises

1. Set `num_coeffs=4` and render. Which features survive?
2. Set `num_coeffs=200`. Is the extra detail worth the render time?
3. Comment out the `Circle(...)` line in `get_outline()`. What remains recognisable?
4. Reverse the sort (`reverse=False`). What does the pen draw first, and why
   does the final picture look the same?
5. Run the scene with `num_samples=30`. What breaks, and why?

## Where to go next

* Complex Fourier series in the continuous limit (the [3Blue1Brown
  lesson](https://www.3blue1brown.com/lessons/fourier-series/) derivation).
* `numpy.fft.fft` — the same numbers, computed in `O(N log N)` instead of `O(N²)`.
* SVG path input, which is what 3Blue1Brown uses: exact curves instead of
  thresholded pixels.
