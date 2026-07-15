# SpecViewer

SpecViewer is a private-by-default repository for reproducible product-specification workflows.
The current development version implements the repository foundation, Markdown/DOCX/text-PDF
normalization, review, and traceable specification rewriting. Delivery estimation remains planned.

## Planned skills

- `product-spec-review` audits specification quality and produces validated findings and questions.
- `product-spec-rewrite` creates a traceable revision from confirmed inputs and explicit assumptions.
- `product-delivery-estimate` estimates delivery and operating scenarios (future stage).

The estimate directory remains an explicit placeholder and is not a production workflow yet.

## Repository map

- `src/spec_viewer/`: deterministic CLI and filesystem logic.
- `schemas/` and `templates/`: machine contracts and safe starting artifacts.
- `standards/`: lifecycle, privacy, IDs, canonical document, and versioning rules.
- `profiles/`: reserved product, team, and operations profiles.
- `examples/`: explicitly classified public examples only.
- `tests/` and `evals/`: deterministic foundation verification.
- `workspaces/`: ignored private project data, created on demand.

## Private workspace policy

> Never place real customer specifications in tracked repository paths.

Real data belongs only under `workspaces/<slug>_private/`. The whole workspace root and every path
containing `_private` are ignored. The privacy checker also inspects Git's tracked/staged paths so a
force-added file cannot bypass policy. Original files under `source/` are immutable.

## Development setup

Python 3.13 is the reference runtime.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

## Commands

```bash
python -m spec_viewer workspace init "Customer Portal"
python -m spec_viewer document normalize workspaces/customer-portal_private path/to/specification.md
python -m spec_viewer workspace validate workspaces/customer-portal_private
python -m spec_viewer review prepare workspaces/customer-portal_private
# Use the product-spec-review skill to populate the printed run directory.
python -m spec_viewer review finalize workspaces/customer-portal_private workspaces/customer-portal_private/artifacts/review/<run-id>
python -m spec_viewer rewrite prepare workspaces/customer-portal_private --mode conservative
# Use the product-spec-rewrite skill to populate the printed run directory.
python -m spec_viewer rewrite finalize workspaces/customer-portal_private workspaces/customer-portal_private/artifacts/rewrite/<run-id>
python -m spec_viewer schema validate schemas/project.schema.json path/to/project.yaml
python -m spec_viewer repository validate
python -m spec_viewer privacy check
./scripts/check.sh
```

Workspace initialization creates `workspaces/customer-portal_private` and prints that relative path.
All validation is offline. `scripts/check.sh` runs the same quality gates as CI.

## Roadmap

1. Repository Foundation — implemented.
2. Review Skill — implemented for the first review vertical slice.
3. Rewrite Skill — implemented with blocking-question and traceability validation.
4. Delivery Estimate Skill.
5. Workspace Lifecycle and Normalization.
6. End-to-End Validation.
