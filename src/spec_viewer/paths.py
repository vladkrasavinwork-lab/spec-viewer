"""Path and identifier safety primitives."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path, PurePosixPath, PureWindowsPath

from .errors import SpecViewerError

MAX_SLUG_LENGTH = 64
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RELATIVE_PATH_PATTERN = re.compile(r"^(?![/\\])(?!.*(?:^|[/\\])\.\.(?:[/\\]|$)).+$")


def normalize_slug(name: str) -> str:
    """Normalize a human project name to a conservative ASCII slug."""
    if not name or any(ord(char) < 32 for char in name):
        raise SpecViewerError("Invalid project slug.")
    raw = name.removesuffix("_private")
    if Path(raw).is_absolute() or PureWindowsPath(raw).is_absolute():
        raise SpecViewerError("Invalid project slug: absolute paths are not allowed.")
    if ".." in raw or "/" in raw or "\\" in raw:
        raise SpecViewerError("Invalid project slug: path components are not allowed.")
    ascii_name = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")
    if not slug or len(slug) > MAX_SLUG_LENGTH or not SLUG_PATTERN.fullmatch(slug):
        raise SpecViewerError("Invalid project slug.")
    return slug


def is_safe_relative_path(value: str) -> bool:
    """Return whether an artifact path is portable, relative, and traversal-free."""
    if not value or not RELATIVE_PATH_PATTERN.fullmatch(value):
        return False
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    return not posix.is_absolute() and not windows.is_absolute() and ".." not in posix.parts


def contained_path(root: Path, child_name: str) -> Path:
    """Resolve a direct child and reject escapes, including symlink escapes."""
    resolved_root = root.resolve()
    candidate = (resolved_root / child_name).resolve(strict=False)
    if candidate.parent != resolved_root:
        raise SpecViewerError("Resolved path escapes the workspace root.")
    return candidate
