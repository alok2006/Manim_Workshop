"""Stage 4 — Groups, rotation, motion and tracing.

This is where the workshop gets interesting: a ``VGroup`` lets you animate
several mobjects as one, ``Rotate`` needs an *anchor* (``about_point``), and
``TracedPath`` turns a moving point into a drawn curve.

Render one, some, or all::

    manim render -ql scenes/04_groups_and_rotation.py CircleAndSquareRotating
    manim render -ql -a scenes/04_groups_and_rotation.py
"""

from manim import *


class CircleAndSquareRotating(Scene):
    """Group a circle and a square, then spin the group around the origin.

    Concepts: ``VGroup``, ``Rotate(..., about_point=ORIGIN, axis=OUT)``.
    """

    def construct(self):
        circle = Circle(radius=1)
        square = Square()
        square.rotate(PI / 4)
        square.next_to(circle, DOWN, buff=0)

        group = VGroup(circle, square)

        self.play(Create(group), run_time=2)
        self.play(circle.animate.set_fill(GREEN, opacity=0.5))
        self.play(Rotate(group, angle=2 * PI, about_point=ORIGIN, axis=OUT, run_time=5))


class CircleAndSquareRotatingWithTracing(Scene):
    """The same spin, but the square's centre leaves a trail behind it.

    Concepts: ``TracedPath(mob.get_center, stroke_color=..., stroke_width=...)``
    — add the path *before* the motion so it is behind everything else.
    """

    def construct(self):
        circle = Circle(radius=1)
        square = Square()
        square.rotate(PI / 4)
        square.next_to(circle, DOWN, buff=0)

        group = VGroup(circle, square)

        path = TracedPath(square.get_center, stroke_color=BLUE, stroke_width=2)
        self.add(path)

        self.play(Create(group), run_time=2)
        self.play(circle.animate.set_fill(GREEN, opacity=0.5))
        self.play(Rotate(group, angle=2 * PI, about_point=ORIGIN, axis=OUT, run_time=5))

        self.play(FadeOut(square))


class CircleAndCircleRotating(Scene):
    """Two touching circles: rotate the pair around the *right* circle's centre.

    The pair is shifted left first, which makes the anchor obvious on screen —
    ``about_point`` is what turns "a rotation" into "an orbit".
    """

    def construct(self):
        c1 = Circle(radius=0.5)
        c1.set_fill(GREEN, opacity=0.6)
        c2 = Circle(radius=0.7)
        c2.set_fill(YELLOW, opacity=0.6)
        c1.next_to(c2, LEFT)

        group = VGroup(c1, c2)
        group.shift(5 * LEFT)

        self.play(Create(group), run_time=2)
        self.play(
            Rotate(
                group, angle=2 * PI, about_point=c2.get_center(), axis=OUT, run_time=5
            )
        )

        self.play(FadeOut(c2))
        self.play(FadeOut(c1))


class CircleAndCircleMoving(Scene):
    """The same pair, translated instead of rotated: ``.animate.move_to``.

    Concepts: ``mob.animate.move_to(point)`` — the group keeps its internal
    layout while its centre travels. Compare with ``shift``, which is relative.
    """

    def construct(self):
        c1 = Circle(radius=0.5)
        c1.set_fill(GREEN, opacity=0.6)
        c2 = Circle(radius=0.7)
        c2.set_fill(YELLOW, opacity=0.6)
        c1.next_to(c2, LEFT)

        group = VGroup(c1, c2)
        group.shift(5 * LEFT)

        self.play(Create(group), run_time=2)
        self.play(group.animate.move_to(5 * RIGHT))

        self.play(FadeOut(c2))
        self.play(FadeOut(c1))


class CircleAndDotRotatingAndTracing(Scene):
    """An ``add_updater`` spin that never stops, while the group travels right.

    Concepts: ``mob.add_updater(lambda mob, dt: ...)`` runs on *every* frame
    (``dt`` is the time since the last frame), so rotation and translation can
    overlap — and ``TracedPath`` records the compounded path.
    """

    def construct(self):
        circle = Circle(radius=0.5).shift(LEFT * 5)
        dot = Dot(circle.get_left())
        group = VGroup(circle, dot)

        trace = TracedPath(dot.get_center)

        group.add_updater(lambda mob, dt: mob.rotate(3 * dt))

        self.add(trace)
        self.play(FadeIn(group))
        self.play(group.animate.shift(RIGHT * 10), run_time=7)
