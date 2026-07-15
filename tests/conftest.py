from __future__ import annotations

import shutil
from pathlib import Path

import pytest


@pytest.fixture
def repository_root() -> Path:
    return Path(__file__).parents[1]


@pytest.fixture
def isolated_repository(tmp_path: Path, repository_root: Path) -> Path:
    for directory in ("schemas", "templates"):
        shutil.copytree(repository_root / directory, tmp_path / directory)
    return tmp_path
