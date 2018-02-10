mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
project_dir := $(dir $(mkfile_path))

.DEFAULT_GOAL := help
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
.PHONY: help
help: ## Print this help message.
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: clean
clean: ## Clean build and test related files.
	git clean -dXf

.PHONY: clean-all
clean-all: clean ## Remove all files that aren't tracked by git.
	git clean -dxf

.PHONY: test
test: ## Run tests in current python environment with pytest.
	python -m pytest -v --cov=gpopup $(project_dir)/tests

.PHONY: test-tox
test-tox: ## Run tests using tox.
	tox
	tox -e examples

.PHONY: dist
dist: clean ## Build source and wheel packages.
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

.PHONY: install
install: ## Install the package to the active Python's site-packages.
	pip install $(project_dir)

.PHONY: install-user
install-user: ## Install the package to the user's home directory.
	pip install --user $(project_dir)

.PHONY: uninstall
uninstall: ## Uninstall the package.
	-pip uninstall gpopup
