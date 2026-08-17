#!/usr/bin/env python3
"""Aggregate the lab gates; comparator failure is intentional at the starting state."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> int:
    completed = subprocess.run(args, cwd=ROOT, check=False)
    return completed.returncode


def main() -> int:
    results = [
        run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"),
        run(sys.executable, "scripts/baseline.py"),
        run(sys.executable, "scripts/compare.py"),
    ]
    if any(results):
        print(f"VERIFY FAIL: gate exit codes={results}")
        return 1
    print("VERIFY PASS: all gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
