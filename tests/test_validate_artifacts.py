import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_artifacts import (
    ValidationError,
    load_data,
    resolve_registered_path,
    validate,
    validate_registered,
    validate_schema_dialect,
)


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

    def test_non_finite_json_is_rejected(self):
        with TemporaryDirectory() as root:
            path = Path(root) / "record.json"
            path.write_text('{"value": NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "non-finite"):
                load_data(path, "json")

    def test_unsupported_schema_keyword_fails_closed(self):
        with self.assertRaisesRegex(ValidationError, "unsupported schema keywords"):
            validate("", {"type": "string", "minLength": 1})
        with self.assertRaisesRegex(ValidationError, "unsupported schema keywords"):
            validate(-1, {"type": "integer", "minimum": 0})
        with self.assertRaisesRegex(ValidationError, "unsupported schema keywords"):
            validate([1, 1], {"type": "array", "uniqueItems": True})

    def test_malformed_enum_and_type_declarations_fail_closed(self):
        for schema in (
            {"enum": "admin"},
            {"enum": None},
            {"enum": []},
            {"enum": [1, 1.0]},
            {"type": [{}]},
        ):
            with self.subTest(schema=schema):
                with self.assertRaises(ValidationError):
                    validate_schema_dialect(schema)

    def test_const_and_enum_do_not_confuse_booleans_with_numbers(self):
        for value, schema in (
            (True, {"const": 1}),
            (1, {"const": True}),
            (True, {"enum": [1]}),
        ):
            with self.subTest(value=value, schema=schema):
                with self.assertRaises(ValidationError):
                    validate(value, schema)
        validate(1.0, {"const": 1})

    def test_registered_paths_cannot_escape_root(self):
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            for value in ("../outside.json", "/tmp/outside.json"):
                with self.assertRaisesRegex(ValidationError, "within the repository"):
                    resolve_registered_path(root, value, "artifact")

    def test_malformed_registry_entry_is_reported(self):
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            (root / "schemas").mkdir()
            registry = root / "registry.json"
            registry.write_text(
                json.dumps({"manifest_version": 1, "artifacts": [{"path": "x"}]}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValidationError, "malformed registry entry"):
                validate_registered(root, registry)


if __name__ == "__main__":
    unittest.main()
