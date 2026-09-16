# Mobjects and animations

*Demonstrated by `HelloCircle`, `FilledCircle`, `CircleAndSquare`.*

## The two-word summary

Everything in Manim is a **mobject** (a mathematical object — a circle, a
square, a group of them), and you make a video by **animating** mobjects, one
`play()` at a time.

```python
from manim import *

class HelloCircle(Scene):
    def construct(self):
        circle = Circle(radius=2)          # a mobject
        self.play(Create(circle), run_time=2)   # an animation of that mobject
```

`construct()` is the whole program. Manim calls it once, records every frame
your `play()` calls imply, and hands the frames to ffmpeg.

## Mobjects

A mobject knows three things: where its points are, how they are styled, and
what its children are.

| Idea | In practice |
|:--|:--|
| **Geometry** | `Circle`, `Square`, `Triangle`, `Line`, `Dot`, `Arc` |
| **Style** | `.set_color()`, `.set_fill(color, opacity)`, `.set_stroke(width=…)` |
| **Placement** | `.shift(direction)`, `.move_to(point)`, `.next_to(other, DOWN)`, `.scale(2)`, `.rotate(PI/4)` |
| **Structure** | `VGroup(a, b, c)` — animate many as one |

Two style rules cause most of the surprise:

1. **A fill needs an opacity.** `Circle(radius=2, fill_color=ORANGE)` draws a
   hollow circle, because `fill_opacity` defaults to `0`. You need
   `.set_fill(ORANGE, opacity=0.5)`.
2. **Strokes and fills are separate colours.** `set_color` sets the stroke; the
   fill only follows if you set it too.

## Animations

`self.play(...)` takes one or more animations and a duration:

```python
self.play(Create(circle))                       # draw it
self.play(circle.animate.set_color(GREEN))      # change a property
self.play(Transform(square, circle))            # morph shape
self.play(FadeOut(circle))                      # remove it
self.play(Create(a), Create(b), run_time=3)     # several, at the same time
```

`self.add(mob)` is different: it puts a mobject on screen *instantly*, with no
animation at all — the difference between "it was already there" and "we drew
it". `FilledCircle` uses this contrast deliberately: swap the first `play` for
an `add` and the circle simply appears.

### The `.animate` syntax

`mob.animate.<anything>` turns a *method call you could have made directly* into
an animation:

```python
self.play(circle.animate.set_color(GREEN).set_fill(ORANGE, opacity=0.5))
```

That single line is two animations chained (colour, then fill) over one
`run_time`. It works for any method that returns the mobject — including
`shift`, `rotate`, `scale`, `move_to`, `become`.

## Layout before animation

`CircleAndSquare` is a deliberate reminder: place things, *then* animate them.

```python
square.next_to(circle, DOWN, buff=0)   # touching, directly below
```

`next_to` reads as: "put me next to that object, in this direction, with this
gap." `DOWN`, `UP`, `LEFT`, `RIGHT` are just vectors (`DOWN == np.array([0,-1,0])`),
so `square.next_to(circle, 0.5*DOWN + 0.5*RIGHT)` also works.

## Pitfalls

| Symptom | Cause | Fix |
|:--|:--|:--|
| the circle is red, not what you asked for | `Circle()` is red by default and you never changed it | `Circle(color=BLUE)` or `.set_color(BLUE)` |
| the fill is invisible | `fill_opacity` defaults to `0` | `.set_fill(color, opacity=0.5)` |
| nothing appears | the mobject was never added or animated | `self.add(mob)` or `self.play(Create(mob))` |
| something appears instantly | you used `add` where you meant `play` | `self.play(FadeIn(mob))` |
| two things fight for the same spot | the layout was never set | place before animating: `next_to`, `move_to`, `arrange` |
| the animation is over in a blink | default `run_time` is 1 second | pass `run_time=…`, or `self.wait()` between plays |

## Exercises

1. Make `HelloCircle` green and give it a 10-pixel stroke.
2. Add a `Dot(color=YELLOW)` at the circle's centre in `FilledCircle`.
3. In `CircleAndSquare`, move the square to the *right* of the circle.
4. Animate the circle growing (`scale`) while the square rotates — in one `play`.
