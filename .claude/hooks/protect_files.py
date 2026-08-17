#!/usr/bin/env python3
"""Add a direct-file-tool guard around protected lab observations.

The sandbox denyWrite policy is the filesystem boundary for Bash. This hook
canonicalizes paths supplied by Edit and Write. It deliberately does not parse
shell command strings, aliases, wrappers, or encoded programs.
"""

import json
import os
import sys
from pathlib import Path

PROTECTED_RELATIVE = (Path("legacy_app"), Path("fixtures/golden-master"))


def project_root() -> Path:
    raw = os.environ.get("CLAUDE_PROJECT_DIR")
    if not raw:
        raise ValueError("CLAUDE_PROJECT_DIR is required")
    return Path(raw).expanduser().resolve()


def canonical_target(root: Path, raw_path: str) -> Path:
    target = Path(raw_path).expanduser()
    if not target.is_absolute():
        target = root / target
    return target.resolve(strict=False)


def protected_marker(root: Path, raw_path: str) -> str | None:
    target = canonical_target(root, raw_path)
    for relative in PROTECTED_RELATIVE:
        protected = (root / relative).resolve(strict=False)
        if target == protected or target.is_relative_to(protected):
            return relative.as_posix() + "/"
    return None


def deny(marker: str) -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Protected lab observation: {marker}",
            }
        },
        sys.stdout,
    )


def fail_closed(reason: str) -> None:
    print(f"hook failed closed: {reason}", file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    try:
        event = json.load(sys.stdin)
        root = project_root()
    except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
        print(f"invalid hook input: {exc}", file=sys.stderr)
        return 2

    tool_name = str(event.get("tool_name", ""))
    tool_input = event.get("tool_input", {})
    if not isinstance(tool_input, dict):
        print("invalid hook input: tool_input must be an object", file=sys.stderr)
        return 2

    marker = None
    if tool_name in {"Edit", "Write"}:
        raw_path = tool_input.get("file_path", "")
        if not isinstance(raw_path, str) or not raw_path.strip():
            fail_closed("matched direct-file event has no valid file_path")
        marker = protected_marker(root, raw_path)
    if marker:
        deny(marker)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
