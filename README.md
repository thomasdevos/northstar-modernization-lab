# Northstar modernization lab

Companion exercises for *Claude Code for Legacy Modernization*. This repository contains a fictional GBP fee-settlement batch designed for evidence-led modernization practice.

**Book:** <https://leanpub.com/claude-code-modernization>  
**Repository:** <https://github.com/thomasdevos/northstar-modernization-lab>

All records and identities are synthetic. Do not introduce production data, credentials, or customer information.

## Start here

```bash
git clone https://github.com/thomasdevos/northstar-modernization-lab.git
cd northstar-modernization-lab
git checkout lab/00-start
python3 --version
make test
make policy
make baseline
make characterize
make compare
```

The final `make compare` command **must fail at the supplied starting state**. `STL-1002` exposes a deliberate rounding difference:

- legacy fee: `1.01`; net: `668.99`
- replacement fee: `1.00`; net: `669.00`

That difference is the first exercise, not an installation failure.

## What the repository supplies

- a standard-library-only Python 3.11+ teaching system;
- legacy and replacement implementations;
- synthetic fixtures and a retained golden master;
- characterization, baseline, and differential checks;
- Claude Code project controls and compatibility wrappers;
- schemas and policy checks;
- full JSON and YAML listings referenced by the book.

The repository supplies the **starting state**, tagged `lab/00-start`. It does not claim that the later chapter states have already been completed or approved. As you work through the book, create each later `lab/NN-*` tag only after its named evidence and human review gate have passed.

## Prerequisites

Core lab:

- Python 3.11 or later;
- GNU Make;
- Git.

Claude Code exercises additionally use the compatibility baseline recorded in `compatibility/claude-code-2.1.170.json`. The wrappers fail closed when a different version is installed. Review the current product documentation and the book's Appendix A before adapting the pin.

## Expected command results at `lab/00-start`

| Command | Expected result | Meaning |
|---|---|---|
| `make test` | Pass | The teaching system and controls are internally consistent. |
| `make policy` | Pass | Registered schemas, settings, hooks, and compatibility checks pass. |
| `make baseline` | Pass | Legacy output matches the retained synthetic golden master. |
| `make characterize` | Pass | The selected behavior is reproduced and recorded locally. |
| `make compare` | Fail on `STL-1002` | The deliberate old/new rounding difference is visible. |
| `make verify` | Fail with gate statuses `[0, 0, 1]` | Tests and baseline pass; differential equivalence does not yet pass. |

## Exercise progression

1. Establish the legacy baseline: `make test-legacy && make baseline`.
2. Retain characterization evidence: `make characterize`.
3. Expose the replacement gap: `make compare`.
4. Inspect `evidence/runs/compare-*.csv` and `docs/decisions/0001-rounding-mismatch.md`.
5. Change only the replacement rounding behavior.
6. Update the differential test so it expects an empty difference.
7. Run `make verify` and retain the evidence required by the chapter.

Later chapters extend this starter state with records, fixtures, tests, gates, and human decisions. A passing script never substitutes for named approval.

## Claude Code controls

Use these stable wrappers from the repository root:

```bash
python3 scripts/claude_compat.py plan
python3 scripts/claude_compat.py reviewed-worktree NAME --approved-revision REVISION
python3 scripts/claude_compat.py structured-task --prompt PROMPT --schema SCHEMA
```

Read `CLAUDE.md` and `compatibility/README.md` first. The direct-file hook deliberately does not inspect Bash strings; the mandatory sandbox supplies the Bash write boundary for protected trees. Project settings constrain routine tool use, while operating-system or container isolation remains the stronger boundary for untrusted work.

## Generated evidence

Generated observations stay under `evidence/runs/` and `evidence/claims/`. They are ignored by Git. The accepted synthetic reference output remains under `fixtures/golden-master/`. Run `make clean` to remove generated evidence without dirtying the repository.

## Support and contributions

Use GitHub Issues for reproducible defects in the lab. Do not include confidential source code, data, logs, prompts, or credentials. See `CONTRIBUTING.md` and `SECURITY.md` before reporting or contributing.

## License

The companion code and exercise assets are licensed under the MIT License. The book text is licensed separately and is not included under this repository license.
