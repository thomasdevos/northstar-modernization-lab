from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.verify_artifact import (
    EXIT_EMPTY, EXIT_INVALID, EXIT_MISSING, EXIT_OK, EXIT_TOKEN, verify,
)


class VerifyArtifactTests(unittest.TestCase):
    def test_missing_path(self):
        code, _ = verify(Path("does-not-exist"), [])
        self.assertEqual(EXIT_MISSING, code)

    def test_empty_file(self):
        with TemporaryDirectory() as root:
            path = Path(root) / "empty.md"
            path.touch()
            self.assertEqual(EXIT_EMPTY, verify(path, [])[0])

    def test_file_and_required_tokens(self):
        with TemporaryDirectory() as root:
            path = Path(root) / "record.md"
            path.write_text("owner: human\ndecision: blocked\n", encoding="utf-8")
            self.assertEqual(EXIT_OK, verify(path, ["owner", "decision"])[0])
            self.assertEqual(EXIT_TOKEN, verify(path, ["revision"])[0])

    def test_non_empty_directory(self):
        with TemporaryDirectory() as root:
            path = Path(root) / "evidence"
            path.mkdir()
            (path / "record.txt").write_text("record", encoding="utf-8")
            self.assertEqual(EXIT_OK, verify(path, [])[0])
            self.assertEqual(EXIT_INVALID, verify(path, ["record"])[0])

    def test_empty_directory(self):
        with TemporaryDirectory() as root:
            path = Path(root) / "evidence"
            path.mkdir()
            self.assertEqual(EXIT_EMPTY, verify(path, [])[0])


if __name__ == "__main__":
    unittest.main()