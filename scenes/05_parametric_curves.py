"""Stage 5 — Parametric curves: let a tracker drive a point.

Every scene here has the same skeleton: a ``ValueTracker`` is the time axis, a
point is recomputed from the tracker with ``always_redraw``, and a ``TracedPath``
inks in where that point has been. Change three numbers and you get a different
curve — that is the lesson.

Render one, some, or all::

    manim render -ql scenes/05_parametric_curves.py SineSnake
    manim render -ql -a scenes/05_parametric_curves.py
"""

import numpy as np
from manim import *


class SineSnake(Scene):
    """One period of a sine wave, drawn by a travelling dot.

    Concepts: ``ValueTracker`` as an abstract time variable, ``always_redraw``,
    ``TracedPath(dissipating_time=...)`` for a fading comet tail.

    Try: change ``run_time`` on the final ``play``; the curve is the same, the
    *pacing* is not.
    """

    def construct(self):
        tracker = ValueTracker(-2 * PI)

        dot = always_redraw(
            lambda: Dot(
                [tracker.get_value(), np.sin(tracker.get_value()), 0],
                color=YELLOW,
            )
        )
        tracer = TracedPath(
            dot.get_center, stroke_color=RED, stroke_width=9, dissipating_time=1.5
        )

        self.add(dot)
        self.add(tracer)
        self.play(tracker.animate.set_value(2 * PI), run_time=15)


class Epicycloid(Scene):
    """A circle orbiting a circle: the classic "spirograph" curve.

    Two rotations nest here — one updater spins the small circle around the big
    one (``f1`` turns), a second spins the dot around the small circle (``f2``
    turns). Their ratio is the whole design space.

    Concepts: two independent ``add_updater`` rotation rates, ``clear_updaters``.
    """

    def construct(self):
        r1, r2 = 0.9, 0.6  # radii of the big wheel and the small wheel
        f1, f2 = 3, 8  # turns per second: orbit rate, spin rate

        c1 = Circle(radius=r1)
        c2 = Circle(radius=r2).next_to(c1, LEFT, buff=0)
        dot = Dot(c2.get_left())
        trace = TracedPath(dot.get_center, dissipating_time=4)

        self.play(FadeIn(dot), run_time=0.25)
        self.play(FadeIn(c2), run_time=0.25)
        self.play(FadeIn(c1), run_time=0.25)

        wheel = VGroup(c2, dot)
        wheel.add_updater(
            lambda mob, dt: mob.rotate(f1 * dt, about_point=c1.get_center())
        )
        dot.add_updater(
            lambda mob, dt: mob.rotate(f2 * dt, about_point=c2.get_center())
        )

        self.add(wheel)
        self.add(trace)

        self.wait(15)

        # Updaters keep running until you stop them.
        wheel.clear_updaters()
        dot.clear_updaters()
        self.play(FadeOut(wheel), FadeOut(trace), run_time=0.5)
        self.play(FadeOut(dot), run_time=0.5)


class LissajousFigures(Scene):
    """Two sine waves, one per axis, out of phase — a Lissajous figure.

    Concepts: independent functions of the *same* tracker parameter; ``phi``
    shifts one axis in time. Changing ``w1``/``w2`` changes the knot; a rational
    ratio closes the curve.

    Try: ``w1=3, w2=4`` (this one), ``w1=3, w2=5``, ``phi=0``.
    """

    def construct(self):
        w1, w2 = 3, 4
        phi = PI / 3

        tracker = ValueTracker(-2 * PI)

        dot = always_redraw(
            lambda: Dot(
                [
                    np.sin(w1 * tracker.get_value()),
                    np.sin(w2 * tracker.get_value() + phi),
                    0,
                ],
                color=YELLOW,
            )
        )
        tracer = TracedPath(
            dot.get_center, stroke_color=RED, stroke_width=9, dissipating_time=None
        )

        self.add(dot)
        self.add(tracer)
        self.play(tracker.animate.set_value(2 * PI), run_time=20)


class RoseCurve(Scene):
    """A rose: polar ``r = sin(k·θ)`` walked in Cartesian coordinates.

    ``k`` is the petal count (for odd ``k``). The two coordinates are the polar
    recipe ``(r·cos θ, r·sin θ)`` written out explicitly.

    Concepts: parametric plotting from polar equations.
    """

    def construct(self):
        k = 5
        scale = 3

        tracker = ValueTracker(-2 * PI)

        dot = always_redraw(
            lambda: Dot(
                [
                    scale
                    * np.sin(k * tracker.get_value())
                    * np.cos(tracker.get_value()),
                    scale
                    * np.sin(k * tracker.get_value())
                    * np.sin(tracker.get_value()),
                    0,
                ],
                color=YELLOW,
            )
        )
        tracer = TracedPath(
            dot.get_center, stroke_color=RED, stroke_width=9, dissipating_time=None
        )

        self.add(dot)
        self.add(tracer)
        self.play(tracker.animate.set_value(2 * PI), run_time=20)
