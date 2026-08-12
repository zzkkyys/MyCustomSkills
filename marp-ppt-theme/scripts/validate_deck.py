#!/usr/bin/env python3
"""Statically validate a deck that uses the bundled Marp blue theme."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
CLASS_RE = re.compile(r'class="([^"]+)"')
PAGE_CLASS_RE = re.compile(r"<!--\s*_class:\s*([^>]+?)\s*-->")
LOCAL_IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?!https?://)([^)\s]+)(?:\s+['\"].*?['\"])?\)")
REMOTE_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(https?://", re.IGNORECASE)
LEGACY_BACKGROUND_RE = re.compile(r"!\[background(?:\s+[^\]]*)?\]\(", re.IGNORECASE)
NATIVE_BACKGROUND_RE = re.compile(r"!\[bg(?:\s+[^\]]*)?\]\(", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path, help="Marp Markdown deck")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    return parser.parse_args()


def parse_frontmatter(block: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def strip_code_examples(text: str) -> str:
    """Mask fenced and inline code so examples are not treated as live markup."""
    output: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            output.append("")
            continue
        if in_fence:
            output.append("")
        else:
            output.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(output)


def split_slides(text: str, frontmatter_match: re.Match[str] | None) -> list[str]:
    body = text[frontmatter_match.end() :] if frontmatter_match else text
    return re.split(r"(?m)^---\s*$", body)


def main() -> int:
    args = parse_args()
    deck = args.deck.expanduser().resolve()
    if not deck.is_file():
        print(f"ERROR: deck not found: {deck}")
        return 2

    text = deck.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    frontmatter_match = FRONTMATTER_RE.search(text)
    if not frontmatter_match:
        errors.append("missing YAML frontmatter")
        frontmatter = {}
    else:
        frontmatter = parse_frontmatter(frontmatter_match.group(1))
    if frontmatter.get("marp", "").lower() != "true":
        errors.append("frontmatter must contain 'marp: true'")
    if frontmatter.get("theme") != "blue":
        errors.append("frontmatter must contain 'theme: blue'")
    if frontmatter.get("size") != "16:9":
        warnings.append("add 'size: 16:9' for deterministic layout")

    theme = deck.parent / "themes" / "blue.css"
    if not theme.is_file():
        errors.append(f"theme not found: {theme}")
        css = ""
    else:
        css = theme.read_text(encoding="utf-8")

    live_text = strip_code_examples(text)
    live_slides = split_slides(live_text, FRONTMATTER_RE.search(live_text))
    if REMOTE_IMAGE_RE.search(live_text):
        warnings.append("deck contains remote images and is not fully offline")
    if LEGACY_BACKGROUND_RE.search(live_text):
        errors.append("use Marp native background syntax '![bg contain](...)', not '![background](...)'")
    for raw_path in LOCAL_IMAGE_RE.findall(live_text):
        clean_path = unquote(raw_path.split("#", 1)[0].split("?", 1)[0])
        if clean_path and not (deck.parent / clean_path).is_file():
            errors.append(f"missing local image: {raw_path}")

    lines = live_text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if re.fullmatch(r"<div(?:\s+[^>]*)?>", stripped):
            next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
            if next_line and not next_line.startswith("<"):
                errors.append(f"line {index + 1}: add a blank line after opening <div>")
        previous_line = lines[index - 1].strip() if index > 0 else ""
        if stripped == "</div>" and previous_line and not previous_line.endswith(">"):
            errors.append(f"line {index + 1}: add a blank line before closing </div>")

    if css:
        css_classes = set(re.findall(r"\.([A-Za-z_][A-Za-z0-9_-]*)", css))
        used_classes = {
            token
            for value in CLASS_RE.findall(live_text)
            for token in value.split()
        }
        used_classes.update(
            token
            for value in PAGE_CLASS_RE.findall(live_text)
            for token in value.split()
        )
        for class_name in sorted(used_classes - css_classes):
            errors.append(f"class not defined by theme: {class_name}")

    if len(live_slides) < 2:
        warnings.append("deck contains fewer than two slides")

    for slide_number, slide in enumerate(live_slides, start=1):
        classes = {
            token
            for value in PAGE_CLASS_RE.findall(slide)
            for token in value.split()
        }
        heading_match = re.search(r"(?m)^#\s+(.+?)\s*$", slide)
        if heading_match and "title" not in classes:
            heading = re.sub(r"<[^>]+>", "", heading_match.group(1)).strip()
            if len(heading) > 32 and "long-title" not in classes:
                warnings.append(
                    f"slide {slide_number}: long H1 ({len(heading)} characters); add page class 'long-title'"
                )
            if len(heading) > 54:
                warnings.append(
                    f"slide {slide_number}: H1 is very long ({len(heading)} characters); shorten it if possible"
                )
        if classes.intersection({"image-slide", "full-image"}):
            if not NATIVE_BACKGROUND_RE.search(slide):
                errors.append(
                    f"slide {slide_number}: image-slide requires Marp native '![bg contain](...)' syntax"
                )
            if "full-image" in classes:
                warnings.append(
                    f"slide {slide_number}: 'full-image' is a compatibility alias; prefer 'image-slide'"
                )

    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")
    if errors or (args.strict and warnings):
        return 1
    print(f"OK: {deck} ({len(live_slides)} slides)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
