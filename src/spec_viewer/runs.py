"""Immutable run-directory creation."""

from __future__ import annotations

import re
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .errors import SpecViewerError
from .schema import load_document, validate_file

SKILLS = {
    "review": "product-spec-review",
    "rewrite": "product-spec-rewrite",
    "estimate": "product-delivery-estimate",
}
RUN_ID_PATTERN = re.compile(r"^\d{8}T\d{6}Z-(review|rewrite|estimate)$")


def make_run_id(skill_type: str, now: datetime | None = None) -> str:
    """Create a UTC run identifier for a supported skill type."""
    if skill_type not in SKILLS:
        raise SpecViewerError("Invalid run skill suffix.")
    instant = (now or datetime.now(UTC)).astimezone(UTC)
    return f"{instant.strftime('%Y%m%dT%H%M%SZ')}-{skill_type}"


def create_run(
    workspace: Path,
    repository_root: Path,
    skill_type: str,
    run_id: str | None = None,
) -> Path:
    """Atomically create a pending run without overwriting any existing path."""
    identifier = run_id or make_run_id(skill_type)
    if (
        skill_type not in SKILLS
        or not RUN_ID_PATTERN.fullmatch(identifier)
        or not identifier.endswith(f"-{skill_type}")
    ):
        raise SpecViewerError("Invalid run ID or skill suffix.")
    project = load_document(workspace / "project.yaml")
    project_id = project["project"]["id"]
    parent = workspace / "artifacts" / skill_type
    destination = parent / identifier
    if destination.exists():
        metadata = destination / "run-metadata.yaml"
        if metadata.exists() and load_document(metadata).get("status") == "completed":
            raise SpecViewerError("Completed run cannot be overwritten.")
        raise SpecViewerError("Run already exists.")
    parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".run-", dir=parent))
    metadata_data: dict[str, Any] = {
        "schema_version": "1.0",
        "run_id": identifier,
        "project_id": project_id,
        "skill_name": SKILLS[skill_type],
        "skill_version": "0.1.0-placeholder",
        "methodology_version": "0.1.0-placeholder",
        "input_hashes": {},
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "pending",
        "confidence": None,
        "error": None,
    }
    try:
        metadata = temporary / "run-metadata.yaml"
        metadata.write_text(yaml.safe_dump(metadata_data, sort_keys=False), encoding="utf-8")
        validate_file(repository_root / "schemas/run-metadata.schema.json", metadata)
        temporary.rename(destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return destination.relative_to(workspace)
