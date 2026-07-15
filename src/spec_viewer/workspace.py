"""Atomic private workspace initialization and validation."""

from __future__ import annotations

import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any

import yaml

from .errors import SpecViewerError
from .paths import contained_path, is_safe_relative_path, normalize_slug
from .schema import load_document, validate_file

DIRECTORIES = (
    "source",
    "normalized/media",
    "context",
    "artifacts/review",
    "artifacts/rewrite",
    "artifacts/estimate",
)
TEMPLATE_FILES = (
    "README.md",
    "context/project-context.md",
    "context/glossary.md",
    "context/constraints.md",
    "context/stakeholder-answers.md",
    "context/estimation-inputs.yaml",
    "normalized/document-metadata.yaml",
    "normalized/conversion-warnings.md",
)


def project_manifest(name: str, slug: str) -> dict[str, Any]:
    """Build a new Stage 1 project manifest."""
    return {
        "schema_version": "1.0",
        "project": {
            "id": f"PRJ-{uuid.uuid4().hex[:12].upper()}",
            "slug": slug,
            "name": name.strip(),
            "privacy": "private",
            "source_language": None,
            "output_language": None,
        },
        "status": {"lifecycle": "created", "specification_readiness": None},
        "source": {
            "original_file": None,
            "normalized_file": None,
            "source_hash": None,
            "normalized_hash": None,
        },
        "latest_runs": {"review": None, "rewrite": None, "estimate": None},
        "latest_artifacts": {
            "review_report": None,
            "issue_register": None,
            "revised_specification": None,
            "estimate_report": None,
        },
        "open_items": {
            "critical_issues": 0,
            "high_issues": 0,
            "unanswered_blocking_questions": 0,
            "unresolved_assumptions": 0,
        },
    }


def init_workspace(name: str, workspace_root: Path, repository_root: Path) -> Path:
    """Create a complete workspace through an atomic directory rename."""
    slug = normalize_slug(name)
    workspace_root.mkdir(parents=True, exist_ok=True)
    if workspace_root.is_symlink():
        raise SpecViewerError("Resolved path escapes the workspace root.")
    destination = contained_path(workspace_root, f"{slug}_private")
    if destination.exists() or destination.is_symlink():
        raise SpecViewerError("Workspace already exists.")
    template_root = repository_root / "templates" / "workspace"
    temporary = Path(tempfile.mkdtemp(prefix=".workspace-", dir=workspace_root.resolve()))
    try:
        for directory in DIRECTORIES:
            (temporary / directory).mkdir(parents=True, exist_ok=True)
        for relative in TEMPLATE_FILES:
            source = template_root / relative
            target = temporary / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        manifest_path = temporary / "project.yaml"
        manifest_path.write_text(
            yaml.safe_dump(project_manifest(name, slug), sort_keys=False), encoding="utf-8"
        )
        validate_file(repository_root / "schemas/project.schema.json", manifest_path)
        temporary.rename(destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return destination.relative_to(repository_root.resolve())


def validate_workspace(workspace: Path, repository_root: Path) -> None:
    """Validate workspace location, required structure, symlinks, and manifest."""
    if not workspace.name.endswith("_private") or workspace.is_symlink():
        raise SpecViewerError("Invalid private workspace path.")
    for path in workspace.rglob("*"):
        if path.is_symlink():
            raise SpecViewerError(f"Symbolic links are not allowed in workspaces: {path}")
    required = ("project.yaml", *DIRECTORIES, *TEMPLATE_FILES)
    missing = [relative for relative in required if not (workspace / relative).exists()]
    if missing:
        raise SpecViewerError("Workspace is incomplete: " + ", ".join(missing))
    validate_file(repository_root / "schemas/project.schema.json", workspace / "project.yaml")
    data = load_document(workspace / "project.yaml")
    if (
        not isinstance(data, dict)
        or data.get("project", {}).get("slug") + "_private" != workspace.name
    ):
        raise SpecViewerError("Workspace directory does not match the project slug.")
    path_values = (
        data["source"]["original_file"],
        data["source"]["normalized_file"],
        *data["latest_runs"].values(),
        *data["latest_artifacts"].values(),
    )
    if any(value is not None and not is_safe_relative_path(value) for value in path_values):
        raise SpecViewerError("Workspace manifest contains an unsafe relative path.")
