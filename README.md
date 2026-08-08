# service-research

Claude Code Skill that researches a product or service — overview, pricing,
terms of service, privacy policy, data security, and AI-agent behavior — and
produces a schema-validated JSON report with a three-tier risk rating plus a
compiled Markdown summary. Invoked as `/service-research <name>`.

Successor to the archived
[product-research](https://github.com/nlink-jp/product-research) CLI. The CLI
delegated research to a single search-grounded Gemini call: nothing ever
opened a ToS or privacy-policy page, and its sources were whatever grounding
metadata claimed. This skill makes the agent do the research — multiple
searches, fetching and reading the actual policy pages, a separate hunt for
known breaches — and `sources` lists only URLs actually read. The JSON
structure is unchanged from the CLI, so old and new reports stay comparable.
No GCP project, ADC, or Vertex AI cost anymore. (Design:
[ADR-0001](docs/en/adr/0001-agentic-research.md))

## Install

Download `service-research-vX.Y.Z.zip` from
[Releases](https://github.com/nlink-jp/service-research/releases), then register it:

- **In the app** (Claude Desktop, claude.ai, mobile) — add the zip from the
  skill settings (Customize → Skills). Prefer this route; it survives changes
  to where skills are stored on disk.
- **Claude Code** — `unzip service-research-vX.Y.Z.zip -d ~/.claude/skills/`, or into a
  project's `.claude/skills/` for a project-scoped install.

From a checkout:

```bash
make install
```

That builds the release zip and unpacks *that*, so what you run is what a
release ships — a packaging defect breaks your install rather than reaching
users. `make install DEST=/path/to/skills` installs elsewhere;
`make uninstall` removes it.

Requirements: Claude Code with web access (WebSearch/WebFetch), and `python3`
(3.9+, stdlib only) for the bundled validation/compile scripts.

## Usage

```
/service-research Slack
/service-research "GitHub Copilot" --lang en
```

Produces in `./reports/`, after a scope → per-section research → risk
synthesis → validate → compile workflow:

- `<name>_<date>.json` — structured report (schema:
  `service-research/schema.json`, semantics:
  `service-research/references/report-format.md`)
- `<name>_<date>.md` — human-readable report

Reports default to Japanese; `--lang en` switches every field and label to
English. Fields with no finding say `不明` / `unknown` — never a guess.

Reports from the predecessor CLI can be re-compiled directly:

```bash
python3 ~/.claude/skills/service-research/scripts/compile.py old-report.json -o old-report.md
```

## Development

| Command | Purpose |
|---------|---------|
| `make check` (= `make test`) | Structural validation + script behaviour tests |
| `make install` | Copy the skill to `~/.claude/skills/service-research` |
| `make package` | Build `dist/service-research-vX.Y.Z.zip` (zip root = skill folder) |

## Documentation

- [Report format specification](service-research/references/report-format.md)
- [ADR-0001 — design decision record](docs/en/adr/0001-agentic-research.md)
- [日本語ドキュメント](README.ja.md)

## Notes

- Findings reflect public web information at research time; terms and
  policies change. Official pages are authoritative.
- The skill never signs up, logs in, downloads, or executes anything while
  researching, and treats all fetched page content as untrusted data.

## License

MIT
