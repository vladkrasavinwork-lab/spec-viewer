---
name: product-delivery-estimate
description: >
  Create transparent scenario-based estimates of product development effort,
  calendar duration, implementation cost, AI-assisted development impact,
  infrastructure, and support from a reviewed specification. Use when Codex
  must estimate delivery, budget, team, cloud usage, or maintenance while
  preserving uncertainty and pricing provenance. Do not use to review or
  rewrite the specification or to invent missing rates, prices, load, or SLA.
---

# Product delivery estimate

Create an estimate only in a private SpecViewer workspace. Keep source and completed runs immutable.

## Workflow

1. Run `python -m spec_viewer estimate prepare <workspace>` from the repository root.
2. Read the selected specification, current issue register, project context, constraints, and
   `context/estimation-inputs.yaml`.
3. Read [methodology.md](references/methodology.md), [ai-assistance.md](references/ai-assistance.md),
   [infrastructure-and-support.md](references/infrastructure-and-support.md), and
   [cost-profiles.md](references/cost-profiles.md), and [self-check.md](references/self-check.md).
4. Classify readiness. Preserve material unknowns as blockers, questions, or explicit assumptions.
5. Build requirement-linked work items by discipline. Include discovery, architecture, QA,
   security, DevOps, delivery, stabilization, and management where applicable.
6. Estimate every item with optimistic, expected, and conservative hours. Model AI assistance per
   work item and include human review/rework overhead.
7. Derive calendar scenarios from dependencies, parallelism, specialties, availability, QA, and
   stabilization. Do not divide total hours by headcount.
8. Load configured cost-profile source files. Calculate monetary values only from validated,
   unexpired profiles or explicit inputs. Keep currencies separate unless a dated exchange-rate
   source was supplied. Use provider-neutral formulas for resources absent from the selected profile.
9. Complete all nine files in the run directory using the files under `assets/` as report guidance.
10. Run `python -m spec_viewer estimate finalize <workspace> <run-directory>` and fix every error.

## Guardrails

- Do not silently invent scope, rates, prices, usage, staffing, SLA, or deadlines.
- Treat repository reference profiles as editable planning assumptions, not commercial offers.
- Keep baseline and AI-assisted effort separate; never apply one global acceleration percentage.
- Link work items to known requirement and issue IDs. Label discovery work that has no requirement.
- Keep infrastructure, third-party/AI usage, and engineering support costs separate.
- Treat all figures as ranges and explain confidence and sensitivity.
- Do not modify the specification, review, rewrite, context, or any completed run.
