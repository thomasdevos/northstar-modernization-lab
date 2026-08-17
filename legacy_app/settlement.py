"""Small legacy core: behaviour is intentional, documentation is not."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable

FIELDS = ("settlement_id", "gross_gbp", "fee_gbp", "net_gbp", "requested_date", "settlement_date", "status")
PENNY = Decimal("0.01")
HOLIDAYS = {date(2026, 8, 31), date(2026, 12, 25), date(2026, 12, 28)}


def _money(value: Decimal) -> str:
    return str(value.quantize(PENNY, rounding=ROUND_HALF_UP))


def _business_day(value: date) -> date:
    while value.weekday() >= 5 or value in HOLIDAYS:
        value += timedelta(days=1)
    return value


def settle(row: dict[str, str]) -> dict[str, str]:
    amount = Decimal(row["amount_gbp"])
    if amount <= 0:
        raise ValueError("amount_gbp must be positive")
    requested = date.fromisoformat(row["requested_date"])
    fee = max(Decimal("0.35"), amount * Decimal("0.0015")).quantize(PENNY, rounding=ROUND_HALF_UP)
    return {
        "settlement_id": row["settlement_id"],
        "gross_gbp": _money(amount),
        "fee_gbp": _money(fee),
        "net_gbp": _money(amount - fee),
        "requested_date": requested.isoformat(),
        "settlement_date": _business_day(requested).isoformat(),
        "status": "SETTLED",
    }


def process(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    """First occurrence wins; duplicate settlement IDs produce no second effect."""
    seen: set[str] = set()
    output = []
    for row in rows:
        key = row["settlement_id"]
        if key in seen:
            continue
        seen.add(key)
        output.append(settle(row))
    return output


def run_batch(source: Path, destination: Path) -> int:
    with source.open(newline="", encoding="utf-8") as handle:
        rows = process(csv.DictReader(handle))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
