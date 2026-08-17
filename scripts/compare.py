#!/usr/bin/env python3
"""Run old and new implementations through the same boundary and diff bytes."""

import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from legacy_app import run_batch as run_legacy
from replacement_service import run_batch as run_replacement
from scripts._paths import INPUT, RUNS


def compare() -> list[str]:
    legacy_output = RUNS / "compare-legacy.csv"
    replacement_output = RUNS / "compare-replacement.csv"
    run_legacy(INPUT, legacy_output)
    run_replacement(INPUT, replacement_output)
    old_bytes = legacy_output.read_bytes()
    new_bytes = replacement_output.read_bytes()
    if old_bytes == new_bytes:
        return []
    old = old_bytes.decode("utf-8").splitlines(keepends=True)
    new = new_bytes.decode("utf-8").splitlines(keepends=True)
    differences = list(difflib.unified_diff(old, new, fromfile="legacy", tofile="replacement"))
    return differences or ["Binary or newline-level output difference detected\n"]


def main() -> int:
    differences = compare()
    if differences:
        print("COMPARE FAIL: replacement differs from legacy")
        sys.stdout.writelines(differences)
        return 1
    print("COMPARE PASS: replacement matches legacy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
