"""Deterministic preparation and finalization for AI-authored delivery estimates."""

from __future__ import annotations

import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .errors import SpecViewerError
from .manifest import atomic_yaml_write
from .normalization import sha256_file
from .runs import create_run
from .schema import load_document, validate_file
from .workspace import validate_workspace

ESTIMATE_FILES = (
    "estimate-report.md",
    "estimate-summary.yaml",
    "work-breakdown.yaml",
    "estimate-assumptions.yaml",
    "development-scenarios.yaml",
    "infrastructure-scenarios.yaml",
    "support-model.yaml",
    "open-estimation-questions.md",
    "run-metadata.yaml",
)
SCHEMA_PAIRS = (
    ("estimate-summary.schema.json", "estimate-summary.yaml"),
    ("work-breakdown.schema.json", "work-breakdown.yaml"),
    ("estimate-assumptions.schema.json", "estimate-assumptions.yaml"),
    ("development-scenarios.schema.json", "development-scenarios.yaml"),
    ("infrastructure-scenarios.schema.json", "infrastructure-scenarios.yaml"),
    ("support-model.schema.json", "support-model.yaml"),
    ("run-metadata.schema.json", "run-metadata.yaml"),
)
PROFILE_SCHEMAS = {
    "development_rates": "development-rates-profile.schema.json",
    "infrastructure_prices": "infrastructure-prices-profile.schema.json",
    "tool_subscriptions": "tool-subscriptions-profile.schema.json",
}


def _safe_run(workspace: Path, run_path: Path) -> Path:
    resolved = run_path.resolve()
    if resolved.parent != workspace.resolve() / "artifacts/estimate" or resolved.is_symlink():
        raise SpecViewerError("Estimate run path must be a direct child of artifacts/estimate.")
    return resolved


def _estimate_inputs(workspace: Path) -> dict[str, Any]:
    path = workspace / "context/estimation-inputs.yaml"
    data = load_document(path)
    if not isinstance(data, dict):
        raise SpecViewerError("Estimation inputs must be a YAML mapping.")
    return data


def _cost_profiles(
    workspace: Path, repository_root: Path
) -> dict[str, tuple[Path, dict[str, Any]]]:
    inputs = _estimate_inputs(workspace)
    configured = inputs.get("cost_profiles") or {}
    if not isinstance(configured, dict):
        raise SpecViewerError("cost_profiles must be a mapping of supported profile paths.")
    unknown = set(configured) - set(PROFILE_SCHEMAS)
    if unknown:
        raise SpecViewerError("Unknown cost profile types: " + ", ".join(sorted(unknown)))
    profile_root = (repository_root / "profiles").resolve()
    loaded: dict[str, tuple[Path, dict[str, Any]]] = {}
    for name, schema_name in PROFILE_SCHEMAS.items():
        relative = configured.get(name)
        if relative is None:
            continue
        if not isinstance(relative, str) or not relative:
            raise SpecViewerError(f"Invalid {name} profile path.")
        path = (repository_root / relative).resolve()
        if not path.is_relative_to(profile_root) or path.is_symlink() or not path.is_file():
            raise SpecViewerError(
                f"Cost profile must be a regular file below profiles/: {relative}"
            )
        validate_file(repository_root / "schemas" / schema_name, path)
        data = load_document(path)
        valid_until = datetime.fromisoformat(data["valid_until"]).date()
        if valid_until < datetime.now(UTC).date():
            raise SpecViewerError(f"Cost profile has expired: {relative}")
        loaded[name] = (path, data)
    return loaded


def _input_paths(workspace: Path) -> tuple[Path, Path, Path]:
    project = load_document(workspace / "project.yaml")
    review_relative = project["latest_runs"]["review"]
    if review_relative is None:
        raise SpecViewerError("Complete a specification review before preparing an estimate.")
    review = workspace / review_relative
    if load_document(review / "run-metadata.yaml")["status"] != "completed":
        raise SpecViewerError("The current review run is not completed.")
    rewrite_relative = project["latest_runs"]["rewrite"]
    if rewrite_relative:
        rewrite = workspace / rewrite_relative
        if load_document(rewrite / "run-metadata.yaml")["status"] != "completed":
            raise SpecViewerError("The current rewrite run is not completed.")
        specification = rewrite / "revised-specification.md"
    else:
        specification = workspace / project["source"]["normalized_file"]
    return (
        specification,
        review / "issue-register.yaml",
        workspace / "context/estimation-inputs.yaml",
    )


def prepare_estimate(workspace: Path, repository_root: Path, run_id: str | None = None) -> Path:
    """Create a running estimate populated with deterministic templates and input hashes."""
    validate_workspace(workspace, repository_root)
    specification, issues, inputs = _input_paths(workspace)
    for path in (specification, issues, inputs):
        if not path.is_file():
            raise SpecViewerError(f"Required estimation input is missing: {path.name}")
    relative = create_run(workspace, repository_root, "estimate", run_id)
    run_path = workspace / relative
    template_root = repository_root / "templates/estimate"
    for name in ESTIMATE_FILES[:-1]:
        shutil.copyfile(template_root / name, run_path / name)
    project = load_document(workspace / "project.yaml")
    for name in (
        "estimate-summary.yaml",
        "work-breakdown.yaml",
        "estimate-assumptions.yaml",
        "development-scenarios.yaml",
        "infrastructure-scenarios.yaml",
        "support-model.yaml",
    ):
        path = run_path / name
        data = load_document(path)
        data["run_id"] = run_path.name
        if name == "estimate-summary.yaml":
            data["project_id"] = project["project"]["id"]
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    metadata_path = run_path / "run-metadata.yaml"
    metadata = load_document(metadata_path)
    metadata["status"] = "running"
    metadata["skill_version"] = "0.4.0"
    metadata["methodology_version"] = "1.1"
    metadata["input_hashes"] = {
        "specification": sha256_file(specification),
        "issue_register": sha256_file(issues),
        "estimation_inputs": sha256_file(inputs),
    }
    for name, (path, _) in _cost_profiles(workspace, repository_root).items():
        metadata["input_hashes"][f"cost_profile_{name}"] = sha256_file(path)
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


def _assert_acyclic(items: list[dict[str, Any]], identifiers: set[str]) -> None:
    graph = {item["id"]: item["dependencies"] for item in items}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in visiting:
            raise SpecViewerError("Work breakdown dependencies contain a cycle.")
        if identifier in visited:
            return
        visiting.add(identifier)
        for dependency in graph[identifier]:
            if dependency not in identifiers:
                raise SpecViewerError("Work item references an unknown dependency.")
            visit(dependency)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in identifiers:
        visit(identifier)


def _sum_effort(items: list[dict[str, Any]], key: str) -> dict[str, float]:
    return {
        field: round(sum(float(item[key][field]) for item in items), 2)
        for field in ("optimistic_hours", "expected_hours", "conservative_hours")
    }


def _assert_ordered(values: dict[str, Any], keys: tuple[str, str, str], label: str) -> None:
    if not float(values[keys[0]]) <= float(values[keys[1]]) <= float(values[keys[2]]):
        raise SpecViewerError(f"{label} range must be ordered from optimistic to conservative.")


def _expected_cost_range(effort: dict[str, Any], hourly_rate: float) -> dict[str, float]:
    return {
        "minimum": round(float(effort["optimistic_hours"]) * hourly_rate, 2),
        "expected": round(float(effort["expected_hours"]) * hourly_rate, 2),
        "maximum": round(float(effort["conservative_hours"]) * hourly_rate, 2),
    }


def finalize_estimate(workspace: Path, run_path: Path, repository_root: Path) -> None:
    """Validate traceability, arithmetic, pricing provenance, and complete an estimate run."""
    validate_workspace(workspace, repository_root)
    run_path = _safe_run(workspace, run_path)
    missing = [name for name in ESTIMATE_FILES if not (run_path / name).is_file()]
    if missing:
        raise SpecViewerError("Estimate run is incomplete: " + ", ".join(missing))
    for schema_name, artifact_name in SCHEMA_PAIRS:
        validate_file(repository_root / "schemas" / schema_name, run_path / artifact_name)
    specification, issues_path, inputs_path = _input_paths(workspace)
    summary = load_document(run_path / "estimate-summary.yaml")
    breakdown = load_document(run_path / "work-breakdown.yaml")
    assumptions = load_document(run_path / "estimate-assumptions.yaml")
    development = load_document(run_path / "development-scenarios.yaml")
    infrastructure = load_document(run_path / "infrastructure-scenarios.yaml")
    support = load_document(run_path / "support-model.yaml")
    metadata = load_document(run_path / "run-metadata.yaml")
    if metadata["status"] == "completed":
        raise SpecViewerError("Completed run cannot be overwritten.")
    for artifact in (summary, breakdown, assumptions, development, infrastructure, support):
        if artifact["run_id"] != run_path.name:
            raise SpecViewerError("Estimate artifact run IDs do not match the run directory.")
    items = breakdown["work_items"]
    if not items:
        raise SpecViewerError("Work breakdown must contain at least one work item.")
    work_ids = _unique_ids(items, "work item")
    assumption_ids = _unique_ids(assumptions["assumptions"], "assumption")
    _assert_acyclic(items, work_ids)
    issue_ids = {issue["id"] for issue in load_document(issues_path)["issues"]}
    requirement_ids = set(
        re.findall(
            r"\b(?:REQ|NFR)-[A-Z0-9]+-[0-9]{3,}\b", specification.read_text(encoding="utf-8")
        )
    )
    for item in items:
        if set(item["requirement_ids"]) - requirement_ids:
            raise SpecViewerError("Work item references an unknown requirement.")
        if set(item["issue_ids"]) - issue_ids:
            raise SpecViewerError("Work item references an unknown review issue.")
        if set(item["assumption_ids"]) - assumption_ids:
            raise SpecViewerError("Work item references an unknown estimate assumption.")
        _assert_ordered(
            item["baseline_effort"],
            ("optimistic_hours", "expected_hours", "conservative_hours"),
            f"{item['id']} baseline effort",
        )
        _assert_ordered(
            item["ai_assisted_effort"],
            ("optimistic_hours", "expected_hours", "conservative_hours"),
            f"{item['id']} AI-assisted effort",
        )
    baseline = _sum_effort(items, "baseline_effort")
    assisted = _sum_effort(items, "ai_assisted_effort")
    if summary["effort"]["baseline"] != baseline or summary["effort"]["ai_assisted"] != assisted:
        raise SpecViewerError("Estimate summary effort must equal the work-breakdown totals.")
    if set(summary["calendar"]["critical_path"]) - work_ids:
        raise SpecViewerError("Critical path references an unknown work item.")
    for scenario in development["scenarios"]:
        if set(scenario["included_work_ids"]) - work_ids:
            raise SpecViewerError("Development scenario references an unknown work item.")
        _assert_ordered(
            scenario["calendar_weeks"],
            ("optimistic", "expected", "conservative"),
            f"{scenario['id']} calendar",
        )
    infrastructure_names = {scenario["name"] for scenario in infrastructure["scenarios"]}
    if infrastructure_names != {
        "prototype",
        "small_production",
        "expected_production",
        "high_growth_production",
    }:
        raise SpecViewerError("Infrastructure must contain the four required scenarios.")
    support_names = {level["name"] for level in support["levels"]}
    if support_names != {"light", "standard", "critical"}:
        raise SpecViewerError("Support model must contain light, standard, and critical levels.")
    inputs = _estimate_inputs(workspace)
    profiles = _cost_profiles(workspace, repository_root)
    rates_profile = profiles.get("development_rates")
    rates_provided = bool(inputs.get("rates")) or rates_profile is not None
    if not rates_provided and summary["development_cost"]["amount_range"] is not None:
        raise SpecViewerError("Development cost cannot be stated when rates are not provided.")
    if rates_profile:
        _, rates_data = rates_profile
        expected_cost = _expected_cost_range(
            summary["effort"]["ai_assisted"], float(rates_data["blended_hourly_rate"])
        )
        if summary["development_cost"].get("profile_id") != rates_data["profile_id"]:
            raise SpecViewerError("Development cost must identify the selected rates profile.")
        if summary["development_cost"]["currency"] != rates_data["currency"]:
            raise SpecViewerError("Development cost currency does not match the rates profile.")
        if summary["development_cost"]["amount_range"] != expected_cost:
            raise SpecViewerError("Development cost does not match effort × blended profile rate.")
    priced_resources = [
        resource
        for scenario in infrastructure["scenarios"]
        for resource in scenario["resources"]
        if resource["amount_range"] is not None
    ]
    if priced_resources and not all(
        resource["price_source"] and resource["price_date"] for resource in priced_resources
    ):
        raise SpecViewerError("Every infrastructure price requires a source and retrieval date.")
    infrastructure_profile = profiles.get("infrastructure_prices")
    if infrastructure_profile:
        _, infrastructure_data = infrastructure_profile
        if infrastructure.get("profile_id") != infrastructure_data["profile_id"]:
            raise SpecViewerError(
                "Infrastructure scenarios must identify the selected price profile."
            )
        if infrastructure["currency"] != infrastructure_data["currency"]:
            raise SpecViewerError("Infrastructure currency does not match the price profile.")
        prices = {price["id"]: price for price in infrastructure_data["prices"]}
        for resource in priced_resources:
            price = prices.get(resource.get("price_id"))
            if price is None:
                raise SpecViewerError(
                    "Priced infrastructure resource has no known profile price ID."
                )
            if resource["price_source"] != price["source_url"]:
                raise SpecViewerError("Infrastructure source does not match the selected profile.")
            if resource["price_date"] != price["source_date"]:
                raise SpecViewerError(
                    "Infrastructure price date does not match the selected profile."
                )
            if resource["unit"] != price["unit"]:
                raise SpecViewerError(
                    "Infrastructure unit does not match the selected profile price."
                )
            if isinstance(resource["quantity"], (int, float)):
                expected_amount = round(float(resource["quantity"]) * float(price["unit_price"]), 2)
                if any(
                    float(resource["amount_range"][key]) != expected_amount
                    for key in ("minimum", "expected", "maximum")
                ):
                    raise SpecViewerError(
                        "Infrastructure amount does not match quantity × profile unit price."
                    )
        for scenario in infrastructure["scenarios"]:
            priced = [
                resource
                for resource in scenario["resources"]
                if resource["amount_range"] is not None
            ]
            expected_total = {
                key: round(sum(float(resource["amount_range"][key]) for resource in priced), 2)
                for key in ("minimum", "expected", "maximum")
            }
            if priced and scenario["monthly_total_range"] != expected_total:
                raise SpecViewerError(
                    "Infrastructure scenario total must equal its priced resource subtotal."
                )
    if not rates_provided and any(
        level["engineering_cost_range"] is not None for level in support["levels"]
    ):
        raise SpecViewerError("Engineering support cost cannot be stated without rates.")
    if rates_profile:
        _, rates_data = rates_profile
        if support.get("rates_profile_id") != rates_data["profile_id"]:
            raise SpecViewerError("Support model must identify the selected rates profile.")
        if support["currency"] != rates_data["currency"]:
            raise SpecViewerError("Support currency does not match the rates profile.")
        for level in support["levels"]:
            expected_support = {
                key: round(
                    float(level["engineering_hours_range"][key])
                    * float(rates_data["blended_hourly_rate"]),
                    2,
                )
                for key in ("minimum", "expected", "maximum")
            }
            if level["engineering_cost_range"] != expected_support:
                raise SpecViewerError("Support cost does not match hours × blended profile rate.")
    subscription_profile = profiles.get("tool_subscriptions")
    if subscription_profile:
        _, subscription_data = subscription_profile
        tooling = summary.get("tooling_cost")
        if not tooling or tooling["profile_id"] != subscription_data["profile_id"]:
            raise SpecViewerError("Tooling cost must identify the selected subscription profile.")
        if tooling["currency"] != subscription_data["currency"]:
            raise SpecViewerError("Tooling currency does not match the subscription profile.")
        monthly = round(
            sum(
                float(item["unit_price"]) * float(item["default_quantity"])
                for item in subscription_data["subscriptions"]
                if item["selected"]
            ),
            2,
        )
        expected_tooling = {"minimum": monthly, "expected": monthly, "maximum": monthly}
        if tooling["monthly_amount_range"] != expected_tooling:
            raise SpecViewerError("Tooling cost does not match selected profile subscriptions.")
    for markdown_name in ("estimate-report.md", "open-estimation-questions.md"):
        if len((run_path / markdown_name).read_text(encoding="utf-8").strip()) < 20:
            raise SpecViewerError(f"Estimate artifact is empty: {markdown_name}")
    if metadata["input_hashes"]["specification"] != sha256_file(specification):
        raise SpecViewerError("Specification changed after the estimate run started.")
    if metadata["input_hashes"]["issue_register"] != sha256_file(issues_path):
        raise SpecViewerError("Review issues changed after the estimate run started.")
    if metadata["input_hashes"]["estimation_inputs"] != sha256_file(inputs_path):
        raise SpecViewerError("Estimation inputs changed after the estimate run started.")
    for name, (path, _) in profiles.items():
        if metadata["input_hashes"].get(f"cost_profile_{name}") != sha256_file(path):
            raise SpecViewerError(f"Cost profile changed after the estimate run started: {name}")
    metadata["status"] = "completed"
    metadata["confidence"] = summary["confidence"]
    atomic_yaml_write(
        run_path / "run-metadata.yaml",
        metadata,
        load_document(repository_root / "schemas/run-metadata.schema.json"),
    )
    project_path = workspace / "project.yaml"
    project = load_document(project_path)
    relative = run_path.relative_to(workspace).as_posix()
    project["status"]["lifecycle"] = "estimated"
    project["latest_runs"]["estimate"] = relative
    project["latest_artifacts"]["estimate_report"] = f"{relative}/estimate-report.md"
    atomic_yaml_write(
        project_path,
        project,
        load_document(repository_root / "schemas/project.schema.json"),
    )
