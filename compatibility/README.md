# Claude Code compatibility layer

This directory pins the version-sensitive CLI surface used by the companion lab. `claude-code-2.1.170.json` records syntax reviewed against the official documentation on 24 July 2026. Its status is `documentation-reviewed-not-locally-invoked`. It does not claim that Claude Code 2.1.170 was installed or run in this lab.

Run `make compatibility` to validate the manifest and structured return schema without invoking Claude. The three stable wrapper commands below check the executable's reported version against the manifest before they invoke it. Set `CLAUDE_BIN` or pass `--claude` to use a controlled executable.

## Stable commands

```bash
python3 scripts/claude_compat.py plan

python3 scripts/claude_compat.py reviewed-worktree bounded-revision \
  --base /approved/repository \
  --approved-revision <reviewed-commit>

python3 scripts/claude_compat.py structured-task \
  --cwd /approved/repository \
  --prompt /approved/task.txt \
  --schema contracts/returns/task-return.schema.json \
  > evidence/proposals/task-return.json
```

The reviewed-worktree wrapper rejects a dirty checkout or a `HEAD` that differs from the approved commit. It then uses Git to create the named branch and worktree at that exact commit before starting Claude in the new directory. It does not rely on the product's default worktree base.

The structured-task wrapper reads the prompt and schema, invokes print mode with JSON output and `dontAsk`, parses the Claude JSON envelope, validates `.structured_output` against the supplied schema, and writes only that object to standard output. It rejects malformed JSON, a missing envelope field, or a schema-invalid payload.

## Reviewed 2.1.170 direct syntax

These commands document the volatile product surface tested by fake-executable wrapper tests. Prefer the stable commands above in numbered chapters and normal operation.

```bash
claude --permission-mode plan
claude --worktree compatibility-smoke
claude -p \
  --output-format json \
  --json-schema "$(cat contracts/returns/task-return.schema.json)" \
  --permission-mode dontAsk \
  "$(cat /approved/task.txt)"
```

The direct worktree command is only a syntax reference. It does not prove that the created worktree starts at the reviewed `HEAD`. The direct structured command returns a JSON envelope; consumers must read `.structured_output` rather than treating the entire envelope as the task object.

## Auto Mode governance boundary

Current Claude Code documentation includes `auto`, where a classifier approves or denies permission prompts. Current releases ignore `permissions.defaultMode: auto` in project and local settings so an untrusted repository cannot grant itself that mode. Auto Mode configuration can come from user settings, managed settings, or invocation-scoped `--settings` or Agent SDK input. Plan mode can use Auto Mode semantics when the feature is available. These behaviours are version-sensitive; confirm them against the installed release and the effective settings.

This pinned companion path uses `dontAsk`. It does not claim that `dontAsk` is the only valid organisational choice. Evaluate Auto Mode separately in a disposable environment with production credentials absent, production routes blocked, the mandatory sandbox active, and managed deny rules unchanged. Compare observable classifier decisions against a human-owned policy oracle for a fixed corpus of tool calls. Retain false allows, false denials, Claude Code version, model, exact tool input, `PermissionDenied` events, and observed side effects. The classifier's internal reasoning is not exposed as an auditable policy artefact and its approval does not supersede a managed deny, sandbox boundary, or human release decision. Compatible newer releases expose built-in and effective configuration through `claude auto-mode defaults`, `claude auto-mode config`, and `claude auto-mode critique`; version-check those commands before use.

Primary references: [permission modes](https://code.claude.com/docs/en/permissions#permission-modes), [Auto Mode configuration](https://code.claude.com/docs/en/auto-mode-config), [permission settings](https://code.claude.com/docs/en/settings#permission-settings), and [hook events](https://code.claude.com/docs/en/hooks#permissiondenied).

The companion lab directory supplied with the book is not a Git repository. Its chapter tags and worktrees remain symbolic and unverified. Do not manufacture progression tags or treat a command example as execution evidence.

Offline artifact validation is intentionally narrow. JSON artifacts use local schemas. YAML artifacts can be validated without a dependency only when serialized as the JSON-compatible YAML 1.2 subset. Broader YAML is rejected with an explicit error rather than partially parsed.
