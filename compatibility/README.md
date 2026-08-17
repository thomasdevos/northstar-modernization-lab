# Claude Code compatibility layer

This directory pins the version-sensitive CLI surface used by the companion lab. `claude-code-2.1.170.json` records syntax reviewed against the official documentation on 24 July 2026. Release QA confirmed that the local executable reported `2.1.170`; no authenticated model task was used as release evidence. The exact wrapper arguments and output handling are exercised with deterministic fake-executable tests.

Run `make compatibility` to validate the manifest and structured return schema without invoking the Claude executable. After installing Claude Code through the current official instructions, run `make compatibility-live` to invoke only `claude --version` and verify the pin. The workflow wrappers repeat that version check before invoking Claude. Set `CLAUDE_BIN` or pass `--claude` to select a controlled executable.

## Stable commands

Run these from the Northstar repository root:

```bash
python3 scripts/claude_compat.py plan

python3 scripts/claude_compat.py reviewed-worktree bounded-revision \
  --base . \
  --approved-revision "$(git rev-parse HEAD)"

python3 scripts/claude_compat.py structured-task \
  --cwd . \
  --prompt prompts/rounding-analysis.txt \
  --schema contracts/returns/task-return.schema.json \
  > evidence/runs/task-return.json
```

The reviewed-worktree wrapper accepts only a clean Northstar lab root at the named revision. It creates the named branch and worktree at that exact commit before starting Claude. It does not rely on the product's default worktree base. The worktree and branch persist for review after the Claude process exits; remove them explicitly with Git when they are no longer needed.

The structured-task wrapper requires the working directory, prompt, and schema to resolve inside this lab after symlink resolution. It invokes print mode with JSON output and `dontAsk`, parses the Claude JSON envelope, validates `.structured_output`, and writes only that object to standard output. It rejects malformed or non-finite JSON, a missing envelope field, paths outside the lab, and unsupported schema assertions.

## Dependency-free schema dialect

Offline validation supports this explicit JSON Schema subset:

- `$schema` and `$id` metadata;
- `type`, `const`, `enum`, and `pattern`;
- `properties`, `required`, and Boolean `additionalProperties`;
- `items` and `minItems`.

Unsupported keywords fail closed. This prevents a schema from appearing validated when an assertion was silently ignored. YAML artifacts can be checked without a dependency only when serialized as the JSON-compatible YAML 1.2 subset; broader YAML is rejected rather than partially parsed.

## Reviewed 2.1.170 direct syntax

These commands document the volatile product surface covered by the wrapper tests. Prefer the stable commands above in numbered chapters and normal operation.

```bash
claude --permission-mode plan
claude --worktree compatibility-smoke
claude -p \
  --output-format json \
  --json-schema "$(cat contracts/returns/task-return.schema.json)" \
  --permission-mode dontAsk \
  "$(cat prompts/rounding-analysis.txt)"
```

The direct worktree command is only a syntax reference. It does not prove that the created worktree starts at the reviewed `HEAD`. The direct structured command returns a JSON envelope; consumers must read `.structured_output` rather than treating the entire envelope as the task object.

## Auto Mode governance boundary

Current Claude Code documentation includes `auto`, where a classifier approves or denies permission prompts. Current releases ignore `permissions.defaultMode: auto` in project and local settings so an untrusted repository cannot grant itself that mode. Auto Mode configuration can come from user settings, managed settings, or invocation-scoped `--settings` or Agent SDK input. Plan mode can use Auto Mode semantics when the feature is available. These behaviours are version-sensitive; confirm them against the installed release and effective settings.

This pinned companion path uses `dontAsk`. It does not claim that `dontAsk` is the only valid organisational choice. Evaluate Auto Mode separately in a disposable environment with production credentials absent, production routes blocked, the mandatory sandbox active, and managed deny rules unchanged. Compare observable classifier decisions against a human-owned policy oracle for a fixed corpus of tool calls. Retain false allows, false denials, Claude Code version, model, exact tool input, `PermissionDenied` events, and observed side effects. The classifier's internal reasoning is not exposed as an auditable policy artefact and its approval does not supersede a managed deny, sandbox boundary, or human release decision. Compatible newer releases expose built-in and effective configuration through `claude auto-mode defaults`, `claude auto-mode config`, and `claude auto-mode critique`; version-check those commands before use.

Primary references: [permission modes](https://code.claude.com/docs/en/permissions#permission-modes), [Auto Mode configuration](https://code.claude.com/docs/en/auto-mode-config), [permission settings](https://code.claude.com/docs/en/settings#permission-settings), and [hook events](https://code.claude.com/docs/en/hooks#permissiondenied).

## Release state

This companion is a real Git repository. `lab/00-start-v2` is the annotated published starting-state tag. Reader exercise branches and progression tags remain local or fork-specific unless the maintainer publishes them. Verify the selected starting commit with `git rev-parse 'lab/00-start-v2^{commit}'`; do not infer execution evidence from a command example alone.
