# Security policy

This repository is an educational lab containing synthetic data only. It must never contain production data, credentials, private prompts or logs, proprietary source code, or customer information.

## Reporting a vulnerability

Use GitHub's **Report a vulnerability** / private Security Advisory flow for vulnerabilities in the supplied code or controls. Do not open a public issue containing exploit details, credentials, confidential code, customer data, private paths, prompts, or production logs.

Include the affected revision, a minimal synthetic reproduction, the expected boundary, and the observed behavior. Security reports do not constitute approval to test systems outside this repository.

If you believe a secret has been committed, do not quote it in an issue. Identify only the file and revision through the private advisory channel. Treat the value as compromised and rotate it; deleting a file from the latest commit does not remove it from Git history.

## Supported release

| Release | Support |
|---|---|
| Maintainer-published `lab/00-start-v2` tag | Supported starter state |
| Current default branch | Supported for repository defects and release preparation |
| Reader-created branches or `lab/NN-*` tags | Local/unofficial unless explicitly published by the maintainer |

Claude Code compatibility is additionally bounded by `compatibility/claude-code-2.1.170.json`. The controls are defence in depth, not an operating-system read boundary. Use stronger OS or container isolation when untrusted content or sensitive local files may be present.
