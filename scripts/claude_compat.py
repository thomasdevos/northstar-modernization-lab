#!/usr/bin/env python3
"""Stable, compatibility-checked wrappers for supported Claude Code workflows."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.validate_artifacts import ROOT, ValidationError, load_data, validate
except ModuleNotFoundError:  # Direct execution adds scripts/, not its parent, to sys.path.
    from validate_artifacts import ROOT, ValidationError, load_data, validate

MANIFEST = ROOT / "compatibility/claude-code-2.1.170.json"
MANIFEST_SCHEMA = ROOT / "schemas/claude-compatibility.schema.json"
RETURN_SCHEMA = ROOT / "contracts/returns/task-return.schema.json"


def load_manifest() -> dict[str, Any]:
    manifest = load_data(MANIFEST, "json")
    validate(manifest, load_data(MANIFEST_SCHEMA, "json"))
    return manifest


def git(path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), *args], text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise ValidationError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def validate_approved_base(path: Path, approved_revision: str) -> str:
    if git(path, "rev-parse", "--is-inside-work-tree") != "true":
        raise ValidationError("approved base is not a Git worktree")
    actual = git(path, "rev-parse", "HEAD")
    approved = git(path, "rev-parse", f"{approved_revision}^{{commit}}")
    if actual != approved:
        raise ValidationError(f"base revision mismatch: HEAD {actual}, approved {approved}")
    if git(path, "status", "--porcelain"):
        raise ValidationError("approved base worktree is not clean")
    return approved


def claude_executable(value: str | None) -> str:
    return value or os.environ.get("CLAUDE_BIN", "claude")


def validate_declared_compatibility(executable: str, manifest: dict[str, Any]) -> None:
    try:
        result = subprocess.run(
            [executable, "--version"], text=True, capture_output=True, check=False
        )
    except OSError as exc:
        raise ValidationError(f"cannot execute Claude CLI: {exc}") from exc
    if result.returncode:
        raise ValidationError(result.stderr.strip() or "Claude CLI version check failed")
    expected = manifest["claude_code"]["verified_version"]
    observed = re.search(r"\b\d+\.\d+\.\d+\b", result.stdout + result.stderr)
    if observed is None or observed.group(0) != expected:
        value = observed.group(0) if observed else "unparseable"
        raise ValidationError(f"Claude Code version mismatch: expected {expected}, observed {value}")


def build_plan_command(manifest: dict[str, Any], executable: str) -> list[str]:
    plan = manifest["plan_session"]
    return [executable, plan["permission_mode_flag"], plan["permission_mode"]]


def build_structured_command(
    manifest: dict[str, Any], executable: str, prompt: Path, schema: Path
) -> list[str]:
    structured = manifest["structured_output"]
    return [
        executable,
        structured["print_flag"],
        structured["output_format_flag"],
        structured["output_format"],
        structured["schema_flag"],
        schema.read_text(encoding="utf-8"),
        structured["permission_mode_flag"],
        structured["permission_mode"],
        prompt.read_text(encoding="utf-8"),
    ]


def extract_structured_output(stdout: str, schema: dict[str, Any]) -> Any:
    try:
        envelope = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Claude CLI returned invalid JSON: {exc.msg}") from exc
    if not isinstance(envelope, dict) or "structured_output" not in envelope:
        raise ValidationError("Claude CLI JSON envelope has no structured_output field")
    payload = envelope["structured_output"]
    validate(payload, schema)
    return payload


def add_common_executable_argument(command: argparse.ArgumentParser) -> None:
    command.add_argument(
        "--claude", help="Claude executable; defaults to CLAUDE_BIN or claude"
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="action", required=True)
    sub.add_parser("check")

    plan = sub.add_parser("plan", help="start a compatibility-checked plan session")
    add_common_executable_argument(plan)

    worktree = sub.add_parser(
        "reviewed-worktree",
        help="create a worktree at an approved clean revision, then start Claude there",
    )
    worktree.add_argument("name")
    worktree.add_argument("--base", type=Path, default=Path.cwd())
    worktree.add_argument("--approved-revision", required=True)
    add_common_executable_argument(worktree)

    structured = sub.add_parser(
        "structured-task", help="run a headless task and emit only validated structured_output"
    )
    structured.add_argument("--prompt", type=Path, required=True)
    structured.add_argument("--schema", type=Path, default=RETURN_SCHEMA)
    structured.add_argument("--cwd", type=Path, default=Path.cwd())
    add_common_executable_argument(structured)
    return result


def run_passthrough(command: list[str], cwd: Path) -> int:
    try:
        return subprocess.run(command, cwd=cwd, check=False).returncode
    except OSError as exc:
        raise ValidationError(f"cannot execute Claude CLI: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        manifest = load_manifest()
        if args.action == "check":
            schema = load_data(RETURN_SCHEMA, "json")
            if schema.get("type") != "object" or not schema.get("required"):
                raise ValidationError("structured return schema is incomplete")
            print(
                "COMPATIBILITY PASS: Claude Code 2.1.170 manifest and structured return schema validated; Claude not invoked"
            )
            return 0

        executable = claude_executable(args.claude)
        validate_declared_compatibility(executable, manifest)

        if args.action == "plan":
            return run_passthrough(build_plan_command(manifest, executable), ROOT)

        if args.action == "reviewed-worktree":
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.name):
                raise ValidationError("worktree name must be a safe branch name")
            base = args.base.resolve()
            approved = validate_approved_base(base, args.approved_revision)
            target = base.parent / args.name
            if target.exists():
                raise ValidationError(f"worktree target already exists: {target}")
            git(base, "worktree", "add", "-b", args.name, str(target), approved)
            return run_passthrough([executable], target)

        if not args.prompt.is_file() or not args.schema.is_file():
            raise ValidationError("prompt and schema must be existing files")
        schema = load_data(args.schema, "json")
        if schema.get("type") != "object":
            raise ValidationError("return schema must describe an object")
        command = build_structured_command(manifest, executable, args.prompt, args.schema)
        try:
            completed = subprocess.run(
                command, cwd=args.cwd.resolve(), text=True, capture_output=True, check=False
            )
        except OSError as exc:
            raise ValidationError(f"cannot execute Claude CLI: {exc}") from exc
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")
        if completed.returncode:
            return completed.returncode
        payload = extract_structured_output(completed.stdout, schema)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValidationError) as exc:
        print(f"COMPATIBILITY FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
