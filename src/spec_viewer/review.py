"""Deterministic preparation and finalization for AI-authored review runs."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

from .errors import SpecViewerError
from .manifest import atomic_yaml_write
from .normalization import sha256_file
from .runs import create_run
from .schema import load_document, validate_file
from .workspace import validate_workspace

REVIEW_FILES = (
    "review-report.md",
    "review-summary.yaml",
    "issue-register.yaml",
    "clarification-questions.md",
    "clarification-register.yaml",
    "run-metadata.yaml",
)


def _safe_run(workspace: Path, run_path: Path) -> Path:
    resolved_workspace = workspace.resolve()
    resolved = run_path.resolve()
    expected_parent = resolved_workspace / "artifacts/review"
    if resolved.parent != expected_parent or resolved.is_symlink():
        raise SpecViewerError("Review run path must be a direct child of artifacts/review.")
    return resolved


def prepare_review(
    workspace: Path,
    repository_root: Path,
    run_id: str | None = None,
) -> Path:
    """Create a running review run populated with valid artifact templates."""
    validate_workspace(workspace, repository_root)
    project_path = workspace / "project.yaml"
    project = load_document(project_path)
    normalized_relative = project["source"]["normalized_file"]
    if project["status"]["lifecycle"] != "normalized" or normalized_relative is None:
        raise SpecViewerError("Normalize a source document before preparing a review.")
    normalized = workspace / normalized_relative
    if not normalized.is_file() or sha256_file(normalized) != project["source"]["normalized_hash"]:
        raise SpecViewerError("Normalized document is missing or its hash has changed.")
    relative = create_run(workspace, repository_root, "review", run_id)
    run_path = workspace / relative
    template_root = repository_root / "templates/review"
    for name in REVIEW_FILES[:-1]:
        shutil.copyfile(template_root / name, run_path / name)
    summary_path = run_path / "review-summary.yaml"
    summary = load_document(summary_path)
    summary["run_id"] = run_path.name
    summary["project_id"] = project["project"]["id"]
    summary_path.write_text(
        yaml.safe_dump(summary, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    issue_path = run_path / "issue-register.yaml"
    issues = load_document(issue_path)
    issues["run_id"] = run_path.name
    issue_path.write_text(
        yaml.safe_dump(issues, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    metadata_path = run_path / "run-metadata.yaml"
    metadata = load_document(metadata_path)
    metadata["status"] = "running"
    metadata["skill_version"] = "0.2.0"
    metadata["methodology_version"] = "1.0"
    metadata["input_hashes"] = {"normalized_specification": project["source"]["normalized_hash"]}
    atomic_yaml_write(
        metadata_path,
        metadata,
        load_document(repository_root / "schemas/run-metadata.schema.json"),
    )
    return relative


def _unique_ids(items: list[dict[str, Any]], label: str) -> set[str]:
    identifiers = [item["id"] for item in items]
    if len(identifiers) != len(set(identifiers)):
        raise SpecViewerError(f"Duplicate {label} IDs are not allowed.")
    return set(identifiers)


def finalize_review(workspace: Path, run_path: Path, repository_root: Path) -> None:
    """Cross-validate review artifacts, complete the run, and update project pointers."""
    validate_workspace(workspace, repository_root)
    run_path = _safe_run(workspace, run_path)
    missing = [name for name in REVIEW_FILES if not (run_path / name).is_file()]
    if missing:
        raise SpecViewerError("Review run is incomplete: " + ", ".join(missing))
    schema_pairs = (
        ("review-summary.schema.json", "review-summary.yaml"),
        ("issue-register.schema.json", "issue-register.yaml"),
        ("clarification-register.schema.json", "clarification-register.yaml"),
        ("run-metadata.schema.json", "run-metadata.yaml"),
    )
    for schema_name, artifact_name in schema_pairs:
        validate_file(repository_root / "schemas" / schema_name, run_path / artifact_name)
    summary = load_document(run_path / "review-summary.yaml")
    register = load_document(run_path / "issue-register.yaml")
    clarifications = load_document(run_path / "clarification-register.yaml")
    metadata = load_document(run_path / "run-metadata.yaml")
    if metadata["status"] == "completed":
        raise SpecViewerError("Completed run cannot be overwritten.")
    if summary["run_id"] != run_path.name or register["run_id"] != run_path.name:
        raise SpecViewerError("Review artifact run IDs do not match the run directory.")
    issue_ids = _unique_ids(register["issues"], "issue")
    question_ids = _unique_ids(clarifications["questions"], "question")
    referenced_questions = {
        question_id for issue in register["issues"] for question_id in issue["question_ids"]
    }
    if referenced_questions - question_ids:
        raise SpecViewerError("An issue references an unknown clarification question.")
    counts = {severity: 0 for severity in ("critical", "high", "medium", "low")}
    for issue in register["issues"]:
        counts[issue["severity"]] += 1
    if summary["issue_counts"] != counts:
        raise SpecViewerError("Review summary issue counts do not match the issue register.")
    blocking_count = sum(
        question["priority"] == "blocking" and question["status"] == "open"
        for question in clarifications["questions"]
    )
    if summary["blocking_question_count"] != blocking_count:
        raise SpecViewerError("Review summary blocking count does not match clarifications.")
    if not issue_ids and summary["readiness"] != "IMPLEMENTATION_READY":
        raise SpecViewerError("A review without issues must be marked IMPLEMENTATION_READY.")
    for markdown_name in ("review-report.md", "clarification-questions.md"):
        if len((run_path / markdown_name).read_text(encoding="utf-8").strip()) < 20:
            raise SpecViewerError(f"Review artifact is empty: {markdown_name}")
    metadata["status"] = "completed"
    metadata["confidence"] = summary["overall_confidence"]
    atomic_yaml_write(
        run_path / "run-metadata.yaml",
        metadata,
        load_document(repository_root / "schemas/run-metadata.schema.json"),
    )
    project_path = workspace / "project.yaml"
    project = load_document(project_path)
    project["status"]["lifecycle"] = "awaiting_answers" if blocking_count else "reviewed"
    project["status"]["specification_readiness"] = summary["readiness"]
    relative_run = run_path.relative_to(workspace).as_posix()
    project["latest_runs"]["review"] = relative_run
    project["latest_artifacts"]["review_report"] = f"{relative_run}/review-report.md"
    project["latest_artifacts"]["issue_register"] = f"{relative_run}/issue-register.yaml"
    project["open_items"]["critical_issues"] = counts["critical"]
    project["open_items"]["high_issues"] = counts["high"]
    project["open_items"]["unanswered_blocking_questions"] = blocking_count
    atomic_yaml_write(
        project_path,
        project,
        load_document(repository_root / "schemas/project.schema.json"),
    )
