# Decision 0001: retain the initial rounding mismatch

**Status:** teaching baseline

The replacement intentionally uses `ROUND_HALF_EVEN`; legacy observations establish `ROUND_HALF_UP`. The GBP 670.00 fixture creates a GBP 1.005 fee and makes the difference visible (GBP 1.00 versus GBP 1.01). We retain the mismatch at the lab's starting revision so the differential gate has consequential work to find. The reader should correct replacement behaviour, not alter legacy or golden-master evidence.
