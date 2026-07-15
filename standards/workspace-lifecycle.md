# Workspace lifecycle

The states are `created`, `normalized`, `reviewed`, `awaiting_answers`, `ready_for_rewrite`,
`rewritten`, `ready_for_estimation`, `estimated`, and `archived`.

Normal transitions follow that order, with `reviewed` optionally moving to `awaiting_answers`, then
back through review before rewrite readiness. Any active state may become `archived`; archived is
terminal. A transition may update `project.yaml` only after the new run validates successfully.
Workspace initialization creates `created`; normalization advances to `normalized`; a completed
review advances to `reviewed` or `awaiting_answers` when blocking questions remain.
A completed rewrite with no unanswered blocking questions advances to `rewritten` and updates only
the current rewrite pointers; previous runs remain immutable.
A completed estimate advances to `estimated`, records the report pointer, and preserves the hashed
specification, issue register, and estimation inputs used by the run.
