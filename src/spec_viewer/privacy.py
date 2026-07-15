"""Defense-in-depth validation for tracked paths and probable secrets."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Iterable
from pathlib import Path, PurePosixPath

from .errors import SpecViewerError
from .schema import load_document, validate_file

SOURCE_DOCUMENT_EXTENSIONS = {".docx", ".pdf", ".pages", ".odt"}
SECRET_FILENAMES = {".env", "credentials.json", "service-account.json", "id_rsa", "id_ed25519"}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(
        r"(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"
    ),
    re.compile(r"(?i)(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://[^\s:@]+:[^\s@]+@"),
)
SUPPRESSION_MARKER = "secret-scan: allow"


def git_paths(repository_root: Path) -> list[str]:
    """Return the union of tracked and staged Git paths without shell interpolation."""
    commands = (
        ("git", "ls-files"),
        ("git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"),
        ("git", "ls-files", "--others", "--exclude-standard"),
    )
    paths: set[str] = set()
    for command in commands:
        result = subprocess.run(
            command, cwd=repository_root, check=True, capture_output=True, text=True
        )
        paths.update(line for line in result.stdout.splitlines() if line)
    return sorted(paths)


def _approved_example_document(repository_root: Path, relative: PurePosixPath) -> bool:
    if not relative.parts or relative.parts[0] != "examples" or len(relative.parts) < 3:
        return False
    classification = repository_root / relative.parts[0] / relative.parts[1] / "classification.yaml"
    if not classification.is_file():
        return False
    try:
        validate_file(
            repository_root / "schemas/example-classification.schema.json", classification
        )
        data = load_document(classification)
    except SpecViewerError:
        return False
    return bool(data.get("approved_for_repository") and not data.get("contains_real_customer_data"))


def validate_paths(repository_root: Path, paths: Iterable[str]) -> None:
    """Reject private, secret-like, and unapproved source-document paths."""
    violations: list[str] = []
    for raw_path in paths:
        path = PurePosixPath(raw_path.replace("\\", "/"))
        lowered_parts = [part.lower() for part in path.parts]
        if lowered_parts and lowered_parts[0] == "workspaces":
            violations.append(f"workspace path is tracked: {raw_path}")
        if any("_private" in part for part in lowered_parts):
            violations.append(f"private path is tracked: {raw_path}")
        if path.name.lower() in SECRET_FILENAMES or (
            path.name.startswith(".env") and path.name != ".env.example"
        ):
            violations.append(f"probable credential file is tracked: {raw_path}")
        if path.suffix.lower() in SOURCE_DOCUMENT_EXTENSIONS and not _approved_example_document(
            repository_root, path
        ):
            violations.append(f"unapproved source document is tracked: {raw_path}")
    if violations:
        raise SpecViewerError("Privacy validation failed.\n" + "\n".join(violations))


def scan_secrets(repository_root: Path, paths: Iterable[str]) -> None:
    """Scan small tracked text files for representative secret material."""
    violations: list[str] = []
    for relative in paths:
        path = repository_root / relative
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relevant_lines = [line for line in content.splitlines() if SUPPRESSION_MARKER not in line]
        if any(pattern.search(line) for line in relevant_lines for pattern in SECRET_PATTERNS):
            violations.append(relative)
    if violations:
        raise SpecViewerError("Probable secret material detected: " + ", ".join(violations))


def privacy_check(repository_root: Path) -> None:
    """Run all local tracked-path and content privacy checks."""
    paths = git_paths(repository_root)
    validate_paths(repository_root, paths)
    scan_secrets(repository_root, paths)
