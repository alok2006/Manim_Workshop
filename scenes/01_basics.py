"""Stage 1 — First contact.

The whole point of this stage is that two ideas carry you a long way:

1. ``Create(mobject)`` draws something onto the screen.
2. ``mobject.animate`` interpolates *any* property you can set on a mobject.

Nothing here needs a timeline, a tracker or a group. If you can write these two
scenes from memory, you are ready for stage 2.

Render either scene with::

    manim render -ql scenes/01_basics.py HelloCircle
    manim render -ql scenes/01_basics.py FilledCircle
"""

from manim import *


class HelloCircle(Scene):
    """Draw a circle — slowly, with a deliberately pleasing rate function.

    Concepts: ``Circle``, ``Create``, ``run_time``, ``rate_func``.
    """

    def construct(self):
        circle = Circle(radius=2)
        self.play(
            Create(circle),
            run_time=2,
            rate_func=rate_functions.ease_in_out_circ,
        )


class FilledCircle(Scene):
    """Recolour an existing circle, then give it a translucent fill.

    Concepts: ``.animate``, ``set_color``, ``set_fill`` (note that a fill needs
    an explicit ``opacity`` or it stays invisible).

    ``self.add(circle)`` would drop the circle on screen instantly instead of
    animating it in — swap the first ``play`` for an ``add`` to see the
    difference.
    """

    def construct(self):
        circle = Circle(radius=2)
        self.play(
            Create(circle),
            run_time=2,
            rate_func=rate_functions.ease_in_out_circ,
        )
        self.play(circle.animate.set_color(GREEN).set_fill(ORANGE, opacity=0.5))
