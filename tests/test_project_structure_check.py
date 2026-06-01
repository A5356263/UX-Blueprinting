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


if __name__ == "__main__":
    unittest.main()
