"""Atomic YAML manifest updates shared by deterministic operations."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import yaml

from .schema import validate_data


def atomic_yaml_write(path: Path, data: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate and atomically replace a YAML document in its current directory."""
    validate_data(data, schema, str(path))
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            yaml.safe_dump(data, stream, sort_keys=False, allow_unicode=True)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
