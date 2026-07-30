#!/usr/bin/env python3
"""Repository-level validation that does not require audio hardware."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "lqp_hifi_rack_player.py"

REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "NOTICE",
    ROOT / "SECURITY.md",
    ROOT / "docs" / "es" / "MANUAL_USUARIO.md",
    ROOT / "docs" / "en" / "USER_MANUAL.md",
    ROOT / "screenshots" / "full-application.png",
    ROOT / "screenshots" / "ai-eq-auto.png",
]

SECRET_PATTERNS = [
    re.compile(r"nvapi-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)authorization\s*[:=]\s*[\"']?bearer\s+[A-Za-z0-9._-]{20,}"),
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_required_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        fail("Missing required files: " + ", ".join(missing))


def validate_python_syntax() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    compile(source, str(SOURCE), "exec")


def validate_no_secrets() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".zip"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"Potential secret found in {path.relative_to(ROOT)}")


def validate_markdown_images() -> None:
    image_pattern = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in image_pattern.findall(text):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                fail(f"Broken image reference in {path.relative_to(ROOT)}: {target}")


def main() -> None:
    validate_required_files()
    validate_python_syntax()
    validate_no_secrets()
    validate_markdown_images()
    print("Repository validation passed.")


if __name__ == "__main__":
    main()
