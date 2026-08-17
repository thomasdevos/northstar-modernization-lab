#!/usr/bin/env python3
"""Execute the legacy CSV boundary and check its retained golden master."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from legacy_app import run_batch
from scripts._paths import GOLDEN, INPUT, RUNS


def main() -> int:
    actual = RUNS / "latest-baseline.csv"
    count = run_batch(INPUT, actual)
    if actual.read_bytes() != GOLDEN.read_bytes():
        print(f"BASELINE FAIL: {actual} differs from {GOLDEN}")
        return 1
    print(f"BASELINE PASS: {count} records match {GOLDEN.relative_to(GOLDEN.parents[2])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
