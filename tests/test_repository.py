from __future__ import annotations

from pathlib import Path

import pytest

from spec_viewer.errors import SpecViewerError
from spec_viewer.normalization import sha256_file
from spec_viewer.repository import validate_repository, validate_skill_frontmatter
from spec_viewer.schema import load_document


def test_repository_contracts_pass(repository_root: Path) -> None:
    validate_repository(repository_root)


def test_invalid_skill_frontmatter_fails(tmp_path: Path) -> None:
    skill = tmp_path / "SKILL.md"
    skill.write_text("# Missing frontmatter\n", encoding="utf-8")
    with pytest.raises(SpecViewerError, match="frontmatter"):
        validate_skill_frontmatter(skill)


def test_synthetic_workspace_hashes_match(repository_root: Path) -> None:
    workspace = repository_root / "examples/synthetic-workspace-example/workspace"
    project = load_document(workspace / "project.yaml")
    assert (
        sha256_file(workspace / project["source"]["original_file"])
        == project["source"]["source_hash"]
    )
    assert (
        sha256_file(workspace / project["source"]["normalized_file"])
        == project["source"]["normalized_hash"]
    )
