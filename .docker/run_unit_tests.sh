#!/bin/bash
set -e
$PYTHON -m pip install pytest-xvfb
$PYTHON -m pip install /app
$PYTHON -m pytest -v --cov=gpopup --cov-report term-missing /app/tests
