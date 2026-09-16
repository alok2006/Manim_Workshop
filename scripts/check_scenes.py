#!/usr/bin/env python3
"""Pre-flight checks for every scene in the workshop.

Three levels of "does it work", cheapest first:

| Command                          | What it proves                                  | Cost |
|----------------------------------|-------------------------------------------------|------|
| ``check_scenes.py``              | every module parses, every scene is documented  | <1 s |
| ``check_scenes.py --dry-run``    | every scene **executes** (Manim builds all frames, writes no video) | seconds |
| ``check_scenes.py --render``     | every scene produces a real ``.mp4``            | minutes |

Examples
--------
List the catalogue with copy-pasteable commands::

    python scripts/check_scenes.py --list

Verify the whole workshop before committing (this is what CI runs)::

    python scripts/check_scenes.py --dry-run

Render everything at low quality, four scenes at a time::

    python scripts/check_scenes.py --render --quality l --jobs 4

Refresh the committed previews (see ``videos/README.md``)::

    python scripts/check_scenes.py --render --quality l --publish videos

Re-check a single scene while iterating on it::

    python scripts/check_scenes.py --dry-run --only FourierEpicycle

Exit codes: ``0`` everything passed, ``1`` at least one failure, ``2`` bad usage.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Running this file directly must work in a fresh clone, before
# `pip install -e .` has been run, so put the repository root on sys.path first.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim_workshop.catalog import (  # noqa: E402
    LEGACY_SCENE_NAMES,
    SCENE_FILE_PATTERN,
    SceneInfo,
    all_scenes,
    module_docstring,
    scene_files,
)
from manim_workshop.runner import (  # noqa: E402
    MANIM_QUALITIES,
    SceneRun,
    find_rendered_video,
    run_scene,
)

DEFAULT_JOBS = 4
"""Scenes are rendered in parallel; each is single-threaded, so this is a floor, not a limit."""

LEGACY_TYPOS = ("Sqaure", "cirlce", "WIth", "Epicyle", "outine", "Sqto", "ANDT")


class Palette:
    """Minimal ANSI colouring that disables itself when not on a terminal."""

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def _wrap(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.enabled else text

    def bold(self, text: str) -> str:
        return self._wrap("1", text)

    def green(self, text: str) -> str:
        return self._wrap("32", text)

    def red(self, text: str) -> str:
        return self._wrap("31", text)

    def yellow(self, text: str) -> str:
        return self._wrap("33", text)

    def dim(self, text: str) -> str:
        return self._wrap("2", text)


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #
def static_problems() -> list[str]:
    """Everything that can be checked by reading files: parse, names, docstrings."""
    problems: list[str] = []

    files = scene_files()
    if not files:
        return [f"no scene modules matched {SCENE_FILE_PATTERN!r} in scenes/"]

    for path in files:
        if not module_docstring(path):
            problems.append(f"{path.name}: missing module docstring")

    scenes = all_scenes()
    seen: dict[str, str] = {}
    for scene in scenes:
        if scene.name in seen:
            problems.append(
                f"{scene.name}: defined twice ({seen[scene.name]} and {scene.relative_path})"
            )
        seen[scene.name] = scene.relative_path

        if not scene.docstring:
            problems.append(f"{scene.name}: missing class docstring")

        for typo in LEGACY_TYPOS:
            if typo in scene.name:
                problems.append(f"{scene.name}: still contains the legacy typo {typo!r}")

    # The old→new table is the migration path for anyone with older slides.
    mapped = set(LEGACY_SCENE_NAMES.values())
    current = set(seen)
    if mapped != current:
        missing = sorted(current - mapped)
        if missing:
            problems.append(f"not in LEGACY_SCENE_NAMES: {', '.join(missing)}")
        stale = sorted(mapped - current)
        if stale:
            problems.append(
                f"LEGACY_SCENE_NAMES points at scenes that no longer exist: {', '.join(stale)}"
            )

    return problems


def run_scenes(
    scenes: list[SceneInfo],
    *,
    dry_run: bool,
    quality: str,
    jobs: int,
    timeout: int,
    palette: Palette,
    media_dir: Path | None = None,
    progress: bool = True,
) -> list[SceneRun]:
    """Execute ``scenes`` (dry-run or for real) with a bounded thread pool."""
    results: list[SceneRun] = []
    total = len(scenes)

    def worker(scene: SceneInfo) -> SceneRun:
        return run_scene(
            scene, quality=quality, dry_run=dry_run, timeout=timeout, media_dir=media_dir
        )

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for index, result in enumerate(pool.map(worker, scenes), start=1):
            results.append(result)
            if progress:
                status = palette.green("ok  ") if result.ok else palette.red("FAIL")
                print(
                    f"  [{index:>2}/{total}] {status} {result.scene.name:<38} {result.duration:6.1f}s",
                    flush=True,
                )
    return results


# --------------------------------------------------------------------------- #
# presentation
# --------------------------------------------------------------------------- #
def print_catalogue(scenes: list[SceneInfo], palette: Palette) -> None:
    print(palette.bold(f"{len(scenes)} scenes across {len(scene_files())} stages\n"))
    stage = None
    for scene in scenes:
        if scene.stage != stage:
            stage = scene.stage
            print(palette.bold(f"  {stage}"))
        print(f"    {scene.name:<38} {palette.dim(scene.render_command())}")
    print()


def print_static_report(problems: list[str], palette: Palette, scenes: list[SceneInfo]) -> None:
    print(palette.bold("Static checks"))
    print(f"  scene modules : {len(scene_files())}")
    print(f"  scene classes : {len(scenes)}")
    if problems:
        print(palette.red(f"  problems      : {len(problems)}"))
        for problem in problems:
            print(palette.red(f"    - {problem}"))
    else:
        print(palette.green("  problems      : none"))


def publish_videos(
    runs: list[SceneRun],
    *,
    destination: Path,
    quality: str,
    media_dir: Path | None,
    palette: Palette,
) -> tuple[int, int]:
    """Copy each successful run's video into ``destination`` (flat layout).

    Only scenes that *just* rendered successfully are copied, so a failure can
    never publish a stale file over a good one. Returns ``(copied, missing)``.
    """
    destination.mkdir(parents=True, exist_ok=True)
    copied = 0
    missing = 0

    for run in runs:
        video = find_rendered_video(run.scene, quality=quality, media_dir=media_dir)
        if video is None:
            print(palette.red(f"    no video found for {run.scene.name} — not published"))
            missing += 1
            continue
        shutil.copy2(video, destination / f"{run.scene.name}.mp4")
        copied += 1

    return copied, missing


def print_run_summary(results: list[SceneRun], palette: Palette, dry_run: bool) -> None:
    failures = [run for run in results if not run.ok]
    mode = "dry-run" if dry_run else "render"
    print()
    print(palette.bold(f"{mode} summary: {len(results) - len(failures)}/{len(results)} passed"))
    for run in failures:
        print(palette.red(f"\n  {run.scene.name} ({run.scene.relative_path}:{run.scene.lineno})"))
        tail = run.output.strip().splitlines()[-15:]
        for line in tail:
            print(f"    {line}")


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="check_scenes.py",
        description="Verify that every scene in the workshop compiles, runs and renders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples")[1] if __doc__ and "Examples" in __doc__ else None,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="execute every scene without writing video (the real compile check)",
    )
    mode.add_argument("--render", action="store_true", help="render every scene to video")
    parser.add_argument(
        "--list", action="store_true", help="print the catalogue with render commands and exit"
    )
    parser.add_argument(
        "--quality", default="l", choices=MANIM_QUALITIES, help="render quality (default: l)"
    )
    parser.add_argument("--only", default="", help="comma-separated scene names to restrict to")
    parser.add_argument(
        "--jobs", type=int, default=DEFAULT_JOBS, help=f"parallel workers (default: {DEFAULT_JOBS})"
    )
    parser.add_argument(
        "--timeout", type=int, default=900, help="per-scene timeout in seconds (default: 900)"
    )
    parser.add_argument(
        "--json", dest="json_path", default=None, help="also write a machine-readable report here"
    )
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colours")
    parser.add_argument(
        "--media-dir",
        default=None,
        help="Manim scratch directory (default: <repo>/media)",
    )
    parser.add_argument(
        "--publish",
        default=None,
        metavar="DIR",
        help="copy every successfully rendered video into DIR (refreshes videos/)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    palette = Palette(enabled=not args.no_color and sys.stdout.isatty())

    scenes = all_scenes()
    if args.only:
        wanted = {name.strip() for name in args.only.split(",") if name.strip()}
        known = {scene.name for scene in scenes}
        unknown = wanted - known
        if unknown:
            print(palette.red(f"unknown scene(s): {', '.join(sorted(unknown))}"), file=sys.stderr)
            print(f"known scenes: {', '.join(sorted(known))}", file=sys.stderr)
            return 2
        scenes = [scene for scene in scenes if scene.name in wanted]

    if args.list:
        print_catalogue(scenes, palette)
        return 0

    problems = static_problems()
    print_static_report(problems, palette, scenes)

    report: dict[str, object] = {
        "scenes": len(scenes),
        "modules": len(scene_files()),
        "static_problems": problems,
        "runs": [],
    }

    exit_code = 1 if problems else 0

    if args.dry_run or args.render:
        print()
        mode = "dry-run" if args.dry_run else f"render -q{args.quality}"
        print(palette.bold(f"Running {len(scenes)} scenes ({mode}), {args.jobs} at a time"))
        started = time.monotonic()
        results = run_scenes(
            scenes,
            dry_run=args.dry_run,
            quality=args.quality,
            jobs=max(1, args.jobs),
            timeout=args.timeout,
            palette=palette,
            media_dir=Path(args.media_dir) if args.media_dir else None,
        )
        print_run_summary(results, palette, dry_run=args.dry_run)
        print(f"\n  total wall time: {time.monotonic() - started:.1f}s")
        report["runs"] = [
            {
                "scene": run.scene.name,
                "file": run.scene.relative_path,
                "mode": "dry-run" if run.dry_run else "render",
                "ok": run.ok,
                "returncode": run.returncode,
            }
            for run in results
        ]
        if any(not run.ok for run in results):
            exit_code = 1

        if args.publish and not args.dry_run:
            published, skipped = publish_videos(
                [run for run in results if run.ok],
                destination=Path(args.publish),
                quality=args.quality,
                media_dir=Path(args.media_dir) if args.media_dir else None,
                palette=palette,
            )
            print(
                f"\n  published {published} video(s) to {args.publish}"
                + (f", {skipped} missing" if skipped else "")
            )
            if skipped:
                exit_code = 1

    if args.json_path:
        Path(args.json_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"  report written to {args.json_path}")

    print()
    if exit_code == 0:
        print(palette.green("all checks passed"))
    else:
        print(palette.red("checks FAILED"))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
