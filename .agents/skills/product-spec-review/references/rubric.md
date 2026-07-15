# Review rubric

Score each category from 0 to 5:

- 0: absent.
- 1: critically insufficient.
- 2: weak.
- 3: acceptable with material gaps.
- 4: good with minor gaps.
- 5: implementation-ready.

Categories:

1. Context and objectives: problem, outcome, success measures.
2. Scope: inclusions, exclusions, boundaries, priorities.
3. Stakeholders and actors: roles, permissions, ownership.
4. Functional completeness: flows, states, rules, data, integrations.
5. Requirement clarity: unambiguous terminology and conditions.
6. Verifiability: observable behavior and acceptance criteria.
7. Consistency: compatible statements, terms, and constraints.
8. Edge cases and failures: validation, recovery, empty and error states.
9. Non-functional requirements: security, privacy, performance, availability, accessibility,
   observability, compliance, and data lifecycle when relevant.
10. Delivery readiness: dependencies, constraints, migrations, rollout, and unresolved decisions.

Readiness:

- `NOT_READY`: any open critical issue, unreadable input, unknown core objective/user/flow.
- `DISCOVERY_REQUIRED`: no critical blocker, but material high issues require discovery.
- `READY_WITH_CONDITIONS`: core scope is clear; remaining gaps are local and explicit.
- `IMPLEMENTATION_READY`: no open critical/high blockers and requirements are testable.

Choose severity by delivery or product impact, never prose style. Lower confidence when evidence may
be incomplete, conversion is lossy, an external source is referenced, or interpretations compete.
