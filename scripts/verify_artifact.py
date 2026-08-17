#!/usr/bin/env python3
"""Verify that a lab artifact exists, is non-empty, and contains tokens."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXIT_OK = 0
EXIT_INVALID = 2
EXIT_MISSING = 3
EXIT_EMPTY = 4
EXIT_TOKEN = 5


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("path", type=Path, help="expected file or directory inside this lab")
    result.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="TOKEN",
        help="literal field name or token required in file content; repeatable",
    )
    return result


def _contained(path: Path, root: Path) -> Path | None:
    resolved = path.resolve()
    base = root.resolve()
    return resolved if resolved.is_relative_to(base) else None


def verify(path: Path, required: list[str], root: Path = ROOT) -> tuple[int, str]:
    try:
        resolved = _contained(path, root)
    except OSError as exc:
        return EXIT_INVALID, f"UNREADABLE PATH: {path}: {exc}"
    if resolved is None:
        return EXIT_INVALID, f"OUTSIDE LAB: {path}"
    if not resolved.exists():
        return EXIT_MISSING, f"MISSING: {path}"
    if resolved.is_dir():
        try:
            files: list[Path] = []
            for item in resolved.rglob("*"):
                target = _contained(item, root)
                if target is None:
                    return EXIT_INVALID, f"OUTSIDE LAB SYMLINK: {item}"
                if target.is_file():
                    files.append(target)
            unique_files = sorted(set(files))
            if not unique_files or not any(item.stat().st_size for item in unique_files):
                return EXIT_EMPTY, f"EMPTY DIRECTORY: {path}"
        except OSError as exc:
            return EXIT_INVALID, f"UNREADABLE DIRECTORY: {path}: {exc}"
        if required:
            return EXIT_INVALID, "--require is valid only for a file artifact"
        return EXIT_OK, f"ARTIFACT PASS: {path} ({len(unique_files)} files)"
    if not resolved.is_file():
        return EXIT_INVALID, f"UNSUPPORTED PATH TYPE: {path}"
    try:
        data = resolved.read_bytes()
    except OSError as exc:
        return EXIT_INVALID, f"UNREADABLE: {path}: {exc}"
    if not data:
        return EXIT_EMPTY, f"EMPTY FILE: {path}"
    text = data.decode("utf-8", errors="replace")
    missing = [token for token in required if token not in text]
    if missing:
        return EXIT_TOKEN, f"MISSING TOKENS: {', '.join(missing)}"
    return EXIT_OK, f"ARTIFACT PASS: {path} ({len(data)} bytes)"


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if any(not token for token in args.require):
        parser().error("--require tokens must not be empty")
    code, message = verify(args.path, args.require)
    stream = sys.stdout if code == EXIT_OK else sys.stderr
    print(message, file=stream)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
