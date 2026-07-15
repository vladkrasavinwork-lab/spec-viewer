# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and semantic
versioning.

## [Unreleased]

### Added

- Deterministic Markdown, DOCX, and text-PDF normalization with source hashes and warnings.
- Working `product-spec-review` skill, review schemas, templates, lifecycle commands, and tests.
- Working `product-spec-rewrite` skill with three modes, provenance, blocking-question enforcement,
  immutable runs, change/assumption/traceability schemas, templates, and tests.
- Working `product-delivery-estimate` skill with three-point work breakdowns, per-item AI impact,
  calendar and operating scenarios, pricing guardrails, immutable runs, schemas, and tests.
- Public synthetic workspace example under `examples/`; real `workspaces/` remain ignored.

### Changed

- Renamed the Python package and CLI from `spec_rigor` to `spec_viewer` / `spec-viewer`.

## [0.1.0] - 2026-07-15

### Added

- Stage 1 repository foundation, placeholder skills, schemas, templates, standards, and examples.
- Safe workspace and immutable run initialization.
- Offline schema, repository, privacy, secret, lint, type, test, and CI validation.
