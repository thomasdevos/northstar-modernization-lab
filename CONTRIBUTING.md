# Contributing

Thank you for improving the Northstar modernization lab.

## Repository-defect contributions

1. Fork the repository and create a focused branch from the current default branch.
2. Use synthetic data only. Never submit proprietary source, customer data, credentials, private paths, prompts, or logs.
3. Preserve the intentional `STL-1002` difference in the upstream starter state. Do not move or rewrite `lab/00-start-v2`.
4. Run `make test`, `make policy`, `make baseline`, and `make characterize`.
5. Confirm that `make compare` fails on `STL-1002` and `make verify` reports `[0, 0, 1]` for the maintained starter state.
6. Run `make clean`, inspect `git status --short`, and confirm the change introduces no generated evidence, credentials, or environment-specific paths.
7. Explain the evidence boundary, expected behavior, and verification output in the pull request.

Changes that alter a published exercise state must update its documentation, tests, and verification evidence. Automated checks cannot provide the human approvals described in the book.

## Exercise solutions

Follow the book on a branch in your own clone or fork. A solved exercise should eventually make its branch-specific gates pass, but it deliberately changes the behavior that upstream CI protects. Do not submit exercise-solution pull requests against the maintained starter state.

Reader-created progression tags are local or fork-specific unless the maintainer explicitly publishes them.
