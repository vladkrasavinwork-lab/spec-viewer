"""Offline JSON Schema validation for YAML and JSON documents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from .errors import SpecViewerError


def load_document(path: Path) -> Any:
    """Load JSON or safe YAML without constructing arbitrary Python objects."""
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
    except (OSError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise SpecViewerError(f"Cannot safely load {path}: {exc}") from exc


def validate_data(data: Any, schema: dict[str, Any], label: str = "document") -> None:
    """Validate loaded data and combine errors into a readable domain failure."""
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    if errors:
        lines = []
        for error in errors:
            location = ".".join(str(part) for part in error.absolute_path) or "$"
            lines.append(f"{label}:{location}: {error.message}")
        raise SpecViewerError("Document does not match the selected schema.\n" + "\n".join(lines))


def validate_file(schema_path: Path, document_path: Path) -> None:
    """Validate a YAML or JSON file against a local JSON Schema."""
    schema = load_document(schema_path)
    if not isinstance(schema, dict):
        raise SpecViewerError(f"Schema must be a JSON object: {schema_path}")
    Draft202012Validator.check_schema(schema)
    validate_data(load_document(document_path), schema, str(document_path))
