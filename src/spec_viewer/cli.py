"""SpecViewer Stage 1 command-line interface."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import typer

from .errors import SpecViewerError
from .estimate import finalize_estimate, prepare_estimate
from .normalization import normalize_document
from .privacy import privacy_check
from .repository import validate_repository
from .review import finalize_review, prepare_review
from .rewrite import finalize_rewrite, prepare_rewrite
from .runs import create_run
from .schema import validate_file
from .workspace import init_workspace, validate_workspace

app = typer.Typer(help="Deterministic SpecViewer foundation tools.", no_args_is_help=True)
workspace_app = typer.Typer(help="Create and validate private workspaces.")
run_app = typer.Typer(help="Create immutable skill runs.")
schema_app = typer.Typer(help="Validate structured documents.")
repository_app = typer.Typer(help="Validate repository contracts.")
privacy_app = typer.Typer(help="Check tracked paths and probable secrets.")
document_app = typer.Typer(help="Normalize source documents.")
review_app = typer.Typer(help="Prepare and finalize specification review runs.")
rewrite_app = typer.Typer(help="Prepare and finalize traceable specification rewrites.")
estimate_app = typer.Typer(help="Prepare and finalize transparent delivery estimates.")
app.add_typer(workspace_app, name="workspace")
app.add_typer(run_app, name="run")
app.add_typer(schema_app, name="schema")
app.add_typer(repository_app, name="repository")
app.add_typer(privacy_app, name="privacy")
app.add_typer(document_app, name="document")
app.add_typer(review_app, name="review")
app.add_typer(rewrite_app, name="rewrite")
app.add_typer(estimate_app, name="estimate")


def _root() -> Path:
    return Path.cwd().resolve()


def _run(operation: Callable[[], object]) -> None:
    try:
        result = operation()
        if result is not None:
            typer.echo(str(result))
    except SpecViewerError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from None


@workspace_app.command("init")
def workspace_init(name: str, root: Path = Path("workspaces")) -> None:
    """Create a private workspace from repository templates."""
    _run(lambda: init_workspace(name, _root() / root, _root()))


@workspace_app.command("validate")
def workspace_validate(path: Path) -> None:
    """Validate a private workspace structure and manifest."""
    _run(lambda: validate_workspace(path.resolve(), _root()))


@run_app.command("create")
def run_create(workspace: Path, skill_type: str, run_id: str | None = None) -> None:
    """Create an immutable pending run directory."""
    _run(lambda: create_run(workspace.resolve(), _root(), skill_type, run_id))


@schema_app.command("validate")
def schema_validate(schema: Path, document: Path) -> None:
    """Validate YAML or JSON against a local schema."""
    _run(lambda: validate_file(schema.resolve(), document.resolve()))


@repository_app.command("validate")
def repository_validate() -> None:
    """Validate all tracked foundation templates and examples."""
    _run(lambda: validate_repository(_root()))


@privacy_app.command("check")
def check_privacy() -> None:
    """Reject tracked private data, unsafe documents, and probable secrets."""
    _run(lambda: privacy_check(_root()))


@document_app.command("normalize")
def document_normalize(workspace: Path, source: Path) -> None:
    """Copy and normalize Markdown, DOCX, or text PDF into a private workspace."""
    _run(lambda: normalize_document(workspace.resolve(), source.resolve(), _root()))


@review_app.command("prepare")
def review_prepare(workspace: Path, run_id: str | None = None) -> None:
    """Create a running review with schema-valid artifact templates."""
    _run(lambda: prepare_review(workspace.resolve(), _root(), run_id))


@review_app.command("finalize")
def review_finalize(workspace: Path, run: Path) -> None:
    """Validate and complete an AI-authored review run."""
    _run(lambda: finalize_review(workspace.resolve(), run.resolve(), _root()))


@rewrite_app.command("prepare")
def rewrite_prepare(
    workspace: Path,
    mode: str = "conservative",
    run_id: str | None = None,
) -> None:
    """Create a running rewrite with traceable artifact templates."""
    _run(lambda: prepare_rewrite(workspace.resolve(), _root(), mode, run_id))


@rewrite_app.command("finalize")
def rewrite_finalize(workspace: Path, run: Path) -> None:
    """Validate and complete an AI-authored specification rewrite."""
    _run(lambda: finalize_rewrite(workspace.resolve(), run.resolve(), _root()))


@estimate_app.command("prepare")
def estimate_prepare(workspace: Path, run_id: str | None = None) -> None:
    """Create a running estimate with schema-valid artifact templates."""
    _run(lambda: prepare_estimate(workspace.resolve(), _root(), run_id))


@estimate_app.command("finalize")
def estimate_finalize(workspace: Path, run: Path) -> None:
    """Validate and complete an AI-authored delivery estimate."""
    _run(lambda: finalize_estimate(workspace.resolve(), run.resolve(), _root()))


if __name__ == "__main__":
    app()
