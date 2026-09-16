"""Stage 6 — Projects: flowers built out of traced petals.

Three scenes, one idea each:

* :class:`FlowerWithColors` — draw the rose one petal at a time, recolouring
  each petal (segments + ``for`` loops).
* :class:`RotatingFlower` — collect the traced petals into a single
  ``VGroup``, throw the scaffolding away, and rotate the flower as a rigid body.
* :class:`FlowerWithGradient` — same flower, but every stroke is a gradient
  between two neighbouring colours.

Render one, some, or all::

    manim render -ql scenes/06_flowers.py RotatingFlower
    manim render -ql -a scenes/06_flowers.py
"""

import numpy as np
from manim import *


class FlowerWithColors(Scene):
    """A five-petal rose, coloured petal by petal.

    The loop walks the tracker forward one petal-period at a time; because each
    petal gets its own ``TracedPath`` with its own colour, the same dot draws a
    multi-coloured flower.

    Concepts: segments, ``for`` loops, ``time_period`` for an odd petal count.
    """

    def construct(self):
        colors = [PINK, RED, ORANGE, GOLD, YELLOW]
        k = 5
        scale = 3

        # Odd k closes after PI, even k needs the full 2*PI.
        time_period = PI / k if k % 2 == 1 else 2 * PI / k
        tracker = ValueTracker(0)

        for x in range(k):
            petal_color = colors[x % len(colors)]
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
                    ]
                )
            )
            path = TracedPath(dot.get_center, stroke_width=9, stroke_color=petal_color)
            self.add(dot, path)

            self.play(tracker.animate.set_value((x + 1) * time_period))


class RotatingFlower(Scene):
    """A twelve-petal rose, then the scaffolding is replaced by one object.

    After the petals are traced, every path is copied into a plain ``VMobject``
    (points only, no updaters), the dot/path originals are removed, and the
    assembled flower is rotated a quarter turn as a rigid body.

    Concepts: ``VGroup`` as a container, ``set_points``/``get_points`` to clone
    geometry, ``remove`` to drop the machinery.
    """

    def construct(self):
        colors = [PINK, RED, ORANGE, GOLD, YELLOW]
        k = 12
        scale = 3

        time_period = PI / k if k % 2 == 1 else 2 * PI / k
        tracker = ValueTracker(0)

        segments = VGroup()
        for x in range(k):
            petal_color = colors[x % len(colors)]
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
                    ]
                )
            )
            path = TracedPath(dot.get_center, stroke_width=9, stroke_color=petal_color)
            self.add(dot, path)
            segments.add(dot, path)

            self.play(tracker.animate.set_value((x + 1) * time_period))

        flower = VGroup(
            *[
                VMobject(
                    stroke_color=segment.stroke_color,
                    stroke_width=segment.stroke_width,
                ).set_points(segment.get_points())
                for segment in segments
            ]
        )
        self.remove(tracker, *segments)
        self.add(flower)

        self.play(Rotate(flower, angle=PI / 2, about_point=ORIGIN, run_time=4))


class FlowerWithGradient(Scene):
    """The twelve-petal rose again — this time every stroke is a gradient.

    ``stroke_color`` accepts a *list* of colours, and Manim interpolates along
    the stroke. Handing petal ``x`` the pair ``(colors[x], colors[x+1])`` makes
    the whole flower cycle smoothly through the palette.

    Concepts: gradient strokes, glow via ``stroke_width``.
    """

    def construct(self):
        colors = [PINK, RED, ORANGE, GOLD, YELLOW]
        k = 12
        scale = 3

        time_period = PI / k if k % 2 == 1 else 2 * PI / k
        tracker = ValueTracker(0)

        segments = VGroup()
        for x in range(k):
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
                    ]
                )
            )
            path = TracedPath(
                dot.get_center,
                stroke_width=9,
                stroke_color=[colors[x % len(colors)], colors[(x + 1) % len(colors)]],
            )
            self.add(dot, path)
            segments.add(dot, path)

            self.play(tracker.animate.set_value((x + 1) * time_period))

        flower = VGroup(
            *[
                VMobject(
                    stroke_color=segment.stroke_color,
                    stroke_width=segment.stroke_width,
                ).set_points(segment.get_points())
                for segment in segments
            ]
        )
        self.remove(tracker, *segments)
        self.add(flower)

        self.play(Rotate(flower, angle=PI / 2, about_point=ORIGIN, run_time=4))
