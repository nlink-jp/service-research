#!/usr/bin/env python3
"""Behaviour tests for the bundled scripts (stdlib only).

Runs validate.py and compile.py as subprocesses — the same way the skill
invokes them — against the fixture report and mutated copies of it.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "service-research" / "scripts"
FIXTURE = REPO / "tests" / "fixtures" / "sample-report.json"

SECTION_PARTS = (
    "overview",
    "terms_of_service",
    "user_data_handling",
    "data_security",
    "ai_agent_behavior",
)


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
    )


class ValidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, data: object, name: str = "report.json") -> Path:
        path = Path(self.tmp.name) / name
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_fixture_validates_full(self) -> None:
        proc = run("validate.py", str(FIXTURE))
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("OK", proc.stdout)

    def test_each_section_part_validates(self) -> None:
        for part in SECTION_PARTS:
            with self.subTest(part=part):
                path = self.write(self.report[part], f"{part}.json")
                proc = run("validate.py", "--part", part, str(path))
                self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_synthesis_part_validates(self) -> None:
        synthesis = {
            k: self.report[k]
            for k in (
                "cautions",
                "overall_risk_level",
                "risk_assessment_notes",
                "natural_language_summary",
            )
        }
        proc = run("validate.py", "--part", "synthesis", str(self.write(synthesis)))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_missing_required_field_fails(self) -> None:
        del self.report["overview"]["provider"]
        proc = run("validate.py", str(self.write(self.report)))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing required field 'provider'", proc.stdout)

    def test_bad_risk_level_fails(self) -> None:
        self.report["overall_risk_level"] = "critical"
        proc = run("validate.py", str(self.write(self.report)))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("overall_risk_level", proc.stdout)

    def test_empty_sources_fails(self) -> None:
        self.report["sources"] = []
        proc = run("validate.py", str(self.write(self.report)))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("at least 1 item", proc.stdout)

    def test_bad_research_date_fails(self) -> None:
        self.report["research_date"] = "31/07/2026"
        proc = run("validate.py", str(self.write(self.report)))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("ISO 8601 date", proc.stdout)

    def test_null_website_is_accepted(self) -> None:
        self.report["overview"]["website"] = None
        proc = run("validate.py", str(self.write(self.report)))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_null_required_string_fails(self) -> None:
        self.report["overview"]["description"] = None
        proc = run("validate.py", str(self.write(self.report)))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("got null", proc.stdout)

    def test_non_boolean_fails(self) -> None:
        self.report["data_security"]["vulnerability_disclosure_program"] = "yes"
        proc = run("validate.py", str(self.write(self.report)))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("expected boolean", proc.stdout)

    def test_invalid_json_fails(self) -> None:
        path = Path(self.tmp.name) / "broken.json"
        path.write_text("{not json", encoding="utf-8")
        proc = run("validate.py", str(path))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("invalid JSON", proc.stdout)


class CompileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def compile(self, *extra: str) -> str:
        out = Path(self.tmp.name) / "report.md"
        proc = run("compile.py", str(FIXTURE), "-o", str(out), *extra)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return out.read_text(encoding="utf-8")

    def test_japanese_layout(self) -> None:
        md = self.compile()
        self.assertIn("# 製品・サービス調査レポート: ExampleChat", md)
        self.assertIn("| **調査日** | 2026-07-31 |", md)
        self.assertIn("| **リスクレベル** | 🟡 Medium |", md)
        self.assertIn("## ⚠️ 重要な注意事項", md)
        self.assertIn("## 📊 リスク評価の根拠", md)
        self.assertIn("## 📚 参照ソース", md)
        self.assertIn("- https://chat.example.com/terms", md)

    def test_english_labels(self) -> None:
        md = self.compile("--lang", "en")
        self.assertIn("# Product/Service Research Report: ExampleChat", md)
        self.assertIn("| **Research date** | 2026-07-31 |", md)
        self.assertIn("## ⚠️ Important Cautions", md)
        self.assertIn("## 📚 Sources", md)

    def test_summary_body_is_embedded(self) -> None:
        md = self.compile()
        self.assertIn("## 製品概要", md)
        self.assertIn("## 総合評価", md)


if __name__ == "__main__":
    unittest.main(verbosity=1)
