#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.pm_methodology import build_pm_methodology_state
from app.services.requirement_collector import (
    STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
    RequirementCollectorService,
)
from app.services.session_store import SQLiteSessionStore
from app.services.structured_requirement_model import REQUIREMENT_ITEM_KEYS, normalize_structured_requirement_model


EXPECTED_CHECKS = [
    "opportunity_solution_tree",
    "success_metric",
    "assumption_risk",
    "prioritization",
    "validation_plan",
    "story_acceptance",
    "roadmap_release",
]


class FakeLLMClient:
    def chat(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        return "{}"


def main() -> int:
    sparse = normalize_structured_requirement_model(
        {
            "background": {
                "objective": "Reduce manual yield review work for production planners.",
            },
            "collection_status": {
                "objective": {
                    "status": "captured",
                    "reason": "Goal mentioned but not tied to measurable outcome.",
                    "pending_questions": ["What outcome should improve?"],
                }
            },
        }
    )
    sparse_state = build_pm_methodology_state(sparse, language="en")
    assert [check["key"] for check in sparse_state["checks"]] == EXPECTED_CHECKS
    assert sparse_state["score"] < 50
    assert sparse_state["ready_for_pm_review"] is False
    assert "success_metric" in sparse_state["missing_evidence"]
    assert "validation_plan" in sparse_state["missing_evidence"]
    assert sparse_state["recommended_next_method"] == "opportunity_solution_tree"

    confirmed = {
        key: {
            "status": "confirmed",
            "reason": "Confirmed by business owner.",
            "pending_questions": [],
        }
        for key in REQUIREMENT_ITEM_KEYS
    }
    rich = normalize_structured_requirement_model(
        {
            "product_context": {
                "business_owner": "Yield operations lead",
                "primary_user": "Production planner",
                "decision_or_action": "Prioritize lots that need manual yield review.",
                "acceptance_owner": "Yield operations lead",
            },
            "background": {
                "objective": "Cut weekly manual yield review time by 30%.",
            },
            "scope": {
                "in_scope": ["P0 yield trend dashboard", "P1 lot drill-down"],
                "out_of_scope": ["Automated disposition workflow"],
            },
            "users_and_scenarios": {
                "target_users": ["Production planner"],
                "core_scenarios": ["Planner reviews low-yield lots before the weekly meeting."],
            },
            "functional_requirements": {
                "feature_details": [
                    {
                        "feature_name": "P0 yield trend",
                        "description": "Show yield by product family and week.",
                        "trigger": "Planner opens dashboard.",
                        "processing_logic": "Aggregate confirmed lot results by week.",
                        "inputs": ["Finished lot data"],
                        "outputs": ["Yield trend"],
                        "exception_cases": ["Missing lot result is flagged."],
                    }
                ],
            },
            "business_rules": ["P0 uses confirmed lots only.", "P1 excludes engineering lots."],
            "data_and_dependencies": ["Yield data refreshes daily and is reconciled with QDM."],
            "risks_and_notes": [
                "Assumption: QDM lot data is complete by 08:00.",
                "Release phase 1 covers dashboard review only.",
            ],
            "acceptance_criteria": [
                "UAT passes when planners can identify low-yield lots within 5 minutes.",
                "Metric: manual review time reduced by 30%.",
            ],
            "collection_status": confirmed,
        }
    )
    rich_state = build_pm_methodology_state(rich, language="en")
    assert rich_state["score"] >= 85
    assert rich_state["ready_for_pm_review"] is True
    assert rich_state["missing_evidence"] == []
    assert rich_state["recommended_next_method"] == ""

    with tempfile.TemporaryDirectory() as tmpdir:
        service = RequirementCollectorService(
            FakeLLMClient(),
            SQLiteSessionStore(str(Path(tmpdir) / "rqmd.sqlite3")),
        )
        session = service.create_session(language="en")
        service._save_structured_requirement_model_cache(
            session.id,
            STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            0,
            sparse,
        )

        pm_prompt = service._pm_prompt(session, "en")
        assert "PM methodology state" in pm_prompt
        assert "Opportunity Solution Tree" in pm_prompt
        assert "What business outcome should this improve" in pm_prompt

        progress = service._structured_requirement_progress(sparse)
        quality_gate_block = service._document_quality_gate_block_markdown(
            sparse,
            progress,
            "en",
            "prd",
            session,
        )
        assert "PM Methodology Gaps" in quality_gate_block
        assert "Success metric" in quality_gate_block
        assert "What metric and target will prove this requirement worked?" in quality_gate_block

    app_vue = (PROJECT_ROOT / "frontend" / "src" / "App.vue").read_text(encoding="utf-8")
    assert "buildDocumentGenerationMethodologyMessage" in app_vue
    assert "pmMethodologyState.value.checks" in app_vue
    assert "documentGenerationMethodologyMessage" in app_vue
    assert ":generation-disabled=\"messagePipelineActive || switchingSession || documentGenerationConfirmOpen || !hasSession\"" in app_vue

    print("PM methodology contracts verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
