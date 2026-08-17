#!/usr/bin/env python3
"""Fail clearly when the lab is run with an unsupported Python version."""
from __future__ import annotations

import sys

MINIMUM = (3, 11)


def main() -> int:
    observed = sys.version_info[:3]
    if observed < MINIMUM:
        print(
            f"ENVIRONMENT FAIL: Python {MINIMUM[0]}.{MINIMUM[1]}+ required; "
            f"observed {observed[0]}.{observed[1]}.{observed[2]}",
            file=sys.stderr,
        )
        return 1
    print(f"ENVIRONMENT PASS: Python {observed[0]}.{observed[1]}.{observed[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
