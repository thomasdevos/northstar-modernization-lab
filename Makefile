.PHONY: check-environment test test-legacy baseline characterize compare verify policy schemas book-assets compatibility compatibility-live clean

PYTHON := python3

check-environment:
	$(PYTHON) scripts/check_environment.py

test: check-environment
	$(PYTHON) -m unittest discover -s tests -v

schemas: check-environment
	$(PYTHON) scripts/validate_artifacts.py

book-assets: check-environment
	$(PYTHON) scripts/validate_book_assets.py

compatibility: check-environment
	$(PYTHON) scripts/claude_compat.py check

compatibility-live: check-environment
	$(PYTHON) scripts/claude_compat.py live-check

policy: schemas book-assets compatibility
	$(PYTHON) -m unittest tests.test_protect_files tests.test_settings_policy tests.test_validate_artifacts tests.test_book_assets tests.test_claude_compat -v

test-legacy: check-environment
	$(PYTHON) -m unittest tests.test_legacy -v

baseline: check-environment
	$(PYTHON) scripts/baseline.py

characterize: check-environment
	$(PYTHON) scripts/characterize.py

compare: check-environment
	$(PYTHON) scripts/compare.py

verify: check-environment
	$(PYTHON) scripts/verify.py

clean:
	rm -f evidence/runs/*.csv evidence/runs/*.json evidence/runs/*.log evidence/claims/characterization.md
