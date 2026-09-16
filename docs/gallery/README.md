# Gallery

One still per scene, sampled at ~80% of each video's timeline: far enough in
that the drawing is complete, early enough to avoid the final `FadeOut` in the
scenes that clear the screen.

These files are **generated** — do not hand-edit them:

```bash
python scripts/make_gallery.py      # or: make gallery
```

which reads the rendered videos from `media/` (create them first with
`make render`). The full motion is in [`../../videos/`](../../videos/).

| Still | Scene | Stage |
|:--|:--|:--|
| [`HelloCircle.png`](HelloCircle.png) | `HelloCircle` | 01 basics |
| [`FilledCircle.png`](FilledCircle.png) | `FilledCircle` | 01 basics |
| [`SquareToCircle.png`](SquareToCircle.png) | `SquareToCircle` | 02 transforms |
| [`CircleAndSquare.png`](CircleAndSquare.png) | `CircleAndSquare` | 03 positioning |
| [`CircleAndSquareRotating.png`](CircleAndSquareRotating.png) | `CircleAndSquareRotating` | 04 groups & rotation |
| [`CircleAndSquareRotatingWithTracing.png`](CircleAndSquareRotatingWithTracing.png) | `CircleAndSquareRotatingWithTracing` | 04 groups & rotation |
| [`CircleAndCircleRotating.png`](CircleAndCircleRotating.png) | `CircleAndCircleRotating` | 04 groups & rotation |
| [`CircleAndCircleMoving.png`](CircleAndCircleMoving.png) | `CircleAndCircleMoving` | 04 groups & rotation |
| [`CircleAndDotRotatingAndTracing.png`](CircleAndDotRotatingAndTracing.png) | `CircleAndDotRotatingAndTracing` | 04 groups & rotation |
| [`SineSnake.png`](SineSnake.png) | `SineSnake` | 05 parametric curves |
| [`Epicycloid.png`](Epicycloid.png) | `Epicycloid` | 05 parametric curves |
| [`LissajousFigures.png`](LissajousFigures.png) | `LissajousFigures` | 05 parametric curves |
| [`RoseCurve.png`](RoseCurve.png) | `RoseCurve` | 05 parametric curves |
| [`FlowerWithColors.png`](FlowerWithColors.png) | `FlowerWithColors` | 06 flowers |
| [`RotatingFlower.png`](RotatingFlower.png) | `RotatingFlower` | 06 flowers |
| [`FlowerWithGradient.png`](FlowerWithGradient.png) | `FlowerWithGradient` | 06 flowers |
| [`FourierEpicycle.png`](FourierEpicycle.png) | `FourierEpicycle` | 07 fourier epicycle |
