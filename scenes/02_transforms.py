"""Stage 2 — Shapes and ``Transform``.

One shape becomes another. The subtle part is *what happens to the original*:
``Transform(a, b)`` keeps ``a`` on screen and rewrites its points to look like
``b``; ``b`` itself is only ever a template.

Render::

    manim render -ql scenes/02_transforms.py SquareToCircle
"""

from manim import *


class SquareToCircle(Scene):
    """Rotate a square, colour it, then ``Transform`` it into a circle.

    Concepts: ``Square``, ``rotate``, ``Transform`` — and the classic gotcha that
    after ``Transform(square, circle)`` you must animate *``square``* (the
    on-screen mobject), not ``circle`` (the template).
    """

    def construct(self):
        circle = Circle(radius=2)
        square = Square()
        square.rotate(PI / 6)

        self.play(Create(square))
        self.play(square.animate.set_color(GREEN))
        self.play(Transform(square, circle))
        self.play(square.animate.set_fill(GREEN, opacity=0.5))
