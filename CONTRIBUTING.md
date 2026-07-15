# Contributing

## Setup and workflow

Create a Python 3.13 virtual environment and install `-e '.[dev]'`. Use a short-lived branch,
focused commits, and run `./scripts/check.sh` before opening a pull request.

## Contract changes

A schema change requires its standard, templates, valid and negative tests, and changelog to change
together. A template change must remain copy-safe and pass repository validation. A new artifact or
issue type requires a documented identifier, schema support, template impact review, and tests.

Skills belong in `.agents/skills/<lowercase-hyphen-name>/` with valid `SKILL.md` frontmatter.
References, scripts, and assets must be loaded only when useful; one skill has one responsibility.

## Pull request checklist

- Run formatting, lint, strict mypy, tests, schemas, repository, privacy, and secret checks.
- Confirm no workspace, `_private` path, credential, or real project document is tracked.
- Classify every example as approved synthetic or sanitized data.
- Update documentation and `CHANGELOG.md` for visible behavior.
- Describe schema and template compatibility effects.
