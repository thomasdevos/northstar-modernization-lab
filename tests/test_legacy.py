import csv
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from legacy_app.settlement import process, run_batch, settle


class LegacySettlementTests(unittest.TestCase):
    def test_minimum_fee(self):
        self.assertEqual("0.35", settle({"settlement_id": "x", "amount_gbp": "100", "requested_date": "2026-07-24"})["fee_gbp"])

    def test_half_penny_rounds_away_from_zero(self):
        self.assertEqual("1.01", settle({"settlement_id": "x", "amount_gbp": "670", "requested_date": "2026-07-24"})["fee_gbp"])

    def test_weekend_rolls_to_monday(self):
        record = settle({"settlement_id": "x", "amount_gbp": "100", "requested_date": "2026-07-25"})
        self.assertEqual("2026-07-27", record["settlement_date"])

    def test_holiday_rolls_to_next_business_day(self):
        record = settle({"settlement_id": "x", "amount_gbp": "100", "requested_date": "2026-08-31"})
        self.assertEqual("2026-09-01", record["settlement_date"])

    def test_duplicate_id_is_idempotent_first_wins(self):
        rows = [
            {"settlement_id": "same", "amount_gbp": "100", "requested_date": "2026-07-24"},
            {"settlement_id": "same", "amount_gbp": "999", "requested_date": "2026-07-24"},
        ]
        result = process(rows)
        self.assertEqual(1, len(result))
        self.assertEqual("100.00", result[0]["gross_gbp"])


if __name__ == "__main__":
    unittest.main()
