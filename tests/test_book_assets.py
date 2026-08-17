import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_book_assets import (
    AssetValidationError,
    MANIFEST,
    ROOT,
    contained_path,
    validate_book_assets,
)


class ValidateBookAssetsTests(unittest.TestCase):
    def test_all_book_assets_validate(self):
        count, statuses = validate_book_assets()
        self.assertEqual(70, count)
        self.assertEqual(41, statuses["executable"])
        self.assertEqual(29, statuses["illustrative"])

    def test_path_escape_and_symlink_are_rejected(self):
        for value in ("../secret", "/tmp/secret"):
            with self.assertRaisesRegex(AssetValidationError, "escapes allowed directory"):
                contained_path(ROOT, value)
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            outside = root / "outside.json"
            outside.write_text("{}", encoding="utf-8")
            listings = root / "listings"
            listings.mkdir()
            (listings / "alias.json").symlink_to(outside)
            with self.assertRaisesRegex(AssetValidationError, "contains a symlink"):
                contained_path(listings, "alias.json")

    def test_checksum_drift_is_rejected(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["listings"][0]["asset"]["sha256"] = "0" * 64
        with TemporaryDirectory() as root_name:
            changed = Path(root_name) / "manifest.json"
            changed.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(AssetValidationError, "SHA-256 mismatch"):
                validate_book_assets(manifest_path=changed)


if __name__ == "__main__":
    unittest.main()
