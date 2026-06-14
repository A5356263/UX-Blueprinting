from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.uxb_run.executor import preflight_check, run_existing_command


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


class UXBRunExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="uxb-run-executor-"))
        self.projects_dir = self.temp_dir / "projects"
        self.repo_root = Path("e:/AI设计/体验蓝图构建思路")
        self.env_patch = patch.dict(
            "os.environ",
            {
                "UXB_ROOT": str(self.repo_root),
                "UXB_PROJECTS_DIR": str(self.projects_dir),
            },
        )
        self.env_patch.start()

    def tearDown(self) -> None:
        self.env_patch.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_preflight_check_reports_placeholder_residue(self) -> None:
        project_id = "preflight-placeholder"
        workspace_dir = self.projects_dir / project_id / "workspace"
        _write_text(workspace_dir / "facts.md", "# Facts\n\n- [待补充]")

        errors, targets = preflight_check(project_id, "gate-facts")
        self.assertIn("存在占位符残留：facts.md", errors)
        self.assertEqual(targets[0].name, "facts.md")

    def test_run_existing_command_auto_writes_provenance_before_gate(self) -> None:
        project_id = "executor-provenance"
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        workspace_dir = project_dir / "workspace"
        runtime_dir = project_dir / "runtime"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        _write_text(source_dir / "task_card.md", "# Task Card\n\n- 任务卡")
        _write_text(workspace_dir / "facts.md", "# Facts\n\n## 1. 核心需求事实\n\n- A")

        called: list[str] = []

        with patch("packages.uxb_run.executor.run_facts_gate", side_effect=lambda pid: called.append(pid) or 0):
            result = run_existing_command("gate-facts", project_id)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(called, [project_id])
        provenance = json.loads((runtime_dir / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(provenance["producer"], "uxb_run")
        self.assertIn("generate-facts", provenance.get("command_chain", []))
        self.assertIn("gate-facts", provenance.get("command_chain", []))

    def test_run_existing_command_infers_business_standard_generate_chain(self) -> None:
        project_id = "executor-business-lite-provenance"
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        workspace_dir = project_dir / "workspace"
        runtime_dir = project_dir / "runtime"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        _write_text(source_dir / "task_card.md", "# Task Card\n\n- 任务卡")
        _write_json(
            runtime_dir / "uxb_route_decision.json",
            {
                "execution_mode": "standard",
                "required_outputs": ["facts.md", "business_blueprint_lite.md", "experience_blueprint.md"],
                "status": "confirmed",
            },
        )
        _write_text(workspace_dir / "business_blueprint_lite.md", "# Business Lite\n\n## 1. 核心流程\n\n- A")

        with patch("packages.uxb_run.executor.run_business_lite_gate", side_effect=lambda pid: 0):
            result = run_existing_command("gate-business-lite", project_id)

        self.assertEqual(result.exit_code, 0)
        provenance = json.loads((runtime_dir / "provenance.json").read_text(encoding="utf-8"))
        self.assertIn("generate-business-lite", provenance.get("command_chain", []))
        self.assertIn("gate-business-lite", provenance.get("command_chain", []))

    def test_run_existing_command_reports_provenance_incomplete(self) -> None:
        project_id = "executor-provenance-incomplete"
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        workspace_dir = project_dir / "workspace"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        _write_text(workspace_dir / "facts.md", "# Facts\n\n## 1. 核心需求事实\n\n- A")

        with patch("packages.uxb_run.executor.run_facts_gate", side_effect=lambda pid: 0):
            result = run_existing_command("gate-facts", project_id)

        self.assertEqual(result.exit_code, 2)
        self.assertTrue(any("provenance.task_card_hash" in item for item in (result.preflight_errors or [])))


if __name__ == "__main__":
    unittest.main()
