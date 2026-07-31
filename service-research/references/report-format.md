# ResearchReport — field semantics and output format

The JSON structure is carried over unchanged from the archived
`product-research` CLI (its Pydantic models), so old and new reports remain
directly comparable. `schema.json` is the structural contract; this file
explains what belongs in each field.

## Conventions

- **Unknown ≠ guessed.** A text field with no finding holds `不明` (ja) /
  `unknown` (en); a list holds `[]`; a nullable URL field holds `null`. A
  boolean that could not be determined is `false`, with the uncertainty
  stated in the nearest notes/concerns field.
- **Language**: every free-text field is written in the report language
  (`--lang`); proper nouns stay as the source writes them.
- **`sources` is evidence, not decoration**: only URLs actually fetched and
  read during this research run. This is what distinguishes the report from
  model recall.

## Sections

### `overview`

What the product is and who sells it. `pricing.model` names the scheme
(subscription / freemium / one-time / usage-based …); `pricing.tiers` lists
plan names, with prices when published. `pricing.notes` carries anything
price-relevant that doesn't fit (regional pricing, mandatory add-ons).

### `terms_of_service`

Extracted from the **fetched, current** ToS page (`url` = the page read).
`key_points` are the clauses a prospective user most needs to know;
`restrictions` are prohibited uses; `termination_conditions` covers both
provider-initiated suspension and user-initiated cancellation.
`last_updated` is the date stated on the page, if any.

### `user_data_handling`

Extracted from the **fetched** privacy policy (`privacy_policy_url`).
`third_party_sharing` names categories or companies as the policy does.
`user_rights` lists the rights granted and under which regimes (GDPR, CCPA,
APPI …). `notable_concerns` is deliberately candid: model-training use,
broad "partners" clauses, indefinite retention, dark-pattern opt-outs.

### `data_security`

Vendor claims (trust center) **plus independent findings**: `known_breaches`
comes from news/incident searching, not the vendor's own page, and each entry
names the year and what happened. `restrictions_for_sensitive_data` states
what the vendor says about regulated data (PHI, PCI, PII) — including "no
commitment found".

### `ai_agent_behavior`

Only meaningful for products with autonomous AI features (agents that plan
and execute, call external services, run code). `action_scope` describes the
blast radius; `user_control_mechanisms` and `approval_required_actions`
describe what stands between the agent and that radius. Products without such
features: `has_autonomous_behavior: false`, empty lists, `該当なし` /
`not applicable` in text fields.

## Risk rating

| Level | Meaning |
|---|---|
| `low` | Mature policies, credible certifications, no unresolved incidents; autonomous behavior (if any) well-controlled |
| `medium` | Gaps or ambiguity in policies, broad data sharing, past incidents since remediated |
| `high` | Recent/unresolved breaches, invasive data practices, unverifiable security posture, or autonomous actions without user controls |

`risk_assessment_notes` must tie the rating to specific findings — it is the
justification, not a restatement. When torn between two levels, pick the
higher and say why.

## `natural_language_summary` headings

Exactly these, in order:

| ja (default) | en (`--lang en`) |
|---|---|
| `## 製品概要` | `## Overview` |
| `## 主要機能` | `## Main Features` |
| `## 利用規約の要点` | `## Terms of Service` |
| `## プライバシー・データ取り扱い` | `## Privacy & Data Handling` |
| `## セキュリティ状況` | `## Security Posture` |
| `## AI エージェント動作と制御` | `## AI Agent Behavior & Controls` |
| `## ユーザーへの注意事項` | `## Cautions for Users` |
| `## 総合評価` | `## Overall Assessment` |

## Markdown output

`scripts/compile.py` renders the JSON deterministically: a header table
(research date / provider / category / risk level with 🟢🟡🔴), the
`natural_language_summary` body, the cautions list, the risk rationale, and
the sources list. The Markdown file is a *view* of the JSON — regenerate it
with compile.py rather than editing it by hand.
