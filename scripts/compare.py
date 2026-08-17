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
    old = legacy_output.read_text(encoding="utf-8").splitlines(keepends=True)
    new = replacement_output.read_text(encoding="utf-8").splitlines(keepends=True)
    return list(difflib.unified_diff(old, new, fromfile="legacy", tofile="replacement"))


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
