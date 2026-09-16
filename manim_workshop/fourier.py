"""The Discrete Fourier Transform of an image outline.

This module is the maths half of the workshop finale
(:class:`scenes.07_fourier_epicycle.FourierEpicycle`). Given a *closed contour*
— here, the outline of Doraemon's silhouette — it answers the question:

    which chain of rotating circles draws exactly this shape?

The recipe is four steps:

1. **Threshold** the image and take its longest external contour
   (:func:`sample_contour`, step 1–3).
2. **Resample** the contour at ``num_samples`` points, evenly spaced along its
   *arc length*, and centre/scale it to fit the Manim frame.
3. **Transform**: treat the sampled points as complex numbers
   ``z = x + i·y`` and take the DFT
   ``c_n = (1/N) · Σ_k z_k · exp(-2πi·n·k/N)``.
4. **Sort** the coefficients by radius. Because each term
   ``c_n · exp(2πi·n·t)`` is a circle of radius ``|c_n|`` rotating ``n`` times
   per unit ``t``, and because the coefficients add tip-to-tail, keeping only
   the biggest ones still draws a recognisable outline.

An annotated walk-through, with the reason each line exists, lives in
``docs/concepts/07-fourier-epicycles.md``.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import cv2
import numpy as np

from manim_workshop.paths import resolve_asset

__all__ = [
    "FourierCoefficient",
    "DEFAULT_NUM_SAMPLES",
    "DEFAULT_NUM_COEFFS",
    "sample_contour",
    "get_fourier_coefficients",
    "evaluate_epicycles",
]

DEFAULT_NUM_SAMPLES = 300
"""How many points the contour is resampled to."""

DEFAULT_NUM_COEFFS = 60
"""How many frequencies to keep. ``60`` yields the 61 terms ``n = -30 … 30``."""


class FourierCoefficient(TypedDict):
    """One term of the epicycle chain.

    Kept as a plain ``dict`` (rather than a dataclass) so that the original
    notebook snippet ``coeff["radius"]`` keeps working unchanged.

    Attributes
    ----------
    freq
        Integer frequency ``n``; also the number of rotations per unit time.
    radius
        ``|c_n|`` — the radius of this circle in Manim units.
    phase
        ``arg(c_n)`` — where on its circle this term starts at ``t = 0``.
    """

    freq: int
    radius: float
    phase: float


def _spans_image(contour: np.ndarray, width: int, height: int, tolerance: float = 0.98) -> bool:
    """True if ``contour`` hugs the image border — i.e. it is the *background*.

    ``cv2.threshold(..., THRESH_BINARY_INV)`` makes a light background white, so
    if the subject is *lighter* than its background the largest "contour" is the
    rectangle around the whole image. Tracing that produces a convincing-looking
    square animation instead of the user's shape, so it is rejected explicitly.
    """
    _, _, box_width, box_height = cv2.boundingRect(contour)
    return box_width >= tolerance * width and box_height >= tolerance * height


def _load_contour_points(image_path: str | Path | None) -> np.ndarray:
    """Threshold an image and return its longest external contour as (M, 2).

    The expected polarity is a **dark subject on a light background**, which is
    what ``assets/doraemon.jpg`` is. An inverted image is rejected with an
    explanation rather than silently traced as its own border.
    """
    path = resolve_asset(image_path)

    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        # cv2.imread returns None for a missing/corrupt file instead of raising;
        # without this check the failure surfaces much later as a numpy error.
        raise FileNotFoundError(f"OpenCV could not read an image at {path}")

    _, thresholded = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError(f"No contour found in {path}; is the background uniform?")

    height, width = thresholded.shape[:2]
    subject_contours = [c for c in contours if not _spans_image(c, width, height)]
    if not subject_contours:
        raise ValueError(
            f"The only contour found in {path} is the image border, which means the "
            "subject is lighter than its background. This pipeline expects a dark "
            "subject on a light background (like assets/doraemon.jpg); invert your "
            "image and try again."
        )

    contour = max(subject_contours, key=len).squeeze()
    if contour.ndim != 2 or contour.shape[1] != 2:
        raise ValueError(f"Degenerate contour in {path} (shape {contour.shape})")
    return np.asarray(contour, dtype=float)


def sample_contour(
    image_path: str | Path | None = None,
    num_samples: int = DEFAULT_NUM_SAMPLES,
) -> np.ndarray:
    """Return ``num_samples`` complex points tracing the image's outline.

    Steps 1–3 of the recipe in the module docstring: threshold → take the
    longest contour → invert ``y`` (image coordinates grow downwards) → centre
    on the origin → scale to fit a radius-3 box → resample evenly along the
    arc length → return as ``x + i·y``.

    Parameters
    ----------
    image_path
        Any path accepted by :func:`manim_workshop.paths.resolve_asset`.
        ``None`` uses the bundled ``assets/doraemon.jpg``.
    num_samples
        Number of points in the returned sequence.

    Returns
    -------
    numpy.ndarray
        Complex array of shape ``(num_samples,)``.
    """
    contour = _load_contour_points(image_path)

    x, y = contour[:, 0], -contour[:, 1]  # invert Y for Cartesian coordinates
    x = x - np.mean(x)
    y = y - np.mean(y)
    scale = max(np.max(np.abs(x)), np.max(np.abs(y))) / 3.0  # fit the Manim frame
    x, y = x / scale, y / scale

    distances = np.sqrt(np.diff(x, prepend=x[0]) ** 2 + np.diff(y, prepend=y[0]) ** 2)
    cumulative_dist = np.cumsum(distances)
    total_length = cumulative_dist[-1]

    interp_dists = np.linspace(0, total_length, num_samples, endpoint=False)
    x_sampled = np.interp(interp_dists, cumulative_dist, x)
    y_sampled = np.interp(interp_dists, cumulative_dist, y)

    return x_sampled + 1j * y_sampled


def get_fourier_coefficients(
    image_path: str | Path | None = None,
    num_samples: int = DEFAULT_NUM_SAMPLES,
    num_coeffs: int = DEFAULT_NUM_COEFFS,
) -> list[FourierCoefficient]:
    """Decompose an image outline into rotating circles, biggest first.

    Parameters
    ----------
    image_path
        Path to the silhouette (see :func:`sample_contour`).
    num_samples
        Resampling density of the contour.
    num_coeffs
        How many frequencies to keep. The returned list has ``num_coeffs + 1``
        entries, spanning ``n = -num_coeffs // 2 … num_coeffs // 2``.

    Returns
    -------
    list[FourierCoefficient]
        Sorted by ``radius`` descending: drawing the chain in this order puts the
        coarse shape down first and adds detail last, which looks intentional on
        screen.
    """
    z = sample_contour(image_path, num_samples=num_samples)
    n_points = len(z)
    k = np.arange(n_points)

    coeffs: list[FourierCoefficient] = []
    for n in range(-num_coeffs // 2, num_coeffs // 2 + 1):
        # c_n = (1/N) * sum_k z_k * exp(-i * 2*pi * n * k / N)
        c_n = np.sum(z * np.exp(-1j * 2 * np.pi * n * k / n_points)) / n_points
        coeffs.append(
            {
                "freq": int(n),
                "radius": float(np.abs(c_n)),
                "phase": float(np.angle(c_n)),
            }
        )

    coeffs.sort(key=lambda item: item["radius"], reverse=True)
    return coeffs


def evaluate_epicycles(coeffs: list[FourierCoefficient], t: float) -> complex:
    """Position of the pen at time ``t``: ``Σ c_n · exp(2πi·n·t)``.

    This is the exact expression the scene evaluates frame by frame; it is
    exposed separately so tests can assert that a full set of coefficients
    reconstructs the sampled contour.

    >>> coeffs = [{"freq": 0, "radius": 1.0, "phase": 0.0}]
    >>> evaluate_epicycles(coeffs, 0.0)
    (1+0j)
    """
    total = 0j
    for coeff in coeffs:
        total += coeff["radius"] * np.exp(1j * (2 * np.pi * coeff["freq"] * t + coeff["phase"]))
    return complex(total)
