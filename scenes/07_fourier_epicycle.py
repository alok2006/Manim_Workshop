"""Stage 7 — The finale: Fourier epicycles trace a real image.

This is the 3Blue1Brown party trick: any closed contour can be rebuilt by a
chain of rotating circles whose radii and phases come from a Discrete Fourier
Transform of the outline. Here the outline is Doraemon's silhouette, extracted
from ``assets/doraemon.jpg`` with OpenCV.

The maths lives in :mod:`manim_workshop.fourier` (see
``docs/concepts/07-fourier-epicycles.md`` for the annotated walk-through); this
scene is only the animation half:

* :func:`~manim_workshop.fourier.get_fourier_coefficients` returns the sorted
  ``(radius, frequency, phase)`` triples,
* each frame stacks the circles tip-to-tail starting from the origin,
* the free end of the last link is the pen, and ``TracedPath`` draws its trail.

Render::

    manim render -ql scenes/07_fourier_epicycle.py FourierEpicycle
    manim render -qh scenes/07_fourier_epicycle.py FourierEpicycle   # keep this one
"""

import numpy as np
from manim import *

from manim_workshop.fourier import get_fourier_coefficients


class FourierEpicycle(Scene):
    """Draw the Doraemon outline with ~61 rotating epicycles.

    Concepts: DFT of a sampled contour, tip-to-tail vector addition,
    ``always_redraw`` for a cheap "recompute everything each frame" scene.

    Try: ``get_fourier_coefficients(num_coeffs=200)`` for a sharper outline (and
    a slower render), or point it at your own image in ``assets/``.
    """

    def construct(self):
        coeffs = get_fourier_coefficients()
        tracker = ValueTracker(0)

        def get_outline():
            """One frame: the epicycle chain at the tracker's current time."""
            current_center = np.array([0, 0, 0])
            group = VGroup()

            for coeff in coeffs:
                t = tracker.get_value()
                radius = coeff["radius"]
                frequency = coeff["freq"]
                phase = coeff["phase"]

                angle = frequency * t + phase
                next_center = (
                    np.array([radius * np.cos(angle), radius * np.sin(angle), 0])
                    + current_center
                )

                circle = Circle(
                    radius=radius,
                    color=BLUE,
                    stroke_opacity=0.4,
                    stroke_width=0.4,
                ).move_to(current_center)
                spoke = Line(
                    current_center,
                    next_center,
                    color=WHITE,
                    stroke_opacity=0.6,
                    stroke_width=0.4,
                )
                group.add(circle, spoke)
                current_center = next_center

            tip = Dot(color=YELLOW, point=current_center)
            group.add(tip)
            return group

        outline = always_redraw(get_outline)

        # The pen sits on the last link's free end; the trail is what we keep.
        dot = Dot().add_updater(lambda mob: mob.move_to(outline[-1].get_center()))
        trace = TracedPath(dot.get_center, stroke_width=9, stroke_color=GOLD)

        self.add(outline, dot, trace)
        self.play(tracker.animate.set_value(2 * PI), run_time=20)
