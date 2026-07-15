# Cost profiles

Read `context/estimation-inputs.yaml → cost_profiles`. Paths must resolve below repository
`profiles/` and match their schemas.

- `development_rates`: use the discipline rates for detailed allocation; use
  `blended_hourly_rate` only for preliminary totals. State whether the profile represents loaded
  internal cost or a billable rate.
- `infrastructure_prices`: use exact provider, region, currency, tax flag, price ID, unit, source,
  and source date. A profile is not a complete architecture bill of materials.
- `tool_subscriptions`: sum only entries with `selected: true`; multiply unit price by quantity.

Treat `valid_until` as a hard boundary. Never silently refresh a value or substitute a different
plan. Do not convert currencies without a dated exchange-rate input and source. Reference salary
profiles are budgeting assumptions derived from market aggregates; confirm actual payroll,
contractor rates, taxes, overhead, discounts, and procurement terms before a commercial estimate.
