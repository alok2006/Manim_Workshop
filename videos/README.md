# Rendered previews

Seventeen videos — one per scene — rendered at **low quality** (854×480, 15 fps,
180 seconds of animation in total) so that anyone can *watch* the workshop
without installing anything, and so a change in behaviour is visible as a
change in these files.

| | |
|:--|:--|
| Scenes | 17 videos, 2.5 MB |
| Quality | `-ql` → 854×480 @ 15 fps |
| Encoder | ffmpeg, driven by Manim CE 0.21.0 |
| Companion stills | [`../docs/gallery/`](../docs/gallery/) — one frame per scene |

This is deliberately *not* the full-quality output: high-quality renders are
large and platform-specific, and belong in a release rather than in git history.

## Regenerate

```bash
python scripts/check_scenes.py --render --quality l --publish videos
```

or simply:

```bash
make videos
```

The command renders every scene, checks that each one succeeded, and only then
copies the videos in — so a broken scene can never publish a stale file over a
good one. For slides, render what you need at a higher quality instead (nothing
in this repository consumes `videos/`):

```bash
manim render -qh scenes/07_fourier_epicycle.py FourierEpicycle
```

## What each file shows

| Video | Scene | In one line | Length | Size |
|:--|:--|:--|--:|--:|
| [`HelloCircle.mp4`](../videos/HelloCircle.mp4) | `HelloCircle` | a circle drawn with an eased rate function | 2 s | 11 KB |
| [`FilledCircle.mp4`](../videos/FilledCircle.mp4) | `FilledCircle` | recolour, then give the circle a translucent fill | 3 s | 25 KB |
| [`SquareToCircle.mp4`](../videos/SquareToCircle.mp4) | `SquareToCircle` | a rotated square morphs into a circle | 4 s | 40 KB |
| [`CircleAndSquare.mp4`](../videos/CircleAndSquare.mp4) | `CircleAndSquare` | `next_to` puts a square directly below a circle | 3 s | 22 KB |
| [`CircleAndSquareRotating.mp4`](../videos/CircleAndSquareRotating.mp4) | `CircleAndSquareRotating` | a group spun around the origin | 8 s | 94 KB |
| [`CircleAndSquareRotatingWithTracing.mp4`](../videos/CircleAndSquareRotatingWithTracing.mp4) | `CircleAndSquareRotatingWithTracing` | the same spin leaves a circular trail | 9 s | 114 KB |
| [`CircleAndCircleRotating.mp4`](../videos/CircleAndCircleRotating.mp4) | `CircleAndCircleRotating` | two circles orbiting their neighbour's centre | 9 s | 44 KB |
| [`CircleAndCircleMoving.mp4`](../videos/CircleAndCircleMoving.mp4) | `CircleAndCircleMoving` | the same pair travelling across the frame | 5 s | 29 KB |
| [`CircleAndDotRotatingAndTracing.mp4`](../videos/CircleAndDotRotatingAndTracing.mp4) | `CircleAndDotRotatingAndTracing` | a spinning pen that also translates — a cycloid | 8 s | 53 KB |
| [`SineSnake.mp4`](../videos/SineSnake.mp4) | `SineSnake` | one period of a sine wave, with a fading tail | 15 s | 49 KB |
| [`Epicycloid.mp4`](../videos/Epicycloid.mp4) | `Epicycloid` | a circle orbiting a circle — spirograph | 17 s | 246 KB |
| [`LissajousFigures.mp4`](../videos/LissajousFigures.mp4) | `LissajousFigures` | two out-of-phase sine waves, one per axis | 20 s | 79 KB |
| [`RoseCurve.mp4`](../videos/RoseCurve.mp4) | `RoseCurve` | polar `r = sin(5θ)` in Cartesian coordinates | 20 s | 99 KB |
| [`FlowerWithColors.mp4`](../videos/FlowerWithColors.mp4) | `FlowerWithColors` | a rose drawn petal by petal in five colours | 5 s | 45 KB |
| [`RotatingFlower.mp4`](../videos/RotatingFlower.mp4) | `RotatingFlower` | twelve traced petals, rebuilt as one object, then rotated | 16 s | 661 KB |
| [`FlowerWithGradient.mp4`](../videos/FlowerWithGradient.mp4) | `FlowerWithGradient` | the same flower with gradient strokes | 16 s | 660 KB |
| [`FourierEpicycle.mp4`](../videos/FourierEpicycle.mp4) | `FourierEpicycle` | Doraemon's outline drawn by 61 rotating circles | 20 s | 225 KB |

> The two flower videos are the largest because they draw twelve long
> `TracedPath` strokes and keep every point on screen — that is the price of the
> effect, not an encoding problem.
