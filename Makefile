.PHONY: test test-legacy baseline characterize compare verify policy schemas compatibility clean

PYTHON := python3

test:
	$(PYTHON) -m unittest discover -s tests -v

schemas:
	$(PYTHON) scripts/validate_artifacts.py

compatibility:
	$(PYTHON) scripts/claude_compat.py check

policy: schemas compatibility
	$(PYTHON) -m unittest tests.test_protect_files tests.test_settings_policy tests.test_validate_artifacts tests.test_claude_compat -v

test-legacy:
	$(PYTHON) -m unittest tests.test_legacy -v

baseline:
	$(PYTHON) scripts/baseline.py

characterize:
	$(PYTHON) scripts/characterize.py

compare:
	$(PYTHON) scripts/compare.py

verify:
	$(PYTHON) scripts/verify.py

clean:
	rm -f evidence/runs/*.csv evidence/claims/characterization.md
