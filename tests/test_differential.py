import unittest

from scripts.compare import compare


class DifferentialHarnessTests(unittest.TestCase):
    def test_starting_state_exposes_known_gap(self):
        differences = "".join(compare())
        self.assertIn("STL-1002,670.00,1.01,668.99", differences)
        self.assertIn("STL-1002,670.00,1.00,669.00", differences)


if __name__ == "__main__":
    unittest.main()
