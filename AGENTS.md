# AI agent instructions

- Communicate with contributors and write code and documentation in English.
- Preserve source files; create new artifacts instead of editing project originals.
- Store real project data only below ignored `workspaces/` paths ending in `_private`.
- Never bypass privacy checks, force-track private paths, or commit an `_private` path.
- Never overwrite a completed run.
- Validate every structured artifact against its repository schema.
- Store only relative artifact paths; reject absolute paths, traversal, and symlink escapes.
- Do not invent or change schemas without updating standards, templates, tests, and changelog.
- Update tests whenever validation behavior changes.
- Update `CHANGELOG.md` for user-visible changes.
- Keep each future skill focused on one responsibility.
- Keep review evidence-based and schema-valid; never hardcode or simulate AI findings in tooling.
- Keep rewrite changes traceable; never turn unanswered decisions or assumptions into requirements.
- Keep estimates scenario-based and requirement-linked; never invent rates, provider prices, load,
  staffing, SLA, or a global AI acceleration percentage.
