"""Stage 3 — Positioning with ``next_to``.

Before animating anything, get the *layout* right. ``next_to`` is the workhorse:
it places a mobject relative to another, and ``buff`` controls the gap
(``buff=0`` makes them touch).

Render::

    manim render -ql scenes/03_positioning.py CircleAndSquare
"""

from manim import *


class CircleAndSquare(Scene):
    """Place a square directly below a circle, then fill the circle.

    Concepts: ``next_to(mob, direction, buff=...)``, ``DOWN``, draw order
    (``Create`` order decides what is on top).
    """

    def construct(self):
        circle = Circle(radius=1)
        square = Square()
        square.rotate(PI / 4)
        square.next_to(circle, DOWN, buff=0)

        self.play(Create(square))
        self.play(Create(circle))
        self.play(circle.animate.set_fill(GREEN, opacity=0.5))
