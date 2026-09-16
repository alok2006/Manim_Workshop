# Updaters and tracing

*Demonstrated by `CircleAndDotRotatingAndTracing`, `CircleAndSquareRotatingWithTracing`,
`SineSnake`, `LissajousFigures`, `Epicycloid`.*

Two tools that make motion feel alive rather than scripted:

* **updaters** — code that runs on every frame, so motion can compound;
* **`TracedPath`** — a mobject that records where another mobject has been.

## Updaters

`mob.add_updater(fn)` registers `fn(mob, dt)` to be called once per frame, with
`dt` the time since the previous frame. That is the whole idea — and it is the
reason a spin can continue while the object also travels:

```python
group.add_updater(lambda mob, dt: mob.rotate(3 * dt))   # 3 radians per second
self.play(group.animate.shift(RIGHT * 10), run_time=7)  # …while moving right
```

Both happen at once: the `.animate` owns the translation, the updater owns the
rotation, and neither fights the other.

The same mechanism in the epicycloid, where *two* updaters compound:

```python
wheel.add_updater(lambda mob, dt: mob.rotate(f1*dt, about_point=c1.get_center()))
dot.add_updater(lambda mob, dt: mob.rotate(f2*dt, about_point=c2.get_center()))
```

**Updaters never stop on their own.** Stop them explicitly:

```python
wheel.clear_updaters()
dot.clear_updaters()
```

Forgetting is the most common cause of "why is it still moving during the next
beat?" — and a real cost, since every live updater runs on every frame.

### The related helper: `always_redraw`

`always_redraw(fn)` is an updater in disguise: it replaces a mobject with a fresh
one built by `fn()` every frame. Use it when the *geometry* depends on state and
rebuilding is cheaper to write than updating:

```python
dot = always_redraw(lambda: Dot([t.get_value(), np.sin(t.get_value()), 0]))
```

It is the standard partner of `ValueTracker` — see
[parametric curves](06-parametric-curves.md).

## `TracedPath`: the ink

`TracedPath(point_fn)` records the positions `point_fn()` takes over time and
draws them as a polyline:

```python
path = TracedPath(square.get_center, stroke_color=BLUE, stroke_width=2)
self.add(path)
self.play(Rotate(group, angle=2*PI, about_point=ORIGIN, run_time=5))
```

Three details worth knowing:

| Parameter | Effect |
|:--|:--|
| `dissipating_time=1.5` | older points fade out — the comet-tail effect (`SineSnake`) |
| `dissipating_time=None` | keep everything (default: keep everything) |
| `stroke_color` / `stroke_width` | it is a `VMobject`, so it styles like one |

Pass a **callable**, not a value: `TracedPath(dot.get_center)` (not
`dot.get_center()`), so the path can ask "where are you *now*?" on each frame.

**Add the trace before you animate.** Mobjects are drawn in the order they were
added, so `self.add(trace)` early puts the ink behind the moving objects — which
is what you want visually.

## Choosing between them

| You want | Reach for |
|:--|:--|
| a point to leave a mark | `TracedPath` |
| motion whose rate changes over time | `add_updater` |
| geometry recomputed from a number | `always_redraw` + `ValueTracker` |
| a title to follow a moving object | `add_updater` (`mob.next_to(target, UP)`) |

## Pitfalls

| Symptom | Cause | Fix |
|:--|:--|:--|
| an object keeps moving after its beat | updater never cleared | `clear_updaters()` |
| the trail disappears | it is drawn *behind* an opaque shape | add it last, or use a fill-free shape |
| the trail is a straight line | you traced two points early and the object jumped | trace from the start of the motion |
| `TypeError: … is not callable` | passed `dot.get_center()` instead of `dot.get_center` | drop the parentheses |
| everything slows to a crawl | dozens of live `always_redraw` mobjects | raise `num_coeffs`/`k` values last, or cache geometry |
| rotation *and* movement cancel out | two updaters touching the same property | give each updater one job |

## Exercises

1. In `CircleAndDotRotatingAndTracing`, change `3 * dt` to `0.5 * dt`. Predict the
   shape of the trace before rendering.
2. Add a `Dissipating` trail to `CircleAndCircleMoving`.
3. Give `SineSnake` a second dot tracing `-sin(x)` and watch both.
4. Make a label follow the pen in `Epicycloid` (`next_to` inside an updater).
