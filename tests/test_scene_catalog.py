"""Invariants for the scene catalogue and the scene modules themselves.

These are the *fast* checks: they parse files and inspect names, but never
import manim and never render. They are the tests that catch the mistakes this
reorganisation could plausibly introduce — a scene left behind in the notebook,
a duplicated class name, a docstring that went missing, a typo returning.

The slow end-to-end render lives in ``tests/test_scenes_smoke.py``.
"""

from __future__ import annotations

import ast
import re

import pytest

from manim_workshop.catalog import (
    LEGACY_SCENE_NAMES,
    all_scenes,
    module_docstring,
    scene_files,
)

EXPECTED_SCENE_COUNT = 17
"""The notebook taught 17 scenes; the extraction must not lose one."""

STAGE_FILE_RE = re.compile(r"^\d{2}_[a-z][a-z_]*\.py$")

LEGACY_TYPOS = ("Sqaure", "cirlce", "WIth", "Epicyle", "outine", "Sqto", "ANDT")
"""Misspellings present in the original notebook. None may survive in a scene name."""


@pytest.fixture(scope="module")
def scenes():
    return all_scenes()


def test_scene_directory_is_not_empty():
    assert scene_files(), "no scene modules matched the NN_name.py pattern"


def test_every_scene_count_matches_the_notebook():
    # Regression guard: the notebook had exactly 17 `%%manim` cells.
    assert len(all_scenes()) == EXPECTED_SCENE_COUNT


def test_stage_files_are_numbered_and_snake_case():
    for path in scene_files():
        assert STAGE_FILE_RE.match(path.name), f"{path.name} breaks the NN_stage_name.py convention"


def test_stage_numbers_are_unique_and_contiguous_from_01():
    numbers = [int(p.name[:2]) for p in scene_files()]
    assert numbers == list(range(1, len(numbers) + 1)), numbers


def test_every_stage_file_has_a_module_docstring():
    for path in scene_files():
        doc = module_docstring(path)
        assert doc, f"{path.name} has no module docstring"
        assert len(doc.splitlines()) >= 2, f"{path.name}'s docstring is too thin to teach from"


def test_every_scene_has_a_docstring(scenes):
    missing = [s.name for s in scenes if not s.docstring]
    assert not missing, f"scenes without a docstring: {missing}"


def test_scene_names_are_unique(scenes):
    names = [s.name for s in scenes]
    duplicates = {name for name in names if names.count(name) > 1}
    assert not duplicates, f"duplicated scene names: {duplicates}"


def test_scene_names_are_camel_case(scenes):
    for scene in scenes:
        assert re.match(r"^[A-Z][A-Za-z0-9]*$", scene.name), f"{scene.name} is not CamelCase"


def test_scene_names_carry_no_legacy_typos(scenes):
    # Regression test for the rename: `Sqaure`/`MyRose`/`Epicyle`… must be gone.
    for scene in scenes:
        for typo in LEGACY_TYPOS:
            assert typo not in scene.name, f"{scene.name} still contains the typo {typo!r}"


def test_legacy_name_map_covers_every_scene(scenes):
    """The old→new table is the migration path for anyone holding old slides."""
    current = {scene.name for scene in scenes}
    mapped = set(LEGACY_SCENE_NAMES.values())
    assert mapped == current, (
        f"scenes with no old name: {sorted(current - mapped)}; "
        f"stale entries in the map: {sorted(mapped - current)}"
    )
    assert len(LEGACY_SCENE_NAMES) == EXPECTED_SCENE_COUNT


def test_legacy_name_map_is_injective():
    values = list(LEGACY_SCENE_NAMES.values())
    assert len(values) == len(set(values)), "two old names point at the same new name"


def test_only_identical_entries_are_unchanged():
    # A handful of names were already correct and must stay untouched.
    unchanged = {old for old, new in LEGACY_SCENE_NAMES.items() if old == new}
    assert unchanged == {"CircleAndCircleMoving", "LissajousFigures"}


def test_renamed_legacy_names_are_gone(scenes):
    current = {scene.name for scene in scenes}
    for old, new in LEGACY_SCENE_NAMES.items():
        if old != new:
            assert old not in current, f"{old} was renamed to {new} but the old name survives"


def test_no_scene_is_defined_twice_across_files(scenes):
    by_name: dict[str, list[str]] = {}
    for scene in scenes:
        by_name.setdefault(scene.name, []).append(scene.relative_path)
    collisions = {name: paths for name, paths in by_name.items() if len(paths) > 1}
    assert not collisions, f"a scene is defined in more than one file: {collisions}"


def test_relative_paths_are_inside_scenes(scenes):
    assert all(s.relative_path.startswith("scenes/") for s in scenes)


def test_render_commands_are_well_formed(scenes):
    for scene in scenes:
        command = scene.render_command()
        assert command.startswith("manim render -ql scenes/")
        assert command.endswith(scene.name)


def test_scene_modules_parse_and_import_manim(scene_source):
    tree = ast.parse(scene_source.text, filename=str(scene_source.path))
    imported_modules = {
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module
    } | {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert "manim" in imported_modules, f"{scene_source.path.name} does not import manim"


def test_every_scene_uses_the_wildcard_manim_idiom(scene_source):
    # `from manim import *` is the documented Manim style (see CONTRIBUTING.md);
    # a scene that imports individual names is inconsistent with the workshop.
    assert any(
        isinstance(node, ast.ImportFrom)
        and node.module == "manim"
        and any(a.name == "*" for a in node.names)
        for node in ast.walk(ast.parse(scene_source.text))
    ), f"{scene_source.path.name} should use `from manim import *`"
