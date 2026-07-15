from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from spec_viewer.errors import SpecViewerError
from spec_viewer.normalization import normalize_document
from spec_viewer.review import finalize_review, prepare_review
from spec_viewer.schema import load_document
from spec_viewer.workspace import init_workspace

RUN_ID = "20260716T100000Z-review"


def _normalized_workspace(repository: Path, tmp_path: Path) -> Path:
    relative = init_workspace("Review Demo", repository / "workspaces", repository)
    workspace = repository / relative
    source = tmp_path / "spec.md"
    source.write_text("# Demo\n\nThe owner can publish an item.\n", encoding="utf-8")
    normalize_document(workspace, source, repository)
    return workspace


def _write_valid_review(run: Path) -> None:
    summary = load_document(run / "review-summary.yaml")
    summary["readiness"] = "DISCOVERY_REQUIRED"
    summary["overall_confidence"] = "high"
    summary["category_scores"] = {key: 3 for key in summary["category_scores"]}
    summary["issue_counts"] = {"critical": 0, "high": 1, "medium": 0, "low": 0}
    summary["blocking_question_count"] = 1
    (run / "review-summary.yaml").write_text(
        yaml.safe_dump(summary, sort_keys=False), encoding="utf-8"
    )
    issues = {
        "schema_version": "1.0",
        "run_id": RUN_ID,
        "issues": [
            {
                "id": "ISSUE-001",
                "type": "undefined_business_rule",
                "severity": "high",
                "confidence": "high",
                "source": {
                    "section": None,
                    "heading": "Demo",
                    "excerpt": "The owner can publish an item.",
                },
                "problem": "Publication approval behavior is undefined.",
                "impact": ["backend", "acceptance_testing"],
                "resolution_strategy": "decision_required",
                "question_ids": ["Q-001"],
                "status": "open",
            }
        ],
    }
    (run / "issue-register.yaml").write_text(
        yaml.safe_dump(issues, sort_keys=False), encoding="utf-8"
    )
    questions = {
        "schema_version": "1.0",
        "questions": [
            {
                "id": "Q-001",
                "priority": "blocking",
                "category": "Business rules",
                "question": "Who approves publication?",
                "reason": "Approval affects permissions and workflow states.",
                "affected_requirements": [],
                "status": "open",
                "answer": None,
                "answer_metadata": None,
            }
        ],
    }
    (run / "clarification-register.yaml").write_text(
        yaml.safe_dump(questions, sort_keys=False), encoding="utf-8"
    )
    (run / "review-report.md").write_text(
        "# Review\n\nThe specification requires product discovery.\n", encoding="utf-8"
    )
    (run / "clarification-questions.md").write_text(
        "# Questions\n\n## Q-001\n\nWho approves publication?\n", encoding="utf-8"
    )


def test_prepare_and_finalize_review(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _normalized_workspace(isolated_repository, tmp_path)
    relative = prepare_review(workspace, isolated_repository, RUN_ID)
    run = workspace / relative
    assert load_document(run / "run-metadata.yaml")["status"] == "running"
    _write_valid_review(run)

    finalize_review(workspace, run, isolated_repository)

    assert load_document(run / "run-metadata.yaml")["status"] == "completed"
    project = load_document(workspace / "project.yaml")
    assert project["status"]["lifecycle"] == "awaiting_answers"
    assert project["latest_runs"]["review"] == relative.as_posix()
    assert project["open_items"]["high_issues"] == 1


def test_finalize_rejects_mismatched_counts(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _normalized_workspace(isolated_repository, tmp_path)
    run = workspace / prepare_review(workspace, isolated_repository, RUN_ID)
    _write_valid_review(run)
    summary = load_document(run / "review-summary.yaml")
    summary["issue_counts"]["high"] = 0
    (run / "review-summary.yaml").write_text(yaml.safe_dump(summary), encoding="utf-8")
    with pytest.raises(SpecViewerError, match="counts"):
        finalize_review(workspace, run, isolated_repository)


def test_completed_review_cannot_be_finalized_again(
    isolated_repository: Path, tmp_path: Path
) -> None:
    workspace = _normalized_workspace(isolated_repository, tmp_path)
    run = workspace / prepare_review(workspace, isolated_repository, RUN_ID)
    _write_valid_review(run)
    finalize_review(workspace, run, isolated_repository)
    with pytest.raises(SpecViewerError, match="Completed run"):
        finalize_review(workspace, run, isolated_repository)


def test_review_requires_normalization(isolated_repository: Path) -> None:
    relative = init_workspace(
        "Empty Review", isolated_repository / "workspaces", isolated_repository
    )
    with pytest.raises(SpecViewerError, match="Normalize"):
        prepare_review(isolated_repository / relative, isolated_repository, RUN_ID)
