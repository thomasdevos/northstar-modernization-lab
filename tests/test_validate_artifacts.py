import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_artifacts import ValidationError, load_data, validate, validate_registered


class ValidateArtifactsTests(unittest.TestCase):
    def test_registered_artifacts_validate(self):
        self.assertEqual((2, 1), validate_registered())

    def test_schema_rejects_missing_required_key(self):
        with self.assertRaisesRegex(ValidationError, "missing required"):
            validate({}, {"type": "object", "required": ["owner"]})

    def test_json_compatible_yaml_is_supported_offline(self):
        with TemporaryDirectory() as root:
            path = Path(root) / "record.yaml"
            path.write_text(json.dumps({"owner": "human"}), encoding="utf-8")
            self.assertEqual({"owner": "human"}, load_data(path, "yaml-json-subset"))

    def test_broader_yaml_is_rejected_honestly(self):
        with TemporaryDirectory() as root:
            path = Path(root) / "record.yaml"
            path.write_text("owner: human\n", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "JSON-compatible YAML"):
                load_data(path, "yaml-json-subset")


if __name__ == "__main__":
    unittest.main()
