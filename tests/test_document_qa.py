"""Unit tests for the structured Document QA module.

These lock the contracts:
  1. ``build_document_qa_state`` produces the structured payload the frontend
     consumes directly (instead of regex-reparsing the document Markdown).
  2. ``to_api_state`` exposes only the fields the client reads (renderer-only
     fields are stripped from the API payload).
  3. ``render_document_qa_appendix`` (rendered FROM that state) keeps a stable,
     well-formed QA section in the generated document, derived from the same
     state so the document text and the structured payload can never drift.
"""

import unittest

from app.services import document_qa
from app.services.structured_requirement_model import normalize_structured_requirement_model

PROGRESS = {
    "readiness_percentage": 100,
    "collection_coverage_percentage": 100,
    "confirmation_percentage": 100,
}


def _model(**overrides):
    base = {
        "background": {"objective": "Monitor current shift output."},
        "business_rules": ["Behind schedule when actual < plan."],
        "functional_requirements": {"overview": "Plan vs actual table."},
        "acceptance_criteria": ["Cross-check with MES report."],
        "open_questions": [
            "Which MES API or database view provides the data?",
            "Is SSO or VPN authentication required?",
            "Are there any branding or color constraints?",
        ],
    }
    base.update(overrides)
    return normalize_structured_requirement_model(base)


class BuildDocumentQaStateTests(unittest.TestCase):
    def test_blocks_production_on_integration_questions_and_rule_finding(self) -> None:
        state = document_qa.build_document_qa_state(
            "# PRD\n\nPlan vs actual dashboard.",
            _model(),
            PROGRESS,
            is_design=False,
            source_kind="prd_doc",
        )
        self.assertEqual(state["source_kind"], "prd_doc")
        self.assertEqual(state["document_type"], "PRD")
        self.assertEqual(state["production_readiness"], "Blocked")
        self.assertEqual(state["demo_readiness"], "Ready with assumptions")
        self.assertEqual(state["open_question_count"], 3)
        # MES + SSO/VPN are production blockers; the branding question is demo-only.
        self.assertEqual(state["classification_counts"]["blocking_for_production"], 2)
        self.assertEqual(state["classification_counts"]["ok_for_demo"], 1)
        # "actual < plan" without time-phasing trips the behind-schedule sanity check.
        self.assertTrue(any("Behind-schedule rule" in f for f in state["business_rule_findings"]))
        self.assertTrue(any("MES" in b for b in state["production_blockers"]))

    def test_ready_when_no_questions_or_findings(self) -> None:
        state = document_qa.build_document_qa_state(
            "# PRD\n\nClean spec.",
            _model(open_questions=[], business_rules=["Behind schedule uses time-phased expected output."]),
            PROGRESS,
            is_design=False,
            source_kind="prd_doc",
        )
        self.assertEqual(state["production_readiness"], "Ready")
        self.assertEqual(state["demo_readiness"], "Ready")
        self.assertEqual(state["open_question_count"], 0)
        self.assertEqual(state["production_blockers"], [])

    def test_design_doc_flags_default_stack_and_mock(self) -> None:
        markdown = (
            "# System Design\n\nDefault technology stack: C#, SQLite.\n"
            "Use mock MES data for demo."
        )
        state = document_qa.build_document_qa_state(
            markdown,
            _model(open_questions=[]),
            PROGRESS,
            is_design=True,
            source_kind="design_doc",
        )
        self.assertEqual(state["document_type"], "Design")
        self.assertTrue(any("Technology stack" in f for f in state["implementation_findings"]))
        self.assertTrue(any("Mock/demo data" in f for f in state["implementation_findings"]))
        # mock data on a design doc adds the "Real MES integration" production blocker.
        self.assertTrue(any("Real MES integration" in b for b in state["production_blockers"]))


class RenderAppendixContractTests(unittest.TestCase):
    """The rendered Markdown keeps a stable, well-formed QA section in the doc."""

    APPENDIX_SECTION_KEYS_EN = (
        "## Document QA",
        "- **Document type**:",
        "- **Demo readiness**:",
        "- **Production readiness**:",
        "- **System-counted open questions**:",
        "### Production Blockers",
        "### Open Question Classification",
        "- **Blocking for production**:",
        "- **OK for demo / polish later**:",
        "- **Implementation assumptions**:",
        "- **Needs review**:",
        "### Business Rule Sanity Checks",
        "### Implementation Assumption Checks",
    )

    def test_en_render_contains_all_parser_keys(self) -> None:
        state = document_qa.build_document_qa_state(
            "# PRD",
            _model(),
            PROGRESS,
            is_design=False,
            source_kind="prd_doc",
        )
        markdown = document_qa.render_document_qa_appendix(state, "en")
        for key in self.APPENDIX_SECTION_KEYS_EN:
            self.assertIn(key, markdown)

    def test_zh_render_uses_bilingual_heading(self) -> None:
        state = document_qa.build_document_qa_state(
            "# PRD",
            _model(),
            PROGRESS,
            is_design=False,
            source_kind="prd_doc",
        )
        markdown = document_qa.render_document_qa_appendix(state, "zh")
        self.assertIn("## 文档质量检查 / Document QA", markdown)
        self.assertIn("### 生产版阻塞项", markdown)
        self.assertIn("- **Production readiness**：", markdown)


class ToApiStateTests(unittest.TestCase):
    """The API payload exposes only the fields the frontend reads."""

    def test_strips_renderer_only_fields(self) -> None:
        full = document_qa.build_document_qa_state(
            "# PRD\n\nPlan vs actual dashboard.",
            _model(),
            PROGRESS,
            is_design=False,
            source_kind="prd_doc",
        )
        # The full state carries renderer-only fields for the Markdown appendix.
        self.assertIn("classified_questions", full)
        self.assertIn("readiness_percentage", full)

        api = document_qa.to_api_state(full)
        for key in (
            "source_kind",
            "document_type",
            "demo_readiness",
            "production_readiness",
            "open_question_count",
            "production_blockers",
            "business_rule_findings",
            "implementation_findings",
            "classification_counts",
        ):
            self.assertIn(key, api)
        for key in (
            "classified_questions",
            "readiness_percentage",
            "collection_coverage_percentage",
            "confirmation_percentage",
        ):
            self.assertNotIn(key, api)

    def test_none_passes_through(self) -> None:
        self.assertIsNone(document_qa.to_api_state(None))


if __name__ == "__main__":
    unittest.main()
