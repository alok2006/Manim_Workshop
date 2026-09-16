# 02 — Workshop outline

The teaching plan: what to say, in what order, and how long each beat takes.
Timings assume a 90-minute session with a live audience typing along.

## Audience and prerequisites

| | |
|:--|:--|
| **Audience** | comfortable with basic Python (variables, functions, `for` loops); no Manim, no animation, no maths beyond secondary school |
| **Not required** | linear algebra, LaTeX, Git, object-oriented programming |
| **Setup done beforehand** | [01 — Getting started](01-getting-started.md) — have everyone arrive with `manim render -ql scenes/01_basics.py HelloCircle` already working |
| **Materials** | this repository, a projector, and [`videos/`](../videos/) as the fallback if someone's laptop misbehaves |

## Run of show

| Time | Beat | What happens | Scenes | Notes |
|--:|:--|:--|:--|:--|
| 0:00 | **Welcome** | play `videos/FourierEpicycle.mp4` *first*: show the destination before the journey | `FourierEpicycle` | "everything after this slide is how that works, one idea at a time" |
| 0:05 | **The two ideas** | a mobject and an animation: `Create` + `.animate` | `HelloCircle`, `FilledCircle` | type it live; let them see the `-ql` render loop |
| 0:20 | **Colour and shape** | `set_color`, `set_fill(opacity=…)`, then `Transform` | `SquareToCircle` | the "why is my circle red?" moment — see the [transforms note](concepts/03-transforms.md#gotcha-why-is-my-circle-red) |
| 0:30 | **Layout** | `next_to`, `buff`, `DOWN`/`LEFT`, draw order | `CircleAndSquare` | layout *before* animating is the habit worth installing |
| 0:40 | **Groups and rotation** | `VGroup`, `Rotate(about_point=…)` | `CircleAndSquareRotating`, `CircleAndCircleRotating`, `CircleAndCircleMoving` | ask: "what does `about_point` change?" — let them predict |
| 0:55 | **Leaving a trail** | `TracedPath`, `add_updater` | `CircleAndSquareRotatingWithTracing`, `CircleAndDotRotatingAndTracing` | the first "wow" of the session |
| 1:05 | **A time variable** | `ValueTracker` + `always_redraw` = a pen you can point anywhere | `SineSnake`, `LissajousFigures` | change `w1`/`w2` live and re-render |
| 1:20 | **Projects** | the rose curve, petals, colours, gradients | `Epicycloid`, `RoseCurve`, `FlowerWithColors`, `RotatingFlower`, `FlowerWithGradient` | let people pick one and hack on it |
| 1:30 | **The finale** | the DFT, then Doraemon | `FourierEpicycle` | [concepts/07](concepts/07-fourier-epicycles.md) has the maths in plain language |
| 1:45 | **Wrap** | "point it at your own photo" + where to go next | — | see the exercises below |

> **If you have only 45 minutes:** welcome → two ideas → transforms → groups →
> finale. Cut the parametric-curve section; it is the most self-contained block.

## The plan that started it all

The original workshop brief lives in this repository's history as `seq.md`. It
is preserved verbatim below — the `scenes/` layout was built to match its order,
and each line maps to one scene or one idea.

```text
Make circle
make rectangle
set color
fill color
introduce vgoup
tranform circle to rectangle
next_to
introduce rotation

now its time for projects

Introduce Sin function (parameters)
color the sine function

introduce flower equation
color the flower equation
color each petal with different colors(introduce segemnts and for loops)
rotate the flower (introduce groups)
add glowing effect

introduce gradient color
add glow effect and gradient effect in each point

make a circle with lots o sin wave
make doraemon

demonstrate Fourier Series
```

### From the brief to the repository

| Line in the brief | Where it landed | Note |
|:--|:--|:--|
| make circle / rectangle, set colour, fill colour | `scenes/01_basics.py` | `HelloCircle`, `FilledCircle` |
| introduce `VGroup`, transform circle to rectangle, `next_to` | `scenes/02_transforms.py`, `scenes/03_positioning.py` | the workshop transforms a *square into a circle*; the reverse is a one-line change (try it as an exercise) |
| introduce rotation | `scenes/04_groups_and_rotation.py` | plus two scenes the brief implies: tracing and translation |
| introduce sin function (parameters), colour the sine function | `scenes/05_parametric_curves.py` | `SineSnake`; the "colour" idea is handled by `stroke_color` |
| flower equation, colour each petal (segments + loops) | `scenes/06_flowers.py` | `FlowerWithColors` |
| rotate the flower (groups), add glowing effect | `scenes/06_flowers.py` | `RotatingFlower`; "glow" is a wide, saturated stroke (`stroke_width=9`) |
| introduce gradient colour | `scenes/06_flowers.py` | `FlowerWithGradient` — gradient strokes need a *list* of colours |
| make a circle with lots of sin waves | `scenes/05_parametric_curves.py` | `RoseCurve` with a larger `k`, or the [exercise below](#exercises) |
| make doraemon, demonstrate Fourier series | `scenes/07_fourier_epicycle.py` | the brief's two final items are in fact one scene |

## Instructor notes

**Show the render loop early and often.** `-ql` renders these scenes in 2–15
seconds. The workshop's real lesson is that animation iteration is fast enough
to be playful.

**Prefer prediction to explanation.** Before running
`CircleAndCircleRotating`, ask which point it will spin around. Wrong guesses
are cheap here and memorable.

**Keep the magic moments.** Three of them land reliably:

1. the trail appearing behind the spinning square (`…WithTracing`);
2. the rose drawing itself petal by petal (`FlowerWithColors`);
3. the epicycle chain suddenly becomes Doraemon (`FourierEpicycle`).

**Do not open the maths first.** In the finale, run the scene, *then* explain
that the circles' radii came from a Fourier transform, then show
[concepts/07](concepts/07-fourier-epicycles.md).

**If someone's environment breaks**, use `videos/` — every scene is there at low
quality, so nobody is blocked on a `libcairo` error while everyone else types.

## Exercises

| # | Task | Scene to start from | Hint |
|:--|:--|:--|:--|
| 1 | Make the circle blue and give it a thicker outline | `HelloCircle` | `Circle(radius=2, color=BLUE, stroke_width=8)` |
| 2 | Transform a *triangle* into a square | `SquareToCircle` | swap `Square()` for `Triangle()` |
| 3 | Change the sine wave's speed without changing its shape | `SineSnake` | only `run_time` changes |
| 4 | Make a 7-petal rose | `RoseCurve` | `k = 7` — what does `time_period` do for odd `k`? |
| 5 | Draw a "circle of sine waves" | `RoseCurve` | `r = sin(k·θ)` with large `k` is a spiky circle; try `k = 24` |
| 6 | Trace *your own* silhouette | `FourierEpicycle` | put a dark drawing on a light background into `assets/`, pass the name to `get_fourier_coefficients("yourfile.png")` |
| 7 | Make the epicycle chain start smaller and grow | `FourierEpicycle` | `get_fourier_coefficients(num_coeffs=…, num_samples=…)` |

## What to teach next

* `Text`/`MathTex` and the LaTeX requirement (this workshop deliberately avoids it).
* `Axes`/`NumberPlane` and animating functions properly (`ParametricFunction`).
* `LaggedStart`, `AnimationGroup`, `Succession` for multi-part choreography.
* Rendering a whole video: sections, voiceovers (`manim-voiceover`), `ffmpeg` post-processing.
