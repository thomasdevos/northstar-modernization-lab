#!/usr/bin/env python3
"""Turn observed legacy behaviour into a small, reviewable claim record."""

import csv
import hashlib
import subprocess
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
    with INPUT.open(encoding="utf-8", newline="") as stream:
        input_rows = sum(1 for _ in csv.DictReader(stream))
    revision = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    tracked_changes = bool(
        subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    )
    fixture_digest = hashlib.sha256(INPUT.read_bytes()).hexdigest()
    golden_digest = hashlib.sha256(GOLDEN.read_bytes()).hexdigest()
    claim = ROOT / "evidence/claims/characterization.md"
    claim.write_text(
        "# Characterization evidence\n\n"
        f"- Fixture: `{INPUT.relative_to(ROOT)}`\n"
        f"- Fixture SHA-256: `{fixture_digest}`\n"
        f"- Golden-master SHA-256: `{golden_digest}`\n"
        f"- Source revision: `{revision}`\n"
        f"- Tracked working-tree changes present: {'yes' if tracked_changes else 'no'}\n"
        f"- Observed records: {count} from {input_rows} input rows (duplicate suppressed)\n"
        "- Fee: max(GBP 0.35, 0.15%), rounded half-up to pennies\n"
        "- Dates: weekends and configured UK holidays roll forward\n"
        "- Observation scope: "
        f"{count} emitted records from `{INPUT.relative_to(ROOT)}` at revision `{revision}`; "
        "no claim of production representativeness\n",
        encoding="utf-8",
    )
    print(f"CHARACTERIZE PASS: wrote {claim.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
