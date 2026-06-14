from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.uxb_run.planner import plan_current_action
from packages.uxb_run.state_reader import read_project_run_state


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def _valid_route_decision(project_id: str, *, outputs: list[str] | None = None) -> dict[str, object]:
    return {
        "schema_version": "uxb_route_decision@5.0",
        "project_id": project_id,
        "created_by": "uxb_ai",
        "confirmed_by_user": True,
        "can_execute_mainline": True,
        "business_depth": "business_blueprint_lite",
        "experience_output": "experience_blueprint",
        "experience_pressure": [],
        "knowledge_selection": {
            "files": [
                "knowledge/wiki/summaries/业务/README.md",
                ".codex/skills/uxb/references/complexity/00_core_complexity_judgment.md",
            ],
            "reasoning": "测试用判断单。",
        },
        "execution": {
            "required_outputs": outputs or ["facts.md", "business_blueprint_lite.md", "experience_blueprint.md"],
            "notes": [],
        },
    }


class UXBRunPlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="uxb-run-planner-"))
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

    def _project_paths(self, project_id: str) -> tuple[Path, Path, Path]:
        project_dir = self.projects_dir / project_id
        return project_dir, project_dir / "source", project_dir / "runtime"

    def _seed_ready_sources(self, source_dir: Path) -> None:
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 这是正式需求。")
        _write_text(source_dir / "background.md", "# Background\n\n- 这是正式背景。")
        _write_text(source_dir / "task_card.md", "# Task Card\n\n- 这是正式任务卡。")

    def test_missing_project_returns_write_formal_inputs(self) -> None:
        state = read_project_run_state("missing-project")
        action = plan_current_action(state)
        self.assertEqual(action.action_type, "write_formal_inputs")
        self.assertEqual(action.owner, "agent")

    def test_missing_formal_inputs_returns_write_formal_inputs(self) -> None:
        project_id = "missing-inputs"
        project_dir, source_dir, _runtime_dir = self._project_paths(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 请在这里粘贴原始需求正文。")
        state = read_project_run_state(project_id)
        action = plan_current_action(state)
        self.assertEqual(action.action_type, "write_formal_inputs")
        self.assertIn("source/background.md 缺失", action.blocking_reasons)

    def test_invalid_route_decision_returns_fix_route_decision(self) -> None:
        project_id = "invalid-route"
        project_dir, source_dir, runtime_dir = self._project_paths(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        self._seed_ready_sources(source_dir)
        _write_json(runtime_dir / "uxb_route_decision.json", {"schema_version": "bad"})
        state = read_project_run_state(project_id)
        action = plan_current_action(state)
        self.assertEqual(action.action_type, "fix_route_decision")
        self.assertEqual(action.stage, "formal")

    def test_missing_context_returns_assemble_context(self) -> None:
        project_id = "missing-context"
        project_dir, source_dir, runtime_dir = self._project_paths(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        self._seed_ready_sources(source_dir)
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        state = read_project_run_state(project_id)
        action = plan_current_action(state)
        self.assertEqual(action.action_type, "assemble_context")

    def test_missing_facts_returns_generate_artifact(self) -> None:
        project_id = "missing-facts"
        project_dir, source_dir, runtime_dir = self._project_paths(project_id)
        workspace_dir = project_dir / "workspace"
        project_dir.mkdir(parents=True, exist_ok=True)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        self._seed_ready_sources(source_dir)
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        state = read_project_run_state(project_id)
        action = plan_current_action(state)
        self.assertEqual(action.action_type, "phase_work")
        self.assertEqual(action.stage, "facts")

    def test_failed_facts_gate_returns_same_phase_work(self) -> None:
        project_id = "failed-facts-gate"
        project_dir, source_dir, runtime_dir = self._project_paths(project_id)
        workspace_dir = project_dir / "workspace"
        project_dir.mkdir(parents=True, exist_ok=True)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        self._seed_ready_sources(source_dir)
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        _write_text(workspace_dir / "facts.md", "# facts")
        _write_json(runtime_dir / "gates" / "facts_gate_status.json", {"status": "failed"})
        state = read_project_run_state(project_id)
        action = plan_current_action(state)
        self.assertEqual(action.action_type, "phase_work")
        self.assertEqual(action.stage, "facts")

    def test_planner_phase_progression_comes_from_phase_state_not_gate_status(self) -> None:
        project_id = "phase-state-drives-planner"
        project_dir, source_dir, runtime_dir = self._project_paths(project_id)
        workspace_dir = project_dir / "workspace"
        project_dir.mkdir(parents=True, exist_ok=True)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        self._seed_ready_sources(source_dir)
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        _write_json(runtime_dir / "phase_state.json", {"phase": "business", "status": "in_progress"})
        _write_json(runtime_dir / "gates" / "facts_gate_status.json", {"status": "failed"})

        state = read_project_run_state(project_id)
        action = plan_current_action(state)
        self.assertEqual(action.action_type, "phase_work")
        self.assertEqual(action.stage, "business")

    def test_legacy_current_action_files_do_not_hold_planner_in_repair_loop(self) -> None:
        project_id = "legacy-repair-state-ignored"
        project_dir, source_dir, runtime_dir = self._project_paths(project_id)
        workspace_dir = project_dir / "workspace"
        project_dir.mkdir(parents=True, exist_ok=True)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        self._seed_ready_sources(source_dir)
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        _write_text(workspace_dir / "facts.md", "# facts")
        _write_json(
            runtime_dir / "current_action.json",
            {
                "schema_version": "uxb_current_action@1.0",
                "project_id": project_id,
                "action_id": "repair-legacy",
                "phase": "repair",
                "action_type": "repair_artifact",
                "stage": "facts",
                "status": "requires_agent",
                "target_artifacts": [f"projects/{project_id}/workspace/facts.md"],
            },
        )
        _write_json(
            runtime_dir / "agent_task_status.json",
            {
                "schema_version": "uxb_agent_task_status@1.0",
                "project_id": project_id,
                "action_id": "repair-legacy",
                "status": "ready",
            },
        )

        state = read_project_run_state(project_id)
        action = plan_current_action(state)
        self.assertEqual(action.action_type, "phase_work")
        self.assertEqual(action.stage, "facts")

    def test_all_outputs_and_checks_pass_returns_preview_then_completed(self) -> None:
        project_id = "ready-preview"
        project_dir, source_dir, runtime_dir = self._project_paths(project_id)
        workspace_dir = project_dir / "workspace"
        preview_dir = runtime_dir / "preview"
        project_dir.mkdir(parents=True, exist_ok=True)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        self._seed_ready_sources(source_dir)
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        _write_text(workspace_dir / "facts.md", "# facts")
        _write_text(workspace_dir / "business_blueprint_lite.md", "# business lite")
        _write_text(workspace_dir / "experience_blueprint.md", "# experience")
        _write_json(runtime_dir / "phase_state.json", {"phase": "final", "status": "passed"})

        state = read_project_run_state(project_id)
        action = plan_current_action(state)
        self.assertEqual(action.action_type, "preview")

        preview_dir.mkdir(parents=True, exist_ok=True)
        _write_text(preview_dir / "index.html", "<html></html>")
        state = read_project_run_state(project_id)
        action = plan_current_action(state)
        self.assertEqual(action.action_type, "completed")

    def test_planner_result_does_not_depend_on_background_text(self) -> None:
        project_id = "stable-structure-only"
        project_dir, source_dir, runtime_dir = self._project_paths(project_id)
        workspace_dir = project_dir / "workspace"
        project_dir.mkdir(parents=True, exist_ok=True)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- A")
        _write_text(source_dir / "background.md", "# Background\n\n- 版本一")
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        state_a = read_project_run_state(project_id)
        action_a = plan_current_action(state_a)

        _write_text(source_dir / "background.md", "# Background\n\n- 版本二，正文更长，但结构化状态不变。")
        context_path = runtime_dir / "context_manifest.json"
        context_payload = json.loads(context_path.read_text(encoding="utf-8"))
        _write_json(context_path, context_payload)
        state_b = read_project_run_state(project_id)
        action_b = plan_current_action(state_b)

        self.assertEqual(action_a.action_type, action_b.action_type)
        self.assertEqual(action_a.stage, action_b.stage)


if __name__ == "__main__":
    unittest.main()
