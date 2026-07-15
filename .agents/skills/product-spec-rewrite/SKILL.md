---
name: product-spec-rewrite
description: >
  Create a revised product or software specification from an existing
  normalized specification, completed review findings, confirmed stakeholder
  answers, and explicit assumptions. Use when the user asks to improve,
  restructure, correct, update, or produce an implementation-ready version of
  a specification with change and requirement traceability. Do not use this
  skill only to review quality or estimate delivery.
---

# Product specification rewrite

Create a new traceable specification without modifying the source or hiding unresolved decisions.

## Workflow

1. Locate the private workspace and read `project.yaml`, the full normalized specification, latest
   completed review artifacts, context, constraints, glossary, and stakeholder answers.
2. Select `conservative` unless the user explicitly requests `structured` or
   `implementation-ready`. Read [references/modes.md](references/modes.md).
3. Run `python -m spec_viewer rewrite prepare <workspace> --mode <mode>` and use the printed run.
4. Read [references/provenance.md](references/provenance.md) and classify every review issue as
   editorial, derived, confirmed decision, or deferred decision-required work.
5. Preserve every confirmed source requirement. Assign stable requirement IDs following
   [references/requirement-writing.md](references/requirement-writing.md).
6. Replace the six prepared artifacts: `revised-specification.md`, `change-log.md`,
   `change-register.yaml`, `assumption-register.yaml`, `unresolved-questions.md`, and
   `requirement-traceability.yaml`. Preserve `run-metadata.yaml`.
7. Never resolve a blocking question without a recorded stakeholder answer. Keep unresolved
   decisions explicit and do not present them as requirements.
8. Apply [references/self-check.md](references/self-check.md).
9. Run `python -m spec_viewer rewrite finalize <workspace> <full-run-path>`. Fix artifacts until it
   succeeds. If blocking questions remain, return them instead of forcing completion.
10. Report the mode, applied/deferred changes, assumptions, revised specification path, and blockers.

## Boundaries

- Do not edit `source/`, `normalized/`, review runs, or completed rewrite runs.
- Do not invent business rules, roles, legal requirements, SLAs, retention, load, budget, or rates.
- Do not delete or weaken a requirement without an explicit change and traceability entry.
- Do not convert recommendations or unconfirmed assumptions into mandatory requirements.
- Do not estimate effort, duration, infrastructure, or cost.
