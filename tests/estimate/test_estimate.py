from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from spec_viewer.errors import SpecViewerError
from spec_viewer.estimate import finalize_estimate, prepare_estimate
from spec_viewer.normalization import normalize_document
from spec_viewer.review import finalize_review, prepare_review
from spec_viewer.schema import load_document
from spec_viewer.workspace import init_workspace

REVIEW_ID = "20260716T120000Z-review"
ESTIMATE_ID = "20260716T130000Z-estimate"


def _workspace(repository: Path, tmp_path: Path) -> Path:
    relative = init_workspace("Estimate Demo", repository / "workspaces", repository)
    workspace = repository / relative
    source = tmp_path / "spec.md"
    source.write_text(
        "# Demo\n\nREQ-CONTENT-001 — The editor can publish an article.\n",
        encoding="utf-8",
    )
    normalize_document(workspace, source, repository)
    run = workspace / prepare_review(workspace, repository, REVIEW_ID)
    summary = load_document(run / "review-summary.yaml")
    summary["category_scores"] = {key: 4 for key in summary["category_scores"]}
    summary["overall_confidence"] = "high"
    summary["readiness"] = "IMPLEMENTATION_READY"
    summary["issue_counts"] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    summary["blocking_question_count"] = 0
    (run / "review-summary.yaml").write_text(yaml.safe_dump(summary), encoding="utf-8")
    (run / "issue-register.yaml").write_text(
        yaml.safe_dump({"schema_version": "1.0", "run_id": REVIEW_ID, "issues": []}),
        encoding="utf-8",
    )
    (run / "clarification-register.yaml").write_text(
        yaml.safe_dump({"schema_version": "1.0", "questions": []}), encoding="utf-8"
    )
    (run / "review-report.md").write_text("# Review\n\nReady for planning.\n", encoding="utf-8")
    (run / "clarification-questions.md").write_text(
        "# Questions\n\nNo questions remain.\n", encoding="utf-8"
    )
    finalize_review(workspace, run, repository)
    return workspace


def _write_valid_estimate(run: Path) -> None:
    effort = {"optimistic_hours": 24, "expected_hours": 40, "conservative_hours": 64}
    ai_effort = {"optimistic_hours": 20, "expected_hours": 34, "conservative_hours": 58}
    item: dict[str, Any] = {
        "id": "WORK-001",
        "title": "Article publication",
        "requirement_ids": ["REQ-CONTENT-001"],
        "issue_ids": [],
        "disciplines": ["backend", "frontend", "qa"],
        "complexity": "medium",
        "baseline_effort": effort,
        "ai_assisted_effort": ai_effort,
        "ai_assistance": {
            "applicability": "medium",
            "expected_acceleration": "moderate",
            "human_review_required": True,
            "review_overhead": "medium",
            "rework_risk": "low",
        },
        "confidence": "medium",
        "assumption_ids": [],
        "dependencies": [],
    }
    (run / "work-breakdown.yaml").write_text(
        yaml.safe_dump(
            {"schema_version": "1.0", "run_id": ESTIMATE_ID, "work_items": [item]},
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    summary = load_document(run / "estimate-summary.yaml")
    summary["readiness"] = "READY_FOR_PLANNING"
    summary["confidence"] = "medium"
    summary["effort"] = {"baseline": effort, "ai_assisted": ai_effort}
    summary["calendar"] = {
        "optimistic_weeks": 1,
        "expected_weeks": 2,
        "conservative_weeks": 3,
        "critical_path": ["WORK-001"],
    }
    summary["main_uncertainties"] = ["Team availability is not confirmed."]
    (run / "estimate-summary.yaml").write_text(
        yaml.safe_dump(summary, sort_keys=False), encoding="utf-8"
    )
    development = load_document(run / "development-scenarios.yaml")
    for scenario in development["scenarios"]:
        scenario["included_work_ids"] = ["WORK-001"]
        scenario["calendar_weeks"] = {"optimistic": 1, "expected": 2, "conservative": 3}
    (run / "development-scenarios.yaml").write_text(
        yaml.safe_dump(development, sort_keys=False), encoding="utf-8"
    )
    (run / "estimate-report.md").write_text(
        "# Delivery estimate\n\nThe scoped feature requires 24–64 baseline hours.\n",
        encoding="utf-8",
    )
    (run / "open-estimation-questions.md").write_text(
        "# Open questions\n\nConfirm team availability before scheduling.\n", encoding="utf-8"
    )


def test_prepare_and_finalize_estimate(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _workspace(isolated_repository, tmp_path)
    relative = prepare_estimate(workspace, isolated_repository, ESTIMATE_ID)
    run = workspace / relative
    _write_valid_estimate(run)

    finalize_estimate(workspace, run, isolated_repository)

    assert load_document(run / "run-metadata.yaml")["status"] == "completed"
    project = load_document(workspace / "project.yaml")
    assert project["status"]["lifecycle"] == "estimated"
    assert project["latest_runs"]["estimate"] == relative.as_posix()


def test_rejects_money_without_rates(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _workspace(isolated_repository, tmp_path)
    run = workspace / prepare_estimate(workspace, isolated_repository, ESTIMATE_ID)
    _write_valid_estimate(run)
    summary = load_document(run / "estimate-summary.yaml")
    summary["development_cost"]["amount_range"] = {
        "minimum": 1000,
        "expected": 2000,
        "maximum": 3000,
    }
    (run / "estimate-summary.yaml").write_text(yaml.safe_dump(summary), encoding="utf-8")

    with pytest.raises(SpecViewerError, match="rates are not provided"):
        finalize_estimate(workspace, run, isolated_repository)


def test_rejects_inconsistent_summary(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _workspace(isolated_repository, tmp_path)
    run = workspace / prepare_estimate(workspace, isolated_repository, ESTIMATE_ID)
    _write_valid_estimate(run)
    summary = load_document(run / "estimate-summary.yaml")
    summary["effort"]["baseline"]["expected_hours"] = 999
    (run / "estimate-summary.yaml").write_text(yaml.safe_dump(summary), encoding="utf-8")

    with pytest.raises(SpecViewerError, match="work-breakdown totals"):
        finalize_estimate(workspace, run, isolated_repository)


def test_rejects_dependency_cycle(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _workspace(isolated_repository, tmp_path)
    run = workspace / prepare_estimate(workspace, isolated_repository, ESTIMATE_ID)
    _write_valid_estimate(run)
    breakdown = load_document(run / "work-breakdown.yaml")
    breakdown["work_items"][0]["dependencies"] = ["WORK-001"]
    (run / "work-breakdown.yaml").write_text(yaml.safe_dump(breakdown), encoding="utf-8")

    with pytest.raises(SpecViewerError, match="cycle"):
        finalize_estimate(workspace, run, isolated_repository)


def test_rejects_unknown_requirement(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _workspace(isolated_repository, tmp_path)
    run = workspace / prepare_estimate(workspace, isolated_repository, ESTIMATE_ID)
    _write_valid_estimate(run)
    breakdown = load_document(run / "work-breakdown.yaml")
    breakdown["work_items"][0]["requirement_ids"] = ["REQ-UNKNOWN-999"]
    (run / "work-breakdown.yaml").write_text(yaml.safe_dump(breakdown), encoding="utf-8")

    with pytest.raises(SpecViewerError, match="unknown requirement"):
        finalize_estimate(workspace, run, isolated_repository)


def test_rejects_unordered_effort_range(isolated_repository: Path, tmp_path: Path) -> None:
    workspace = _workspace(isolated_repository, tmp_path)
    run = workspace / prepare_estimate(workspace, isolated_repository, ESTIMATE_ID)
    _write_valid_estimate(run)
    breakdown = load_document(run / "work-breakdown.yaml")
    breakdown["work_items"][0]["baseline_effort"] = {
        "optimistic_hours": 80,
        "expected_hours": 40,
        "conservative_hours": 64,
    }
    (run / "work-breakdown.yaml").write_text(yaml.safe_dump(breakdown), encoding="utf-8")
    summary = load_document(run / "estimate-summary.yaml")
    summary["effort"]["baseline"] = breakdown["work_items"][0]["baseline_effort"]
    (run / "estimate-summary.yaml").write_text(yaml.safe_dump(summary), encoding="utf-8")

    with pytest.raises(SpecViewerError, match="range must be ordered"):
        finalize_estimate(workspace, run, isolated_repository)
