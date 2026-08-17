# Contributing

Thank you for improving the Northstar modernization lab.

1. Fork the repository and create a focused branch.
2. Use synthetic data only. Never submit proprietary source, customer data, credentials, prompts, or logs.
3. Preserve the intentional `STL-1002` difference on the `lab/00-start` teaching state.
4. Run `make test`, `make policy`, `make baseline`, and `make characterize`.
5. Confirm that `make compare` fails on `STL-1002` at the starting state.
6. Explain the evidence boundary and expected behavior in the pull request.

Changes that alter a published exercise state must update its documentation and verification evidence. Automated checks cannot provide the human approvals described in the book.
