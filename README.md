# Northstar modernization lab

Companion exercises for *Claude Code for Legacy Modernization*. This repository contains a fictional GBP fee-settlement batch designed for evidence-led modernization practice.

**Book:** <https://leanpub.com/claude-code-modernization>  
**Repository:** <https://github.com/thomasdevos/northstar-modernization-lab>

All records and identities are synthetic. Do not introduce production data, credentials, proprietary source code, customer information, or private prompts and logs.

## Start here

Clone the published starting state onto a branch you own. The `lab/00-start-v2` tag is the maintained reference point; do not move or rewrite it.

```bash
git clone https://github.com/thomasdevos/northstar-modernization-lab.git
cd northstar-modernization-lab
git switch -c exercises/rounding-fix lab/00-start-v2
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

That difference is the first exercise, not an installation failure. Creating an exercise branch avoids detached-HEAD work and protects the published tag.

To inspect the tag object and the exact commit selected in your clone:

```bash
git cat-file -t lab/00-start-v2
git rev-parse 'lab/00-start-v2^{commit}'
```

## What the repository supplies

- a standard-library-only Python 3.11+ teaching system;
- legacy and replacement implementations;
- synthetic fixtures and a retained golden master;
- characterization, baseline, and byte-level differential checks;
- Claude Code project controls and compatibility wrappers;
- local schemas and fail-closed policy checks;
- full JSON and YAML listings referenced by the book, with checksums and provenance metadata.

The repository supplies the **starting state**, tagged `lab/00-start-v2`. It does not claim that later chapter states have already been completed or approved. As you work through the book, create later `lab/NN-*` tags only in your own fork or clone, and only after the named evidence and human review gate have passed. Reader-created tags are not official releases from this repository.

## Prerequisites

Core lab:

- Python 3.11 or later;
- GNU Make;
- Git.

The CI gate explicitly exercises Python 3.11 and 3.13. The lab has no third-party Python dependencies and performs no network calls during its core tests.

Claude Code exercises additionally use the compatibility baseline recorded in `compatibility/claude-code-2.1.170.json`. Install Claude Code using the current official product instructions, authenticate according to your organisation's policy, and run:

```bash
claude --version
make compatibility-live
```

The live check invokes only `claude --version`; it does not submit a model task. The wrappers fail closed when a different version is installed. Review `compatibility/README.md` and the book's Appendix A before adapting the pin.

## Expected command results at `lab/00-start-v2`

| Command | Expected result | Meaning |
|---|---|---|
| `make test` | Pass | The teaching system and controls are internally consistent. |
| `make policy` | Pass | Registered schemas, book assets, settings, hooks, and offline compatibility checks pass. |
| `make book-assets` | Pass | All 70 companion listings, hashes, line counts, and catalog links agree. |
| `make baseline` | Pass | Legacy output matches the retained synthetic golden master. |
| `make characterize` | Pass | The selected behavior is reproduced with fixture, revision, and digest evidence. |
| `make compare` | Fail on `STL-1002` | The deliberate old/new rounding difference is visible. |
| `make verify` | Fail with gate statuses `[0, 0, 1]` | Tests and baseline pass; differential equivalence does not yet pass. |

## Exercise progression

1. Establish the legacy baseline: `make test-legacy && make baseline`.
2. Retain characterization evidence: `make characterize`.
3. Expose the replacement gap: `make compare`.
4. Inspect `evidence/runs/compare-*.csv`, `evidence/claims/characterization.md`, and `docs/decisions/0001-rounding-mismatch.md`.
5. Change only the replacement rounding behavior.
6. Update the differential test so it expects an empty difference.
7. Run `make verify`; it must pass on your solved exercise branch.
8. Review the generated comparison output, record the human decision required by the chapter, and commit only the intended conclusion or decision record—not unreviewed generated output.
9. Run `make clean` and confirm `git status --short` contains only your intended source, test, and decision changes before creating a progression tag.

Later chapters extend this starter state with records, fixtures, tests, gates, and human decisions. A passing script never substitutes for named approval.

The upstream CI intentionally verifies the published **starter state**, including the `STL-1002` mismatch. Exercise solutions belong on reader branches or forks and are not accepted as pull requests that change the upstream starter state.

## Claude Code controls

Use these stable wrappers from the repository root:

```bash
python3 scripts/claude_compat.py plan
python3 scripts/claude_compat.py reviewed-worktree NAME --approved-revision REVISION
python3 scripts/claude_compat.py structured-task --prompt PROMPT --schema SCHEMA
```

The wrappers require the declared Claude Code version. Structured-task prompts, schemas, and working directories must resolve inside this lab. Reviewed worktrees must originate from a clean Northstar lab checkout at the approved revision. The local validator supports a documented dependency-free JSON Schema subset and rejects unsupported schema keywords rather than silently ignoring them.

Read `CLAUDE.md` and `compatibility/README.md` first. The direct-file hook deliberately does not inspect Bash strings; the mandatory sandbox supplies the Bash write boundary for protected trees. Project settings constrain routine tool use, while operating-system or container isolation remains the stronger boundary for untrusted work.

## Book assets and provenance

`book-assets/` contains 70 externalized listings. In its manifest, `executable` means the listing is textually complete and has no detected omission marker. It does **not** mean independently runnable, safe for production, or approved for a particular environment. Validate environment-specific values before use.

The manifest's `chapter` value is the practical-book chapter number. Provenance paths and line ranges refer to the separately licensed manuscript revision from which the listing was extracted; those manuscript files are intentionally not included in this MIT-licensed repository. `make book-assets` verifies the public listing files, catalog, hashes, line counts, and parseable complete JSON without claiming access to the separately licensed source text.

## Generated evidence

The supplied commands write generated CSV observations under `evidence/runs/` and a generated characterization record at `evidence/claims/characterization.md`. Those known outputs are ignored by Git. The accepted synthetic reference output remains under `fixtures/golden-master/`. `make clean` removes the generated CSV, log, and characterization files produced by the documented workflow.

Before committing any other evidence or conclusion, inspect it for private paths, names, credentials, prompts, logs, or production-derived material. Generated evidence is not automatically safe merely because it is located under `evidence/`.

## Support and contributions

Use GitHub Issues for reproducible defects in the lab. Do not include confidential source code, data, logs, prompts, or credentials. See `CONTRIBUTING.md` and `SECURITY.md` before reporting or contributing.

## License

The companion code and exercise assets are licensed under the MIT License. The book text is licensed separately and is not included under this repository license.
