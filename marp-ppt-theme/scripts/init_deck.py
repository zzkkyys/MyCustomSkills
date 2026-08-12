#!/usr/bin/env python3
"""Create a portable Marp deck from the bundled blue-theme template."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "project-template"
THEME_SETTING = "./themes/blue.css"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Target presentation directory")
    parser.add_argument("--deck-name", default="slides.md", help="Starter deck filename")
    parser.add_argument(
        "--include-demo",
        action="store_true",
        help="Also copy demo.md and visual-regression.md",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite bundled target files")
    return parser.parse_args()


def load_settings(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Cannot merge {path}: it is not strict JSON ({exc}). "
            "Merge markdown.marp.themes manually."
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Cannot merge {path}: top-level value must be an object")
    return value


def copy_file(source: Path, destination: Path, force: bool) -> None:
    if destination.exists() and not force:
        raise SystemExit(f"Refusing to overwrite existing file: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> int:
    args = parse_args()
    target = args.target.expanduser().resolve()
    deck_name = Path(args.deck_name)
    if deck_name.name != args.deck_name or deck_name.suffix.lower() != ".md":
        raise SystemExit("--deck-name must be a Markdown filename without directories")
    settings_path = target / ".vscode" / "settings.json"
    settings = load_settings(settings_path)

    themes = settings.get("markdown.marp.themes", [])
    if not isinstance(themes, list):
        raise SystemExit("markdown.marp.themes must be a JSON array")
    if THEME_SETTING not in themes:
        themes.append(THEME_SETTING)
    settings["markdown.marp.themes"] = themes

    planned: list[tuple[Path, Path]] = [
        (TEMPLATE_ROOT / "themes" / "blue.css", target / "themes" / "blue.css"),
        (TEMPLATE_ROOT / "slides.md", target / deck_name),
    ]
    for asset in sorted((TEMPLATE_ROOT / "assets").iterdir()):
        if asset.is_file():
            planned.append((asset, target / "assets" / asset.name))
    if args.include_demo:
        planned.extend(
            [
                (TEMPLATE_ROOT / "demo.md", target / "demo.md"),
                (
                    TEMPLATE_ROOT / "visual-regression.md",
                    target / "visual-regression.md",
                ),
            ]
        )

    conflicts = [destination for _, destination in planned if destination.exists()]
    if conflicts and not args.force:
        conflict_list = "\n".join(f"- {path}" for path in conflicts)
        raise SystemExit(f"Refusing to overwrite existing files:\n{conflict_list}")

    target.mkdir(parents=True, exist_ok=True)
    for source, destination in planned:
        copy_file(source, destination, args.force)

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Created Marp deck in {target}")
    print(f"Starter: {target / deck_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
