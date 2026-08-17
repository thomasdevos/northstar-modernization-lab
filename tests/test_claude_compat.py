import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.claude_compat import (
    extract_structured_output,
    load_manifest,
    main,
    validate_approved_base,
)
from scripts.validate_artifacts import ValidationError


def run(*args: str, cwd: Path) -> str:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def make_fake(root: Path) -> tuple[Path, Path]:
    executable = root / "fake-claude"
    log = root / "argv.jsonl"
    executable.write_text(
        """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys
record = {"argv": sys.argv[1:], "cwd": str(Path.cwd())}
with Path(os.environ["FAKE_CLAUDE_LOG"]).open("a", encoding="utf-8") as stream:
    stream.write(json.dumps(record) + "\\n")
if sys.argv[1:] == ["--version"]:
    print(os.environ.get("FAKE_CLAUDE_VERSION", "2.1.170 (Claude Code)"))
else:
    output = os.environ.get("FAKE_CLAUDE_OUTPUT")
    if output:
        print(output)
""",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    return executable, log


def records(log: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


class ClaudeCompatibilityTests(unittest.TestCase):
    def test_manifest_declares_all_three_workflows(self):
        manifest = load_manifest()
        self.assertEqual("plan", manifest["plan_session"]["permission_mode"])
        self.assertEqual("json", manifest["structured_output"]["output_format"])
        self.assertTrue(manifest["worktree"]["wrapper_uses_git_for_reviewed_base"])

    def test_plan_wrapper_checks_version_and_passes_exact_argv(self):
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            fake, log = make_fake(root)
            with patch.dict(os.environ, {"FAKE_CLAUDE_LOG": str(log)}, clear=False):
                self.assertEqual(0, main(["plan", "--claude", str(fake)]))
            calls = records(log)
            self.assertEqual(["--version"], calls[0]["argv"])
            self.assertEqual(["--permission-mode", "plan"], calls[1]["argv"])

    def test_structured_wrapper_passes_exact_argv_and_extracts_envelope(self):
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            fake, log = make_fake(root)
            prompt = root / "prompt.txt"
            schema = root / "return.schema.json"
            prompt.write_text("Bounded task", encoding="utf-8")
            schema.write_text(
                '{"type":"object","required":["status"],"properties":{"status":{"const":"ok"}},"additionalProperties":false}',
                encoding="utf-8",
            )
            envelope = json.dumps({"result": "display text", "structured_output": {"status": "ok"}})
            output = io.StringIO()
            with patch.dict(
                os.environ,
                {"FAKE_CLAUDE_LOG": str(log), "FAKE_CLAUDE_OUTPUT": envelope},
                clear=False,
            ), contextlib.redirect_stdout(output):
                result = main([
                    "structured-task", "--claude", str(fake), "--cwd", str(root),
                    "--prompt", str(prompt), "--schema", str(schema),
                ])
            self.assertEqual(0, result)
            self.assertEqual({"status": "ok"}, json.loads(output.getvalue()))
            argv = records(log)[1]["argv"]
            self.assertEqual(
                [
                    "-p", "--output-format", "json", "--json-schema",
                    schema.read_text(encoding="utf-8"), "--permission-mode", "dontAsk",
                    "Bounded task",
                ],
                argv,
            )

    def test_structured_wrapper_rejects_missing_or_invalid_envelope(self):
        schema = {"type": "object", "required": ["status"]}
        with self.assertRaisesRegex(ValidationError, "no structured_output"):
            extract_structured_output('{"result":"text"}', schema)
        with self.assertRaisesRegex(ValidationError, "invalid JSON"):
            extract_structured_output("not json", schema)
        with self.assertRaises(ValidationError):
            extract_structured_output('{"structured_output":{}}', schema)

    def test_reviewed_worktree_is_created_at_exact_revision_before_claude(self):
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            repo = root / "repo"
            repo.mkdir()
            run("git", "init", "-q", cwd=repo)
            run("git", "config", "user.email", "lab@example.invalid", cwd=repo)
            run("git", "config", "user.name", "Lab test", cwd=repo)
            (repo / "tracked.txt").write_text("approved\n", encoding="utf-8")
            run("git", "add", "tracked.txt", cwd=repo)
            run("git", "commit", "-qm", "approved base", cwd=repo)
            revision = run("git", "rev-parse", "HEAD", cwd=repo)
            fake, log = make_fake(root)
            with patch.dict(os.environ, {"FAKE_CLAUDE_LOG": str(log)}, clear=False):
                result = main([
                    "reviewed-worktree", "reviewed-change", "--base", str(repo),
                    "--approved-revision", revision, "--claude", str(fake),
                ])
            self.assertEqual(0, result)
            target = root / "reviewed-change"
            self.assertEqual(revision, run("git", "rev-parse", "HEAD", cwd=target))
            self.assertEqual([], records(log)[1]["argv"])
            self.assertEqual(str(target.resolve()), records(log)[1]["cwd"])

    def test_dirty_or_wrong_approved_base_fails_before_claude(self):
        with TemporaryDirectory() as root_name:
            repo = Path(root_name)
            run("git", "init", "-q", cwd=repo)
            run("git", "config", "user.email", "lab@example.invalid", cwd=repo)
            run("git", "config", "user.name", "Lab test", cwd=repo)
            (repo / "one").write_text("one", encoding="utf-8")
            run("git", "add", "one", cwd=repo)
            run("git", "commit", "-qm", "one", cwd=repo)
            old = run("git", "rev-parse", "HEAD", cwd=repo)
            (repo / "two").write_text("two", encoding="utf-8")
            run("git", "add", "two", cwd=repo)
            run("git", "commit", "-qm", "two", cwd=repo)
            with self.assertRaisesRegex(ValidationError, "revision mismatch"):
                validate_approved_base(repo, old)
            current = run("git", "rev-parse", "HEAD", cwd=repo)
            (repo / "two").write_text("dirty", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "not clean"):
                validate_approved_base(repo, current)

    def test_version_mismatch_stops_before_workflow_invocation(self):
        with TemporaryDirectory() as root_name:
            root = Path(root_name)
            fake, log = make_fake(root)
            stderr = io.StringIO()
            with patch.dict(
                os.environ,
                {"FAKE_CLAUDE_LOG": str(log), "FAKE_CLAUDE_VERSION": "9.9.9"},
                clear=False,
            ), contextlib.redirect_stderr(stderr):
                self.assertEqual(1, main(["plan", "--claude", str(fake)]))
            self.assertIn("version mismatch", stderr.getvalue())
            self.assertEqual(1, len(records(log)))


if __name__ == "__main__":
    unittest.main()
