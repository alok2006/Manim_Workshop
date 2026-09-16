"""Tests for the DFT helper behind the Fourier epicycle finale.

The interesting assertions here are the last few: they check actual
*mathematics* (that a full set of coefficients reconstructs the contour it came
from, and that a drawn circle produces exactly one dominant harmonic) rather
than merely checking that functions return something.
"""

from __future__ import annotations

import numpy as np
import pytest

from manim_workshop.fourier import (
    DEFAULT_NUM_COEFFS,
    evaluate_epicycles,
    get_fourier_coefficients,
    sample_contour,
)
from manim_workshop.paths import resolve_asset


@pytest.fixture(scope="module")
def doraemon_coeffs():
    return get_fourier_coefficients(num_samples=256, num_coeffs=16)


# --------------------------------------------------------------------------- #
# paths and asset resolution
# --------------------------------------------------------------------------- #
def test_bundled_asset_exists():
    assert resolve_asset().name == "doraemon.jpg"


def test_missing_asset_lists_every_location(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError) as excinfo:
        resolve_asset("definitely-not-here.png")
    message = str(excinfo.value)
    assert "definitely-not-here.png" in message
    assert "assets" in message, "the error should name the bundled assets directory"


def test_image_in_cwd_wins_over_the_bundled_asset(tmp_path, monkeypatch):
    # An explicit user choice must not be shadowed by the shipped image.
    local = tmp_path / "doraemon.jpg"
    local.write_bytes(b"pretend-jpeg")
    monkeypatch.chdir(tmp_path)
    assert resolve_asset("doraemon.jpg") == local.resolve()


# --------------------------------------------------------------------------- #
# contour sampling
# --------------------------------------------------------------------------- #
def test_sample_contour_shape_and_dtype():
    z = sample_contour(num_samples=128)
    assert z.shape == (128,)
    assert np.iscomplexobj(z)


def test_sample_contour_fits_the_manim_frame():
    z = sample_contour(num_samples=512)
    # `sample_contour` scales the contour so its *larger* extent reaches 3.0;
    # resampling can miss the exact extremum, hence the small tolerance.
    extent = max(np.max(np.abs(z.real)), np.max(np.abs(z.imag)))
    assert extent == pytest.approx(3.0, rel=0.02)
    # …and centring puts the mean near the origin (resampling shifts it slightly).
    assert abs(z.mean()) < 0.5


@pytest.mark.parametrize("num_samples", [64, 300, 1024])
def test_sample_contour_is_parameterisable(num_samples):
    assert sample_contour(num_samples=num_samples).shape == (num_samples,)


def test_unreadable_image_is_reported_clearly(tmp_path):
    broken = tmp_path / "broken.png"
    broken.write_text("this is not a PNG")
    with pytest.raises(FileNotFoundError, match="OpenCV could not read"):
        get_fourier_coefficients(broken, num_samples=16, num_coeffs=4)


def test_image_without_contour_raises(tmp_path):
    import cv2

    blank = tmp_path / "blank.png"
    cv2.imwrite(str(blank), np.full((32, 32), 255, dtype=np.uint8))
    with pytest.raises(ValueError, match="No contour"):
        get_fourier_coefficients(blank, num_samples=16, num_coeffs=4)


# --------------------------------------------------------------------------- #
# coefficients
# --------------------------------------------------------------------------- #
def test_coefficient_count_sorting_and_types(doraemon_coeffs):
    assert len(doraemon_coeffs) == 16 + 1  # n = -8 … 8
    radii = [coeff["radius"] for coeff in doraemon_coeffs]
    assert radii == sorted(radii, reverse=True), "biggest circles must come first"
    assert {coeff["freq"] for coeff in doraemon_coeffs} == set(range(-8, 9))
    for coeff in doraemon_coeffs:
        assert isinstance(coeff["freq"], int)
        assert isinstance(coeff["radius"], float)
        assert isinstance(coeff["phase"], float)
        assert coeff["radius"] >= 0.0
        assert -np.pi <= coeff["phase"] <= np.pi


def test_coefficients_support_dict_access(doraemon_coeffs):
    # The original notebook snippet used `coeff["radius"]`; that must keep working,
    # and the values must stay plain (JSON-serialisable) dicts.
    import json

    first = doraemon_coeffs[0]
    assert set(first) == {"freq", "radius", "phase"}
    assert json.loads(json.dumps(first)) == first
    assert doraemon_coeffs[0]["radius"] == max(c["radius"] for c in doraemon_coeffs)


def test_default_num_coeffs_is_the_documented_value():
    assert DEFAULT_NUM_COEFFS == 60  # n = -30 … 30, i.e. 61 epicycles


# --------------------------------------------------------------------------- #
# the mathematics
# --------------------------------------------------------------------------- #
def test_full_coefficient_set_reconstructs_the_contour_exactly():
    """A complete DFT round-trip must be exact to floating-point precision.

    This is the test that pins the *sign convention*: if the forward transform
    (``exp(-2πi·n·k/N)``) and :func:`evaluate_epicycles` (``exp(+2πi·n·t)``)
    ever disagreed, this fails loudly instead of producing a scrambled drawing.
    """
    n_points = 64
    k = np.arange(n_points)
    # Two counter-rotating harmonics, so the test cannot pass by symmetry.
    z = np.exp(2j * np.pi * 3 * k / n_points) + 0.5 * np.exp(-2j * np.pi * 5 * k / n_points)

    coeffs = []
    for n in range(n_points):
        c_n = np.sum(z * np.exp(-2j * np.pi * n * k / n_points)) / n_points
        coeffs.append({"freq": int(n), "radius": float(abs(c_n)), "phase": float(np.angle(c_n))})

    for sample in range(n_points):
        t = sample / n_points
        assert evaluate_epicycles(coeffs, t) == pytest.approx(z[sample], abs=1e-9)


def test_a_drawn_circle_yields_one_dominant_harmonic(tmp_path):
    """End-to-end through OpenCV: a circle is a single rotating vector.

    The contour of a filled circle of radius ``r`` has exactly one non-zero
    Fourier coefficient, ``|c_1| = r`` — scaled here to 3.0 by the frame fit.

    Note the polarity: a **dark** circle on a **light** background, matching
    ``assets/doraemon.jpg``. The inverse case is covered separately.
    """
    import cv2

    image = np.full((240, 240), 255, dtype=np.uint8)  # light background
    cv2.circle(image, (120, 120), 80, 0, thickness=-1)  # dark subject
    path = tmp_path / "circle.png"
    cv2.imwrite(str(path), image)

    coeffs = get_fourier_coefficients(path, num_samples=256, num_coeffs=4)
    dominant = [coeff for coeff in coeffs if coeff["radius"] > 0.1]

    assert len(dominant) == 1, f"expected one harmonic, got {dominant}"
    assert dominant[0]["freq"] == 1, "a counter-clockwise circle is frequency +1"
    assert dominant[0]["radius"] == pytest.approx(3.0, rel=0.02)

    # And the single term really does trace a circle of that radius.
    for t in np.linspace(0, 1, 32, endpoint=False):
        assert abs(evaluate_epicycles(dominant, t)) == pytest.approx(3.0, rel=0.02)


def test_light_subject_on_dark_background_is_rejected_not_traced(tmp_path):
    """Regression: an inverted image used to trace the *image border*.

    A white circle on a black background inverts to "white everywhere except the
    circle", so OpenCV's largest external contour is the frame — a square. That
    silently produced a plausible-looking wrong animation; now it is an error
    that names the cause.
    """
    import cv2

    image = np.zeros((240, 240), dtype=np.uint8)  # dark background
    cv2.circle(image, (120, 120), 80, 255, thickness=-1)  # light subject
    path = tmp_path / "inverted.png"
    cv2.imwrite(str(path), image)

    with pytest.raises(ValueError, match="lighter than its background"):
        get_fourier_coefficients(path, num_samples=64, num_coeffs=4)


def test_doraemon_outline_spans_the_frame():
    """The traced outline is a real 2-D silhouette, not a flat line."""
    z = sample_contour(num_samples=512)
    extent = max(np.max(np.abs(z.real)), np.max(np.abs(z.imag)))
    assert extent == pytest.approx(3.0, rel=0.02), "the widest axis fills the frame"
    assert np.ptp(z.real) > 1.0, "the silhouette has real width"
    assert np.ptp(z.imag) > 1.0, "the silhouette has real height"
