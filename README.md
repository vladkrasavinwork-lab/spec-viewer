# SpecViewer

SpecViewer is a private-by-default repository for reproducible product-specification workflows.
The current development version implements the repository foundation, Markdown/DOCX/text-PDF
normalization, review, traceable specification rewriting, and transparent delivery estimation.

## Skills

- `product-spec-review` audits specification quality and produces validated findings and questions.
- `product-spec-rewrite` creates a traceable revision from confirmed inputs and explicit assumptions.
- `product-delivery-estimate` estimates delivery effort, schedule, cost formulas, infrastructure,
  and support scenarios without inventing rates or prices.

## Repository map

- `src/spec_viewer/`: deterministic CLI and filesystem logic.
- `schemas/` and `templates/`: machine contracts and safe starting artifacts.
- `standards/`: lifecycle, privacy, IDs, canonical document, and versioning rules.
- `profiles/`: versioned product, team-cost, infrastructure-price, and subscription profiles.
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
# Add confirmed team, rates, load, infrastructure, AI usage, and support inputs when available.
# Missing inputs remain explicit uncertainties; the skill never invents rates or provider prices.
# Optional cost-profile paths below profiles/ can be set in context/estimation-inputs.yaml.
python -m spec_viewer estimate prepare workspaces/customer-portal_private
# Use the product-delivery-estimate skill to populate the printed run directory.
python -m spec_viewer estimate finalize workspaces/customer-portal_private workspaces/customer-portal_private/artifacts/estimate/<run-id>
python -m spec_viewer schema validate schemas/project.schema.json path/to/project.yaml
python -m spec_viewer repository validate
python -m spec_viewer privacy check
./scripts/check.sh
```

Workspace initialization creates `workspaces/customer-portal_private` and prints that relative path.
All validation is offline. `scripts/check.sh` runs the same quality gates as CI.

## Reference cost profiles

The repository includes dated, editable examples for Russian loaded team rates, Yandex Cloud prices,
and AI-development subscriptions. Configure their relative paths under `cost_profiles` in the
workspace estimation inputs. Profiles are hash-pinned per run and rejected after `valid_until`.
They are planning inputs, not salary offers or provider quotations. Different currencies remain
separate unless the workspace supplies a dated exchange rate and source.

## Implementation status

1. Repository Foundation — implemented.
2. Review Skill — implemented for the first review vertical slice.
3. Rewrite Skill — implemented with blocking-question and traceability validation.
4. Delivery Estimate Skill — implemented with scenario and pricing-provenance validation.
5. Workspace Lifecycle and Normalization — implemented.
6. End-to-End Validation — the review → rewrite → estimate workflow is covered by deterministic
   tests and has been exercised on a private workspace; broader eval automation remains planned.
