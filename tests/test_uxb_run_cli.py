from __future__ import annotations

import json
import shutil
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from packages.task_bootstrap import run_task_bootstrap
from packages.uxb_run.cli import _append_warning_entries, _write_terminal_report, run_uxb_run
from packages.uxb_run.models import CurrentAction, ProjectRunState


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def _valid_route_decision(project_id: str) -> dict[str, object]:
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
            "required_outputs": ["facts.md", "business_blueprint_lite.md", "experience_blueprint.md"],
            "notes": [],
        },
    }


def _task_card(project_id: str) -> str:
    return f"""
# Task Card

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.3
- Task ID: {project_id}
- Task Name: UXB run 收尾测试
- Domain: 权限管理

## Required Inputs

- projects/{project_id}/source/requirement.md
- projects/{project_id}/source/background.md

## Required Outputs

- projects/{project_id}/workspace/facts.md
- projects/{project_id}/workspace/business_blueprint_lite.md
- projects/{project_id}/workspace/experience_blueprint.md
- projects/{project_id}/workspace/check_status.json

## Constraints

- 不得臆造业务事实。
- 信息不足处保留 `[GAP]`。
- 正式产出必须写入 `workspace/`。

## Templates

- templates/facts.template.md
- templates/business_blueprint_lite.template.md
- templates/experience_blueprint.template.md

## Checks

- specs/08_fact_extraction_contract.md
- specs/17_business_blueprint_lite_contract.md
- specs/10_experience_blueprint_contract.md
""".strip()


class UXBRunCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path("e:/AI设计/体验蓝图构建思路")
        self.projects_dir = self.repo_root / "projects"
        self.env_patch = patch.dict("os.environ", {"UXB_ROOT": str(self.repo_root)})
        self.env_patch.start()
        self.project_ids: list[str] = []

    def tearDown(self) -> None:
        self.env_patch.stop()
        for project_id in self.project_ids:
            shutil.rmtree(self.projects_dir / project_id, ignore_errors=True)

    def test_run_bootstraps_missing_project_and_writes_formal_phase_state(self) -> None:
        project_id = f"_ci_uxb_run_cli_bootstrap_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        exit_code = run_uxb_run(project_id, domain="权限管理", task_name="中控器测试")
        self.assertEqual(exit_code, 0)

        runtime_dir = self.projects_dir / project_id / "runtime"
        phase_state = json.loads((runtime_dir / "phase_state.json").read_text(encoding="utf-8"))
        stage_context = json.loads((runtime_dir / "stage_context.json").read_text(encoding="utf-8"))

        self.assertEqual(phase_state["phase"], "formal")
        self.assertIn(f"projects/{project_id}/source/task_card.md", phase_state["target_artifacts"])
        self.assertIn(f"projects/{project_id}/source/requirement.md", phase_state["target_artifacts"])
        self.assertIn(f"projects/{project_id}/source/background.md", phase_state["target_artifacts"])
        self.assertIn(f"projects/{project_id}/runtime/uxb_route_decision.json", phase_state["target_artifacts"])
        self.assertIn("source/task_card.md", phase_state["required_inputs"])
        self.assertIn("selection_source", stage_context["context"])
        self.assertIn("knowledge_trace", stage_context)
        self.assertFalse((runtime_dir / "agent_next_task.md").exists())
        self.assertFalse((runtime_dir / "uxb_run_report.json").exists())

    def test_run_missing_task_card_blocks_with_full_formal_handoff_checklist(self) -> None:
        project_id = f"_ci_uxb_run_cli_missing_task_card_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        run_task_bootstrap(project_id, domain="权限管理", task_name="缺任务卡", force=False)
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        runtime_dir = project_dir / "runtime"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        task_card_path = source_dir / "task_card.md"
        if task_card_path.exists():
            task_card_path.unlink()

        exit_code = run_uxb_run(project_id)
        self.assertEqual(exit_code, 0)

        phase_state = json.loads((runtime_dir / "phase_state.json").read_text(encoding="utf-8"))
        self.assertEqual(phase_state["phase"], "formal")
        self.assertEqual(phase_state["status"], "in_progress")
        self.assertIn("source/task_card.md 缺失", phase_state["preflight_errors"])
        self.assertIn("缺少以下正式交接文件：", phase_state["preflight_errors"])
        self.assertIn("  ✗ source/task_card.md", phase_state["preflight_errors"])
        self.assertIn("  ✓ source/requirement.md", phase_state["preflight_errors"])
        self.assertIn("  ✓ source/background.md", phase_state["preflight_errors"])
        self.assertIn("  ✗ runtime/uxb_route_decision.json", phase_state["preflight_errors"])
        self.assertIn("请补齐后重新运行。", phase_state["preflight_errors"])

    def test_run_generates_fix_route_decision_phase_state_when_route_invalid(self) -> None:
        project_id = f"_ci_uxb_run_cli_fix_route_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        run_task_bootstrap(project_id, domain="权限管理", task_name="修判断单", force=False)
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        runtime_dir = project_dir / "runtime"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        _write_text(source_dir / "task_card.md", _task_card(project_id))
        _write_json(runtime_dir / "uxb_route_decision.json", {"schema_version": "bad"})

        exit_code = run_uxb_run(project_id)
        self.assertEqual(exit_code, 0)

        phase_state = json.loads((runtime_dir / "phase_state.json").read_text(encoding="utf-8"))
        self.assertEqual(phase_state["phase"], "formal")
        self.assertEqual(phase_state["target_artifacts"], [f"projects/{project_id}/runtime/uxb_route_decision.json"])
        self.assertIn(".codex/skills/uxb/references/uxb_route_decision_authoring_guide.md", phase_state["rule_refs"])

    def test_run_auto_assembles_then_stops_at_facts_phase_state(self) -> None:
        project_id = f"_ci_uxb_run_cli_assemble_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        run_task_bootstrap(project_id, domain="权限管理", task_name="自动装配", force=False)
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        runtime_dir = project_dir / "runtime"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        _write_text(source_dir / "task_card.md", _task_card(project_id))
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))

        exit_code = run_uxb_run(project_id)
        self.assertEqual(exit_code, 0)

        phase_state = json.loads((runtime_dir / "phase_state.json").read_text(encoding="utf-8"))
        stage_context = json.loads((runtime_dir / "stage_context.json").read_text(encoding="utf-8"))
        self.assertEqual(phase_state["phase"], "facts")
        self.assertEqual(phase_state["template_refs"], ["templates/facts.template.md"])
        self.assertTrue((runtime_dir / "context_manifest.json").exists())
        self.assertFalse((runtime_dir / "knowledge_trace.json").exists())
        self.assertIn("selection_source", stage_context["context"])
        self.assertEqual(stage_context["knowledge_trace"]["reasoning"], "测试用判断单。")

    def test_run_failed_gate_triggers_repair_plan_and_repair_phase_state(self) -> None:
        project_id = f"_ci_uxb_run_cli_repair_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        run_task_bootstrap(project_id, domain="权限管理", task_name="修复接管", force=False)
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        runtime_dir = project_dir / "runtime"
        workspace_dir = project_dir / "workspace"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        _write_text(workspace_dir / "facts.md", "# facts")
        _write_json(
            runtime_dir / "gates" / "facts_gate_status.json",
            {
                "status": "failed",
                "issues": {"blockers": ["facts 内容不完整"], "warnings": [], "infos": []},
                "issue_details": [
                    {
                        "source": "facts_gate",
                        "stage": "facts",
                        "severity": "blocker",
                        "category": "content_depth",
                        "message": "facts 内容不完整",
                        "target_artifacts": [f"projects/{project_id}/workspace/facts.md"],
                    }
                ],
            },
        )

        exit_code = run_uxb_run(project_id)
        self.assertEqual(exit_code, 0)

        remediation_dir = runtime_dir / "remediation"
        phase_state = json.loads((runtime_dir / "phase_state.json").read_text(encoding="utf-8"))
        self.assertEqual(phase_state["phase"], "facts")
        self.assertEqual(phase_state["status"], "needs_revision")
        self.assertTrue(phase_state["repair_mode"])
        self.assertIn(f"projects/{project_id}/runtime/remediation/remediation_plan.json", phase_state["repair_refs"])
        self.assertTrue((remediation_dir / "issue_index.json").exists())
        self.assertTrue((remediation_dir / "remediation_plan.json").exists())
        self.assertTrue((remediation_dir / "retry_scope.json").exists())

    def test_run_warning_gate_accumulates_warning_and_advances_phase(self) -> None:
        project_id = f"_ci_uxb_run_cli_warning_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        run_task_bootstrap(project_id, domain="权限管理", task_name="warning 承接", force=False)
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        runtime_dir = project_dir / "runtime"
        workspace_dir = project_dir / "workspace"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        _write_text(source_dir / "task_card.md", _task_card(project_id))
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        _write_text(workspace_dir / "facts.md", "# Facts\n\n## 1. 核心需求事实\n\n- A")

        def _fake_run_existing_command(command_name: str, current_project_id: str, options: dict[str, object] | None = None):
            del options
            if command_name == "gate-facts":
                _write_json(
                    runtime_dir / "gates" / "facts_gate_status.json",
                    {
                        "status": "warning",
                        "can_proceed": True,
                        "issues": {"blockers": [], "warnings": ["facts 仍可补强"], "infos": []},
                    },
                )

            class _Result:
                def __init__(self, name: str) -> None:
                    self.command_name = name
                    self.exit_code = 0
                    self.preflight_errors = []
                    self.target_artifacts = []

            return _Result(command_name)

        with patch("packages.uxb_run.cli.run_existing_command", side_effect=_fake_run_existing_command):
            exit_code = run_uxb_run(project_id)

        self.assertEqual(exit_code, 0)
        phase_state = json.loads((runtime_dir / "phase_state.json").read_text(encoding="utf-8"))
        stage_context = json.loads((runtime_dir / "stage_context.json").read_text(encoding="utf-8"))
        self.assertEqual(phase_state["phase"], "business")
        self.assertTrue(any(item.get("phase") == "facts" and item.get("message") == "facts 仍可补强" for item in stage_context["accumulated_warnings"]))

    def test_run_preflight_failure_writes_repair_phase_state_without_gate_roundtrip(self) -> None:
        project_id = f"_ci_uxb_run_cli_preflight_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        run_task_bootstrap(project_id, domain="权限管理", task_name="预检查失败", force=False)
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        runtime_dir = project_dir / "runtime"
        workspace_dir = project_dir / "workspace"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        _write_text(workspace_dir / "facts.md", "# Facts\n\n- [待补充]")

        exit_code = run_uxb_run(project_id)
        self.assertEqual(exit_code, 0)

        phase_state = json.loads((runtime_dir / "phase_state.json").read_text(encoding="utf-8"))
        self.assertEqual(phase_state["phase"], "facts")
        self.assertEqual(phase_state["status"], "needs_revision")
        self.assertTrue(phase_state["repair_mode"])
        self.assertIn("存在占位符残留：facts.md", phase_state["preflight_errors"])

    def test_run_same_invocation_advances_from_facts_check_to_business_phase(self) -> None:
        project_id = f"_ci_uxb_run_cli_phase_shift_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        run_task_bootstrap(project_id, domain="权限管理", task_name="同次切阶段", force=False)
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        runtime_dir = project_dir / "runtime"
        workspace_dir = project_dir / "workspace"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        _write_text(workspace_dir / "facts.md", "# Facts\n\n## 1. 核心需求事实\n\n- A")

        called: list[str] = []

        def _fake_run_existing_command(command_name: str, current_project_id: str, options: dict[str, object] | None = None):
            del options
            called.append(f"{command_name}:{current_project_id}")
            if command_name == "gate-facts":
                _write_json(runtime_dir / "gates" / "facts_gate_status.json", {"status": "passed"})

            class _Result:
                def __init__(self, name: str) -> None:
                    self.command_name = name
                    self.exit_code = 0
                    self.preflight_errors = []
                    self.target_artifacts = []

            return _Result(command_name)

        with patch("packages.uxb_run.cli.run_existing_command", side_effect=_fake_run_existing_command):
            exit_code = run_uxb_run(project_id)

        self.assertEqual(exit_code, 0)
        self.assertIn(f"gate-facts:{project_id}", called)
        phase_state = json.loads((runtime_dir / "phase_state.json").read_text(encoding="utf-8"))
        history_lines = (runtime_dir / "uxb_run_history.jsonl").read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(phase_state["phase"], "business")
        self.assertEqual(phase_state["target_artifacts"], [f"projects/{project_id}/workspace/business_blueprint_lite.md"])
        self.assertEqual(len(history_lines), 1)
        history_payload = json.loads(history_lines[0])
        self.assertEqual(history_payload["phase_before"], "facts")
        self.assertEqual(history_payload["phase_after"], "business")
        self.assertEqual(history_payload["next_phase"], "business")

    def test_run_final_coverage_blocker_enters_repair_and_retry_scope_rechecks_validate_then_coverage(self) -> None:
        project_id = f"_ci_uxb_run_cli_final_blocker_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        run_task_bootstrap(project_id, domain="权限管理", task_name="final blocker", force=False)
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        runtime_dir = project_dir / "runtime"
        workspace_dir = project_dir / "workspace"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        _write_text(source_dir / "task_card.md", _task_card(project_id))
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        _write_text(workspace_dir / "facts.md", "# Facts\n\n## 1. 核心需求事实\n\n- A")
        _write_text(workspace_dir / "business_blueprint_lite.md", "# Business Lite\n\n## 1. 核心流程\n\n- A")
        _write_text(workspace_dir / "experience_blueprint.md", "# Experience\n\n## 1. 页面蓝图\n\n- A")
        _write_json(runtime_dir / "phase_state.json", {"phase": "final", "status": "in_progress"})

        def _fake_run_existing_command(command_name: str, current_project_id: str, options: dict[str, object] | None = None):
            del options
            if command_name == "validate-lite":
                _write_json(workspace_dir / "check_status.json", {"status": "passed", "issues": {"blockers": [], "warnings": [], "infos": []}})
            elif command_name == "coverage-lite":
                _write_json(
                    workspace_dir / "check_status.json",
                    {
                        "status": "failed",
                        "issues": {"blockers": ["缺少关键覆盖"], "warnings": [], "infos": []},
                        "issue_details": [
                            {
                                "issue_id": "coverage-gap-1",
                                "source": "coverage_lite",
                                "stage": "final",
                                "severity": "blocker",
                                "category": "coverage_gap",
                                "message": "缺少关键覆盖",
                                "target_artifacts": [f"projects/{project_id}/workspace/experience_blueprint.md"],
                                "repair_mode": "rewrite",
                            }
                        ],
                    },
                )
                return type("Result", (), {"command_name": command_name, "exit_code": 1, "preflight_errors": [], "target_artifacts": []})()
            elif command_name == "repair-plan":
                remediation_dir = runtime_dir / "remediation"
                _write_json(remediation_dir / "issue_index.json", {"issues": [{"issue_id": "coverage-gap-1", "severity": "blocker", "status": "open", "stage": "final", "category": "coverage_gap", "repair_mode": "rewrite"}]})
                _write_json(remediation_dir / "remediation_plan.json", {"items": ["fix coverage"]})
                _write_json(
                    remediation_dir / "retry_scope.json",
                    {
                        "recommended_commands": [
                            f"python -m packages validate-lite {project_id}",
                            f"python -m packages coverage-lite {project_id}",
                        ]
                    },
                )
                _write_text(remediation_dir / "repair_summary.md", "# Repair\n\n- fix coverage")
            return type("Result", (), {"command_name": command_name, "exit_code": 0, "preflight_errors": [], "target_artifacts": []})()

        with patch("packages.uxb_run.cli.run_existing_command", side_effect=_fake_run_existing_command):
            exit_code = run_uxb_run(project_id)

        self.assertEqual(exit_code, 0)
        phase_state = json.loads((runtime_dir / "phase_state.json").read_text(encoding="utf-8"))
        retry_scope = json.loads((runtime_dir / "remediation" / "retry_scope.json").read_text(encoding="utf-8"))
        self.assertEqual(phase_state["phase"], "final")
        self.assertEqual(phase_state["status"], "needs_revision")
        self.assertTrue(phase_state["repair_mode"])
        self.assertEqual(
            retry_scope["recommended_commands"],
            [
                f"python -m packages validate-lite {project_id}",
                f"python -m packages coverage-lite {project_id}",
            ],
        )

    def test_run_final_warning_skips_repair_and_finishes_with_passed_with_warnings(self) -> None:
        project_id = f"_ci_uxb_run_cli_final_warning_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        run_task_bootstrap(project_id, domain="权限管理", task_name="final warning", force=False)
        project_dir = self.projects_dir / project_id
        source_dir = project_dir / "source"
        runtime_dir = project_dir / "runtime"
        workspace_dir = project_dir / "workspace"
        _write_text(source_dir / "requirement.md", "# Requirement\n\n- 正式需求")
        _write_text(source_dir / "background.md", "# Background\n\n- 正式背景")
        _write_text(source_dir / "task_card.md", _task_card(project_id))
        _write_json(runtime_dir / "uxb_route_decision.json", _valid_route_decision(project_id))
        _write_json(runtime_dir / "context_manifest.json", {"selection_source": "runtime/uxb_route_decision.json"})
        (runtime_dir / "context_bundle").mkdir(parents=True, exist_ok=True)
        _write_text(workspace_dir / "facts.md", "# Facts\n\n## 1. 核心需求事实\n\n- A")
        _write_text(workspace_dir / "business_blueprint_lite.md", "# Business Lite\n\n## 1. 核心流程\n\n- A")
        _write_text(workspace_dir / "experience_blueprint.md", "# Experience\n\n## 1. 页面蓝图\n\n- A")
        _write_json(runtime_dir / "phase_state.json", {"phase": "final", "status": "in_progress"})

        def _fake_run_existing_command(command_name: str, current_project_id: str, options: dict[str, object] | None = None):
            del options, current_project_id
            if command_name == "validate-lite":
                _write_json(workspace_dir / "check_status.json", {"status": "passed", "issues": {"blockers": [], "warnings": [], "infos": []}})
            elif command_name == "coverage-lite":
                _write_json(
                    workspace_dir / "check_status.json",
                    {
                        "status": "warning",
                        "issues": {"blockers": [], "warnings": ["覆盖可补强"], "infos": []},
                    },
                )
            return type("Result", (), {"command_name": command_name, "exit_code": 0, "preflight_errors": [], "target_artifacts": []})()

        with patch("packages.uxb_run.cli.run_existing_command", side_effect=_fake_run_existing_command):
            exit_code = run_uxb_run(project_id, skip_preview=True)

        self.assertEqual(exit_code, 0)
        phase_state = json.loads((runtime_dir / "phase_state.json").read_text(encoding="utf-8"))
        stage_context = json.loads((runtime_dir / "stage_context.json").read_text(encoding="utf-8"))
        self.assertEqual(phase_state["status"], "passed_with_warnings")
        self.assertIn("覆盖可补强", phase_state["warnings"])
        self.assertTrue(any(item.get("message") == "覆盖可补强" for item in stage_context["accumulated_warnings"]))

    def test_terminal_phase_warnings_only_keep_current_phase_messages(self) -> None:
        project_id = f"_ci_uxb_run_cli_terminal_warning_scope_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        run_task_bootstrap(project_id, domain="权限管理", task_name="terminal warning scope", force=False)
        project_dir = self.projects_dir / project_id
        runtime_dir = project_dir / "runtime"
        _write_json(runtime_dir / "phase_state.json", {"phase": "final", "status": "passed_with_warnings", "warnings": []})
        _write_json(runtime_dir / "stage_context.json", {"accumulated_warnings": [{"phase": "experience", "source": "gate-experience", "message": "experience 仍可补强"}]})

        action = CurrentAction(
            project_id=project_id,
            action_id="final-complete-1",
            phase="finalize",
            action_type="completed",
            owner="system",
            execution_mode="standard",
            stage="final",
            status="completed",
            created_at="2026-06-14T12:00:00+08:00",
            updated_at="2026-06-14T12:00:00+08:00",
        )
        state = ProjectRunState(
            project_id=project_id,
            project_dir=project_dir,
            source_dir=project_dir / "source",
            runtime_dir=runtime_dir,
            workspace_dir=project_dir / "workspace",
            preview_dir=project_dir / "preview",
            project_exists=True,
            source_ready=True,
            phase_state={"phase": "final", "status": "passed_with_warnings", "warnings": []},
            stage_context={"accumulated_warnings": [{"phase": "experience", "source": "gate-experience", "message": "experience 仍可补强"}]},
        )

        _write_terminal_report(project_id, action, [], "passed_with_warnings", state)

        phase_state = json.loads((runtime_dir / "phase_state.json").read_text(encoding="utf-8"))
        self.assertEqual(phase_state["status"], "passed_with_warnings")
        self.assertEqual(phase_state["warnings"], [])

    def test_append_warning_entries_skips_duplicate_check_status_message_from_gate(self) -> None:
        project_id = f"_ci_uxb_run_cli_warning_dedupe_{uuid.uuid4().hex[:8]}"
        self.project_ids.append(project_id)
        run_task_bootstrap(project_id, domain="权限管理", task_name="warning dedupe", force=False)
        project_dir = self.projects_dir / project_id
        runtime_dir = project_dir / "runtime"
        _write_json(
            runtime_dir / "stage_context.json",
            {
                "accumulated_warnings": [
                    {"phase": "business", "source": "gate-business", "message": "覆盖不足"},
                    {"phase": "business", "source": "gate-business", "message": "待确认问题格式建议"},
                ]
            },
        )
        action = CurrentAction(
            project_id=project_id,
            action_id="final-phase-1",
            phase="mainline",
            action_type="phase_work",
            owner="agent",
            execution_mode="standard",
            stage="final",
            status="requires_agent",
            target_artifacts=[],
            required_inputs=[],
            status_sources=[],
            blocking_reasons=[],
        )
        state = ProjectRunState(
            project_id=project_id,
            project_dir=project_dir,
            project_exists=True,
            source_ready=True,
            runtime_dir=runtime_dir,
            source_dir=project_dir / "source",
            workspace_dir=project_dir / "workspace",
            preview_dir=project_dir / "runtime" / "preview",
            phase_state={},
            stage_context={
                "accumulated_warnings": [
                    {"phase": "business", "source": "gate-business", "message": "覆盖不足"},
                    {"phase": "business", "source": "gate-business", "message": "待确认问题格式建议"},
                ]
            },
        )

        _append_warning_entries(project_id, state, action, ["覆盖不足", "business gate 状态为 warning"])

        stage_context = json.loads((runtime_dir / "stage_context.json").read_text(encoding="utf-8"))
        messages = [item.get("message") for item in stage_context["accumulated_warnings"]]
        self.assertEqual(messages.count("覆盖不足"), 1)
        self.assertIn("business gate 状态为 warning", messages)


if __name__ == "__main__":
    unittest.main()
