# Schemas

All schemas use JSON Schema Draft 2020-12 and are versioned through each artifact's
`schema_version`. JSON Schema checks portable relative-path syntax; filesystem containment and
symlink safety are additionally enforced by the CLI because schemas cannot resolve paths.

Review schemas define category scoring, readiness, evidence-backed issues, and clarification data.
Rewrite schemas define change provenance, explicit assumptions, and requirement-level traceability.
Estimate schemas define readiness, work-item effort, AI impact, delivery scenarios, provider-neutral
infrastructure, support levels, assumptions, and monetary-value provenance.
Cost-profile schemas define dated development rates, provider price units, and selected tool
subscriptions. Reference profiles are immutable inputs within a run and must be refreshed explicitly.
