# Parametric curves

*Demonstrated by `SineSnake`, `Epicycloid`, `LissajousFigures`, `RoseCurve`,
`FlowerWithColors`, `RotatingFlower`, `FlowerWithGradient`.*

## The pattern

Every scene in stages 5 and 6 has the same three-part skeleton:

```python
tracker = ValueTracker(-2 * PI)                      # 1. an abstract "time"

dot = always_redraw(                                 # 2. a point that depends on it
    lambda: Dot([np.sin(tracker.get_value()),
                 np.cos(tracker.get_value()), 0])
)

tracer = TracedPath(dot.get_center, stroke_color=RED)  # 3. ink

self.add(dot, tracer)
self.play(tracker.animate.set_value(2 * PI), run_time=20)   # walk time forward
```

Change the function in step 2 and you get a different curve — that is the entire
lesson. `ValueTracker` holds a number; `always_redraw` rebuilds the point from it
every frame; `TracedPath` remembers where the point has been.

## Why `ValueTracker` rather than a loop

You could compute the curve yourself and draw it instantly, but the *drawing* is
the point. `ValueTracker` gives you:

* a single number to animate (`tracker.animate.set_value(target)`);
* any rate function you like, so you can speed up or slow down mid-draw;
* the ability to compute several quantities from the same parameter — which is
  exactly what a parametric curve is.

## A gallery of formulas

| Scene | Parameters | What the formula is |
|:--|:--|:--|
| `SineSnake` | `x = t`, `y = sin t` | the definition of a sine wave |
| `LissajousFigures` | `x = sin(3t)`, `y = sin(4t + π/3)` | two independent oscillations per axis |
| `RoseCurve` | `r = sin(5θ)`, mapped to `(r cos θ, r sin θ)` | polar curve, 5 petals |
| `Epicycloid` | nested rotation, `f1 = 3`, `f2 = 8` | one circle rolling around another |
| `FlowerWithColors` | as `RoseCurve`, one `TracedPath` per petal | segments and loops |

### Polar to Cartesian, spelled out

`RoseCurve` writes out the conversion instead of using a helper:

```python
x = scale * np.sin(k * theta) * np.cos(theta)   # r · cos θ
y = scale * np.sin(k * theta) * np.sin(theta)   # r · sin θ
```

where `r = scale * sin(k*theta)`. Given a polar equation `r = f(θ)`, the
Cartesian form is always these two lines.

### `time_period`: why the petals close

The flower scenes draw one petal per `play`:

```python
time_period = PI / k if k % 2 == 1 else 2 * PI / k
...
self.play(tracker.animate.set_value((x + 1) * time_period))
```

A rose with **odd** `k` closes after `π` radians (petals are traced twice over a
full turn); an **even** `k` needs the full `2π`. Advancing the tracker by exactly
one petal-period per iteration is what makes each traced segment land on one
petal instead of across two.

### Colours per segment

Because each iteration creates its own `TracedPath`, each petal gets its own
style — that is the trick behind `FlowerWithColors`:

```python
for x in range(k):
    petal_color = colors[x % len(colors)]
    path = TracedPath(dot.get_center, stroke_width=9, stroke_color=petal_color)
```

`FlowerWithGradient` pushes the same idea further: `stroke_color` accepts a
**list**, and Manim interpolates along the stroke:

```python
stroke_color=[colors[x % len(colors)], colors[(x + 1) % len(colors)]]
```

## Turning the drawing into an object

`RotatingFlower` ends by throwing away the machinery that drew the flower and
keeping only the geometry:

```python
flower = VGroup(*[
    VMobject(
        stroke_color=segment.stroke_color,
        stroke_width=segment.stroke_width,
    ).set_points(segment.get_points())
    for segment in segments
])
self.remove(tracker, *segments)
self.add(flower)

self.play(Rotate(flower, angle=PI/2, about_point=ORIGIN, run_time=4))
```

`get_points()`/`set_points()` copy raw geometry; the new `VMobject` has no
updaters and no tracer attached, so it can be rotated as a rigid body — which a
`TracedPath` (whose job is to follow a moving point) cannot sensibly be.

This "draw it with machinery, then freeze the result" pattern is worth
remembering whenever the animation of creation differs from the animation of the
finished object.

## Pitfalls

| Symptom | Cause | Fix |
|:--|:--|:--|
| the curve is drawn but nothing is visible | the `TracedPath` was added *after* an opaque object | `self.add(dot, tracer)` early |
| petals don't line up | wrong `time_period` for the parity of `k` | `PI/k` for odd, `2*PI/k` for even |
| the dot is frozen | `always_redraw` closes over a *value* rather than the tracker | call `tracker.get_value()` inside the lambda |
| the curve is a straight line | you changed one coordinate only | both `x` and `y` must depend on the parameter |
| the flower won't rotate | you are rotating the `TracedPath`s, not the frozen `VMobject`s | copy the points out (above) |
| `RuntimeError: dictionary changed size` | mutating a `VGroup` while iterating it | build a list first, then `VGroup(*items)` |

## Exercises

1. `SineSnake`: draw `sin(2x)` instead.
2. `LissajousFigures`: find a ratio that produces a closed curve with 5 lobes.
3. `RoseCurve`: what does `k = 6` look like, and how many petals do you get?
4. `FlowerWithColors`: make the petals alternate only two colours.
5. `Epicycloid`: set `f1 = f2`. Predict the curve, then render.
