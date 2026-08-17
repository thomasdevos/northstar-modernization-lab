#!/usr/bin/env python3
"""Verify that a chapter artifact exists, is non-empty, and contains tokens."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_INVALID = 2
EXIT_MISSING = 3
EXIT_EMPTY = 4
EXIT_TOKEN = 5


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("path", type=Path, help="expected file or directory")
    result.add_argument(
        "--require", action="append", default=[], metavar="TOKEN",
        help="literal field name or token required in file content; repeatable",
    )
    return result


def verify(path: Path, required: list[str]) -> tuple[int, str]:
    if not path.exists():
        return EXIT_MISSING, f"MISSING: {path}"
    if path.is_dir():
        files = sorted(item for item in path.rglob("*") if item.is_file())
        if not files or not any(item.stat().st_size for item in files):
            return EXIT_EMPTY, f"EMPTY DIRECTORY: {path}"
        if required:
            return EXIT_INVALID, "--require is valid only for a file artifact"
        return EXIT_OK, f"ARTIFACT PASS: {path} ({len(files)} files)"
    if not path.is_file():
        return EXIT_INVALID, f"UNSUPPORTED PATH TYPE: {path}"
    try:
        data = path.read_bytes()
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