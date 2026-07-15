# Clarification protocol

Create a question only when an answer can resolve or materially narrow a finding. Use priorities:

- `blocking`: the current or next stage cannot proceed safely.
- `important`: work can proceed only with an explicit assumption or bounded risk.
- `optional`: useful refinement with no material correctness impact.

Order questions by impact on business logic, architecture, security, delivery, cost, and compliance.
Limit each iteration to ten. Check stakeholder answers before asking; reuse stable question IDs and
never repeat an answered question unless relevant inputs changed.

In `clarification-questions.md`, include the ID, priority, category, direct question, why it matters,
suggested options only when they do not imply a preferred answer, and affected requirement IDs.
Keep `clarification-register.yaml` machine-readable and schema-valid. Open questions have `answer`
and `answer_metadata` set to null.
