---
name: product-spec-review
description: >
  Review product and software development specifications for completeness,
  clarity, consistency, testability, delivery readiness, and product risks.
  Use when the user asks to audit, evaluate, validate, check, or identify gaps
  in a PRD, requirements document, or technical specification, including
  Markdown, DOCX, and text PDF inputs. Produce evidence-backed review and
  clarification artifacts. Do not rewrite the specification or estimate delivery.
---

# Product specification review

Perform an evidence-based audit without changing or extending the specification.

## Workflow

1. Locate the repository root and target private workspace. If the user supplied only a document,
   initialize a workspace with `python -m spec_viewer workspace init "<project name>"`.
2. If `normalized/specification.md` is absent, normalize the source with
   `python -m spec_viewer document normalize <workspace> <source>`.
3. Read the entire normalized specification, `normalized/conversion-warnings.md`, and available
   files under `context/`. Do not claim a requirement is absent before searching the full document.
4. Run `python -m spec_viewer review prepare <workspace>` and use the printed run directory.
5. Read [references/rubric.md](references/rubric.md),
   [references/taxonomy.md](references/taxonomy.md), and
   [references/clarification-protocol.md](references/clarification-protocol.md).
6. Score all ten categories, identify and deduplicate material findings, attach source evidence,
   assign severity and confidence, and connect decision-required findings to questions.
7. Replace the five prepared artifact templates in the review run:
   `review-report.md`, `review-summary.yaml`, `issue-register.yaml`,
   `clarification-questions.md`, and `clarification-register.yaml`. Preserve `run-metadata.yaml`.
8. Apply [references/self-check.md](references/self-check.md).
9. Run `python -m spec_viewer review finalize <workspace> <full-run-path>`. Fix artifacts until it
   succeeds. Never manually mark the run completed or update `project.yaml`.
10. Return the readiness, issue counts, artifact path, and highest-priority open questions.

## Boundaries

- Treat conversion warnings as input uncertainty, not automatically as specification defects.
- Quote only short evidence excerpts and always give the nearest heading or source marker.
- Do not invent roles, policies, loads, budgets, SLAs, retention, or business rules.
- Do not rewrite source text, resolve stakeholder decisions, or estimate effort and cost.
- Ask at most ten questions per iteration and do not repeat answered questions.
