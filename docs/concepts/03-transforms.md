# Transformations

*Demonstrated by `SquareToCircle`.*

## What `Transform` actually does

`Transform(a, b)` animates **`a`** until its points coincide with **`b`**'s. After
the animation, `a` is still the mobject on screen — it has simply been rewritten
to look like `b`. `b` was a template and is never added to the scene.

```python
circle = Circle(radius=2)
square = Square()
square.rotate(PI / 6)

self.play(Create(square))
self.play(Transform(square, circle))     # square becomes circle-shaped
self.play(square.animate.set_fill(GREEN, opacity=0.5))   # keep animating `square`
```

That last line is the classic beginner trap: after `Transform(square, circle)`,
`circle` is *still not in the scene*. Animating it does nothing visible.

## The transform family

| Animation | Keeps | Use it when |
|:--|:--|:--|
| `Transform(a, b)` | `a` (morphs into `b`) | you want a continuing object |
| `ReplacementTransform(a, b)` | `b` (`a` is removed) | you want to swap objects, e.g. to keep animating `b` afterwards |
| `TransformFromCopy(a, b)` | both | a copy of `a` becomes `b`; good for "this becomes that, and the original stays" |
| `FadeTransform(a, b)` | both, cross-faded | unrelated shapes; avoids the "how do the points pair up?" question |
| `FadeTransformPieces(a, b)` | many small cross-fades | similar but chunkier |

`Transform` pairs points, so it can produce strange paths when the two shapes
have very different point counts. `FadeTransform` sidesteps this.

## Gotcha: why is my circle red?

Run `SquareToCircle` and watch the colours carefully:

1. `Square()` starts **white** (verified: `Square().get_stroke_color()` is
   `#FFFFFF`).
2. `square.animate.set_color(GREEN)` makes it green.
3. `Transform(square, circle)` makes the *square* take on the *circle's* style —
   and `Circle()` defaults to **red** (`#FC6255`, verified on Manim CE 0.21.0).
4. So the morph lands on a red circle, no matter that we painted the square
   green first.

The lesson is not "Manim is weird" — it is **be explicit about style**:

```python
circle = Circle(radius=2, color=GREEN)     # now the transform lands green
```

Working out *why* a colour survived a morph is the fastest way to internalise
that `Transform` copies style as well as shape.

## Chaining transforms

Transformations compose. A common pattern is a sequence of states of the same
object:

```python
self.play(Transform(square, circle))
self.play(Transform(square, triangle))
self.play(Transform(square, star))
```

…or the `Succession`/`AnimationGroup` composition classes if you want them in one
call with different timings.

## Pitfalls

| Symptom | Cause | Fix |
|:--|:--|:--|
| the object I transformed "disappeared" | you animated the *target*, not the source | keep animating the source mobject |
| the morph looks like it went through a blender | point pairing between very different shapes | `FadeTransform` |
| the target appears twice | you also `add`ed the target | don't add targets |
| style changed unexpectedly | transforms copy style (see above) | set `color=`/`fill_color=` on the target explicitly |
| a transform of a `VGroup` loses submobject styles | submobjects are paired by index | keep the two groups structurally similar |

## Exercises

1. Transform a `Triangle()` into a `Square()`.
2. Do the reverse of the workshop's scene: circle → square.
3. Make the morph land **green** without editing the `set_color` line.
4. Use `ReplacementTransform` and then animate the *circle* afterwards — this is
   the version most people actually want.
