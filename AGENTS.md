# AGENTS.md — service-research

## Project summary

Claude Code Skill that researches a product or service — overview, pricing,
terms of service, privacy policy, data security, AI-agent behavior — by
reading the primary sources on the web, and emits a schema-validated JSON
report with a three-tier risk rating plus a compiled Markdown summary.
Invoked as `/service-research <name>`. Successor to the archived
product-research CLI ([ADR-0001](docs/en/adr/0001-agentic-research.md));
same JSON structure, but research is an
agentic loop that actually fetches ToS/privacy pages instead of one
search-grounded Gemini call.

## Key commands

| Command | Purpose |
|---------|---------|
| `make check` (= `make test`) | Structural validation + script behaviour tests |
| `make install` | Copy the skill to `~/.claude/skills/service-research` |
| `make install DEST=<path>` | Copy to a custom skills directory |
| `make uninstall` | Remove the installed copy |
| `make package` | Build `dist/service-research-vX.Y.Z.zip` (zip root = skill folder) |
| `make clean` | Remove `dist/` |

## Directory structure

```
service-research/
├── service-research/        The skill — the only thing that ships
│   ├── SKILL.md             Frontmatter + phased research workflow
│   ├── schema.json          ResearchReport JSON Schema (draft-07 subset)
│   ├── references/
│   │   └── report-format.md Field semantics, risk criteria, output layout
│   └── scripts/             stdlib-only Python (3.9+), no third-party deps
│       ├── validate.py      Schema validation (full or --part <section>)
│       └── compile.py       Markdown renderer (ja/en), ported from the CLI
├── tests/
│   ├── validate-skill.sh    Frontmatter + link structure checks (vendored)
│   ├── run-script-tests.py  unittest suite for the scripts
│   └── fixtures/            sample-report.json — simulated product, safe
│                            placeholder domains only
├── Makefile
├── README.md / README.ja.md
├── CHANGELOG.md
├── CLAUDE.md / AGENTS.md
└── LICENSE
```

## Gotchas

- The `service-research/` subdirectory is the distribution boundary
  (ADR-004): `make package` zips exactly that directory, so the zip root is
  the skill folder — the layout claude.ai accepts. Never add repo-level
  files inside it, and never bundle README.md into the zip.
- The directory name is the slash command; frontmatter `name` must match it.
  `make check` enforces this.
- **Scripts must stay stdlib-only** — they run wherever the skill is
  installed (Claude Code hosts, claude.ai sandboxes); a pip dependency would
  break them silently.
- `scripts/validate.py` is a deliberate subset of JSON Schema (type incl.
  `["string","null"]` unions, required, properties, items, enum, minItems,
  format: date). If schema.json ever grows beyond that subset, extend the
  validator with it.
- `tests/validate-skill.sh` is a byte-identical vendored copy of
  `.github/templates/validate-skill.sh` (ADR-006) — never edit it here;
  check-org.sh check 10b fails on drift.
- The JSON structure is carried over from the archived product-research CLI
  so old reports stay valid — `test_fixture_validates_full` and the compile
  tests pin this; don't remove or retype existing fields casually.
- `tests/fixtures/sample-report.json` is a simulated product using
  example.com domains only; keep it free of real vendor data and real URLs.
- SKILL.md's security preamble (fetched pages are untrusted data) is the
  injection defense and sits first by design — keep it at the top.
- After editing SKILL.md or scripts, run `make install` to refresh the
  deployed copy.
- Releases follow the org checklist with `make package` in place of a binary
  build; before uploading, unzip the artifact and confirm
  `service-research/SKILL.md` sits directly under the zip root.

## Module path

Repository: `github.com/nlink-jp/service-research`
