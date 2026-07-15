from __future__ import annotations

import copy
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from spec_viewer.errors import SpecViewerError
from spec_viewer.schema import load_document, validate_data, validate_file

CASES = (
    ("project.schema.json", "templates/workspace/project.yaml"),
    ("document-metadata.schema.json", "templates/workspace/normalized/document-metadata.yaml"),
    ("run-metadata.schema.json", "templates/runs/run-metadata.yaml"),
    ("review-summary.schema.json", "templates/review/review-summary.yaml"),
    ("issue-register.schema.json", "templates/review/issue-register.yaml"),
    ("clarification-register.schema.json", None),
    ("assumption-register.schema.json", "templates/rewrite/assumption-register.yaml"),
    ("change-register.schema.json", "templates/rewrite/change-register.yaml"),
    (
        "requirement-traceability.schema.json",
        "templates/rewrite/requirement-traceability.yaml",
    ),
    ("example-classification.schema.json", "templates/examples/classification.yaml"),
)


def _minimal(name: str) -> dict[str, Any]:
    if name == "clarification-register.schema.json":
        return {"schema_version": "1.0", "questions": []}
    raise AssertionError(name)


@pytest.mark.parametrize("schema_name,document", CASES)
def test_valid_schema_fixture(
    repository_root: Path, schema_name: str, document: str | None
) -> None:
    schema_path = repository_root / "schemas" / schema_name
    if document:
        validate_file(schema_path, repository_root / document)
    else:
        validate_data(_minimal(schema_name), load_document(schema_path))


@pytest.mark.parametrize("schema_name,document", CASES)
def test_rejects_missing_required_and_unknown_field(
    repository_root: Path, schema_name: str, document: str | None
) -> None:
    schema = load_document(repository_root / "schemas" / schema_name)
    data = load_document(repository_root / document) if document else _minimal(schema_name)
    missing = copy.deepcopy(data)
    missing.pop("schema_version")
    with pytest.raises(SpecViewerError):
        validate_data(missing, schema)
    unknown = copy.deepcopy(data)
    unknown["unexpected"] = True
    with pytest.raises(SpecViewerError):
        validate_data(unknown, schema)


def test_project_rejects_invalid_enum_type_and_path(repository_root: Path) -> None:
    schema = load_document(repository_root / "schemas/project.schema.json")
    data = load_document(repository_root / "templates/workspace/project.yaml")
    mutations: tuple[Callable[[dict[str, Any]], None], ...] = (
        lambda item: item["status"].update(lifecycle="invalid"),
        lambda item: item["open_items"].update(critical_issues="one"),
        lambda item: item["source"].update(original_file="../secret.pdf"),
    )
    for mutate in mutations:
        invalid = copy.deepcopy(data)
        mutate(invalid)
        with pytest.raises(SpecViewerError):
            validate_data(invalid, schema)
