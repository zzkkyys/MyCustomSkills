#!/usr/bin/env python3
"""Render a trusted Marp deck with the bundled blue theme."""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
from pathlib import Path


FORMATS = ("html", "pdf", "pptx", "png", "images")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path, help="Marp Markdown deck")
    parser.add_argument("--format", choices=FORMATS, default="html")
    parser.add_argument("--output", type=Path, help="Output path")
    parser.add_argument("--theme", type=Path, help="Theme CSS; defaults to ./themes/blue.css")
    parser.add_argument("--marp-command", type=Path, help="Path to Marp CLI; defaults to marp on PATH")
    parser.add_argument("--trusted", action="store_true", help="Confirm the deck is trusted before enabling HTML")
    parser.add_argument("--allow-local-files", action="store_true", help="Allow trusted local assets during conversion")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output; image sequences may retain stale extra pages",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the Marp command without executing it")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    deck = args.deck.expanduser().resolve()
    if not deck.is_file():
        raise SystemExit(f"Deck not found: {deck}")
    if not args.trusted and not args.dry_run:
        raise SystemExit("Refusing to enable HTML for an unconfirmed deck. Re-run with --trusted.")

    theme = (args.theme or deck.parent / "themes" / "blue.css").expanduser().resolve()
    if not theme.is_file():
        raise SystemExit(f"Theme not found: {theme}")
    if args.output:
        output = args.output.expanduser().resolve()
    elif args.format == "images":
        output = deck.with_name(f"{deck.stem}-pages.png").resolve()
    else:
        output = deck.with_suffix(f".{args.format}").resolve()

    conflicts = [output]
    if args.format == "images":
        conflicts = sorted(output.parent.glob(f"{output.stem}.*{output.suffix}"))
    conflicts = [path for path in conflicts if path.exists()]
    if conflicts and not args.force and not args.dry_run:
        rendered = "\n".join(f"- {path}" for path in conflicts)
        raise SystemExit(
            f"Refusing to overwrite existing output:\n{rendered}\nRe-run with --force."
        )

    marp = str(args.marp_command.expanduser().resolve()) if args.marp_command else shutil.which("marp")
    if marp and not Path(marp).is_file():
        raise SystemExit(f"Marp CLI not found: {marp}")
    if not marp and not args.dry_run:
        raise SystemExit("Marp CLI is not installed or not available on PATH")
    command = [marp or "marp", "--theme-set", str(theme), "--html"]
    if args.allow_local_files:
        command.append("--allow-local-files")
    if args.format == "pdf":
        command.append("--pdf")
    elif args.format == "pptx":
        command.append("--pptx")
    elif args.format == "png":
        command.extend(["--image", "png"])
    elif args.format == "images":
        command.extend(["--images", "png"])
    command.extend([str(deck), "-o", str(output)])

    print(shlex.join(command))
    if args.dry_run:
        return 0
    try:
        subprocess.run(command, check=True, cwd=deck.parent)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Marp CLI failed with exit code {exc.returncode}") from exc
    print(f"Rendered: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
