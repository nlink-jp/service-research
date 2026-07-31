#!/usr/bin/env python3
"""Render a service-research JSON report as Markdown (stdlib only).

Usage:
    compile.py report.json -o report.md            # Japanese labels (default)
    compile.py report.json -o report.md --lang en  # English labels

The layout is ported from the product-research CLI's format_full_output():
header table, natural-language summary, cautions, risk rationale, sources.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RISK_EMOJI = {"low": "🟢 Low", "medium": "🟡 Medium", "high": "🔴 High"}

LABELS = {
    "ja": {
        "title": "製品・サービス調査レポート",
        "col_item": "項目",
        "col_value": "内容",
        "date": "調査日",
        "provider": "提供元",
        "category": "カテゴリ",
        "risk": "リスクレベル",
        "cautions": "## ⚠️ 重要な注意事項",
        "risk_notes": "## 📊 リスク評価の根拠",
        "sources": "## 📚 参照ソース",
    },
    "en": {
        "title": "Product/Service Research Report",
        "col_item": "Item",
        "col_value": "Value",
        "date": "Research date",
        "provider": "Provider",
        "category": "Category",
        "risk": "Risk level",
        "cautions": "## ⚠️ Important Cautions",
        "risk_notes": "## 📊 Risk Assessment Rationale",
        "sources": "## 📚 Sources",
    },
}


def render(report: dict, lang: str) -> str:
    lb = LABELS[lang]
    risk = report["overall_risk_level"]
    risk_label = RISK_EMOJI.get(risk.lower(), risk)
    lines = [
        f"# {lb['title']}: {report['product_name']}",
        "",
        f"| {lb['col_item']} | {lb['col_value']} |",
        "|------|------|",
        f"| **{lb['date']}** | {report['research_date']} |",
        f"| **{lb['provider']}** | {report['overview']['provider']} |",
        f"| **{lb['category']}** | {report['overview']['category']} |",
        f"| **{lb['risk']}** | {risk_label} |",
        "",
        "---",
        "",
        report["natural_language_summary"],
        "",
    ]

    if report.get("cautions"):
        lines += ["", lb["cautions"]]
        lines += [f"- {c}" for c in report["cautions"]]

    lines += ["", lb["risk_notes"], report["risk_assessment_notes"]]

    if report.get("sources"):
        lines += ["", lb["sources"]]
        lines += [f"- {s}" for s in report["sources"]]

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--lang", choices=["ja", "en"], default="ja")
    args = parser.parse_args()

    try:
        report = json.loads(args.json_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: {args.json_file}: invalid JSON: {e}", file=sys.stderr)
        return 1

    args.output.write_text(render(report, args.lang), encoding="utf-8")
    print(f"compiled: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
