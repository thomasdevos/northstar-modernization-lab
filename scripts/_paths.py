from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "fixtures/synthetic/settlements.csv"
GOLDEN = ROOT / "fixtures/golden-master/settlements.expected.csv"
RUNS = ROOT / "evidence/runs"
