"""Deterministic preparation and finalization for AI-authored specification rewrites."""

from __future__ import annotations

import re
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

REWRITE_MODES = {"conservative", "structured", "implementation-ready"}
REWRITE_FILES = (
    "revised-specification.md",
    "change-log.md",
    "change-register.yaml",
    "assumption-register.yaml",
    "unresolved-questions.md",
    "requirement-traceability.yaml",
    "run-metadata.yaml",
)


def answered_question_ids(path: Path) -> set[str]:
    """Extract question IDs with a non-empty answer from the stakeholder Markdown file."""
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    headings = list(re.finditer(r"(?m)^##\s+(Q-[0-9]{3,})\b", text))
    answered: set[str] = set()
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        block = text[heading.end() : end]
        answer = re.search(
            r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?(?:Answer|Ответ)(?:\*\*)?:\s*(.+)$",
            block,
        )
        if answer and answer.group(1).strip() not in {"", "-", "null", "TODO"}:
            answered.add(heading.group(1))
    return answered


def _safe_run(workspace: Path, run_path: Path) -> Path:
    resolved = run_path.resolve()
    if resolved.parent != workspace.resolve() / "artifacts/rewrite" or resolved.is_symlink():
        raise SpecViewerError("Rewrite run path must be a direct child of artifacts/rewrite.")
    return resolved


def _review_inputs(workspace: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    project = load_document(workspace / "project.yaml")
    review_relative = project["latest_runs"]["review"]
    if review_relative is None:
        raise SpecViewerError("Complete a specification review before preparing a rewrite.")
    review_path = workspace / review_relative
    metadata = load_document(review_path / "run-metadata.yaml")
    if metadata["status"] != "completed":
        raise SpecViewerError("The current review run is not completed.")
    return (
        review_path,
        load_document(review_path / "issue-register.yaml"),
        load_document(review_path / "clarification-register.yaml"),
    )


def prepare_rewrite(
    workspace: Path,
    repository_root: Path,
    mode: str = "conservative",
    run_id: str | None = None,
) -> Path:
    """Create a running rewrite populated with traceable artifact templates."""
    validate_workspace(workspace, repository_root)
    if mode not in REWRITE_MODES:
        raise SpecViewerError("Invalid rewrite mode.")
    project = load_document(workspace / "project.yaml")
    normalized = workspace / project["source"]["normalized_file"]
    if not normalized.is_file() or sha256_file(normalized) != project["source"]["normalized_hash"]:
        raise SpecViewerError("Normalized document is missing or its hash has changed.")
    review_path, _, _ = _review_inputs(workspace)
    relative = create_run(workspace, repository_root, "rewrite", run_id)
    run_path = workspace / relative
    template_root = repository_root / "templates/rewrite"
    for name in REWRITE_FILES[:-1]:
        shutil.copyfile(template_root / name, run_path / name)
    for name in (
        "change-register.yaml",
        "assumption-register.yaml",
        "requirement-traceability.yaml",
    ):
        path = run_path / name
        data = load_document(path)
        data["run_id"] = run_path.name
        if name == "change-register.yaml":
            data["mode"] = mode
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    metadata_path = run_path / "run-metadata.yaml"
    metadata = load_document(metadata_path)
    metadata["status"] = "running"
    metadata["skill_version"] = "0.3.0"
    metadata["methodology_version"] = "1.0"
    metadata["input_hashes"] = {
        "normalized_specification": sha256_file(normalized),
        "issue_register": sha256_file(review_path / "issue-register.yaml"),
        "clarification_register": sha256_file(review_path / "clarification-register.yaml"),
        "stakeholder_answers": sha256_file(workspace / "context/stakeholder-answers.md"),
    }
    atomic_yaml_write(
        metadata_path,
        metadata,
        load_document(repository_root / "schemas/run-metadata.schema.json"),
    )
    return relative


def _unique_ids(items: list[dict[str, Any]], label: str, key: str = "id") -> set[str]:
    identifiers = [item[key] for item in items]
    if len(identifiers) != len(set(identifiers)):
        raise SpecViewerError(f"Duplicate {label} IDs are not allowed.")
    return set(identifiers)


def finalize_rewrite(workspace: Path, run_path: Path, repository_root: Path) -> None:
    """Validate provenance, block unanswered decisions, and complete a rewrite run."""
    validate_workspace(workspace, repository_root)
    run_path = _safe_run(workspace, run_path)
    missing = [name for name in REWRITE_FILES if not (run_path / name).is_file()]
    if missing:
        raise SpecViewerError("Rewrite run is incomplete: " + ", ".join(missing))
    schema_pairs = (
        ("change-register.schema.json", "change-register.yaml"),
        ("assumption-register.schema.json", "assumption-register.yaml"),
        ("requirement-traceability.schema.json", "requirement-traceability.yaml"),
        ("run-metadata.schema.json", "run-metadata.yaml"),
    )
    for schema_name, artifact_name in schema_pairs:
        validate_file(repository_root / "schemas" / schema_name, run_path / artifact_name)
    review_path, issue_register, clarification_register = _review_inputs(workspace)
    answers_path = workspace / "context/stakeholder-answers.md"
    answered_ids = answered_question_ids(answers_path)
    answered_ids.update(
        question["id"]
        for question in clarification_register["questions"]
        if question["status"] == "answered" and question["answer"]
    )
    blocking_ids = {
        question["id"]
        for question in clarification_register["questions"]
        if question["priority"] == "blocking"
        and question["status"] == "open"
        and question["id"] not in answered_ids
    }
    if blocking_ids:
        unresolved_text = (run_path / "unresolved-questions.md").read_text(encoding="utf-8")
        if not all(question_id in unresolved_text for question_id in blocking_ids):
            raise SpecViewerError("All unanswered blocking questions must be preserved explicitly.")
        raise SpecViewerError(
            "Rewrite cannot be completed while blocking questions remain unanswered: "
            + ", ".join(sorted(blocking_ids))
        )
    changes = load_document(run_path / "change-register.yaml")
    assumptions = load_document(run_path / "assumption-register.yaml")
    traceability = load_document(run_path / "requirement-traceability.yaml")
    metadata = load_document(run_path / "run-metadata.yaml")
    if metadata["status"] == "completed":
        raise SpecViewerError("Completed run cannot be overwritten.")
    for artifact in (changes, assumptions, traceability):
        if artifact["run_id"] != run_path.name:
            raise SpecViewerError("Rewrite artifact run IDs do not match the run directory.")
    issue_ids = _unique_ids(issue_register["issues"], "issue")
    change_ids = _unique_ids(changes["changes"], "change")
    assumption_ids = _unique_ids(assumptions["assumptions"], "assumption")
    traced_requirement_ids = _unique_ids(
        traceability["entries"], "requirement", key="requirement_id"
    )
    revised_text = (run_path / "revised-specification.md").read_text(encoding="utf-8")
    revised_requirement_ids = set(re.findall(r"\b(?:REQ|NFR)-[A-Z0-9]+-[0-9]{3,}\b", revised_text))
    if traced_requirement_ids != revised_requirement_ids:
        missing_ids = sorted(revised_requirement_ids - traced_requirement_ids)
        extra_ids = sorted(traced_requirement_ids - revised_requirement_ids)
        raise SpecViewerError(
            "Requirement traceability does not match the revised specification. "
            f"Missing: {missing_ids}; extra: {extra_ids}."
        )
    for change in changes["changes"]:
        if set(change["source_issue_ids"]) - issue_ids:
            raise SpecViewerError("A change references an unknown review issue.")
        if set(change["answer_ids"]) - answered_ids:
            raise SpecViewerError("A change references an unanswered stakeholder question.")
        if set(change["assumption_ids"]) - assumption_ids:
            raise SpecViewerError("A change references an unknown assumption.")
    for entry in traceability["entries"]:
        if set(entry["issue_ids"]) - issue_ids:
            raise SpecViewerError("Traceability references an unknown review issue.")
        if set(entry["answer_ids"]) - answered_ids:
            raise SpecViewerError("Traceability references an unanswered stakeholder question.")
        if set(entry["assumption_ids"]) - assumption_ids:
            raise SpecViewerError("Traceability references an unknown assumption.")
        if set(entry["change_ids"]) - change_ids:
            raise SpecViewerError("Traceability references an unknown change.")
    if changes["mode"] == "implementation-ready" and any(
        assumption["status"] == "unconfirmed" for assumption in assumptions["assumptions"]
    ):
        raise SpecViewerError("Implementation-ready mode cannot contain unconfirmed assumptions.")
    for markdown_name in ("revised-specification.md", "change-log.md", "unresolved-questions.md"):
        if len((run_path / markdown_name).read_text(encoding="utf-8").strip()) < 20:
            raise SpecViewerError(f"Rewrite artifact is empty: {markdown_name}")
    normalized = workspace / "normalized/specification.md"
    if metadata["input_hashes"]["normalized_specification"] != sha256_file(normalized):
        raise SpecViewerError("Normalized source changed after the rewrite run started.")
    if metadata["input_hashes"]["issue_register"] != sha256_file(
        review_path / "issue-register.yaml"
    ):
        raise SpecViewerError("Review issues changed after the rewrite run started.")
    if metadata["input_hashes"]["clarification_register"] != sha256_file(
        review_path / "clarification-register.yaml"
    ):
        raise SpecViewerError("Review clarifications changed after the rewrite run started.")
    if metadata["input_hashes"]["stakeholder_answers"] != sha256_file(answers_path):
        raise SpecViewerError("Stakeholder answers changed after the rewrite run started.")
    metadata["status"] = "completed"
    metadata["confidence"] = "high" if not assumptions["assumptions"] else "medium"
    atomic_yaml_write(
        run_path / "run-metadata.yaml",
        metadata,
        load_document(repository_root / "schemas/run-metadata.schema.json"),
    )
    project_path = workspace / "project.yaml"
    project = load_document(project_path)
    relative_run = run_path.relative_to(workspace).as_posix()
    project["status"]["lifecycle"] = "rewritten"
    project["latest_runs"]["rewrite"] = relative_run
    project["latest_artifacts"]["revised_specification"] = (
        f"{relative_run}/revised-specification.md"
    )
    project["open_items"]["unresolved_assumptions"] = sum(
        assumption["status"] == "unconfirmed" for assumption in assumptions["assumptions"]
    )
    project["open_items"]["unanswered_blocking_questions"] = 0
    atomic_yaml_write(
        project_path,
        project,
        load_document(repository_root / "schemas/project.schema.json"),
    )
