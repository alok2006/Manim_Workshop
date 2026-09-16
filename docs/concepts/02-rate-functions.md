# Rate functions and pacing

*Demonstrated by `HelloCircle` (`rate_functions.ease_in_out_circ`), `Epicycloid`
(`run_time=0.25`), `SineSnake` (`run_time=15`).*

## What a rate function is

An animation is a function from *time* to *state*. The rate function decides how
the state gets there: it maps the animation's progress `t ∈ [0, 1]` to a
"completion" value, usually also in `[0, 1]`.

```python
self.play(Create(circle), run_time=2, rate_func=rate_functions.ease_in_out_circ)
```

Manim's default is `smooth` (a slow start, fast middle, slow end). Swapping the
rate function changes the *feel* of an animation without touching its geometry
or its duration — which is exactly why it is the cheapest quality upgrade
available to you.

## The ones worth knowing

| Rate function | Shape | Use it for |
|:--|:--|:--|
| `smooth` (default) | slow–fast–slow | almost everything |
| `linear` | constant speed | mechanical motion, rotations that must not "breathe" |
| `there_and_back` | out and back | pulses, a nudge |
| `rush_into` / `rush_from` | fast start / fast end | arrivals, departures |
| `ease_in_out_circ` | gently accelerating, sharply decelerating | **drawing** a shape — the first scene's choice |
| `ease_in_out_sine` | a softer version of the above | text, subtle motion |
| `exponential_decay` | fast then asymptotic | decay, settling |
| `running_start` | slow start, overshoot feel | comedic timing |

`rate_functions` is a module, not a single function — call it as
`rate_functions.<name>`. To see the full list in your own environment:

```python
from manim import rate_functions
print([n for n in dir(rate_functions) if not n.startswith("_")])
```

## Duration is the other half

```python
self.play(Create(dot), run_time=0.25)     # a beat
self.play(tracker.animate.set_value(2*PI), run_time=20)   # a slow drawing
```

`run_time` is in seconds and defaults to `1`. Two habits:

* **Pacing is not decoration.** `SineSnake` and the rose scenes are the *same*
  geometry at `run_time=15` and `run_time=20`; the curve is identical, the
  experience is not. A drawing that takes as long as it takes to understand is a
  drawing that teaches.
* **Iterate fast, then slow down.** While developing, set `run_time=2`; at the
  end, put the real value back. Twenty seconds of rendering is twenty seconds you
  paid for a timing decision you had not made yet.

## How they interact

| | `run_time` small | `run_time` large |
|:--|:--|:--|
| `linear` | mechanical, abrupt | hypnotic, metronomic |
| `smooth` | snappy, businesslike | calm, deliberate |
| `ease_in_out_circ` | a quick flourish | a "drawn by hand" feel |

The first scene in the workshop uses `ease_in_out_circ` on purpose: the drawing
speeds up in the middle and lands softly, the way a pen does.

## Duration arithmetic

A scene's length is the sum of its plays and waits — useful when you are
budgeting a video:

```python
self.play(Create(a), run_time=2)   # 2 s
self.play(Rotate(a, PI), run_time=5)  # 5 s
self.wait(1)                        # 1 s
```

Total: 8 seconds — which is exactly the length of `CircleAndSquareRotating`
(`2 + 1 + 5`), and why the videos in `videos/` have the lengths they do.

## Pitfalls

| Symptom | Cause | Fix |
|:--|:--|:--|
| animation feels robotic | `linear` used for something human | try `smooth` or `ease_in_out_sine` |
| the scene drags | too many `run_time=1` plays back to back | combine plays, or raise `run_time` on the interesting one |
| a rotation visibly stutters | default `smooth` on a full turn | `rate_func=linear` for constant spin |
| `run_time=0` | Manim treats it as invalid/near-instant | use `self.add()` if you want no animation |

## Exercises

1. Render `HelloCircle` three times: default, `linear`, `ease_in_out_circ`.
   Describe each in one word.
2. Make `CircleAndSquareRotating` spin at constant speed.
3. Shorten `SineSnake` to 5 seconds. Does it still teach the idea?
