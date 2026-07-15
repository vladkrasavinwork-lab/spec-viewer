# Rewrite modes

- `conservative`: preserve source order and wording wherever possible. Apply editorial fixes,
  confirmed answers, stable IDs, and clearly derived acceptance criteria. Default to this mode.
- `structured`: reorganize confirmed content into a consistent product-specification structure.
  Record every move or merge; preserve source semantics and omissions as unresolved items.
- `implementation-ready`: produce testable requirements and acceptance criteria only when all
  blocking decisions are answered and no unconfirmed assumptions remain.

Changing structure does not authorize changing scope. If the requested mode cannot be completed
safely, keep the run incomplete and report the blocking IDs.
