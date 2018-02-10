mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
project_dir := $(dir $(mkfile_path))

.PHONY: clean clean-test clean-pyc clean-build docs help wheel
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts
	git clean -dxf

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -rf .pytest_cache
	rm -f .coverage
	rm -fr htmlcov/

lint: ## check style with flake8
	flake8 src/gpopup tests

test: ## run tests quickly with the default Python
	python -m pytest -v --cov=gpopup $(project_dir)/tests

test-tox:
	tox
	tox -e examples

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/gpopup.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ src/gpopup
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes (requires python-watchdog)
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .
# watchmedo is a program found in python-watchdog

dist: clean ## builds source and wheel package (requires python-wheel)
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

install_user: ## install the package to the user's home directory
	pip install --user $(project_dir)

install_develop: ## install the package to the user's home directory as symlinks
	pip install --user -e $(project_dir)

uninstall: ## install the package
	-pip uninstall gpopup

wheel:
	@python setup.py bdist_wheel

