from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.project_structure_check import run_project_structure_check
from packages.task_bootstrap import run_task_bootstrap


class ProjectStructureCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="uxb-structure-test-"))
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

    def test_bootstrap_no_longer_creates_exports_and_runs_structure_check(self) -> None:
        project_id = "bootstrap-clean"
        exit_code = run_task_bootstrap(project_id, domain="权限管理", task_name="结构收敛", force=False)
        self.assertEqual(exit_code, 0)

        project_dir = self.projects_dir / project_id
        self.assertTrue((project_dir / "source").exists())
        self.assertTrue((project_dir / "workspace").exists())
        self.assertTrue((project_dir / "runtime").exists())
        self.assertTrue((project_dir / "meta.json").exists())
        self.assertFalse((project_dir / "exports").exists())

        check_json = project_dir / "runtime" / "project_structure_check.json"
        check_md = project_dir / "runtime" / "project_structure_check.md"
        self.assertTrue(check_json.exists())
        self.assertTrue(check_md.exists())
        self.assertFalse((project_dir / "workspace" / "facts.md").exists())
        self.assertFalse((project_dir / "workspace" / "business_blueprint.md").exists())
        self.assertFalse((project_dir / "workspace" / "experience_blueprint.md").exists())
        self.assertFalse((project_dir / "workspace" / "gap_list.md").exists())
        self.assertFalse((project_dir / "workspace" / "check_report.md").exists())
        self.assertFalse((project_dir / "workspace" / "check_status.json").exists())
        payload = json.loads(check_json.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("status"), "passed")
        self.assertEqual(payload.get("missing_entries"), [])

    def test_structure_check_fails_when_runtime_missing(self) -> None:
        project_id = "missing-runtime"
        project_dir = self.projects_dir / project_id
        (project_dir / "source").mkdir(parents=True, exist_ok=True)
        (project_dir / "workspace").mkdir(parents=True, exist_ok=True)
        (project_dir / "meta.json").write_text("{}", encoding="utf-8")

        exit_code = run_project_structure_check(project_id)
        self.assertEqual(exit_code, 1)

        payload = json.loads((project_dir / "runtime" / "project_structure_check.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("status"), "failed")
        self.assertIn("runtime/", payload.get("missing_entries", []))

    def test_structure_check_blocks_workspace_template_pollution(self) -> None:
        project_id = "workspace-template"
        project_dir = self.projects_dir / project_id
        (project_dir / "source").mkdir(parents=True, exist_ok=True)
        (project_dir / "workspace").mkdir(parents=True, exist_ok=True)
        (project_dir / "runtime").mkdir(parents=True, exist_ok=True)
        (project_dir / "meta.json").write_text("{}", encoding="utf-8")
        (project_dir / "workspace" / "facts.template.md").write_text("template", encoding="utf-8")

        exit_code = run_project_structure_check(project_id)
        self.assertEqual(exit_code, 1)

        payload = json.loads((project_dir / "runtime" / "project_structure_check.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("status"), "failed")
        issue_paths = {item["path"] for item in payload.get("issues", [])}
        self.assertIn(f"projects/{project_id}/workspace/facts.template.md", issue_paths)

    def test_structure_check_blocks_runtime_formal_artifact_pollution(self) -> None:
        project_id = "runtime-pollution"
        project_dir = self.projects_dir / project_id
        (project_dir / "source").mkdir(parents=True, exist_ok=True)
        (project_dir / "workspace").mkdir(parents=True, exist_ok=True)
        (project_dir / "runtime").mkdir(parents=True, exist_ok=True)
        (project_dir / "meta.json").write_text("{}", encoding="utf-8")
        (project_dir / "runtime" / "experience_blueprint.md").write_text("content", encoding="utf-8")

        exit_code = run_project_structure_check(project_id)
        self.assertEqual(exit_code, 1)

        payload = json.loads((project_dir / "runtime" / "project_structure_check.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("status"), "failed")
        issue_paths = {item["path"] for item in payload.get("issues", [])}
        self.assertIn(f"projects/{project_id}/runtime/experience_blueprint.md", issue_paths)

    def test_structure_check_blocks_source_runtime_status_pollution(self) -> None:
        project_id = "source-status"
        project_dir = self.projects_dir / project_id
        (project_dir / "source").mkdir(parents=True, exist_ok=True)
        (project_dir / "workspace").mkdir(parents=True, exist_ok=True)
        (project_dir / "runtime").mkdir(parents=True, exist_ok=True)
        (project_dir / "meta.json").write_text("{}", encoding="utf-8")
        (project_dir / "source" / "check_status.json").write_text("{}", encoding="utf-8")

        exit_code = run_project_structure_check(project_id)
        self.assertEqual(exit_code, 1)

        payload = json.loads((project_dir / "runtime" / "project_structure_check.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("status"), "failed")
        issue_paths = {item["path"] for item in payload.get("issues", [])}
        self.assertIn(f"projects/{project_id}/source/check_status.json", issue_paths)

    def test_structure_check_blocks_task_id_mismatch(self) -> None:
        project_id = "task-a"
        project_dir = self.projects_dir / project_id
        (project_dir / "source").mkdir(parents=True, exist_ok=True)
        (project_dir / "workspace").mkdir(parents=True, exist_ok=True)
        (project_dir / "runtime").mkdir(parents=True, exist_ok=True)
        (project_dir / "meta.json").write_text("{}", encoding="utf-8")
        (project_dir / "source" / "task_card.md").write_text(
            "\n".join(
                [
                    "## Protocol",
                    "",
                    "- Protocol Name: UXB",
                    "- Protocol Version: 1.0",
                    "- Task ID: task-b",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        exit_code = run_project_structure_check(project_id)
        self.assertEqual(exit_code, 1)

        payload = json.loads((project_dir / "runtime" / "project_structure_check.json").read_text(encoding="utf-8"))
        self.assertEqual(payload.get("status"), "failed")
        issue_paths = {item["path"] for item in payload.get("issues", [])}
        self.assertIn(f"projects/{project_id}/source/task_card.md", issue_paths)


if __name__ == "__main__":
    unittest.main()
