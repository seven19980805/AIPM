from __future__ import annotations

import copy

import pytest

from app.services.interview_state import build_interview_state_v2


FAST_DECISION_ORDER = (
    "outcome",
    "actor_action",
    "v1_flow",
    "data_boundary",
    "acceptance",
)


def _empty_model() -> dict:
    return {
        "product_context": {
            "business_owner": "",
            "primary_user": "",
            "decision_or_action": "",
            "acceptance_owner": "",
        },
        "background": {"objective": ""},
        "scope": {"in_scope": [], "out_of_scope": []},
        "users_and_scenarios": {
            "target_users": [],
            "core_scenarios": [],
        },
        "functional_requirements": {
            "overview": "",
            "feature_details": [],
        },
        "business_rules": [],
        "data_and_dependencies": [],
        "acceptance_criteria": [],
        "collection_status": {
            key: {
                "status": "missing",
                "reason": "",
                "pending_questions": [],
            }
            for key in (
                "objective",
                "scope",
                "users",
                "scenarios",
                "features",
                "rules",
                "integrations",
                "acceptance",
                "ownership",
            )
        },
    }


def _confirm_fast_decision(model: dict, decision_id: str) -> None:
    status = model["collection_status"]
    if decision_id == "outcome":
        model["background"]["objective"] = (
            "Reduce false-fail e-test escapes by 15% next quarter."
        )
        status["objective"]["status"] = "confirmed"
    elif decision_id == "actor_action":
        model["product_context"]["primary_user"] = "Shift supervisor"
        model["product_context"]["decision_or_action"] = (
            "Schedule retests using yield trends by product code."
        )
        model["users_and_scenarios"]["target_users"] = ["Shift supervisor"]
        status["users"]["status"] = "confirmed"
    elif decision_id == "v1_flow":
        model["scope"]["in_scope"] = ["Real-time yield dashboard"]
        model["scope"]["out_of_scope"] = ["Automated lot disposition"]
        model["users_and_scenarios"]["core_scenarios"] = [
            "Inspect yield trends and choose lots for retest."
        ]
        model["functional_requirements"]["overview"] = (
            "Filter yield trends by product code."
        )
        status["scope"]["status"] = "confirmed"
        status["scenarios"]["status"] = "confirmed"
        status["features"]["status"] = "confirmed"
    elif decision_id == "data_boundary":
        model["data_and_dependencies"] = [
            "Read e-test results from SQL Server.",
            "The first release is read-only and performs no production writeback.",
        ]
        status["integrations"]["status"] = "confirmed"
    elif decision_id == "acceptance":
        model["acceptance_criteria"] = [
            "The shift supervisor can identify the top loss code by product code."
        ]
        status["acceptance"]["status"] = "confirmed"
    else:
        raise AssertionError(f"Unknown decision: {decision_id}")


def _fast_ready_model() -> dict:
    model = _empty_model()
    for decision_id in FAST_DECISION_ORDER:
        _confirm_fast_decision(model, decision_id)
    return model


def _strict_ready_model() -> dict:
    model = _fast_ready_model()
    model["data_and_dependencies"] = [
        "Read-only SQL Server view dbo.v_e_test_results; no source-system writeback.",
        "Join by lot_id and product_code; fields include yield_pct and loss_code.",
        "Refresh the view every five minutes.",
    ]
    model["business_rules"] = [
        "Yield uses the approved finished-lot calculation."
    ]
    model["collection_status"]["rules"]["status"] = "confirmed"
    model["product_context"]["business_owner"] = "Quality manager"
    model["product_context"]["acceptance_owner"] = "Quality manager"
    model["collection_status"]["ownership"]["status"] = "confirmed"
    return model


@pytest.mark.parametrize(
    ("confirmed_count", "expected_next"),
    tuple(enumerate(FAST_DECISION_ORDER)),
)
def test_fast_decisions_follow_one_authoritative_order(
    confirmed_count: int,
    expected_next: str,
) -> None:
    model = _empty_model()
    for decision_id in FAST_DECISION_ORDER[:confirmed_count]:
        _confirm_fast_decision(model, decision_id)

    state = build_interview_state_v2(
        model,
        document_status="missing",
        language="en",
    )

    assert state["stage"] == "brief_discovery"
    assert state["brief"]["confirmed_decisions"] == confirmed_count
    assert state["brief"]["total_decisions"] == 5
    assert state["next_decision"]["decision_id"] == expected_next
    assert state["next_decision"]["mode"] == "free_text"


def test_vague_outcome_stays_active_until_it_contains_measurable_evidence() -> None:
    model = _empty_model()
    model["background"]["objective"] = "Improve production visibility."
    model["collection_status"]["objective"]["status"] = "confirmed"

    vague_state = build_interview_state_v2(
        model,
        document_status="missing",
        language="en",
    )

    assert vague_state["brief"]["confirmed_decisions"] == 0
    assert vague_state["next_decision"]["decision_id"] == "outcome"

    model["background"]["objective"] = (
        "Reduce false-fail escapes by 15% within the next quarter."
    )
    measurable_state = build_interview_state_v2(
        model,
        document_status="missing",
        language="en",
    )

    assert measurable_state["brief"]["confirmed_decisions"] == 1
    assert measurable_state["next_decision"]["decision_id"] == "actor_action"


def test_product_description_with_a_metric_word_is_not_a_measurable_outcome() -> None:
    model = _empty_model()
    model["background"]["objective"] = "Build a quality defect disposition dashboard."
    model["collection_status"]["objective"]["status"] = "confirmed"

    state = build_interview_state_v2(
        model,
        document_status="missing",
        language="en",
        business_route="quality",
    )

    assert state["brief"]["confirmed_decisions"] == 0
    assert state["next_decision"]["decision_id"] == "outcome"


def test_vague_acceptance_stays_active_until_it_names_observable_evidence() -> None:
    model = _empty_model()
    for decision_id in FAST_DECISION_ORDER[:4]:
        _confirm_fast_decision(model, decision_id)
    model["acceptance_criteria"] = ["The solution should work well."]
    model["collection_status"]["acceptance"]["status"] = "confirmed"

    vague_state = build_interview_state_v2(
        model,
        document_status="missing",
        language="en",
    )

    assert vague_state["brief"]["confirmed_decisions"] == 4
    assert vague_state["next_decision"]["decision_id"] == "acceptance"

    model["acceptance_criteria"] = [
        "The supervisor can export a retest list within five minutes."
    ]
    observable_state = build_interview_state_v2(
        model,
        document_status="missing",
        language="en",
    )

    assert observable_state["brief"]["confirmed_decisions"] == 5
    assert observable_state["stage"] == "brief_ready"


def test_fast_decisions_unlock_build_brief_before_strict_review() -> None:
    state = build_interview_state_v2(
        _fast_ready_model(),
        document_status="missing",
        language="en",
    )

    assert set(state) == {
        "schema_version",
        "stage",
        "brief",
        "review",
        "next_decision",
        "actions",
    }
    assert state["schema_version"] == "2.0"
    assert state["stage"] == "brief_ready"
    assert state["brief"] == {
        "confirmed_decisions": 5,
        "total_decisions": 5,
        "assumption_count": 0,
        "ready": True,
        "document_status": "missing",
    }
    assert state["review"] == {
        "remaining_count": 3,
        "remaining_keys": ["rules", "integrations", "ownership"],
        "ready": False,
        "asked_count": 0,
        "max_questions": 2,
        "input_mode": "question",
    }
    assert state["next_decision"] is None
    assert state["actions"] == {
        "can_generate_brief": True,
        "can_handoff": False,
    }


def test_deferred_fast_evidence_moves_on_but_remains_an_assumption() -> None:
    model = _empty_model()
    for decision_id in FAST_DECISION_ORDER[1:]:
        _confirm_fast_decision(model, decision_id)

    state = build_interview_state_v2(
        model,
        document_status="missing",
        language="en",
        deferred_decision_ids=["outcome"],
    )

    assert state["stage"] == "brief_ready"
    assert state["brief"]["confirmed_decisions"] == 4
    assert state["brief"]["assumption_count"] == 1
    assert state["brief"]["ready"]
    assert state["next_decision"] is None
    assert state["actions"]["can_generate_brief"]
    assert not state["actions"]["can_handoff"]
    assert state["review"]["remaining_count"] >= 1


def test_current_brief_enters_strict_review_with_ownership_separate_from_users() -> None:
    model = _fast_ready_model()
    model["data_and_dependencies"] = [
        "Read-only SQL Server view dbo.v_e_test_results; no source-system writeback.",
        "Join by lot_id and product_code; fields include yield_pct and loss_code.",
        "Refresh the view every five minutes.",
    ]
    model["product_context"]["business_owner"] = "Quality manager"
    model["product_context"]["acceptance_owner"] = "Quality manager"

    state = build_interview_state_v2(
        model,
        document_status="current",
        language="en",
    )

    assert state["stage"] == "strict_review"
    assert state["review"] == {
        "remaining_count": 2,
        "remaining_keys": ["rules", "ownership"],
        "ready": False,
        "asked_count": 0,
        "max_questions": 2,
        "input_mode": "question",
    }
    assert state["next_decision"]["decision_id"] == "rules"
    assert not state["actions"]["can_generate_brief"]
    assert not state["actions"]["can_handoff"]

    model["business_rules"] = ["Use the approved finished-lot yield formula."]
    model["collection_status"]["rules"]["status"] = "confirmed"
    state_after_rules = build_interview_state_v2(
        model,
        document_status="current",
        language="en",
    )

    assert state_after_rules["review"]["remaining_count"] == 1
    assert state_after_rules["next_decision"]["decision_id"] == "ownership"


def test_fast_data_boundary_does_not_pass_strict_integration_review() -> None:
    model = _strict_ready_model()
    model["data_and_dependencies"] = [
        "Read e-test results from SQL Server.",
        "The first release is read-only and performs no production writeback.",
    ]

    state = build_interview_state_v2(
        model,
        document_status="current",
        language="en",
    )

    assert state["brief"]["ready"]
    assert state["stage"] == "strict_review"
    assert state["next_decision"]["decision_id"] == "integrations"
    assert state["review"]["remaining_count"] == 1
    assert not state["actions"]["can_handoff"]


def test_strict_review_uses_the_specific_pending_question_and_matching_options() -> None:
    model = _strict_ready_model()
    model["collection_status"]["scope"].update(
        {
            "status": "pending_confirmation",
            "reason": "The time range still needs confirmation.",
            "pending_questions": ["趋势展示的时间范围是否固定？"],
        }
    )

    state = build_interview_state_v2(
        model,
        document_status="current",
        language="zh",
        business_route="quality",
    )

    decision = state["next_decision"]
    assert decision["decision_id"] == "scope"
    assert decision["question"] == "趋势展示的时间范围是否固定？"
    assert len(decision["options"]) == 3
    assert all("首版展示缺陷趋势" not in item["text"] for item in decision["options"])
    assert any("30 天" in item["text"] for item in decision["options"])


def test_strict_review_reuses_measurable_and_observable_evidence_gates() -> None:
    model = _strict_ready_model()
    model["background"]["objective"] = "Improve visibility."
    model["acceptance_criteria"] = ["The solution should work well."]

    state = build_interview_state_v2(
        model,
        document_status="current",
        language="en",
        deferred_decision_ids=["outcome", "acceptance"],
    )

    assert state["brief"]["ready"]
    assert state["stage"] == "strict_review"
    assert state["review"]["remaining_keys"] == ["objective", "acceptance"]
    assert state["next_decision"]["decision_id"] == "objective"
    assert not state["actions"]["can_handoff"]


def test_strict_review_question_cap_switches_to_manual_blocker_mode() -> None:
    state = build_interview_state_v2(
        _fast_ready_model(),
        document_status="current",
        language="en",
        strict_review_turn_count=2,
    )

    assert state["stage"] == "strict_review"
    assert state["review"]["asked_count"] == 2
    assert state["review"]["input_mode"] == "manual"
    assert state["next_decision"] is None
    assert not state["actions"]["can_handoff"]


def test_strict_ready_requirements_with_stale_brief_require_refresh() -> None:
    state = build_interview_state_v2(
        _strict_ready_model(),
        document_status="stale",
        language="en",
    )

    assert state["stage"] == "refresh_brief"
    assert state["review"] == {
        "remaining_count": 0,
        "remaining_keys": [],
        "ready": True,
        "asked_count": 0,
        "max_questions": 2,
        "input_mode": "complete",
    }
    assert state["next_decision"] is None
    assert state["actions"] == {
        "can_generate_brief": True,
        "can_handoff": False,
    }


def test_handoff_requires_strict_review_and_a_current_brief() -> None:
    state = build_interview_state_v2(
        _strict_ready_model(),
        document_status="current",
        language="en",
    )

    assert state["stage"] == "handoff_ready"
    assert state["review"] == {
        "remaining_count": 0,
        "remaining_keys": [],
        "ready": True,
        "asked_count": 0,
        "max_questions": 2,
        "input_mode": "complete",
    }
    assert state["next_decision"] is None
    assert state["actions"] == {
        "can_generate_brief": False,
        "can_handoff": True,
    }


@pytest.mark.parametrize(
    ("language", "expected_label", "expected_question"),
    (
        (
            "en",
            "Measurable business outcome",
            "What measurable business result should the first release improve?",
        ),
        (
            "de",
            "Messbares Geschäftsergebnis",
            "Welches messbare Geschäftsergebnis soll die erste Version verbessern?",
        ),
        (
            "zh",
            "可衡量的业务结果",
            "首版要改善什么可衡量的业务结果？",
        ),
        (
            "ms",
            "Hasil perniagaan yang boleh diukur",
            "Apakah hasil perniagaan yang boleh diukur yang perlu ditambah baik oleh keluaran pertama?",
        ),
    ),
)
def test_active_question_uses_the_selected_ui_language(
    language: str,
    expected_label: str,
    expected_question: str,
) -> None:
    state = build_interview_state_v2(
        _empty_model(),
        document_status="missing",
        language=language,
    )

    assert state["next_decision"]["label"] == expected_label
    assert state["next_decision"]["question"] == expected_question
    assert state["next_decision"]["hint"]


@pytest.mark.parametrize(
    ("business_route", "expected_phrase"),
    (
        ("production", "production"),
        ("quality", "quality"),
        ("tdi", "request"),
    ),
)
def test_active_question_offers_three_route_specific_answers(
    business_route: str,
    expected_phrase: str,
) -> None:
    state = build_interview_state_v2(
        _empty_model(),
        document_status="missing",
        language="en",
        business_route=business_route,
    )

    options = state["next_decision"]["options"]
    assert len(options) == 3
    assert len({option["option_id"] for option in options}) == 3
    assert all(option["text"] for option in options)
    assert any(
        expected_phrase in option["text"].casefold()
        for option in options
    )


def test_answer_options_follow_the_active_decision_and_ui_language() -> None:
    model = _empty_model()
    _confirm_fast_decision(model, "outcome")

    state = build_interview_state_v2(
        model,
        document_status="missing",
        language="zh",
        business_route="quality",
    )

    assert state["next_decision"]["decision_id"] == "actor_action"
    assert len(state["next_decision"]["options"]) == 3
    assert any(
        "质量" in option["text"] or "工程师" in option["text"]
        for option in state["next_decision"]["options"]
    )


def test_matching_single_proposal_switches_only_the_active_decision_to_confirmation() -> None:
    model = _empty_model()
    proposal = {
        "decision_id": "outcome",
        "proposal_id": "proposal-123",
        "text": "Reduce false-fail e-test escapes by 15% next quarter.",
        "allowed_fields": ["background.objective"],
    }

    state = build_interview_state_v2(
        model,
        document_status="missing",
        language="en",
        active_proposal=proposal,
    )

    assert state["next_decision"]["decision_id"] == "outcome"
    assert state["next_decision"]["mode"] == "confirm_proposal"
    assert state["next_decision"]["proposal"] == {
        "proposal_id": "proposal-123",
        "text": "Reduce false-fail e-test escapes by 15% next quarter.",
    }

    stale_state = build_interview_state_v2(
        copy.deepcopy(model),
        document_status="missing",
        language="en",
        active_proposal={**proposal, "decision_id": "actor_action"},
    )
    assert stale_state["next_decision"]["mode"] == "free_text"
    assert stale_state["next_decision"]["proposal"] is None


def test_explicit_primary_user_action_advances_fast_flow_without_passing_strict_user_review() -> None:
    model = _empty_model()
    _confirm_fast_decision(model, "outcome")
    model["product_context"]["primary_user"] = "Shift supervisor"
    model["users_and_scenarios"]["target_users"] = ["Shift supervisor"]
    model["users_and_scenarios"]["core_scenarios"] = [
        "Shift supervisor schedules retests from yield trends by product code."
    ]
    model["collection_status"]["users"].update(
        {
            "status": "pending_confirmation",
            "reason": "The primary user is explicit; additional users can be reviewed later.",
            "pending_questions": ["Are there any other target users?"],
        }
    )
    model["collection_status"]["scenarios"].update(
        {
            "status": "confirmed",
            "reason": "The business action was explicitly stated.",
            "pending_questions": [],
        }
    )

    state = build_interview_state_v2(
        model,
        document_status="missing",
        language="en",
    )

    assert state["brief"]["confirmed_decisions"] == 2
    assert state["next_decision"]["decision_id"] == "v1_flow"
    assert state["review"]["remaining_count"] == 7
