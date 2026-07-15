# Schemas

All schemas use JSON Schema Draft 2020-12 and are versioned through each artifact's
`schema_version`. JSON Schema checks portable relative-path syntax; filesystem containment and
symlink safety are additionally enforced by the CLI because schemas cannot resolve paths.

Review schemas define category scoring, readiness, evidence-backed issues, and clarification data.
