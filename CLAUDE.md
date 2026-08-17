# Claude Code operating instructions

- Scope all work to this lab. Discovery sessions must be launched with `python3 scripts/claude_compat.py plan` from the lab root. The wrapper checks the declared compatible release before selecting plan mode. In plan mode, Claude Code's read-only tools may read within the working directory and configured additional directories by default. This project admits no additional or external directory.
- Implementation sessions use `permissions.defaultMode: dontAsk`. Unapproved tools are denied instead of prompting. Narrow Make, Python, and Bash commands are pre-approved; there is no `bypassPermissions` mode.
- Treat `legacy_app/` and `fixtures/golden-master/` as observed, protected contracts; do not edit them. Chapter exercises may prepare review candidates under `fixtures/candidates/`. A named human promotes an approved candidate into the protected golden-master tree and records matching digests.
- The sandbox `filesystem.denyWrite` policy is the Bash write boundary for those trees. Sandbox startup is mandatory and unsandboxed commands are disabled.
- Path-scoped `Edit` deny rules and the `Edit|Write` pre-tool hook add direct-file-tool denials. Do not add path-scoped `Write(...)` rules because they do not match Write requests in the compatible release. The hook canonicalizes file paths. It does not parse Bash. The mandatory sandbox `denyWrite` policy is the Bash filesystem boundary.
- Project settings are not an operating-system boundary for direct read tools. Run from the lab root, admit no external directory, keep secrets out of the tree, and use OS isolation where stronger read confinement is required.
- Use Python standard library only; add no dependencies or network calls.
- Reproduce a failure before changing `replacement_service/`.
- Run `make test-legacy`, `make baseline`, `make compare`, then `make verify`.
- Run `python3 -m unittest tests.test_protect_files tests.test_settings_policy -v` after changing controls.
- Keep generated observations in `evidence/runs/`; record conclusions in `evidence/claims/` or `docs/decisions/`.
- Never use real settlement/customer data or credentials.
- The initial comparator failure is intentional; fix behaviour, not the fixture.
