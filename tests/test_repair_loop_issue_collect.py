from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.repair_loop.issue_collect import collect_issue_sources


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class RepairLoopIssueCollectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="uxb-repair-loop-test-"))
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

    def test_collect_issue_sources_tolerates_missing_check_report(self) -> None:
        project_id = "repair-no-check-report"
        project_dir = self.projects_dir / project_id
        runtime_dir = project_dir / "runtime"
        workspace_dir = project_dir / "workspace"
        gates_dir = runtime_dir / "gates"

        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        _write_json(runtime_dir / "uxb_route_decision.json", {"status": "confirmed"})
        _write_json(runtime_dir / "trace_index.json", {"items": []})
        _write_json(runtime_dir / "gate_metrics.json", {"stages": []})

        status_payload = {"status": "passed", "issues": {"blockers": [], "warnings": []}}
        _write_json(gates_dir / "facts_gate_status.json", status_payload)
        _write_json(gates_dir / "business_gate_status.json", status_payload)
        _write_json(gates_dir / "experience_gate_status.json", status_payload)
        _write_json(workspace_dir / "check_status.json", status_payload)

        collected = collect_issue_sources(project_id)

        self.assertEqual(collected.get("raw_issues", []), [])
        final_artifact = next(item for item in collected.get("source_artifacts", []) if item.get("source") == "validate")
        self.assertTrue(final_artifact.get("status_exists"))
        self.assertFalse(final_artifact.get("report_exists"))
