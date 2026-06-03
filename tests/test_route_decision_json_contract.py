from __future__ import annotations

import json
import shutil
import unittest
import uuid
from pathlib import Path

from packages.common import get_project_dir, get_repo_root
from packages.route_decision import load_uxb_execution_decision


class RouteDecisionJsonContractTests(unittest.TestCase):
    def test_template_uses_files_and_reasoning_fields(self) -> None:
        template_path = get_repo_root() / ".codex" / "skills" / "uxb" / "assets" / "uxb_route_decision.template.json"
        payload = json.loads(template_path.read_text(encoding="utf-8"))

        knowledge_selection = payload.get("knowledge_selection")
        self.assertIsInstance(knowledge_selection, dict)
        self.assertIn("files", knowledge_selection)
        self.assertIn("reasoning", knowledge_selection)
        self.assertNotIn("raw_escalation_plan", knowledge_selection)
        self.assertNotIn("selection_reasons", knowledge_selection)

    def test_invalid_json_reports_parse_error_instead_of_missing_file(self) -> None:
        project_id = f"_route_decision_bad_json_{uuid.uuid4().hex[:8]}"
        project_dir = get_project_dir(project_id)
        runtime_dir = project_dir / "runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        self.addCleanup(shutil.rmtree, project_dir, ignore_errors=True)

        bad_json = """{
  "schema_version": "uxb_route_decision@5.0",
  "knowledge_selection": {
    "files": ["knowledge/wiki/summaries/业务/权限管理/README.md"],
    "reasoning": "这里直接写了 "未转义" 双引号"
  }
}
"""
        (runtime_dir / "uxb_route_decision.json").write_text(bad_json, encoding="utf-8")

        decision = load_uxb_execution_decision(project_id)

        self.assertEqual(decision.get("status"), "needs_rejudgment")
        errors = [str(item) for item in decision.get("validation_errors", [])]
        self.assertTrue(any("invalid JSON" in item for item in errors), errors)
        self.assertFalse(any(item == "Missing runtime/uxb_route_decision.json" for item in errors), errors)


if __name__ == "__main__":
    unittest.main()
