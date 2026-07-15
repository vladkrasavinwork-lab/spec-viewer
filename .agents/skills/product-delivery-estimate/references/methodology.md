# Estimation methodology

## Readiness

- `PRELIMINARY`: early concept; useful only for order-of-magnitude planning.
- `LOW_CONFIDENCE`: scope is estimable but sensitive to several assumptions.
- `BLOCKED_BY_OPEN_DECISIONS`: unresolved choices materially change architecture or cost.
- `READY_FOR_PLANNING`: scope and delivery inputs are stable enough for team planning.

Do not stop merely because confidence is low. Produce ranges and a question list unless no coherent
scope boundary exists.

## Work breakdown and effort

Create outcome-oriented work items, not a feature-name inventory. Include applicable discovery,
product, UX/UI, architecture, frontend, backend, mobile, data, QA, security, DevOps, documentation,
stabilization, and project-management work.

Use three-point estimates for every item. Maintain `optimistic ≤ expected ≤ conservative`. Include
integration, review, testing, deployment, and rework inside visible items rather than hidden buffers.

## Calendar

Use dependency order, parallel work streams, specialist availability, external approvals, review
bottlenecks, QA, deployment windows, and stabilization. State the assumed team. Identify the
critical path and the main limits to parallelism.

## Traceability and uncertainty

Reference stable requirement IDs and relevant open issue IDs. Record every material assumption with
its basis, sensitivity, owner, and confirmation status. Prefer a parameterized model when an input
is unknown. Explain exclusions explicitly.
