# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-07-31

### Added

- Initial release. Claude Code Skill successor to the
  [product-research](https://github.com/nlink-jp/product-research) CLI
  (v0.1.x), converted per
  [ADR-007](https://github.com/nlink-jp/.github/blob/main/adr/007-service-research-skill.md):
  the CLI's "autonomous web research" was a single search-grounded Gemini
  call that never opened a policy page.
- Agentic research workflow: scope → five research sections (overview / ToS /
  privacy / security / AI-agent behavior), each fetching and reading the
  primary pages and validated on the spot → risk synthesis → assembly →
  compile. `sources` lists only URLs actually read; known breaches are
  searched independently of vendor claims.
- `scripts/validate.py` — stdlib-only schema validation (full report or
  per-section `--part`), including risk-level enum, ISO-date, nullable-URL,
  and non-empty-`sources` checks.
- `scripts/compile.py` — Markdown renderer ported from the CLI's
  `format_full_output()`; adds an `--lang en` label set (the CLI rendered
  Japanese labels only).
- JSON structure unchanged from the CLI (`schema.json`,
  `references/report-format.md`); CLI-produced reports validate and compile
  as-is.
- Out of scope vs the CLI: `--json-only`/`--no-save` pipe mode — and no GCP
  project, ADC, or Vertex AI cost required anymore.
