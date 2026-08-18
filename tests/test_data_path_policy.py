"""Contract tests for the approved data-path policy.

The interview gate and the delivery documents must agree on the same answer:
a dependency the interview confirms may never be scrubbed to "unconfirmed" in
the Build Brief, and a dependency the documents reject may never unlock Go
Coding.
"""

from __future__ import annotations

import unittest

from app.services.build_brief import render_build_brief
from app.services.coding_contract import build_coding_contract
from app.services.data_source_policy import sanitize_data_dependencies
from app.services.interview_state import decision_has_required_evidence_v2
from tests.test_ai_pm_production_contract import confirmed_requirement_model


APPROVED_READ_ONLY_PATHS = {
    "sql_server": "Read finished-lot records from SQL Server; the first release is read-only.",
    "sap": "Read approved master data from SAP; no source-system writeback.",
    "mes": "Read lot travel history from MES; the first release is read-only.",
    "qis": "Read inspection results from QIS; no source-system writeback.",
    "qms": "Read CAPA records from QMS; the first release is read-only.",
    "excel_csv": "Start from a user-uploaded Excel or CSV file; no production writeback.",
}

UNAPPROVED_DATABASES = ("PostgreSQL", "MySQL", "Oracle", "MongoDB")


def _brief(model: dict, language: str = "en") -> str:
    return render_build_brief(
        model,
        title="Data path policy",
        intake_mode="scratch",
        business_route="production",
        language=language,
    )


class ApprovedReadOnlyPathTest(unittest.TestCase):
    def test_approved_read_only_sources_confirm_and_reach_delivery_docs(self) -> None:
        for source, dependency in APPROVED_READ_ONLY_PATHS.items():
            with self.subTest(source=source):
                model = confirmed_requirement_model()
                model["data_and_dependencies"] = [dependency]

                self.assertTrue(
                    decision_has_required_evidence_v2(model, "data_boundary"),
                    f"{source} read-only path should confirm the data boundary",
                )
                brief = _brief(model)
                self.assertIn(dependency, brief)
                self.assertNotIn("Unconfirmed data source", brief)

    def test_cjk_upload_wording_is_an_approved_path(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = ["由用户手动上传良率数据，首版只读。"]

        self.assertTrue(
            decision_has_required_evidence_v2(model, "data_boundary")
        )
        self.assertEqual(
            ["由用户手动上传良率数据，首版只读。"],
            sanitize_data_dependencies(
                model["data_and_dependencies"],
                language="zh",
            ),
        )


class UnapprovedSourceTest(unittest.TestCase):
    def test_unapproved_databases_neither_confirm_nor_reach_delivery_docs(self) -> None:
        for source in UNAPPROVED_DATABASES:
            with self.subTest(source=source):
                model = confirmed_requirement_model()
                model["data_and_dependencies"] = [
                    f"Read quality records from {source}; the first release is read-only."
                ]

                self.assertFalse(
                    decision_has_required_evidence_v2(model, "data_boundary"),
                    f"{source} is not an approved path and must not confirm",
                )
                brief = _brief(model)
                self.assertNotIn(source, brief)
                self.assertIn("Unconfirmed data source", brief)


class WritebackAuthorizationTest(unittest.TestCase):
    WRITEBACK = "Write the disposition result back to MES by posting the QA decision."

    AUTHORIZATION = {
        "target_system": "MES",
        "action": "Post the QA disposition to the lot record",
        "authorization_owner": "Quality manager",
        "acceptance_evidence": "MES shows the posted disposition within 5 minutes.",
    }

    def test_writeback_without_its_own_authorization_stays_pending(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = [self.WRITEBACK]

        self.assertFalse(
            decision_has_required_evidence_v2(model, "data_boundary"),
            "a session-wide owner and acceptance must not authorize writeback",
        )

    def test_writeback_without_named_action_stays_pending(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = ["Writeback to MES is allowed."]

        self.assertFalse(
            decision_has_required_evidence_v2(model, "data_boundary")
        )

    def test_pending_writeback_is_flagged_not_scrubbed_as_unconfirmed(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = [self.WRITEBACK]
        model["acceptance_criteria"] = []

        brief = _brief(model)

        self.assertIn("MES", brief)
        self.assertNotIn("Unconfirmed data source", brief)
        self.assertIn("Writeback not authorized", brief)

    def test_pending_writeback_does_not_unlock_go_coding(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = [self.WRITEBACK]
        model["acceptance_criteria"] = []

        contract = build_coding_contract(
            model,
            session_id="pending-writeback-session",
            title="Pending writeback",
            workflow_mode="scratch",
            language="en",
        )

        self.assertEqual("forbidden", contract["data_policy"]["writeback_default"])
        self.assertFalse(contract["data_policy"]["writeback_authorized"])
        self.assertIn("mes", contract["data_policy"]["referenced_sources"])

    def test_fully_authorized_writeback_confirms_the_boundary(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = [self.WRITEBACK]
        model["writeback_authorization"] = dict(self.AUTHORIZATION)

        self.assertTrue(
            decision_has_required_evidence_v2(model, "data_boundary")
        )
        contract = build_coding_contract(
            model,
            session_id="authorized-writeback-session",
            title="Authorized writeback",
            workflow_mode="scratch",
            language="en",
        )
        self.assertTrue(contract["data_policy"]["writeback_authorized"])


class DetailOnlyDependencyTest(unittest.TestCase):
    """Neutral detail lines survive once a legitimate source is already named."""

    DETAILS = {
        "en": (
            "Read finished-lot records from SQL Server; the first release is read-only.",
            "Join by lot_id and product_code; fields include yield_pct and loss_code.",
            "Refresh the view every five minutes.",
        ),
        "zh": (
            "从 SQL Server 读取成品批次记录，首版只读。",
            "按 lot_id 和 product_code 关联；字段包含 yield_pct 与 loss_code。",
            "视图每五分钟刷新一次。",
        ),
    }

    def test_detail_only_lines_reach_the_build_brief(self) -> None:
        for language, dependencies in self.DETAILS.items():
            with self.subTest(language=language):
                model = confirmed_requirement_model()
                model["data_and_dependencies"] = list(dependencies)

                brief = _brief(model, language=language)

                for dependency in dependencies:
                    self.assertIn(dependency, brief)
                self.assertNotIn("Unconfirmed data source", brief)
                self.assertNotIn("数据来源待确认", brief)
                self.assertTrue(
                    decision_has_required_evidence_v2(model, "data_boundary")
                )

    def test_detail_only_lines_reach_the_coding_contract(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = list(self.DETAILS["en"])

        contract = build_coding_contract(
            model,
            session_id="detail-only-session",
            title="Detail only dependencies",
            workflow_mode="scratch",
            language="en",
        )
        dependency_text = " ".join(
            item["requirement"] for item in contract["data_dependencies"]
        )

        self.assertIn("lot_id", dependency_text)
        self.assertIn("five minutes", dependency_text)
        self.assertNotIn("Unconfirmed data source", dependency_text)

    def test_detail_lines_do_not_rescue_an_unapproved_database(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = [
            "Read quality records from MySQL; the first release is read-only.",
            "Join by lot_id and product_code.",
            "Refresh every five minutes.",
        ]

        brief = _brief(model)

        self.assertNotIn("MySQL", brief)
        self.assertIn("Unconfirmed data source", brief)
        self.assertFalse(
            decision_has_required_evidence_v2(model, "data_boundary")
        )

    def test_detail_lines_without_any_source_stay_unconfirmed(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = ["Refresh every five minutes."]

        self.assertFalse(
            decision_has_required_evidence_v2(model, "data_boundary")
        )
        self.assertIn("Unconfirmed data source", _brief(model))


class NamedSourceStrictnessTest(unittest.TestCase):
    """A data path must name the actual system, not a generic technology."""

    AMBIGUOUS = (
        "Read-only access to a SQL view refreshed every 15 minutes.",
        "Read-only access to our database; no source-system writeback.",
        "只读访问我们的数据库，不回写。",
    )

    def test_ambiguous_technology_names_do_not_confirm(self) -> None:
        for dependency in self.AMBIGUOUS:
            with self.subTest(dependency=dependency):
                model = confirmed_requirement_model()
                model["data_and_dependencies"] = [dependency]

                self.assertFalse(
                    decision_has_required_evidence_v2(model, "data_boundary"),
                    "a generic technology name is not a named data path",
                )

    def test_ambiguous_sources_are_flagged_in_the_brief(self) -> None:
        for dependency in self.AMBIGUOUS:
            with self.subTest(dependency=dependency):
                model = confirmed_requirement_model()
                model["data_and_dependencies"] = [dependency]

                brief = _brief(model)

                self.assertIn(
                    "Unconfirmed data source",
                    brief,
                    "a blocked decision must not render as a clean brief",
                )

    def test_named_sql_server_still_confirms(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = [
            "Read-only access to the SQL Server view dbo.v_e_test; refreshed every 15 minutes."
        ]

        self.assertTrue(
            decision_has_required_evidence_v2(model, "data_boundary")
        )


class StrayNoteTest(unittest.TestCase):
    """Detail lines ride along only when they are actual data details."""

    SOURCE = "Read finished-lot records from SQL Server; the first release is read-only."

    def test_stray_note_never_reaches_delivery_docs(self) -> None:
        strays = (
            "Let me check with my team tomorrow.",
            "The plant manager prefers a dark theme.",
            "下周再和团队确认一下。",
        )
        for stray in strays:
            with self.subTest(stray=stray):
                model = confirmed_requirement_model()
                model["data_and_dependencies"] = [self.SOURCE, stray]

                brief = _brief(model)
                contract = build_coding_contract(
                    model,
                    session_id="stray-note",
                    title="Stray note",
                    workflow_mode="scratch",
                    language="en",
                )
                dependency_text = " ".join(
                    item["requirement"] for item in contract["data_dependencies"]
                )

                self.assertNotIn(stray, brief)
                self.assertNotIn(stray, dependency_text)

    def test_real_data_details_still_ride_along(self) -> None:
        details = (
            "Join by lot_id and product_code; fields include yield_pct.",
            "Refresh the view every five minutes.",
            "Read from the dbo.v_e_test view.",
        )
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = [self.SOURCE, *details]

        brief = _brief(model)

        for detail in details:
            self.assertIn(detail, brief)
        self.assertNotIn("Unconfirmed data source", brief)


class PolicyAgreementTest(unittest.TestCase):
    """The interview gate and the delivery documents may never disagree."""

    def test_confirmed_answers_are_never_scrubbed_as_unconfirmed(self) -> None:
        cases = {
            **APPROVED_READ_ONLY_PATHS,
            "unapproved_db": (
                "Read quality records from MySQL; the first release is read-only."
            ),
            "pending_writeback": (
                "Write the disposition result back to MES by posting the QA decision."
            ),
            "detail_only": (
                "Join by lot_id and product_code; refresh every five minutes."
            ),
        }

        for label, dependency in cases.items():
            with self.subTest(case=label):
                model = confirmed_requirement_model()
                model["data_and_dependencies"] = [dependency]
                confirmed = decision_has_required_evidence_v2(
                    model,
                    "data_boundary",
                )
                scrubbed = "Unconfirmed data source" in _brief(model)

                self.assertFalse(
                    confirmed and scrubbed,
                    f"{label} is confirmed by the interview but scrubbed in the brief",
                )

    def test_every_layer_agrees_on_the_same_dependency_set(self) -> None:
        """interview_state, build_brief, and coding_contract stay in lockstep."""

        cases = {
            "approved_read_only": [
                "Read finished-lot records from SQL Server; the first release is read-only.",
                "Join by lot_id; refresh every five minutes.",
            ],
            "unapproved_db": [
                "Read quality records from Oracle; the first release is read-only.",
            ],
            "pending_writeback": [
                "Read lot records from MES; the first release is read-only.",
                "Write the disposition back to MES by posting the QA decision.",
            ],
        }

        for label, dependencies in cases.items():
            with self.subTest(case=label):
                model = confirmed_requirement_model()
                model["data_and_dependencies"] = dependencies

                confirmed = decision_has_required_evidence_v2(
                    model,
                    "data_boundary",
                )
                brief = _brief(model)
                contract = build_coding_contract(
                    model,
                    session_id=f"consistency-{label}",
                    title="Layer consistency",
                    workflow_mode="scratch",
                    language="en",
                )
                policy = contract["data_policy"]
                contract_clean = not policy["pending_writeback"] and all(
                    "Unconfirmed data source" not in item["requirement"]
                    for item in contract["data_dependencies"]
                )
                brief_clean = "Unconfirmed data source" not in brief

                self.assertEqual(
                    confirmed,
                    brief_clean and contract_clean,
                    f"{label}: interview={confirmed} brief_clean={brief_clean} "
                    f"contract_clean={contract_clean}",
                )


if __name__ == "__main__":
    unittest.main()


class PolicyCopyConsistencyTest(unittest.TestCase):
    """Every layer must state the same approved data paths."""

    def test_build_brief_policy_footer_names_the_approved_systems(self) -> None:
        for language in ("en", "zh", "de", "ms"):
            with self.subTest(language=language):
                model = confirmed_requirement_model()
                model["data_and_dependencies"] = [
                    "Read lot records from MES; the first release is read-only."
                ]

                brief = _brief(model, language=language)

                self.assertIn(
                    "MES",
                    brief,
                    "the brief keeps a MES dependency but its policy footer "
                    "must not call MES disallowed",
                )
                self.assertNotIn("upload only", brief)
                self.assertNotIn("upload sahaja", brief)
                self.assertNotIn("仅限", brief)

    def test_extraction_prompt_states_the_current_data_policy(self) -> None:
        from app.services.structured_requirement_model import (
            STRUCTURED_REQUIREMENT_MODEL_SYSTEM_PROMPT,
        )

        self.assertNotIn(
            "is not a connector",
            STRUCTURED_REQUIREMENT_MODEL_SYSTEM_PROMPT,
            "the extractor must not be told MES/QIS is disallowed",
        )
        self.assertIn("MES", STRUCTURED_REQUIREMENT_MODEL_SYSTEM_PROMPT)
