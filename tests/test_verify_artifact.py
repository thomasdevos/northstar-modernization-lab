from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.verify_artifact import (
    EXIT_EMPTY,
    EXIT_INVALID,
    EXIT_MISSING,
    EXIT_OK,
    EXIT_TOKEN,
    verify,
)


class VerifyArtifactTests(unittest.TestCase):
    def test_missing_path(self):
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            code, _ = verify(root / "does-not-exist", [], root)
            self.assertEqual(EXIT_MISSING, code)

    def test_empty_file(self):
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            path = root / "empty.md"
            path.touch()
            self.assertEqual(EXIT_EMPTY, verify(path, [], root)[0])

    def test_file_and_required_tokens(self):
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            path = root / "record.md"
            path.write_text("owner: human\ndecision: blocked\n", encoding="utf-8")
            self.assertEqual(EXIT_OK, verify(path, ["owner", "decision"], root)[0])
            self.assertEqual(EXIT_TOKEN, verify(path, ["revision"], root)[0])

    def test_non_empty_directory(self):
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            path = root / "evidence"
            path.mkdir()
            (path / "record.txt").write_text("record", encoding="utf-8")
            self.assertEqual(EXIT_OK, verify(path, [], root)[0])
            self.assertEqual(EXIT_INVALID, verify(path, ["record"], root)[0])

    def test_empty_directory(self):
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            path = root / "evidence"
            path.mkdir()
            self.assertEqual(EXIT_EMPTY, verify(path, [], root)[0])

    def test_outside_path_and_symlink_are_rejected(self):
        with TemporaryDirectory() as root_name, TemporaryDirectory() as outside_name:
            root = Path(root_name)
            outside = Path(outside_name) / "secret.txt"
            outside.write_text("not lab evidence", encoding="utf-8")
            self.assertEqual(EXIT_INVALID, verify(outside, [], root)[0])
            alias = root / "alias.txt"
            alias.symlink_to(outside)
            self.assertEqual(EXIT_INVALID, verify(alias, [], root)[0])


if __name__ == "__main__":
    unittest.main()
