"""Subprocess tests for the Claude Code protected-file hook."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude/hooks/protect_files.py"


class ProtectFilesHookTest(unittest.TestCase):
    def invoke(self, tool_name: str, tool_input: dict) -> subprocess.CompletedProcess[str]:
        event = json.dumps({"tool_name": tool_name, "tool_input": tool_input})
        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = str(ROOT)
        return subprocess.run(
            [sys.executable, str(HOOK)],
            input=event,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def assert_allowed(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def assert_denied(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(
            output["hookSpecificOutput"]["permissionDecision"], "deny"
        )

    def assert_failed_closed(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("failed closed", result.stderr.lower())

    def test_allows_unprotected_relative_path(self) -> None:
        self.assert_allowed(self.invoke("Write", {"file_path": "replacement_service/new.py"}))

    def test_allows_candidate_fixture_path(self) -> None:
        self.assert_allowed(self.invoke("Write", {"file_path": "fixtures/candidates/09-fee/cases.csv"}))
        self.assert_allowed(
            self.invoke("Bash", {"command": "printf x > fixtures/candidates/09-fee/cases.csv"})
        )

    def test_denies_direct_protected_path(self) -> None:
        self.assert_denied(self.invoke("Edit", {"file_path": "legacy_app/settlement.py"}))

    def test_denies_absolute_protected_path(self) -> None:
        target = ROOT / "fixtures/golden-master/settlements.expected.csv"
        self.assert_denied(self.invoke("Write", {"file_path": str(target)}))

    def test_denies_relative_traversal_into_protected_path(self) -> None:
        path = "replacement_service/../legacy_app/settlement.py"
        self.assert_denied(self.invoke("Write", {"file_path": path}))

    def test_denies_existing_symlink_alias_into_protected_path(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            alias = Path(temporary) / "legacy-alias"
            alias.symlink_to(ROOT / "legacy_app", target_is_directory=True)
            self.assert_denied(
                self.invoke("Write", {"file_path": str(alias / "settlement.py")})
            )

    def test_allows_prefix_collision_path(self) -> None:
        self.assert_allowed(
            self.invoke("Write", {"file_path": "legacy_app_copy/settlement.py"})
        )

    def test_matched_direct_file_event_without_path_fails_closed(self) -> None:
        for value in (None, 42, "", "   "):
            payload = {} if value is None else {"file_path": value}
            with self.subTest(value=value):
                self.assert_failed_closed(self.invoke("Write", payload))

    def test_does_not_claim_to_parse_bash(self) -> None:
        command = "python3 -c 'open(\"fixtures/golden-master/x\", \"w\").write(\"x\")'"
        self.assert_allowed(self.invoke("Bash", {"command": command}))


if __name__ == "__main__":
    unittest.main()
