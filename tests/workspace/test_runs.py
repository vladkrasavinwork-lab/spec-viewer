from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from spec_viewer.errors import SpecViewerError
from spec_viewer.runs import RUN_ID_PATTERN, create_run, make_run_id
from spec_viewer.schema import validate_file
from spec_viewer.workspace import init_workspace


def _workspace(repository: Path) -> Path:
    relative = init_workspace("Run Demo", repository / "workspaces", repository)
    return repository / relative


def test_run_id_and_creation(isolated_repository: Path) -> None:
    workspace = _workspace(isolated_repository)
    run_id = "20260715T143000Z-review"
    relative = create_run(workspace, isolated_repository, "review", run_id)
    metadata = workspace / relative / "run-metadata.yaml"
    assert RUN_ID_PATTERN.fullmatch(make_run_id("review"))
    assert relative.as_posix() == f"artifacts/review/{run_id}"
    validate_file(isolated_repository / "schemas/run-metadata.schema.json", metadata)


def test_duplicate_and_completed_run_are_rejected(isolated_repository: Path) -> None:
    workspace = _workspace(isolated_repository)
    run_id = "20260715T143000Z-review"
    relative = create_run(workspace, isolated_repository, "review", run_id)
    with pytest.raises(SpecViewerError, match="already exists"):
        create_run(workspace, isolated_repository, "review", run_id)
    metadata = workspace / relative / "run-metadata.yaml"
    data = yaml.safe_load(metadata.read_text())
    data["status"] = "completed"
    metadata.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(SpecViewerError, match="Completed run"):
        create_run(workspace, isolated_repository, "review", run_id)


@pytest.mark.parametrize(
    "skill,run_id",
    [("other", None), ("review", "bad-review"), ("review", "20260715T143000Z-rewrite")],
)
def test_invalid_run_identifiers(isolated_repository: Path, skill: str, run_id: str | None) -> None:
    with pytest.raises(SpecViewerError, match="Invalid"):
        create_run(_workspace(isolated_repository), isolated_repository, skill, run_id)
