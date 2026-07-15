# Security policy

## Data handling

SpecViewer is private by default. Public repository content may be public documentation, source
code, or explicitly approved synthetic/sanitized examples. Real customer documents, personal or
confidential data, credentials, tokens, private keys, and production connection strings are
prohibited. Store local secrets in ignored `.env` files; commit only placeholder `.env.example`.
Never place secrets in logs, fixtures, issue reports, or pull requests.

The local scanner supports a line-level `secret-scan: allow` marker only for reviewed synthetic
detector fixtures. Every suppression must include a reason and must never conceal usable material.

Sanitized examples require removal of identifiers, secrets, proprietary content, and reversible
references, followed by explicit classification approval.

## Reporting

Report vulnerabilities privately to repository maintainers using GitHub's private security
reporting channel when available. Do not paste confidential specifications into public issues.
Maintainers will acknowledge and triage reports as capacity permits; this policy makes no legal or
fixed response-time commitment.

## Accidental commits

Stop sharing the repository, notify maintainers privately, remove the file from the index/history,
and rotate any exposed credential. Do not merely add the path to `.gitignore`: already tracked data
remains in history. Preserve only non-sensitive incident metadata needed for remediation.
