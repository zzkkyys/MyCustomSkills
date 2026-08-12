#!/usr/bin/env python3
"""Check a Marp PNG sequence for page count, numbering, and dimensions."""

from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path, help="Source Marp Markdown deck")
    parser.add_argument(
        "--output",
        type=Path,
        help="Image-sequence output base; defaults to <deck-stem>-pages.png",
    )
    parser.add_argument("--width", type=int, default=1280, help="Expected PNG width")
    parser.add_argument("--height", type=int, default=720, help="Expected PNG height")
    return parser.parse_args()


def slide_count(deck: Path) -> int:
    text = deck.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.search(text)
    body = text[match.end() :] if match else text
    return len(re.split(r"(?m)^---\s*$", body))


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise ValueError("not a valid PNG with an IHDR header")
    return struct.unpack(">II", header[16:24])


def main() -> int:
    args = parse_args()
    deck = args.deck.expanduser().resolve()
    if not deck.is_file():
        print(f"ERROR: deck not found: {deck}")
        return 2

    output = (
        args.output.expanduser().resolve()
        if args.output
        else deck.with_name(f"{deck.stem}-pages.png").resolve()
    )
    images = sorted(output.parent.glob(f"{output.stem}.*{output.suffix}"))
    expected_count = slide_count(deck)
    errors: list[str] = []

    if len(images) != expected_count:
        errors.append(f"expected {expected_count} PNG pages, found {len(images)}")

    for expected_number, image in enumerate(images, start=1):
        match = re.search(r"\.(\d+)\.png$", image.name, re.IGNORECASE)
        if not match or int(match.group(1)) != expected_number:
            errors.append(f"unexpected page numbering: {image.name}")
        try:
            dimensions = png_dimensions(image)
        except ValueError as exc:
            errors.append(f"{image.name}: {exc}")
            continue
        if dimensions != (args.width, args.height):
            errors.append(
                f"{image.name}: expected {args.width}x{args.height}, got {dimensions[0]}x{dimensions[1]}"
            )

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"OK: {len(images)} PNG pages at {args.width}x{args.height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
