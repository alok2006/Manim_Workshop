"""The documentation is part of the product — these tests keep it honest.

Three failure modes this file exists to prevent:

1. a scene is added but never documented;
2. a documented command points at a scene that no longer exists;
3. a relative link in the docs rots because a file moved.

All three have happened to somebody's project. None of them should happen here,
and none of them need a human to notice.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from manim_workshop.catalog import LEGACY_SCENE_NAMES, all_scenes
from manim_workshop.paths import REPO_ROOT

CATALOG = REPO_ROOT / "docs" / "03-scene-catalog.md"
README = REPO_ROOT / "README.md"
DOCS_INDEX = REPO_ROOT / "docs" / "README.md"

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
HTML_SRC_RE = re.compile(r'<img[^>]*src="([^"]+)"')

SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "tel:")


def markdown_files() -> list[Path]:
    return sorted(
        [REPO_ROOT / "README.md", REPO_ROOT / "CONTRIBUTING.md", REPO_ROOT / "CHANGELOG.md"]
        + list(REPO_ROOT.glob("docs/**/*.md"))
        + list(REPO_ROOT.glob("videos/*.md"))
    )


@pytest.fixture(scope="module")
def catalog_text() -> str:
    assert CATALOG.exists(), "docs/03-scene-catalog.md is missing"
    return CATALOG.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# every scene is documented
# --------------------------------------------------------------------------- #
def test_every_scene_appears_in_the_catalog(catalog_text):
    missing = [scene.name for scene in all_scenes() if f"`{scene.name}`" not in catalog_text]
    assert not missing, f"scenes missing from the catalog: {missing}"


def test_every_scene_has_a_render_command(catalog_text):
    for scene in all_scenes():
        expected = scene.render_command()
        assert expected in catalog_text, f"the catalog does not show how to run {scene.name}"


def test_catalog_does_not_document_ghost_scenes(catalog_text):
    known = {scene.name for scene in all_scenes()}
    # Scenes referenced in `manim render … <Name>` form.
    documented = set(re.findall(r"manim render -q[l|mh|p|k]+ \S+ (\w+)", catalog_text))
    ghosts = documented - known
    assert not ghosts, f"the catalog documents scenes that no longer exist: {ghosts}"


# --------------------------------------------------------------------------- #
# the migration table is complete
# --------------------------------------------------------------------------- #
def test_migration_table_lists_every_old_name(catalog_text):
    missing = [old for old in LEGACY_SCENE_NAMES if f"`{old}`" not in catalog_text]
    assert not missing, f"old scene names missing from the migration table: {missing}"


# --------------------------------------------------------------------------- #
# the install documentation really covers the install
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "requirement",
    [
        "uv venv",  # the uv recipe
        "python3 -m venv",  # the venv recipe
        "conda create",  # the conda recipe
        "pip install -r requirements.txt",
        "pip install -e .",
        "source .venv/bin/activate",
        "manim render -ql",
    ],
)
def test_readme_documents_the_setup(requirement):
    assert requirement in README.read_text(encoding="utf-8"), (
        f"README.md no longer shows {requirement!r} — the environment instructions "
        "are a deliverable, not a footnote"
    )


@pytest.mark.parametrize(
    "requirement",
    [
        "apt install build-essential python3-dev libcairo2-dev libpango1.0-dev",
        "dnf install python3-devel pkg-config cairo-devel pango-devel",
        "pacman -Syu base-devel cairo pango",
        "brew install cairo pkg-config",
        "manim checkhealth",
        "ipykernel install",
    ],
)
def test_getting_started_covers_every_platform(requirement):
    text = (REPO_ROOT / "docs" / "01-getting-started.md").read_text(encoding="utf-8")
    assert requirement in text, f"docs/01-getting-started.md no longer mentions {requirement!r}"


# --------------------------------------------------------------------------- #
# no broken relative links
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("markdown", markdown_files(), ids=lambda path: path.name)
def test_relative_links_resolve(markdown: Path):
    text = markdown.read_text(encoding="utf-8")
    targets = MARKDOWN_LINK_RE.findall(text) + HTML_SRC_RE.findall(text)

    broken = []
    for target in targets:
        if target.startswith(SKIP_PREFIXES):
            continue
        cleaned = target.split("#", 1)[0]
        if not cleaned:  # a bare anchor
            continue
        resolved = (markdown.parent / cleaned).resolve()
        # Links that escape the repository (e.g. GitHub's `../../actions/...`)
        # are not file references we can check.
        try:
            resolved.relative_to(REPO_ROOT.resolve())
        except ValueError:
            continue
        if not resolved.exists():
            broken.append(target)

    assert not broken, f"{markdown.relative_to(REPO_ROOT)} has broken links: {broken}"


# --------------------------------------------------------------------------- #
# the docs index stays a real index
# --------------------------------------------------------------------------- #
def test_docs_index_links_every_document():
    index = DOCS_INDEX.read_text(encoding="utf-8")
    missing = [
        path.name
        for path in REPO_ROOT.glob("docs/*.md")
        if path.name != "README.md" and path.name not in index
    ]
    assert not missing, f"docs/README.md does not link: {missing}"


def test_docs_index_links_every_concept_note():
    index = DOCS_INDEX.read_text(encoding="utf-8")
    missing = [path.name for path in REPO_ROOT.glob("docs/concepts/*.md") if path.name not in index]
    assert not missing, f"docs/README.md does not link: {missing}"
