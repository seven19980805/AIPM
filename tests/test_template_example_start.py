import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.business_template_library import BusinessTemplateLibrary
from app.services.requirement_collector import (
    STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
    RequirementCollectorService,
)
from app.services.session_store import SQLiteSessionStore
from app.services.structured_requirement_model import REQUIREMENT_ITEM_KEYS, normalize_structured_requirement_model


class FakeLLMClient:
    def __init__(self) -> None:
        self.calls: list[list[dict[str, str]]] = []
        self.stream_calls: list[list[dict[str, str]]] = []
        self.chat_response = "# Generated PRD\n\nGenerated from seeded example requirements."
        self.stream_response_parts: list[dict[str, str]] | None = None

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        self.calls.append(messages)
        return self.chat_response

    def stream_chat(self, messages: list[dict[str, str]], temperature: float = 0.3):
        self.stream_calls.append(messages)
        if self.stream_response_parts is not None:
            yield from self.stream_response_parts
            return
        yield {"type": "content", "text": "# Generated Streamed Document\n\n"}
        yield {"type": "content", "text": "Generated from seeded example requirements."}


class TemplateExampleStartTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        db_path = Path(self.tmpdir.name) / "rqmd.sqlite3"
        self.llm_client = FakeLLMClient()
        self.service = RequirementCollectorService(
            self.llm_client,
            SQLiteSessionStore(str(db_path)),
        )
        self.template_id = "business_process_requirement_template_en"

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _cache_ready_requirement_model(self, session_id: str) -> None:
        session = self.service._require_session(session_id)
        collection_status = {
            key: {
                "status": "confirmed",
                "reason": "Confirmed for document generation.",
                "pending_questions": [],
            }
            for key in REQUIREMENT_ITEM_KEYS
        }
        model = normalize_structured_requirement_model(
            {
                "document_info": {"project_name": "Lot yield dashboard"},
                "background": {
                    "objective": "Track lot yield losses for Quality review.",
                    "summary": "Quality needs a lot yield dashboard.",
                },
                "product_context": {
                    "requesting_department": "Quality",
                    "primary_user": "Quality manager",
                    "decision_or_action": "Review yield loss by lot and defect type.",
                    "software_type": "Dashboard",
                    "business_owner": "Quality manager",
                    "acceptance_owner": "Quality manager",
                },
                "scope": {
                    "in_scope": ["Lot yield loss dashboard"],
                    "out_of_scope": ["Production writeback"],
                },
                "users_and_scenarios": {
                    "target_users": ["Quality manager"],
                    "core_scenarios": ["Review yield loss by lot"],
                },
                "functional_requirements": {
                    "overview": "Dashboard, filters, export, and drilldown.",
                    "feature_details": [
                        {
                            "feature_name": "Yield loss dashboard",
                            "description": "Show loss by lot and defect type.",
                            "inputs": ["QIS/MES export"],
                            "outputs": ["Dashboard and export"],
                        }
                    ],
                },
                "page_and_interaction": {
                    "pages": [
                        {
                            "page_name": "Yield dashboard",
                            "entry_point": "Dashboard home",
                            "primary_actions": ["Filter", "Export"],
                        }
                    ],
                },
                "business_rules": ["No production writeback before approval."],
                "data_and_dependencies": ["QIS/MES export"],
                "acceptance_criteria": ["Quality manager can verify loss by lot."],
                "collection_status": collection_status,
            }
        )
        self.service._save_structured_requirement_model_cache(
            session_id,
            STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            self.service._message_count(session.messages),
            model,
        )

    def test_guided_template_session_stays_empty(self) -> None:
        session = self.service.create_session(
            template_id=self.template_id,
            language="en",
        )

        self.assertEqual(session.applied_template_id, self.template_id)
        self.assertEqual(session.messages, [])

    def test_guided_template_prompt_uses_conversation_chain(self) -> None:
        session = self.service.create_session(
            template_id=self.template_id,
            language="en",
        )

        prompt = self.service._pm_prompt(session, "en")

        self.assertIn("Template conversation chain", prompt)
        self.assertIn("progressive interview chain", prompt)
        self.assertNotIn("IC Substrate initial chain", prompt)

    def test_pm_prompt_uses_skill_style_discovery_method(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        prompt = self.service._pm_prompt(session, "zh")

        self.assertIn("AI PM skill-style 工作法", prompt)
        self.assertIn("沿需求决策树逐支拆解", prompt)
        self.assertIn("每个问题必须带一个可快速确认的推荐答案或选项示例", prompt)
        self.assertIn("建立共享领域语言", prompt)
        self.assertIn("PRD 质量门", prompt)
        self.assertIn("如果这些关键块已经足够生成文档，不要继续开新坑", prompt)
        self.assertIn("最后一段必须使用 A/B/C 选项格式", prompt)

    def test_open_clarification_question_gets_choice_fallback(self) -> None:
        text = "我理解你想做排产预测系统。首版主要服务哪个部门？"

        formatted = self.service._ensure_choice_question_format(text, "zh")

        self.assertIn("A. 同意按上面的建议口径作为首版假设继续推进", formatted)
        self.assertIn("B. 不同意，我补充实际业务口径或例外情况", formatted)
        self.assertIn("C. 这个点先记为待确认", formatted)

    def test_existing_choice_question_is_not_duplicated(self) -> None:
        text = "请选择首版入口：\nA. Production\nB. Quality\nC. TDI"

        formatted = self.service._ensure_choice_question_format(text, "zh")

        self.assertEqual(formatted, text)

    def test_streamed_open_question_gets_ui_language_choice_fallback_before_save(self) -> None:
        self.llm_client.stream_response_parts = [
            {"type": "content", "text": "Which department owns this first-version requirement?"}
        ]
        session = self.service.create_session(language="zh")

        events: list[dict[str, object]] = []
        for event in self.service.stream_user_message(
            session.id,
            "我想做一个 IC Substrate dashboard",
            language="en",
        ):
            events.append(event)
            if event.get("event") == "assistant_done":
                break

        streamed_text = "".join(
            str(event.get("delta", ""))
            for event in events
            if event.get("event") == "content"
        )
        refreshed = self.service.get_session(session.id)
        self.assertIsNotNone(refreshed)

        self.assertIn("Which department owns this first-version requirement?", streamed_text)
        self.assertIn("A. Use the suggested interpretation above as the version-one assumption", streamed_text)
        self.assertIn("Reply with A, B, C", streamed_text)
        self.assertNotIn("同意按上面的建议口径", streamed_text)
        self.assertEqual(refreshed.messages[-1]["content"], streamed_text)

    def test_streamed_reply_does_not_wait_for_structured_summary_generation(self) -> None:
        self.llm_client.stream_response_parts = [
            {"type": "content", "text": "请确认是否生成需求文档？\n\nA. 确认，生成需求文档\nB. 继续补充"}
        ]
        session = self.service.create_session(language="zh")

        events = list(
            self.service.stream_user_message(
                session.id,
                "我想做一个 IC Substrate Quality dashboard",
                language="zh",
            )
        )
        event_names = [str(event.get("event")) for event in events]

        self.assertIn("assistant_done", event_names)
        self.assertEqual(event_names[-1], "done")
        self.assertNotIn("summary", event_names)
        self.assertEqual(len(self.llm_client.stream_calls), 1)
        self.assertEqual(len(self.llm_client.calls), 0)

    def test_non_question_summary_does_not_get_choice_fallback(self) -> None:
        text = "已确认：首版聚焦 Production 的排产预测，目标用户是 planner。"

        formatted = self.service._ensure_choice_question_format(text, "zh")

        self.assertEqual(formatted, text)

    def test_structured_requirement_prompt_extracts_shared_domain_language(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        prompt = self.service._structured_requirement_model_prompt(session, "zh")

        self.assertIn("Skill-style 抽取补充规则", prompt)
        self.assertIn("共享领域语言", prompt)
        self.assertIn("业务术语、KPI 名称、状态名、对象粒度、owner、数据源、验收口径", prompt)
        self.assertIn("不新增 schema", prompt)
        self.assertIn("不要升级为 confirmed", prompt)

    def test_prd_prompt_uses_skill_style_document_rules(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        prompt = self.service._prd_doc_prompt(session, "zh")

        self.assertIn("Skill-style PRD 写作规则", prompt)
        self.assertIn("PRD 不是聊天纪要", prompt)
        self.assertIn("Glossary / Definitions", prompt)
        self.assertIn("User Stories 必须覆盖真实业务场景", prompt)
        self.assertIn("Implementation Decisions", prompt)
        self.assertIn("Out of Scope", prompt)

    def test_user_message_response_language_follows_ui_language_selection(self) -> None:
        session = self.service.create_session(language="en")

        self.service.send_user_message(session.id, "我想做一个排产预测系统", language="en")

        first_system_prompt = self.llm_client.calls[0][0]["content"]
        self.assertIn("Respond entirely in English", first_system_prompt)
        self.assertNotIn("输出语言要求", first_system_prompt)

    def test_attachment_display_message_stays_separate_from_model_context(self) -> None:
        session = self.service.create_session(language="zh")
        display_message = "请结合附件继续梳理需求。\n\n[附件：cost-model.pptx]"
        full_message = f"{display_message}\n\n[附件：cost-model.pptx]\n完整PPT解析内容和图表说明"

        self.service.send_user_message(
            session.id,
            full_message,
            language="zh",
            display_message=display_message,
        )

        refreshed = self.service.get_session(session.id)
        self.assertIsNotNone(refreshed)
        self.assertEqual(refreshed.messages[0]["content"], full_message)
        self.assertEqual(refreshed.messages[0]["display_content"], display_message)
        self.assertEqual(self.llm_client.calls[0][-1]["content"], full_message)

    def test_collection_status_does_not_regress_after_confirmation(self) -> None:
        previous_status = {
            key: {"status": "missing", "reason": "", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        previous_status["rules"] = {
            "status": "confirmed",
            "reason": "User confirmed the cost formula.",
            "pending_questions": [],
        }
        previous_status["integrations"] = {
            "status": "captured",
            "reason": "SAP was mentioned.",
            "pending_questions": ["Confirm source of truth."],
        }
        current_status = {
            key: {"status": "missing", "reason": "", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        current_status["rules"] = {
            "status": "pending_confirmation",
            "reason": "LLM wants to re-confirm the formula.",
            "pending_questions": ["Is the formula correct?"],
        }
        current_status["integrations"] = {
            "status": "missing",
            "reason": "",
            "pending_questions": [],
        }

        merged = self.service._merge_structured_requirement_collection_status(
            {"collection_status": current_status},
            {"collection_status": previous_status},
        )

        self.assertEqual(merged["collection_status"]["rules"]["status"], "confirmed")
        self.assertEqual(merged["collection_status"]["integrations"]["status"], "captured")

    def test_generation_readiness_allows_assumptions_with_open_questions(self) -> None:
        # Reachable gate: no conflict + coverage >= 75% + confirmation >= 40%.
        # Open/pending questions become assumptions and do NOT block generation,
        # though they keep fully_confirmed False.
        collection_status = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        ready_model = normalize_structured_requirement_model(
            {"collection_status": collection_status, "open_questions": []}
        )

        ready_progress = self.service._structured_requirement_progress(ready_model)

        self.assertTrue(ready_progress["fully_confirmed"])
        self.assertTrue(ready_progress["ready_to_generate"])

        collection_status["acceptance"] = {
            "status": "confirmed",
            "reason": "Acceptance candidate exists.",
            "pending_questions": ["Confirm acceptance owner."],
        }
        with_assumptions_model = normalize_structured_requirement_model(
            {
                "collection_status": collection_status,
                "open_questions": ["Confirm API auth and rate limits."],
            }
        )

        with_assumptions_progress = self.service._structured_requirement_progress(with_assumptions_model)

        # Not "fully confirmed" (questions remain) ...
        self.assertFalse(with_assumptions_progress["fully_confirmed"])
        self.assertEqual(with_assumptions_progress["pending_question_count"], 1)
        self.assertEqual(with_assumptions_progress["open_question_count"], 1)
        # ... but generation is still unlocked (unknowns become assumptions).
        self.assertTrue(with_assumptions_progress["ready_to_generate"])

    def test_generation_readiness_blocks_on_conflict_or_low_coverage(self) -> None:
        # Conflict blocks readiness even at full coverage.
        conflict_status = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        conflict_status["scope"] = {"status": "conflict", "reason": "Conflicting scope.", "pending_questions": []}
        conflict_progress = self.service._structured_requirement_progress(
            normalize_structured_requirement_model({"collection_status": conflict_status})
        )
        self.assertFalse(conflict_progress["ready_to_generate"])

        # One missing field is tolerated (8/9 = 89% coverage) -> still ready.
        one_missing = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        one_missing["pages"] = {"status": "missing", "reason": "", "pending_questions": []}
        one_missing_progress = self.service._structured_requirement_progress(
            normalize_structured_requirement_model({"collection_status": one_missing})
        )
        self.assertTrue(one_missing_progress["ready_to_generate"])

        # Too many missing fields (low coverage) blocks readiness.
        low_coverage = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        for key in ("pages", "rules", "integrations", "acceptance"):
            low_coverage[key] = {"status": "missing", "reason": "", "pending_questions": []}
        low_coverage_progress = self.service._structured_requirement_progress(
            normalize_structured_requirement_model({"collection_status": low_coverage})
        )
        self.assertFalse(low_coverage_progress["ready_to_generate"])

    def test_convergence_guidance_stops_open_ended_questions_when_collection_complete(self) -> None:
        collection_status = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        collection_status["rules"] = {
            "status": "pending_confirmation",
            "reason": "Candidate rule needs final confirmation.",
            "pending_questions": ["Confirm the formula."],
        }

        guidance = self.service._requirement_convergence_guidance_for_prompt(
            {"collection_status": collection_status},
            "zh",
        )

        self.assertIn("不要继续挖新细节", guidance)
        self.assertIn("确认", guidance)

    def test_ic_substrate_template_prompt_uses_active_department_routing(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        prompt = self.service._pm_prompt(session, "zh")

        self.assertIn("模板对话链路", prompt)
        self.assertIn("IC Substrate 专业对话链路", prompt)
        self.assertIn("AI 产品经理，不是制造/质量/工程顾问", prompt)
        self.assertIn("软件、Web dashboard、流程工具、报表或数据产品", prompt)
        self.assertIn("当前 IT scope 只开放 Production、Quality、TDI 和 General 四个同级入口", prompt)
        self.assertIn("其他部门链路先隐藏，统一归入 General", prompt)
        self.assertIn("首问选项只能列这四个入口", prompt)
        self.assertIn("Production、Quality、TDI，还是 General", prompt)
        self.assertNotIn("Customer/Program、EHS、Engineering/Process", prompt)
        self.assertNotIn("Warehouse/Logistics", prompt)
        self.assertNotIn("核心制造链路的专业样板，不是唯一入口", prompt)
        self.assertIn("部门/业务 owner 路由", prompt)
        self.assertIn("来自哪个部门", prompt)
        self.assertIn("反问必须先落到软件需求", prompt)
        self.assertIn("首版软件形态", prompt)
        self.assertIn("Finished Lot", prompt)
        self.assertIn("MRB", prompt)
        self.assertIn("CAPA", prompt)
        self.assertIn("不要擅自展开缩写", prompt)
        self.assertIn("不要擅自引入未确认的站点缩写", prompt)
        self.assertIn("每轮只能有一个问句", prompt)
        self.assertIn("2-5 个业务选项", prompt)
        self.assertIn("TDI 只能写作 TDI", prompt)
        self.assertIn("部门首问的选项说明里也不能展开 TDI", prompt)
        self.assertIn("不要自造 TDI case 状态名、SLA 数字、owner 角色或审批层级", prompt)
        self.assertIn("Created/In Progress/Closed、24 小时、QA 签核", prompt)
        self.assertIn("不要替 Production 编 route/站点/yield 公式", prompt)
        self.assertIn("不要替 Quality 编 inspection point/defect taxonomy/spec limit/MRB/CAPA 流程", prompt)
        self.assertIn("FVI、AOI、E-test、AVI、SAP、EAP、SPC", prompt)
        self.assertIn("不要擅自引入未确认的站点缩写、工艺站点名、设备名、供应商名、系统品牌", prompt)
        self.assertIn("需求形态明确但用户没有说清发起部门或业务 owner", prompt)
        self.assertIn("先问部门/owner", prompt)
        self.assertIn("当前开放入口平级", prompt)
        self.assertNotIn("核心主线", prompt)
        self.assertNotIn("Planning/PMC", prompt)
        self.assertNotIn("Equipment/Maintenance", prompt)
        self.assertNotIn("Finance/Cost", prompt)
        self.assertIn("当前节点专业追问方向", prompt)

    def test_ic_substrate_template_prompt_has_german_expert_chain(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_de",
            language="de",
        )

        prompt = self.service._pm_prompt(session, "de")
        snapshot = self.service.get_structured_requirement_snapshot(session.id, "de")
        chain_state = snapshot["conversation_chain_state"]

        self.assertIn("Vorlagen-Dialogkette", prompt)
        self.assertIn("IC Substrate Experten-Dialogkette", prompt)
        self.assertIn("AI Product Manager", prompt)
        self.assertIn("Production, Quality, TDI und General", prompt)
        self.assertIn("Harte Regel: TDI", prompt)
        self.assertIn("Runtime-Hard-Constraints", prompt)
        self.assertNotIn("Template conversation chain", prompt)
        self.assertEqual(chain_state["current_node_label"], "Anfordernden Bereich, Business Owner und First-Version Szenario klaeren")
        production_scope = next(node for node in chain_state["nodes"] if node["node"] == "production_scope")
        self.assertIn("Produkt, Werk, Linie", production_scope["label"])

    def test_ic_substrate_template_prompt_has_malay_expert_chain(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_ms",
            language="ms",
        )

        prompt = self.service._pm_prompt(session, "ms")
        snapshot = self.service.get_structured_requirement_snapshot(session.id, "ms")
        chain_state = snapshot["conversation_chain_state"]

        self.assertIn("Rantaian dialog templat", prompt)
        self.assertIn("Rantaian dialog pakar IC Substrate", prompt)
        self.assertIn("Production, Quality, TDI dan General", prompt)
        self.assertIn("Peraturan keras: tulis TDI hanya sebagai TDI", prompt)
        self.assertIn("Peraturan keras runtime", prompt)
        self.assertNotIn("Template conversation chain", prompt)
        self.assertEqual(chain_state["current_node_label"], "Sahkan jabatan pemohon, business owner dan senario versi pertama")
        production_scope = next(node for node in chain_state["nodes"] if node["node"] == "production_scope")
        self.assertIn("Sahkan product, plant, line", production_scope["label"])

    def test_ic_substrate_runtime_guardrails_follow_template_context(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        prompt = self.service._pm_prompt(session, "zh")

        self.assertGreater(prompt.index("运行时硬约束"), prompt.index("Template context"))
        self.assertIn("本轮 prompt 的最终规则", prompt)
        self.assertIn("每轮只能问一个问题", prompt)
        self.assertIn("模板来源术语只能作为证据，不要自动变成选项", prompt)
        self.assertIn("TDI 只能写作 TDI", prompt)
        self.assertIn("不要自造公式、状态、站点、系统名、缺陷分类、SLA 数字或 owner 角色", prompt)
        self.assertIn("第一问先确认来自哪个入口或首版业务 owner", prompt)

    def test_no_template_ic_substrate_session_preserves_expert_chain_from_cached_model(self) -> None:
        session = self.service.create_session(language="zh")
        self.service._append_message(session.id, "user", "我想做一个电测站点的良率损失dashboard")
        self.service._append_message(
            session.id,
            "user",
            "B. 趋势分析与汇报：生产主管或质量经理需要按班次/日/周查看良率损失结构。",
        )
        self.service._append_message(
            session.id,
            "user",
            "B. 质量经理为主：按产品、测试程序、缺陷类型分析损失结构占比，生产主管可作为辅助使用者。",
        )

        cached_model = self.service._empty_structured_requirement_model()
        cached_model["product_context"]["requesting_department"] = "Quality"
        cached_model["product_context"]["software_type"] = "Dashboard"
        cached_model["background"]["summary"] = "电测站点良率损失 Dashboard，用于 Quality 趋势分析与汇报。"
        self.service._save_structured_requirement_model_cache(
            session.id,
            STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            3,
            cached_model,
        )
        self.service._append_message(
            session.id,
            "user",
            "A. 来自电测设备（ATE/测试机）直接上报的测试项目代码。",
        )
        session = self.service._require_session(session.id)

        prompt = self.service._pm_prompt(session, "zh")
        chain_state = self.service.build_conversation_chain_state(session, cached_model, "zh")

        self.assertIn("IC Substrate 专业对话链路", prompt)
        self.assertIn("当前对话链路状态", prompt)
        self.assertIn("链路类型：ic_substrate", prompt)
        self.assertIn("运行时硬约束", prompt)
        self.assertTrue(chain_state["enabled"])
        self.assertEqual(chain_state["mode"], "ic_substrate")
        self.assertEqual(chain_state["intent_track"], "quality")

    def test_ic_substrate_guided_session_exposes_chain_state(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        snapshot = self.service.get_structured_requirement_snapshot(session.id, "zh")
        chain_state = snapshot["conversation_chain_state"]

        self.assertTrue(chain_state["enabled"])
        self.assertEqual(chain_state["mode"], "ic_substrate")
        self.assertEqual(chain_state["current_track"], "Routing")
        self.assertEqual(chain_state["current_node"], "scope_triage")
        self.assertEqual(chain_state["current_node_label"], "确认需求发起部门、业务 owner 和首版场景")
        self.assertEqual(chain_state["current_step_index"], 0)
        self.assertEqual(chain_state["status"], "not_started")
        self.assertEqual(chain_state["next_question_source"], "ic_substrate_department_first_chain")
        self.assertEqual(chain_state["total_steps"], 16)
        self.assertEqual(
            set(chain_state["tracks"]),
            {
                "Production",
                "TDI",
                "Quality",
                "General",
            },
        )
        self.assertEqual(chain_state["nodes"][0]["node"], "scope_triage")
        self.assertEqual(chain_state["nodes"][0]["status"], "current")
        self.assertIn("production_scope", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("production_metrics", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("production_workflow", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("production_data_acceptance", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("tdi_scope", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("tdi_metrics", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("tdi_workflow", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("tdi_data_acceptance", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("quality_scope", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("quality_metrics", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("quality_workflow", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("quality_data_acceptance", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("general_scope", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("general_metrics", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("general_workflow", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("general_data_acceptance", [node["node"] for node in chain_state["nodes"]])
        self.assertNotIn("planning_scope", [node["node"] for node in chain_state["nodes"]])
        self.assertNotIn("finance_metrics", [node["node"] for node in chain_state["nodes"]])
        self.assertNotIn("it_data_data_acceptance", [node["node"] for node in chain_state["nodes"]])

    def test_ic_substrate_active_departments_have_expert_chains(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        snapshot = self.service.get_structured_requirement_snapshot(session.id, "zh")
        nodes = snapshot["conversation_chain_state"]["nodes"]

        for department in (
            "production",
            "tdi",
            "quality",
            "general",
        ):
            with self.subTest(department=department):
                department_nodes = [node["node"] for node in nodes if node["node"].startswith(f"{department}_")]
                self.assertIn(f"{department}_scope", department_nodes)
                self.assertIn(f"{department}_metrics", department_nodes)
                self.assertIn(f"{department}_workflow", department_nodes)
                self.assertIn(f"{department}_data_acceptance", department_nodes)
        hidden_departments = (
            "planning",
            "engineering",
            "equipment",
            "material",
            "warehouse",
            "customer",
            "finance",
            "ehs",
            "it_data",
            "management",
        )
        node_names = [node["node"] for node in nodes]
        for department in hidden_departments:
            with self.subTest(hidden_department=department):
                self.assertFalse(any(node_name.startswith(f"{department}_") for node_name in node_names))

    def test_non_template_session_disables_chain_state(self) -> None:
        session = self.service.create_session(language="en")

        snapshot = self.service.get_structured_requirement_snapshot(session.id, "en")

        self.assertEqual(snapshot["conversation_chain_state"], {"enabled": False})

    def test_prd_generation_strips_embedded_thinking(self) -> None:
        self.llm_client.chat_response = "<think>private reasoning</think>\n# Clean PRD\n\nReady."
        session = self.service.create_session(
            template_id=self.template_id,
            language="en",
        )
        # Seed minimal user message so build_prd_document calls the LLM stub
        self.service.send_user_message(session.id, "We want to track lot yield.", language="en")
        self._cache_ready_requirement_model(session.id)

        result = self.service.build_prd_document(session.id, "en", save_history=False)

        # The LLM-authored core content must appear and the raw <think> tag must never leak through.
        self.assertIn("# Clean PRD", result["document_markdown"])
        self.assertIn("Ready.", result["document_markdown"])
        self.assertNotIn("<think>", result["document_markdown"])
        self.assertNotIn("</think>", result["document_markdown"])

    def test_prd_generation_falls_back_to_template_when_model_returns_empty(self) -> None:
        # When the LLM only produces a <think> block, the parsed body is empty
        # and build_prd_document falls back to the loaded template scaffold.
        self.llm_client.chat_response = "<think>private reasoning only</think>"
        session = self.service.create_session(
            template_id=self.template_id,
            language="en",
        )
        self.service.send_user_message(session.id, "We want to track lot yield.", language="en")
        self._cache_ready_requirement_model(session.id)

        result = self.service.build_prd_document(session.id, "en", save_history=False)

        self.assertTrue(result["document_markdown"].lstrip().startswith("#"))
        self.assertNotIn("<think>", result["document_markdown"])
        self.assertNotIn("</think>", result["document_markdown"])

    def test_prd_generation_blocks_before_readiness(self) -> None:
        session = self.service.create_session(
            template_id=self.template_id,
            language="en",
        )
        self.service.send_user_message(session.id, "We want to track lot yield.", language="en")
        calls_before = len(self.llm_client.calls)

        result = self.service.build_prd_document(session.id, "en", save_history=False)

        self.assertEqual(result["status"], "quality_gate_blocked")
        self.assertIn("Formal Document Quality Gate Not Passed", result["document_markdown"])
        self.assertEqual(len(self.llm_client.calls), calls_before)

    def test_document_generation_messages_include_quality_gate(self) -> None:
        session = self.service.create_session(language="en")
        self.service._append_message(session.id, "user", "We need a cost simulation dashboard.")
        session = self.service.get_session(session.id)
        self.assertIsNotNone(session)
        collection_status = {
            key: {"status": "missing", "reason": "", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        collection_status["objective"] = {
            "status": "confirmed",
            "reason": "Business goal is clear.",
            "pending_questions": [],
        }
        collection_status["rules"] = {
            "status": "pending_confirmation",
            "reason": "Formula candidate needs final confirmation.",
            "pending_questions": ["Confirm the cost formula."],
        }
        model = {
            "background": {"objective": "Simulate cost by activity rate.", "summary": ""},
            "collection_status": collection_status,
        }
        progress = self.service._structured_requirement_progress(
            normalize_structured_requirement_model(model),
        )
        chat_messages = self.service._chat_history_messages(session.messages)

        prd_payload = self.service._build_prd_doc_messages(
            session,
            chat_messages,
            model,
            progress,
            "en",
        )[1]["content"]
        design_payload = self.service._build_design_doc_messages(
            session,
            chat_messages,
            model,
            progress,
            "# System Design Document\n\nTBD",
            "en",
        )[1]["content"]

        self.assertIn("Document quality gate", prd_payload)
        self.assertIn("pending_confirmation_items", prd_payload)
        self.assertIn("Do not present captured or pending_confirmation items as confirmed facts", prd_payload)
        self.assertIn("Document quality gate", design_payload)
        self.assertIn("Confirm the cost formula.", design_payload)
