#!/usr/bin/env python3
"""Verify the companion book-asset catalog, files, and recorded checksums."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "book-assets/manifest.json"
CATALOG = ROOT / "book-assets/README.md"
SHA256 = re.compile(r"[0-9a-f]{64}")


class AssetValidationError(ValueError):
    pass


def load_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(
                AssetValidationError(f"non-finite JSON number: {value}")
            ),
        )
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        raise AssetValidationError(f"cannot read manifest: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise AssetValidationError("unsupported or malformed book-assets manifest")
    return data


def contained_path(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise AssetValidationError("asset path must be a non-empty relative path")
    supplied = Path(value)
    base = root.resolve()
    candidate = base / supplied
    if supplied.is_absolute() or ".." in supplied.parts:
        raise AssetValidationError(f"asset path escapes allowed directory: {value}")
    current = candidate
    while current != base:
        if current.is_symlink():
            raise AssetValidationError(f"asset path contains a symlink: {value}")
        current = current.parent
    resolved = candidate.resolve()
    if not resolved.is_relative_to(base):
        raise AssetValidationError(f"asset path escapes allowed directory: {value}")
    return resolved


def validate_book_assets(
    root: Path = ROOT, manifest_path: Path = MANIFEST, catalog_path: Path = CATALOG
) -> tuple[int, Counter[str]]:
    manifest = load_manifest(manifest_path)
    listings = manifest.get("listings")
    if not isinstance(listings, list) or manifest.get("listing_count") != len(listings):
        raise AssetValidationError("listing_count does not match listings")
    try:
        catalog = catalog_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AssetValidationError(f"cannot read catalog: {exc}") from exc

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    statuses: Counter[str] = Counter()
    for index, entry in enumerate(listings):
        label = f"listings[{index}]"
        if not isinstance(entry, dict):
            raise AssetValidationError(f"{label}: expected object")
        listing_id = entry.get("id")
        language = entry.get("language")
        status = entry.get("status")
        asset = entry.get("asset")
        provenance = entry.get("provenance")
        if not isinstance(listing_id, str) or not re.fullmatch(r"ch\d{2}-listing-\d{3}", listing_id):
            raise AssetValidationError(f"{label}: invalid id")
        if listing_id in seen_ids:
            raise AssetValidationError(f"duplicate listing id: {listing_id}")
        seen_ids.add(listing_id)
        if language not in {"json", "yaml"} or status not in {"executable", "illustrative"}:
            raise AssetValidationError(f"{listing_id}: invalid language or status")
        if not isinstance(asset, dict) or set(asset) != {"path", "sha256"}:
            raise AssetValidationError(f"{listing_id}: malformed asset record")
        relative = asset["path"]
        prefix = Path("book-assets/listings")
        try:
            listing_relative = Path(str(relative)).relative_to(prefix)
        except ValueError as exc:
            raise AssetValidationError(
                f"{listing_id}: asset is outside listings directory"
            ) from exc
        path = contained_path(root / prefix, listing_relative.as_posix())
        expected_suffix = ".json" if language == "json" else ".yaml"
        if path.suffix != expected_suffix or not path.is_file():
            raise AssetValidationError(f"{listing_id}: listing file missing or extension mismatch")
        if relative in seen_paths:
            raise AssetValidationError(f"duplicate asset path: {relative}")
        seen_paths.add(relative)
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if asset["sha256"] != digest or not SHA256.fullmatch(str(asset["sha256"])):
            raise AssetValidationError(f"{listing_id}: SHA-256 mismatch")
        line_count = len(content.decode("utf-8").splitlines())
        if entry.get("content_lines") != line_count:
            raise AssetValidationError(f"{listing_id}: line-count mismatch")
        if status == "executable" and language == "json":
            try:
                json.loads(
                    content,
                    parse_constant=lambda value: (_ for _ in ()).throw(
                        AssetValidationError(f"{listing_id}: non-finite JSON number: {value}")
                    ),
                )
            except (json.JSONDecodeError, UnicodeError) as exc:
                raise AssetValidationError(f"{listing_id}: executable JSON is invalid") from exc
        if not isinstance(provenance, dict) or not SHA256.fullmatch(
            str(provenance.get("sha256", ""))
        ):
            raise AssetValidationError(f"{listing_id}: malformed provenance")
        if not isinstance(provenance.get("path"), str) or not provenance["path"].startswith(
            "chapters/chapter-"
        ):
            raise AssetValidationError(f"{listing_id}: malformed manuscript provenance path")
        start = provenance.get("content_line_start")
        end = provenance.get("content_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
            raise AssetValidationError(f"{listing_id}: invalid provenance line range")
        catalog_link = Path(relative).relative_to("book-assets").as_posix()
        if catalog.count(f"`{listing_id}`") != 1 or catalog.count(f"({catalog_link})") != 1:
            raise AssetValidationError(f"{listing_id}: catalog entry missing or duplicated")
        statuses[status] += 1

    summary = (
        f"Listings: {len(listings)} total, {statuses['executable']} executable, "
        f"{statuses['illustrative']} illustrative."
    )
    if summary not in catalog:
        raise AssetValidationError("catalog summary does not match manifest")
    return len(listings), statuses


def main() -> int:
    try:
        count, statuses = validate_book_assets()
    except (AssetValidationError, KeyError, TypeError, UnicodeError) as exc:
        print(f"BOOK ASSETS FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        f"BOOK ASSETS PASS: {count} listings verified "
        f"({statuses['executable']} executable, {statuses['illustrative']} illustrative)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
