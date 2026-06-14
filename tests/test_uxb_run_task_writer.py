from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.uxb_run import PhaseState, StageContext, UXBRunHistoryItem, append_run_history, write_phase_state, write_stage_context


class UXBRunTaskWriterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="uxb-run-task-writer-"))
        self.projects_dir = self.temp_dir / "projects"
        self.repo_root = self.temp_dir
        self.env_patch = patch.dict(
            "os.environ",
            {
                "UXB_ROOT": str(self.repo_root),
                "UXB_PROJECTS_DIR": str(self.projects_dir),
            },
        )
        self.env_patch.start()
        self.project_id = "uxb-run-phase2"
        self.runtime_dir = self.projects_dir / self.project_id / "runtime"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.env_patch.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_write_phase_state_and_stage_context_and_history(self) -> None:
        phase_state = PhaseState(
            project_id=self.project_id,
            phase="facts",
            execution_mode="standard",
            status="in_progress",
            target_artifact=f"projects/{self.project_id}/workspace/facts.md",
            target_artifacts=[f"projects/{self.project_id}/workspace/facts.md"],
            required_inputs=[
                f"projects/{self.project_id}/source/requirement.md",
                f"projects/{self.project_id}/source/background.md",
            ],
            template_refs=["templates/facts.template.md"],
            rule_refs=["specs/08_fact_extraction_contract.md"],
            created_at="2026-06-13T12:00:00+08:00",
            updated_at="2026-06-13T12:00:00+08:00",
        )
        stage_context = StageContext(
            project_id=self.project_id,
            context={"selection_source": "runtime/uxb_route_decision.json"},
            knowledge_trace={"files": ["knowledge/wiki/summaries/业务/README.md"], "reasoning": "测试"},
            execution_trace={},
            accumulated_warnings=[],
            updated_at="2026-06-13T12:00:00+08:00",
        )
        history_item = UXBRunHistoryItem(
            timestamp="2026-06-13T12:00:00+08:00",
            project_id=self.project_id,
            command=f"python -m packages run {self.project_id}",
            phase_before="facts",
            phase_after="business",
            action_type="phase_work",
            owner="agent",
            result="requires_agent",
            next_phase="business",
        )

        phase_state_path = write_phase_state(self.project_id, phase_state)
        stage_context_path = write_stage_context(self.project_id, stage_context)
        history_path = append_run_history(self.project_id, history_item)

        phase_payload = json.loads(phase_state_path.read_text(encoding="utf-8"))
        context_payload = json.loads(stage_context_path.read_text(encoding="utf-8"))
        history_lines = history_path.read_text(encoding="utf-8").strip().splitlines()

        self.assertEqual(phase_payload["schema_version"], "uxb_phase_state@2.0")
        self.assertEqual(phase_payload["phase"], "facts")
        self.assertEqual(phase_payload["template_refs"], ["templates/facts.template.md"])
        self.assertEqual(context_payload["schema_version"], "uxb_stage_context@2.0")
        self.assertEqual(context_payload["context"]["selection_source"], "runtime/uxb_route_decision.json")
        self.assertEqual(context_payload["knowledge_trace"]["reasoning"], "测试")
        self.assertEqual(len(history_lines), 1)
        history_payload = json.loads(history_lines[0])
        self.assertEqual(history_payload["phase_before"], "facts")
        self.assertEqual(history_payload["phase_after"], "business")
        self.assertEqual(history_payload["next_phase"], "business")

    def test_write_phase_state_removes_legacy_runtime_files(self) -> None:
        for filename in ("current_action.json", "agent_next_task.md", "agent_task_status.json", "uxb_run_report.json", "knowledge_trace.json"):
            (self.runtime_dir / filename).write_text("legacy", encoding="utf-8")

        write_phase_state(
            self.project_id,
            PhaseState(
                project_id=self.project_id,
                phase="formal",
                status="in_progress",
                target_artifact=f"projects/{self.project_id}/source/requirement.md",
                target_artifacts=[f"projects/{self.project_id}/source/requirement.md"],
            ),
        )

        self.assertTrue((self.runtime_dir / "phase_state.json").exists())
        self.assertFalse((self.runtime_dir / "current_action.json").exists())
        self.assertFalse((self.runtime_dir / "agent_next_task.md").exists())
        self.assertFalse((self.runtime_dir / "agent_task_status.json").exists())
        self.assertFalse((self.runtime_dir / "uxb_run_report.json").exists())
        self.assertFalse((self.runtime_dir / "knowledge_trace.json").exists())


if __name__ == "__main__":
    unittest.main()
