# Finding taxonomy

Use only schema-supported types:

- Requirements: `missing_requirement`, `ambiguous_requirement`, `conflicting_requirement`,
  `non_testable_requirement`, `missing_acceptance_criteria`.
- Actors and rules: `undefined_actor`, `undefined_business_rule`, `scope_uncertainty`.
- Behavior: `missing_error_scenario`, `missing_edge_case`, `terminology_inconsistency`.
- Quality: `missing_non_functional_requirement`, `security_risk`, `privacy_risk`,
  `compliance_risk`.
- Data and integration: `missing_dependency`, `missing_data_definition`,
  `missing_integration_contract`.
- Delivery: `delivery_risk`, `estimation_blocker`, `conversion_uncertainty`.

Resolution strategies:

- `editorial`: wording/structure correction needs no product decision.
- `derived`: correction follows uniquely from confirmed requirements; cite supporting evidence.
- `decision_required`: a human must select or confirm behavior.

Use `critical` only when safe implementation cannot proceed or major harm is plausible. Use `high`
for material scope, architecture, security, or acceptance gaps; `medium` for localized rework or
quality risk; and `low` for small, non-blocking improvements.
