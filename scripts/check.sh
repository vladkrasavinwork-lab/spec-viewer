#!/usr/bin/env bash
set -euo pipefail

python -m ruff format --check .
python -m ruff check .
python -m mypy src tests
python -m pytest
python -m spec_viewer repository validate
python -m spec_viewer privacy check
