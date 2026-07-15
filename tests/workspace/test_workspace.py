from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from spec_viewer.errors import SpecViewerError
from spec_viewer.schema import load_document
from spec_viewer.workspace import init_workspace, validate_workspace


def test_initializes_normalized_private_workspace(isolated_repository: Path) -> None:
    relative = init_workspace(
        "Customer Portal", isolated_repository / "workspaces", isolated_repository
    )
    workspace = isolated_repository / relative

    assert relative.as_posix() == "workspaces/customer-portal_private"
    assert (workspace / "source").is_dir()
    assert (workspace / "normalized/media").is_dir()
    assert (workspace / "artifacts/review").is_dir()
    assert load_document(workspace / "project.yaml")["status"]["lifecycle"] == "created"
    validate_workspace(workspace, isolated_repository)


def test_duplicate_workspace_is_rejected_without_modification(isolated_repository: Path) -> None:
    root = isolated_repository / "workspaces"
    relative = init_workspace("Customer Portal", root, isolated_repository)
    marker = isolated_repository / relative / "context/project-context.md"
    before = marker.read_bytes()

    with pytest.raises(SpecViewerError, match="already exists"):
        init_workspace("Customer Portal", root, isolated_repository)

    assert marker.read_bytes() == before


@pytest.mark.parametrize(
    "name", ["../../outside", "/tmp/project", r"..\\outside", "nested/path", "", "bad\x01name"]
)
def test_rejects_unsafe_project_names(isolated_repository: Path, name: str) -> None:
    with pytest.raises(SpecViewerError, match="Invalid project slug"):
        init_workspace(name, isolated_repository / "workspaces", isolated_repository)


def test_rejects_workspace_root_symlink(isolated_repository: Path, tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    root = isolated_repository / "workspaces"
    root.symlink_to(outside, target_is_directory=True)
    with pytest.raises(SpecViewerError, match="escapes"):
        init_workspace("Safe Name", root, isolated_repository)


def test_workspace_validation_rejects_windows_absolute_manifest_path(
    isolated_repository: Path,
) -> None:
    relative = init_workspace(
        "Windows Path", isolated_repository / "workspaces", isolated_repository
    )
    workspace = isolated_repository / relative
    manifest = workspace / "project.yaml"
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    data["source"]["original_file"] = r"C:\\customer\\spec.docx"
    manifest.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(SpecViewerError, match="unsafe relative path"):
        validate_workspace(workspace, isolated_repository)
