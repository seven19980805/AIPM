from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class BusinessTemplateLibrary:
    LANGUAGE_ALIASES = {
        "zh": "zh",
        "zh-cn": "zh",
        "zh_cn": "zh",
        "en": "en",
        "de": "de",
        "ms": "ms",
    }

    def __init__(self, templates_dir: str | Path) -> None:
        self.templates_dir = Path(templates_dir)
        self._templates = self._load_templates()

    def list_templates(self) -> list[dict[str, Any]]:
        return [self._to_summary(template) for template in self._templates.values()]

    def get_template(self, template_id: str) -> dict[str, Any] | None:
        template = self._templates.get(str(template_id).strip())
        if template is None:
            return None
        return self._to_detail(template)

    def get_localized_template(self, template_id: str, language: str | None) -> dict[str, Any] | None:
        template = self._resolve_template_variant(template_id, language)
        if template is None:
            return None
        return self._to_detail(template)

    def get_template_prompt_context(
        self,
        template_id: str,
        language: str | None = None,
    ) -> dict[str, Any] | None:
        template = self._resolve_template_variant(template_id, language)
        if template is None:
            return None

        sections = template.get("sections")
        section_items = sections if isinstance(sections, list) else []
        return {
            "template_id": template.get("template_id", ""),
            "template_key": template.get("template_key", ""),
            "template_name": template.get("template_name", ""),
            "template_category": template.get("template_category", ""),
            "business_domain": template.get("business_domain", ""),
            "business_route": template.get("business_route", ""),
            "language": template.get("language", ""),
            "version": template.get("version", ""),
            "description": template.get("description", ""),
            "tags": self._string_list(template.get("tags")),
            "applicable_scenarios": self._string_list(template.get("applicable_scenarios")),
            "section_titles": [
                str(item.get("section_title", "")).strip()
                for item in section_items
                if isinstance(item, dict) and str(item.get("section_title", "")).strip()
            ],
            "example_model": self._example_model(template),
            "prompt_hints": self._dict_list(template.get("prompt_hints")),
            "prompt_questions": self._dict_list(template.get("prompt_questions")),
        }

    def get_template_markdown(self, template_id: str, language: str | None = None) -> str:
        template = self._resolve_template_variant(template_id, language)
        if template is None:
            return ""

        return self._read_template_markdown(template)

    def get_template_example_model(self, template_id: str, language: str | None = None) -> dict[str, Any]:
        template = self._resolve_template_variant(template_id, language)
        if template is None:
            return {}
        return self._example_model(template)

    def _read_template_markdown(self, template: dict[str, Any]) -> str:
        render_config = template.get("render_config")
        if not isinstance(render_config, dict):
            return ""

        relative_path = str(render_config.get("markdown_relative_path", "")).strip()
        if not relative_path:
            return ""

        project_root = self.templates_dir.parent.parent
        template_path = (project_root / relative_path).resolve()
        if not template_path.exists():
            return ""
        try:
            return template_path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def _resolve_template_variant(
        self,
        template_id: str,
        language: str | None = None,
    ) -> dict[str, Any] | None:
        template = self._templates.get(str(template_id).strip())
        if template is None:
            return None

        normalized_language = self._normalize_language(language)
        if not normalized_language:
            return template

        template_key = str(template.get("template_key", "")).strip()
        if not template_key:
            return template

        localized_template = self._find_template_by_key_and_language(
            template_key,
            normalized_language,
        )
        return localized_template or template

    def _find_template_by_key_and_language(
        self,
        template_key: str,
        language: str,
    ) -> dict[str, Any] | None:
        normalized_language = self._normalize_language(language)
        for template in self._templates.values():
            if str(template.get("template_key", "")).strip() != template_key:
                continue
            if self._normalize_language(template.get("language")) == normalized_language:
                return template
        return None

    def _load_templates(self) -> dict[str, dict[str, Any]]:
        templates: list[dict[str, Any]] = []
        if not self.templates_dir.exists():
            return {}

        for candidate in sorted(self.templates_dir.glob("*.json")):
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue

            if not isinstance(payload, dict):
                continue

            template_id = str(payload.get("template_id", "")).strip()
            if not template_id:
                continue

            status = str(payload.get("status", "enabled")).strip().lower()
            if status == "disabled":
                continue

            templates.append(payload)

        templates.sort(
            key=lambda item: (
                str(item.get("template_category", "")).strip(),
                str(item.get("template_name", "")).strip(),
            )
        )
        return {
            str(template.get("template_id", "")).strip(): template
            for template in templates
        }

    def _to_summary(self, template: dict[str, Any]) -> dict[str, Any]:
        sections = template.get("sections")
        section_items = sections if isinstance(sections, list) else []
        return {
            "template_id": str(template.get("template_id", "")).strip(),
            "template_key": str(template.get("template_key", "")).strip(),
            "template_name": str(template.get("template_name", "")).strip(),
            "template_category": str(template.get("template_category", "")).strip(),
            "business_domain": str(template.get("business_domain", "")).strip(),
            "business_route": str(template.get("business_route", "")).strip(),
            "language": str(template.get("language", "")).strip(),
            "version": str(template.get("version", "")).strip(),
            "description": str(template.get("description", "")).strip(),
            "tags": self._string_list(template.get("tags")),
            "applicable_scenarios": self._string_list(template.get("applicable_scenarios")),
            "has_example_model": bool(self._example_model(template)),
            "section_count": len(section_items),
            "section_titles": [
                str(item.get("section_title", "")).strip()
                for item in section_items
                if isinstance(item, dict) and str(item.get("section_title", "")).strip()
            ],
        }

    def _to_detail(self, template: dict[str, Any]) -> dict[str, Any]:
        summary = self._to_summary(template)
        sections = template.get("sections")
        section_items = sections if isinstance(sections, list) else []
        summary["sections"] = sorted(
            [
            {
                "section_key": str(item.get("section_key", "")).strip(),
                "section_title": str(item.get("section_title", "")).strip(),
                "sort_order": int(item.get("sort_order", 0) or 0),
                "field_count": len(item.get("fields")) if isinstance(item.get("fields"), list) else 0,
            }
            for item in section_items
            if isinstance(item, dict)
            ],
            key=lambda item: (item["sort_order"], item["section_title"]),
        )
        summary["storage_model"] = str(template.get("storage_model", "")).strip()
        summary["render_config"] = template.get("render_config") if isinstance(template.get("render_config"), dict) else {}
        summary["template_markdown"] = self._read_template_markdown(template)
        summary["example_model"] = self._example_model(template)
        summary["prompt_hints"] = self._dict_list(template.get("prompt_hints"))
        summary["prompt_questions"] = self._dict_list(template.get("prompt_questions"))
        return summary

    def _example_model(self, template: dict[str, Any]) -> dict[str, Any]:
        example_model = template.get("example_model")
        return example_model if isinstance(example_model, dict) else {}

    def _string_list(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return []

    def _dict_list(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict)]

    def _normalize_language(self, value: Any) -> str:
        normalized = str(value or "").strip().lower()
        if not normalized:
            return ""
        return self.LANGUAGE_ALIASES.get(normalized, normalized)
