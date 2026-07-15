"""Repository-wide foundation contract validation."""

from __future__ import annotations

from pathlib import Path

from .errors import SpecViewerError
from .schema import validate_file

STRUCTURED_FILES = (
    ("schemas/project.schema.json", "templates/workspace/project.yaml"),
    (
        "schemas/document-metadata.schema.json",
        "templates/workspace/normalized/document-metadata.yaml",
    ),
    ("schemas/run-metadata.schema.json", "templates/runs/run-metadata.yaml"),
    ("schemas/review-summary.schema.json", "templates/review/review-summary.yaml"),
    ("schemas/issue-register.schema.json", "templates/review/issue-register.yaml"),
    (
        "schemas/clarification-register.schema.json",
        "templates/review/clarification-register.yaml",
    ),
    ("schemas/change-register.schema.json", "templates/rewrite/change-register.yaml"),
    (
        "schemas/assumption-register.schema.json",
        "templates/rewrite/assumption-register.yaml",
    ),
    (
        "schemas/requirement-traceability.schema.json",
        "templates/rewrite/requirement-traceability.yaml",
    ),
    ("schemas/estimate-summary.schema.json", "templates/estimate/estimate-summary.yaml"),
    ("schemas/work-breakdown.schema.json", "templates/estimate/work-breakdown.yaml"),
    (
        "schemas/estimate-assumptions.schema.json",
        "templates/estimate/estimate-assumptions.yaml",
    ),
    (
        "schemas/development-scenarios.schema.json",
        "templates/estimate/development-scenarios.yaml",
    ),
    (
        "schemas/infrastructure-scenarios.schema.json",
        "templates/estimate/infrastructure-scenarios.yaml",
    ),
    ("schemas/support-model.schema.json", "templates/estimate/support-model.yaml"),
    (
        "schemas/development-rates-profile.schema.json",
        "profiles/team/russia-standard-2026.yaml",
    ),
    (
        "schemas/infrastructure-prices-profile.schema.json",
        "profiles/operations/yandex-cloud-russia-2026.yaml",
    ),
    (
        "schemas/tool-subscriptions-profile.schema.json",
        "profiles/operations/ai-development-subscriptions-2026.yaml",
    ),
    ("schemas/example-classification.schema.json", "templates/examples/classification.yaml"),
    (
        "schemas/example-classification.schema.json",
        "examples/synthetic-foundation-example/classification.yaml",
    ),
    ("schemas/project.schema.json", "examples/synthetic-foundation-example/project.yaml"),
    (
        "schemas/document-metadata.schema.json",
        "examples/synthetic-foundation-example/document-metadata.yaml",
    ),
    (
        "schemas/project.schema.json",
        "examples/synthetic-workspace-example/workspace/project.yaml",
    ),
    (
        "schemas/document-metadata.schema.json",
        "examples/synthetic-workspace-example/workspace/normalized/document-metadata.yaml",
    ),
)
SKILLS = ("product-spec-review", "product-spec-rewrite", "product-delivery-estimate")


def validate_skill_frontmatter(path: Path, require_placeholder: bool = False) -> None:
    """Check the minimal repository skill placeholder contract."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\nname:" not in text or "\ndescription:" not in text:
        raise SpecViewerError(f"Invalid skill frontmatter: {path}")
    if require_placeholder and "Stage 1 placeholder" not in text:
        raise SpecViewerError(f"Skill is not marked as a Stage 1 placeholder: {path}")


def validate_repository(repository_root: Path) -> None:
    """Validate schemas, templates, examples, and skill placeholders offline."""
    for schema, document in STRUCTURED_FILES:
        validate_file(repository_root / schema, repository_root / document)
    for skill in SKILLS:
        validate_skill_frontmatter(
            repository_root / ".agents/skills" / skill / "SKILL.md",
            require_placeholder=False,
        )
    examples = [path for path in (repository_root / "examples").iterdir() if path.is_dir()]
    for example in examples:
        if not (example / "classification.yaml").is_file():
            raise SpecViewerError(f"Example classification is missing: {example}")
