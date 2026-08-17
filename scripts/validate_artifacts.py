#!/usr/bin/env python3
"""Offline validation for registered JSON and JSON-compatible YAML artifacts."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "schemas/artifacts.manifest.json"


class ValidationError(ValueError):
    pass


def load_data(path: Path, format_name: str) -> Any:
    # JSON is a strict YAML 1.2 subset. This keeps the lab dependency-free and
    # rejects broader YAML instead of pretending a partial parser is complete.
    if format_name not in {"json", "yaml-json-subset"}:
        raise ValidationError(f"unsupported format: {format_name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        label = "JSON-compatible YAML" if format_name == "yaml-json-subset" else "JSON"
        raise ValidationError(f"{path}: invalid {label}: {exc}") from exc


def _type_matches(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
        "null": value is None,
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
    }.get(expected, False)


def validate(value: Any, schema: dict[str, Any], location: str = "$") -> None:
    expected = schema.get("type")
    if expected is not None:
        choices = expected if isinstance(expected, list) else [expected]
        if not any(_type_matches(value, item) for item in choices):
            raise ValidationError(f"{location}: expected type {expected}")
    if "const" in schema and value != schema["const"]:
        raise ValidationError(f"{location}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{location}: value is not in enum")
    if isinstance(value, str) and "pattern" in schema and not re.search(schema["pattern"], value):
        raise ValidationError(f"{location}: does not match {schema['pattern']!r}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ValidationError(f"{location}: too few items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate(item, item_schema, f"{location}[{index}]")
    if isinstance(value, dict):
        required = schema.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            raise ValidationError(f"{location}: missing required keys {missing}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                raise ValidationError(f"{location}: unexpected keys {extra}")
        for key, child_schema in properties.items():
            if key in value:
                validate(value[key], child_schema, f"{location}.{key}")


def validate_registered(root: Path = ROOT, registry_path: Path = REGISTRY) -> tuple[int, int]:
    registry = load_data(registry_path, "json")
    if registry.get("manifest_version") != 1 or not isinstance(registry.get("artifacts"), list):
        raise ValidationError("invalid artifact registry")
    checked = skipped = 0
    for entry in registry["artifacts"]:
        artifact = root / entry["path"]
        if not artifact.exists() and not entry["required"]:
            skipped += 1
            continue
        if not artifact.is_file():
            raise ValidationError(f"required artifact missing: {entry['path']}")
        schema = load_data(root / entry["schema"], "json")
        validate(load_data(artifact, entry["format"]), schema)
        checked += 1
    # Every local schema must at least be valid JSON and identify an object schema.
    for path in sorted((root / "schemas").glob("*.schema.json")) + sorted((root / "contracts").rglob("*.schema.json")):
        schema = load_data(path, "json")
        if not isinstance(schema, dict) or "$schema" not in schema or "type" not in schema:
            raise ValidationError(f"{path}: incomplete local schema")
    return checked, skipped


def main() -> int:
    try:
        checked, skipped = validate_registered()
    except ValidationError as exc:
        print(f"SCHEMA FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"SCHEMA PASS: {checked} registered artifacts validated, {skipped} optional artifacts absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
