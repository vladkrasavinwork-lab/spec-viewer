# Change provenance

Classify each substantive change:

- `editorial`: formatting, terminology, numbering, deduplication, or an obvious local clarification.
  Use `confirmation_status: not_required`.
- `derived`: follows uniquely from confirmed source requirements. Cite source sections and review
  issues; never use derivation to choose among plausible business rules.
- `confirmed_decision`: comes from a stakeholder answer. Include at least one `Q-...` answer ID and
  use `confirmation_status: confirmed`.

Use an assumption only to expose uncertainty, never to disguise a decision. Mark it `unconfirmed`,
identify an owner and impact, reference it from affected changes/requirements, and keep the wording
visibly conditional. `implementation-ready` output cannot contain unconfirmed assumptions.

For each revised requirement, connect source sections/IDs, issue IDs, answer IDs, assumption IDs,
and change IDs in `requirement-traceability.yaml`. Record removals as status `removed`; never reuse
an old requirement ID for a different meaning.
