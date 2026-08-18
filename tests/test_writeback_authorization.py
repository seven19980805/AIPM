"""Writeback must be authorized by its own explicit evidence.

A writeback is only authorized when the writeback decision itself names a target
system, a writeback action, an authorization owner, and observable acceptance
evidence. It may never borrow the session's global business owner or unrelated
acceptance criteria, and a caller-supplied "authorized" status is never trusted.
"""

from __future__ import annotations

import unittest

from app.services.build_brief import render_build_brief
from app.services.coding_contract import build_coding_contract
from app.services.interview_state import decision_has_required_evidence_v2
from app.services.structured_requirement_model import (
    normalize_structured_requirement_model,
)
from tests.test_ai_pm_production_contract import confirmed_requirement_model


WRITEBACK_DEPENDENCY = (
    "Write the disposition result back to MES by posting the QA decision."
)

AUTHORIZED_EN = {
    "target_system": "MES",
    "action": "Post the QA disposition to the lot record",
    "authorization_owner": "Quality manager",
    "acceptance_evidence": "MES shows the posted disposition within 5 minutes.",
}

AUTHORIZED_ZH = {
    "target_system": "MES",
    "action": "写入判定结果到批次记录",
    "authorization_owner": "质量经理",
    "acceptance_evidence": "MES 中可以在 5 分钟内看到已写入的判定结果。",
}


def _writeback_model(authorization: dict | None, language: str = "en") -> dict:
    model = confirmed_requirement_model()
    model["data_and_dependencies"] = [
        "Read lot records from MES; refresh every 15 minutes."
        if language == "en"
        else "从 MES 读取批次记录，每 15 分钟刷新。",
        WRITEBACK_DEPENDENCY
        if language == "en"
        else "把判定结果回写到 MES，登记 QA 判定。",
    ]
    if authorization is not None:
        model["writeback_authorization"] = authorization
    return model


def _contract(model: dict) -> dict:
    return build_coding_contract(
        model,
        session_id="writeback-session",
        title="Writeback authorization",
        workflow_mode="scratch",
        language="en",
    )


class WritebackFailsClosedTest(unittest.TestCase):
    def test_legacy_model_without_the_block_stays_pending(self) -> None:
        model = _writeback_model(None)

        self.assertFalse(
            decision_has_required_evidence_v2(model, "data_boundary")
        )
        contract = _contract(model)
        self.assertFalse(contract["data_policy"]["writeback_authorized"])
        self.assertTrue(contract["data_policy"]["pending_writeback"])
        self.assertEqual("forbidden", contract["data_policy"]["writeback_default"])

    def test_global_owner_and_acceptance_no_longer_authorize_writeback(self) -> None:
        model = _writeback_model(None)
        model["product_context"]["business_owner"] = "Quality manager"
        model["product_context"]["acceptance_owner"] = "Quality manager"
        model["acceptance_criteria"] = [
            "Quality engineer can identify the top loss code within 5 minutes."
        ]

        self.assertFalse(
            decision_has_required_evidence_v2(model, "data_boundary"),
            "a global owner and unrelated acceptance must not authorize writeback",
        )
        self.assertFalse(_contract(model)["data_policy"]["writeback_authorized"])

    def test_client_supplied_authorized_status_is_not_trusted(self) -> None:
        model = _writeback_model({"status": "authorized"})

        normalized = normalize_structured_requirement_model(model)
        self.assertEqual(
            "pending",
            normalized["writeback_authorization"]["status"],
        )
        self.assertFalse(
            decision_has_required_evidence_v2(model, "data_boundary")
        )
        self.assertFalse(_contract(model)["data_policy"]["writeback_authorized"])

    def test_partial_authorization_stays_pending(self) -> None:
        for missing in AUTHORIZED_EN:
            with self.subTest(missing=missing):
                authorization = dict(AUTHORIZED_EN)
                authorization[missing] = ""
                model = _writeback_model(authorization)

                self.assertFalse(
                    decision_has_required_evidence_v2(model, "data_boundary")
                )

    def test_unapproved_target_system_is_not_authorized(self) -> None:
        authorization = dict(AUTHORIZED_EN, target_system="MySQL")
        model = _writeback_model(authorization)

        self.assertEqual(
            "pending",
            normalize_structured_requirement_model(model)[
                "writeback_authorization"
            ]["status"],
        )
        self.assertFalse(
            decision_has_required_evidence_v2(model, "data_boundary")
        )

    def test_unobservable_acceptance_evidence_is_not_authorized(self) -> None:
        authorization = dict(
            AUTHORIZED_EN,
            acceptance_evidence="It should be fine.",
        )
        model = _writeback_model(authorization)

        self.assertFalse(
            decision_has_required_evidence_v2(model, "data_boundary")
        )


class WritebackEvidenceStrictnessTest(unittest.TestCase):
    """Vague authorization evidence must not pass a production gate."""

    VAGUE_EVIDENCE = (
        "shows it",
        "it works",
        "看到了",
        "OK",
    )
    VAGUE_ACTION = (
        "post",
        "update",
        "写入",
    )

    def test_vague_acceptance_evidence_is_rejected(self) -> None:
        for evidence in self.VAGUE_EVIDENCE:
            with self.subTest(evidence=evidence):
                model = _writeback_model(
                    dict(AUTHORIZED_EN, acceptance_evidence=evidence)
                )
                self.assertFalse(
                    decision_has_required_evidence_v2(model, "data_boundary")
                )

    def test_bare_action_verb_is_rejected(self) -> None:
        for action in self.VAGUE_ACTION:
            with self.subTest(action=action):
                model = _writeback_model(dict(AUTHORIZED_EN, action=action))
                self.assertFalse(
                    decision_has_required_evidence_v2(model, "data_boundary")
                )

    NATURAL_ACTIONS = (
        "Record the QA disposition on the lot record",
        "Log the inspection result to the lot",
        "Save the corrected yield to the lot row",
        "Submit the disposition to the lot record",
        "Mark the lot as released in the system",
        "Write the disposition onto the lot record",
        "回填判定结果到批次记录",
        "记录检验结果到批次",
        "保存修正后的良率到批次行",
        "上报判定结果到批次记录",
        "Die QA-Entscheidung im Los eintragen",
        "Das Ergebnis im Los speichern",
        "Rekod keputusan QA pada rekod lot",
        "Simpan keputusan pemeriksaan ke lot",
    )

    def test_natural_action_wording_is_not_rejected(self) -> None:
        for action in self.NATURAL_ACTIONS:
            with self.subTest(action=action):
                model = _writeback_model(dict(AUTHORIZED_EN, action=action))

                self.assertTrue(
                    decision_has_required_evidence_v2(model, "data_boundary"),
                    f"a legitimate writeback action was rejected: {action}",
                )

    def test_specific_action_and_evidence_are_accepted(self) -> None:
        for language, authorization in (
            ("en", AUTHORIZED_EN),
            ("zh", AUTHORIZED_ZH),
        ):
            with self.subTest(language=language):
                model = _writeback_model(authorization, language=language)
                self.assertTrue(
                    decision_has_required_evidence_v2(model, "data_boundary")
                )


class WritebackAuthorizedTest(unittest.TestCase):
    def test_complete_authorization_confirms_and_reaches_delivery_docs(self) -> None:
        for language, authorization in (
            ("en", AUTHORIZED_EN),
            ("zh", AUTHORIZED_ZH),
        ):
            with self.subTest(language=language):
                model = _writeback_model(authorization, language=language)

                self.assertEqual(
                    "authorized",
                    normalize_structured_requirement_model(model)[
                        "writeback_authorization"
                    ]["status"],
                )
                self.assertTrue(
                    decision_has_required_evidence_v2(model, "data_boundary")
                )
                brief = render_build_brief(
                    model,
                    title="Authorized writeback",
                    intake_mode="scratch",
                    business_route="quality",
                    language=language,
                )
                self.assertNotIn("Writeback not authorized", brief)
                self.assertNotIn("写回尚未授权", brief)

    def test_contract_publishes_the_authorization_record(self) -> None:
        model = _writeback_model(AUTHORIZED_EN)

        policy = _contract(model)["data_policy"]

        self.assertTrue(policy["writeback_authorized"])
        self.assertFalse(policy["pending_writeback"])
        self.assertEqual("forbidden", policy["writeback_default"])
        self.assertEqual(
            "MES",
            policy["writeback_authorization"]["target_system"],
        )
        self.assertEqual(
            "Quality manager",
            policy["writeback_authorization"]["authorization_owner"],
        )


if __name__ == "__main__":
    unittest.main()
