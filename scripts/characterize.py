#!/usr/bin/env python3
"""Turn observed legacy behaviour into a small, reviewable claim record."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from legacy_app import run_batch
from scripts._paths import GOLDEN, INPUT, ROOT, RUNS


def main() -> int:
    observed = RUNS / "latest-characterization.csv"
    count = run_batch(INPUT, observed)
    if observed.read_bytes() != GOLDEN.read_bytes():
        print("CHARACTERIZE FAIL: observation does not match retained golden master")
        return 1
    claim = ROOT / "evidence/claims/characterization.md"
    claim.write_text(
        "# Characterization evidence\n\n"
        f"- Fixture: `{INPUT.relative_to(ROOT)}`\n"
        f"- Observed records: {count} from 5 input rows (duplicate suppressed)\n"
        "- Fee: max(GBP 0.35, 0.15%), rounded half-up to pennies\n"
        "- Dates: weekends and configured UK holidays roll forward\n"
        "- Observation scope: "
        f"{count} emitted records from `{INPUT.relative_to(ROOT)}` at the recorded revision; "
        "no claim of production representativeness\n",
        encoding="utf-8",
    )
    print(f"CHARACTERIZE PASS: wrote {claim.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
