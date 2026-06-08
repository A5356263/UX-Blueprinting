from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.routed_main.core import run_routed_main
from packages.task_bootstrap import run_task_bootstrap


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class RoutedMainEntryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="uxb-routed-main-entry-"))
        self.projects_dir = self.temp_dir / "projects"
        self.env_patch = patch.dict(
            "os.environ",
            {
                "UXB_PROJECTS_DIR": str(self.projects_dir),
            },
        )
        self.env_patch.start()

    def tearDown(self) -> None:
        self.env_patch.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_routed_main_blocks_bootstrap_placeholders_before_generation(self) -> None:
        project_id = "placeholder-entry-check"
        exit_code = run_task_bootstrap(project_id, domain="权限管理", task_name="入口约束", force=False)
        self.assertEqual(exit_code, 0)

        runtime_dir = self.projects_dir / project_id / "runtime"
        _write_json(
            runtime_dir / "uxb_route_decision.json",
            {
                "schema_version": "uxb_route_decision@5.0",
                "created_by": "uxb_ai",
                "confirmed_by_user": True,
                "can_execute_mainline": True,
                "business_depth": "business_blueprint_lite",
                "experience_output": "experience_blueprint",
                "experience_pressure": [],
                "execution": {
                    "required_outputs": [
                        "facts.md",
                        "business_blueprint_lite.md",
                        "experience_blueprint.md",
                    ]
                },
                "knowledge_selection": {
                    "files": ["knowledge/wiki/index.md"],
                    "reasoning": "test",
                },
            },
        )

        run_code = run_routed_main(project_id, route="auto", skip_preview=True, strict=False)
        self.assertEqual(run_code, 1)

        report = json.loads((runtime_dir / "routed_main_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report.get("status"), "failed")
        self.assertEqual(report.get("stopped_at"), "formal-inputs")
        self.assertEqual(report.get("mainline_entry"), "user_confirmed_formal_blueprint_task")
        blocking_issue = str(report.get("blocking_issue") or "")
        self.assertIn("source/requirement.md still contains bootstrap placeholder content", blocking_issue)
        self.assertIn("source/background.md still contains bootstrap placeholder content", blocking_issue)


if __name__ == "__main__":
    unittest.main()
