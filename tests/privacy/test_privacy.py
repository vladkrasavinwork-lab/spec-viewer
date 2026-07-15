from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from spec_viewer.errors import SpecViewerError
from spec_viewer.privacy import scan_secrets, validate_paths


@pytest.mark.parametrize("path", ["workspaces/demo/source.md", "nested/demo_private/file.txt"])
def test_rejects_private_paths(repository_root: Path, path: str) -> None:
    with pytest.raises(SpecViewerError, match="Privacy validation failed"):
        validate_paths(repository_root, [path])


def test_force_added_private_path_is_detectable(tmp_path: Path) -> None:
    subprocess.run(("git", "init"), cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / ".gitignore").write_text("workspaces/\n", encoding="utf-8")
    private = tmp_path / "workspaces/demo_private"
    private.mkdir(parents=True)
    (private / "data.txt").write_text("fictional", encoding="utf-8")
    subprocess.run(
        ("git", "add", "-f", "workspaces/demo_private/data.txt"), cwd=tmp_path, check=True
    )
    tracked = subprocess.run(
        ("git", "ls-files"), cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    with pytest.raises(SpecViewerError, match="private path"):
        validate_paths(tmp_path, tracked)


def test_allows_normal_source_and_env_example(repository_root: Path) -> None:
    validate_paths(repository_root, ["src/spec_viewer/cli.py", ".env.example"])


@pytest.mark.parametrize(
    "path", ["customer.pdf", "docs/input.docx", "examples/unclassified/source.odt"]
)
def test_rejects_unapproved_documents(repository_root: Path, path: str) -> None:
    with pytest.raises(SpecViewerError, match="unapproved source document"):
        validate_paths(repository_root, [path])


def test_allows_approved_synthetic_document(tmp_path: Path, repository_root: Path) -> None:
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    (schemas / "example-classification.schema.json").write_bytes(
        (repository_root / "schemas/example-classification.schema.json").read_bytes()
    )
    example = tmp_path / "examples/demo"
    example.mkdir(parents=True)
    (example / "classification.yaml").write_text(
        "schema_version: '1.0'\n"
        "data_classification: public_synthetic\n"
        "sanitized: true\n"
        "contains_real_customer_data: false\n"
        "approved_for_repository: true\n",
        encoding="utf-8",
    )
    validate_paths(tmp_path, ["examples/demo/source.pdf"])


@pytest.mark.parametrize("path", [".env", "config/.env.local", "credentials.json"])
def test_rejects_credential_files(repository_root: Path, path: str) -> None:
    with pytest.raises(SpecViewerError, match="credential"):
        validate_paths(repository_root, [path])


def test_detects_private_key_without_real_secret(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture.txt"
    fixture.write_text(
        "-----BEGIN PRIVATE KEY-----\nsynthetic-test-marker",  # secret-scan: allow
        encoding="utf-8",
    )
    with pytest.raises(SpecViewerError, match="Probable secret"):
        scan_secrets(tmp_path, ["fixture.txt"])
