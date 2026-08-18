import unittest
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.requirement_collector import RequirementCollectorService


class ImplementationPromptLanguageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = object.__new__(RequirementCollectorService)

    def build_prompt(self, language: str) -> str:
        return self.service._build_implementation_prompt(
            session_id="session-1",
            session_title="Test Session",
            prd_path="prd.md",
            design_path="design.md",
            language=language,
        )

    def test_builds_german_implementation_prompt(self) -> None:
        prompt = self.build_prompt("de")

        self.assertIn("Du bist", prompt)
        self.assertIn("PRD-Dokument: prd.md", prompt)
        self.assertNotIn("You are a senior", prompt)

    def test_builds_malay_implementation_prompt(self) -> None:
        prompt = self.build_prompt("ms")

        self.assertIn("Anda ialah", prompt)
        self.assertIn("Dokumen PRD: prd.md", prompt)
        self.assertNotIn("You are a senior", prompt)


if __name__ == "__main__":
    unittest.main()
