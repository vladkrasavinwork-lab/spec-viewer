from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from spec_viewer.errors import SpecViewerError
from spec_viewer.normalization import normalize_document
from spec_viewer.review import finalize_review, prepare_review
from spec_viewer.rewrite import answered_question_ids, finalize_rewrite, prepare_rewrite
from spec_viewer.schema import load_document
from spec_viewer.workspace import init_workspace

REVIEW_ID = "20260716T100000Z-review"
REWRITE_ID = "20260716T110000Z-rewrite"


def _workspace(repository: Path, tmp_path: Path) -> Path:
    relative = init_workspace("Rewrite Demo", repository / "workspaces", repository)
    workspace = repository / relative
    source = tmp_path / "spec.md"
    source.write_text("# Demo\n\nThe editor can publish an article.\n", encoding="utf-8")
    normalize_document(workspace, source, repository)
    return workspace


def _complete_review(repository: Path, workspace: Path, blocking: bool = False) -> None:
    run = workspace / prepare_review(workspace, repository, REVIEW_ID)
    summary = load_document(run / "review-summary.yaml")
    summary["category_scores"] = {key: 4 for key in summary["category_scores"]}
    summary["overall_confidence"] = "high"
    summary["readiness"] = "DISCOVERY_REQUIRED" if blocking else "IMPLEMENTATION_READY"
    summary["issue_counts"] = {
        "critical": 0,
        "high": 1 if blocking else 0,
        "medium": 0,
        "low": 0,
    }
    summary["blocking_question_count"] = 1 if blocking else 0
    (run / "review-summary.yaml").write_text(yaml.safe_dump(summary), encoding="utf-8")
    issues: dict[str, Any] = {"schema_version": "1.0", "run_id": REVIEW_ID, "issues": []}
    questions: dict[str, Any] = {"schema_version": "1.0", "questions": []}
    if blocking:
        issues["issues"] = [
            {
                "id": "ISSUE-001",
                "type": "undefined_business_rule",
                "severity": "high",
                "confidence": "high",
                "source": {"section": "Demo", "heading": "Demo", "excerpt": "publish"},
                "problem": "Approval is undefined.",
                "impact": ["workflow"],
                "resolution_strategy": "decision_required",
                "question_ids": ["Q-001"],
                "status": "open",
            }
        ]
        questions["questions"] = [
            {
                "id": "Q-001",
                "priority": "blocking",
                "category": "Workflow",
                "question": "Who approves publication?",
                "reason": "Approval changes the workflow.",
                "affected_requirements": [],
                "status": "open",
                "answer": None,
                "answer_metadata": None,
            }
        ]
    (run / "issue-register.yaml").write_text(yaml.safe_dump(issues), encoding="utf-8")
    (run / "clarification-register.yaml").write_text(yaml.safe_dump(questions), encoding="utf-8")
    (run / "review-report.md").write_text(
        "# Review\n\nCompleted synthetic review.\n", encoding="utf-8"
    )
    (run / "clarification-questions.md").write_text(
        "# Questions\n\nQ-001 is open.\n" if blocking else "# Questions\n\nNo questions remain.\n",
        encoding="utf-8",
    )
    finalize_review(workspace, run, repository)


def _write_valid_rewrite(run: Path) -> None:
    changes = {
        "schema_version": "1.0",
        "run_id": REWRITE_ID,
        "mode": "conservative",
        "changes": [
            {
                "id": "CHANGE-001",
                "affected_section": "Demo",
                "source_issue_ids": [],
                "change_type": "editorial",
                "before": "The editor can publish an article.",
                "after": "REQ-CONTENT-001 — The editor can publish an article.",
                "rationale": "Assign a stable requirement ID without changing meaning.",
                "confidence": "high",
                "confirmation_status": "not_required",
                "answer_ids": [],
                "assumption_ids": [],
                "status": "applied",
            }
        ],
    }
    traceability = {
        "schema_version": "1.0",
        "run_id": REWRITE_ID,
        "entries": [
            {
                "requirement_id": "REQ-CONTENT-001",
                "status": "modified",
                "source_sections": ["Demo"],
                "source_requirement_ids": [],
                "issue_ids": [],
                "answer_ids": [],
                "assumption_ids": [],
                "change_ids": ["CHANGE-001"],
            }
        ],
    }
    (run / "change-register.yaml").write_text(yaml.safe_dump(changes), encoding="utf-8")
    (run / "requirement-traceability.yaml").write_text(
        yaml.safe_dump(traceability), encoding="utf-8"
    )
    (run / "revised-specification.md").write_text(
        "# Revised specification\n\nREQ-CONTENT-001 — The editor can publish an article.\n",
        encoding="utf-8",
    )
    (run / "change-log.md").write_text(
        "# Change log\n\nCHANGE-001 assigned a stable requirement ID.\n", encoding="utf-8"
    )
    (run / "unresolved-questions.md").write_text(
        "# Unresolved questions\n\nNo unresolved questions remain.\n", encoding="utf-8"
    )


def test_prepare_and_finalize_rewrite(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _workspace(isolated_repository, tmp_path)
    _complete_review(isolated_repository, workspace)
    relative = prepare_rewrite(workspace, isolated_repository, "conservative", REWRITE_ID)
    run = workspace / relative
    _write_valid_rewrite(run)

    finalize_rewrite(workspace, run, isolated_repository)

    assert load_document(run / "run-metadata.yaml")["status"] == "completed"
    project = load_document(workspace / "project.yaml")
    assert project["status"]["lifecycle"] == "rewritten"
    assert project["latest_runs"]["rewrite"] == relative.as_posix()


def test_rewrite_blocks_unanswered_question(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _workspace(isolated_repository, tmp_path)
    _complete_review(isolated_repository, workspace, blocking=True)
    run = workspace / prepare_rewrite(workspace, isolated_repository, "conservative", REWRITE_ID)
    (run / "unresolved-questions.md").write_text(
        "# Unresolved questions\n\nQ-001 remains unanswered.\n", encoding="utf-8"
    )
    with pytest.raises(SpecViewerError, match="Q-001"):
        finalize_rewrite(workspace, run, isolated_repository)


def test_answer_allows_confirmed_decision(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _workspace(isolated_repository, tmp_path)
    _complete_review(isolated_repository, workspace, blocking=True)
    answers = workspace / "context/stakeholder-answers.md"
    answers.write_text(
        "# Answers\n\n## Q-001\n\n**Answer:** The owner approves.\n", encoding="utf-8"
    )
    relative = prepare_rewrite(workspace, isolated_repository, "conservative", REWRITE_ID)
    assert (workspace / relative / "run-metadata.yaml").is_file()


def test_rejects_invalid_mode(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _workspace(isolated_repository, tmp_path)
    _complete_review(isolated_repository, workspace)
    with pytest.raises(SpecViewerError, match="mode"):
        prepare_rewrite(workspace, isolated_repository, "inventive", REWRITE_ID)


def test_parses_russian_stakeholder_answer(tmp_path: Path) -> None:
    answers = tmp_path / "answers.md"
    answers.write_text("## Q-007\n\n**Ответ:** Подтверждено владельцем.\n", encoding="utf-8")
    assert answered_question_ids(answers) == {"Q-007"}
