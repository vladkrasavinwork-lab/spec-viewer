"""Deterministic Markdown, DOCX, and text-PDF normalization."""

from __future__ import annotations

import hashlib
import re
import shutil
import uuid
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from docx import Document
from docx.document import Document as DocumentObject
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from pypdf import PdfReader

from .errors import SpecViewerError
from .manifest import atomic_yaml_write
from .schema import load_document, validate_data
from .workspace import validate_workspace

SUPPORTED_FORMATS = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".docx": "docx",
    ".pdf": "text_pdf",
}


def sha256_file(path: Path) -> str:
    """Return a streaming SHA-256 digest without modifying the input."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_markdown(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    lines = [line.rstrip() for line in normalized.split("\n")]
    return "\n".join(lines).rstrip() + "\n"


def _iter_blocks(parent: DocumentObject | _Cell) -> Iterator[Paragraph | Table]:
    body = parent.element.body if isinstance(parent, DocumentObject) else parent._tc
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def _run_text(run: Run) -> str:
    text = run.text
    if run.bold and text:
        text = f"**{text}**"
    if run.italic and text:
        text = f"*{text}*"
    return text


def _docx_to_markdown(path: Path) -> tuple[str, list[str]]:
    try:
        document = Document(str(path))
    except Exception as exc:
        raise SpecViewerError(f"Cannot read DOCX document: {path.name}") from exc
    output: list[str] = []
    warnings: list[str] = []
    for block in _iter_blocks(document):
        if isinstance(block, Paragraph):
            text = "".join(_run_text(run) for run in block.runs).strip()
            has_image = any(
                "graphic" in run._r.xml or "drawing" in run._r.xml for run in block.runs
            )
            if has_image:
                warnings.append(
                    "An embedded image was detected; image extraction is not yet available."
                )
            if "hyperlink" in block._p.xml:
                warnings.append("A hyperlink was detected; verify its target after conversion.")
            if not text:
                continue
            style = block.style.name if block.style else ""
            heading = re.fullmatch(r"Heading ([1-6])", style)
            if heading:
                output.append(f"{'#' * int(heading.group(1))} {text}")
            elif "List Bullet" in style:
                output.append(f"- {text}")
            elif "List Number" in style:
                output.append(f"1. {text}")
            else:
                output.append(text)
        else:
            rows = [
                [cell.text.strip().replace("\n", "<br>") for cell in row.cells]
                for row in block.rows
            ]
            if rows:
                width = max(len(row) for row in rows)
                padded = [row + [""] * (width - len(row)) for row in rows]
                output.append("| " + " | ".join(padded[0]) + " |")
                output.append("| " + " | ".join("---" for _ in range(width)) + " |")
                output.extend("| " + " | ".join(row) + " |" for row in padded[1:])
    if not output:
        raise SpecViewerError("The DOCX document contains no readable content.")
    return _canonical_markdown("\n\n".join(output)), sorted(set(warnings))


def _pdf_to_markdown(path: Path) -> tuple[str, list[str]]:
    try:
        reader = PdfReader(path)
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
    except Exception as exc:
        raise SpecViewerError(f"Cannot read PDF document: {path.name}") from exc
    if not pages or not any(pages):
        raise SpecViewerError(
            "The PDF has no extractable text and may be scanned; OCR is unsupported."
        )
    warnings = ["PDF layout, columns, tables, and reading order may not be preserved exactly."]
    sections = [
        f"<!-- source: page {number} -->\n\n{text}" for number, text in enumerate(pages, 1) if text
    ]
    return _canonical_markdown("\n\n---\n\n".join(sections)), warnings


def _normalize_content(source: Path, source_format: str) -> tuple[str, list[str]]:
    if source_format == "markdown":
        try:
            return _canonical_markdown(source.read_text(encoding="utf-8")), []
        except UnicodeDecodeError as exc:
            raise SpecViewerError("Markdown input must be UTF-8 encoded.") from exc
    if source_format == "docx":
        return _docx_to_markdown(source)
    return _pdf_to_markdown(source)


def _warning_markdown(warnings: Iterable[str]) -> str:
    items = list(warnings)
    if not items:
        return "# Conversion warnings\n\nNo known conversion warnings.\n"
    return "# Conversion warnings\n\n" + "\n".join(f"- {item}" for item in items) + "\n"


def normalize_document(workspace: Path, source: Path, repository_root: Path) -> Path:
    """Copy an immutable source and create canonical Markdown plus metadata."""
    validate_workspace(workspace, repository_root)
    if source.is_symlink() or not source.is_file():
        raise SpecViewerError("Source document must be a regular file, not a symbolic link.")
    source_format = SUPPORTED_FORMATS.get(source.suffix.lower())
    if source_format is None:
        raise SpecViewerError("Unsupported source format. Use Markdown, DOCX, or text PDF.")
    source_hash_before = sha256_file(source)
    markdown, warnings = _normalize_content(source, source_format)
    if sha256_file(source) != source_hash_before:
        raise SpecViewerError("Source document changed during normalization.")
    source_target = workspace / "source" / source.name
    if source_target.exists():
        raise SpecViewerError("Source document already exists in the workspace.")
    normalized_target = workspace / "normalized/specification.md"
    if normalized_target.exists():
        raise SpecViewerError("Normalized document already exists; create a new workspace or run.")
    shutil.copyfile(source, source_target)
    if sha256_file(source_target) != source_hash_before:
        source_target.unlink(missing_ok=True)
        raise SpecViewerError("Copied source hash does not match the original.")
    normalized_target.write_text(markdown, encoding="utf-8")
    normalized_hash = sha256_file(normalized_target)
    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    metadata: dict[str, Any] = {
        "schema_version": "1.0",
        "document_id": f"DOC-{uuid.uuid4().hex[:12].upper()}",
        "title": source.stem,
        "document_type": "product_specification",
        "source_format": source_format,
        "source_language": None,
        "normalized_language": None,
        "source_filename": source.name,
        "source_hash": source_hash_before,
        "converted_at": generated_at,
        "conversion_status": "completed" if not warnings else "partial",
        "converter_version": "spec-viewer/0.2.0",
        "warnings_count": len(warnings),
    }
    metadata_schema = load_document(repository_root / "schemas/document-metadata.schema.json")
    validate_data(metadata, metadata_schema, "document metadata")
    (workspace / "normalized/document-metadata.yaml").write_text(
        yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    (workspace / "normalized/conversion-warnings.md").write_text(
        _warning_markdown(warnings), encoding="utf-8"
    )
    project_path = workspace / "project.yaml"
    project = load_document(project_path)
    project["status"]["lifecycle"] = "normalized"
    project["source"] = {
        "original_file": source_target.relative_to(workspace).as_posix(),
        "normalized_file": normalized_target.relative_to(workspace).as_posix(),
        "source_hash": source_hash_before,
        "normalized_hash": normalized_hash,
    }
    project_schema = load_document(repository_root / "schemas/project.schema.json")
    atomic_yaml_write(project_path, project, project_schema)
    return normalized_target.relative_to(workspace)
