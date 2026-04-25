from __future__ import annotations

import json
import shutil
import textwrap
import unittest
from pathlib import Path

from packages.common import get_repo_root
from packages.context_assemble.core import run_context_assemble
from packages.generation.reasoning.facts_reasoner import build_facts_model
from packages.task_card_resolve.core import resolve_task_card
from packages.validate.core import check_runtime_contract


def make_task_card(task_id: str, include_read_order: bool = True) -> str:
    read_order_section = """
## Read Order

1. 先读 runtime 合同
2. 再读 Required Inputs
""" if include_read_order else ""
    return textwrap.dedent(
        f"""\
        # Task Card

        ## Protocol

        - Protocol Name: Cross-AI Task Card
        - Protocol Version: v0.2
        - Task ID: {task_id}
        - Task Name: Runtime Contract Test
        - Domain: permission

        ## Task Goal

        - 生成正式产物
        - 保持 runtime 合同优先

        ## Task Scenario

        - 当前任务用于验证 runtime 合同承接

        ## Required Inputs

        - projects/{task_id}/source/requirement.md
        - projects/{task_id}/source/background.md

        ## Required Outputs

        - projects/{task_id}/workspace/facts.md
        - projects/{task_id}/workspace/business_blueprint.md
        - projects/{task_id}/workspace/experience_blueprint.md
        - projects/{task_id}/workspace/gap_list.md
        - projects/{task_id}/workspace/check_report.md
        - projects/{task_id}/workspace/check_status.json

        {read_order_section}
        ## Constraints

        - 不得臆造业务事实
        - 信息不足处保留 [GAP]

        ## Templates

        - templates/facts.template.md
        - templates/business_blueprint.template.md
        - templates/experience_blueprint.template.md
        - templates/gap_list.template.md
        - templates/check_report.template.md

        ## Checks

        - specs/06_check_contract.md
        - specs/08_fact_extraction_contract.md
        - specs/09_business_blueprint_contract.md
        - specs/10_experience_blueprint_contract.md

        ## Result Locations

        - 执行中结果: projects/{task_id}/workspace/
        - 归档结果: projects/{task_id}/exports/final/

        ## Completion Criteria

        - 必需输出文件全部存在
        - 无 blocker

        ## Facts Output Requirements

        ### Required Sections

        - 任务意图

        ### Recommended ID Prefixes

        - F

        ### Boundary

        - mode: input-first extraction
        - forbidden: promote unconfirmed knowledge as confirmed task facts

        ## Business Output Requirements

        ### Required Sections

        - 评审对象与任务边界

        ### Recommended ID Prefixes

        - J

        ### Boundary

        - mode: facts-first judgment
        - forbidden: output UI or implementation decisions in business blueprint

        ## Experience Output Requirements

        ### Required Sections

        - 体验目标与任务边界

        ### Recommended ID Prefixes

        - EXP

        ### Boundary

        - mode: business-first translation
        - forbidden: output high-fidelity visual specs or implementation details

        ## Notes

        - 这是一条补充说明
        """
    )


class RuntimeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = get_repo_root()
        self.project_id = "ut_runtime_contract"
        self.project_dir = self.repo_root / "projects" / self.project_id
        if self.project_dir.exists():
            shutil.rmtree(self.project_dir)
        (self.project_dir / "source").mkdir(parents=True)
        (self.project_dir / "runtime").mkdir(parents=True)
        (self.project_dir / "workspace").mkdir(parents=True)

    def tearDown(self) -> None:
        if self.project_dir.exists():
            shutil.rmtree(self.project_dir)

    def write_project_file(self, relative_path: str, content: str) -> Path:
        path = self.project_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_resolve_task_card_parses_runtime_semantic_fields(self) -> None:
        resolved = resolve_task_card(make_task_card("001"), "001")
        self.assertEqual(resolved["task_goal"], ["生成正式产物", "保持 runtime 合同优先"])
        self.assertEqual(resolved["task_scenario"], ["当前任务用于验证 runtime 合同承接"])
        self.assertEqual(resolved["execution_constraints"], ["不得臆造业务事实", "信息不足处保留 [GAP]"])
        self.assertEqual(resolved["read_order"], ["先读 runtime 合同", "再读 Required Inputs"])
        self.assertEqual(resolved["notes"], ["这是一条补充说明"])

    def test_resolve_task_card_warns_when_read_order_missing(self) -> None:
        resolved = resolve_task_card(make_task_card("001", include_read_order=False), "001")
        self.assertIn("Read Order section is missing", resolved["warnings"])

    def test_context_assemble_writes_task_contract_and_stage_boundaries(self) -> None:
        self.write_project_file("source/task_card.md", make_task_card(self.project_id))
        self.write_project_file("source/requirement.md", "# Requirement\n\n- 员工可以申请权限\n")
        self.write_project_file("source/background.md", "# Background\n\n- 需要审批流\n")

        exit_code = run_context_assemble(self.project_id, strict=False)
        self.assertEqual(exit_code, 0)

        manifest = json.loads((self.project_dir / "runtime" / "context_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["task_contract"]["task_goal"], ["生成正式产物", "保持 runtime 合同优先"])
        self.assertEqual(manifest["task_contract"]["read_order"], ["先读 runtime 合同", "再读 Required Inputs"])
        self.assertEqual(
            manifest["stage_boundaries"],
            {
                "facts": [
                    "mode: input-first extraction",
                    "forbidden: promote unconfirmed knowledge as confirmed task facts",
                ],
                "business": [
                    "mode: facts-first judgment",
                    "forbidden: output UI or implementation decisions in business blueprint",
                ],
                "experience": [
                    "mode: business-first translation",
                    "forbidden: output high-fidelity visual specs or implementation details",
                ],
            },
        )

    def test_facts_model_prefers_runtime_contract_and_keeps_business_sources_clean(self) -> None:
        self.write_project_file("source/task_card.md", make_task_card(self.project_id))
        self.write_project_file("source/requirement.md", "# Requirement\n\n员工提交权限申请，系统触发审批流。\n")
        self.write_project_file("source/background.md", "# Background\n\n审批通过后自动生效。\n")
        self.write_project_file(
            "runtime/task_card_resolved.json",
            json.dumps(
                {
                    "task_goal": ["基于 runtime 合同生成任务意图"],
                    "task_scenario": ["当前任务用于验证 facts 默认读取 runtime 合同"],
                    "execution_constraints": ["不得把任务目标当成业务事实"],
                    "read_order": ["先读 resolved", "再读 manifest"],
                    "notes": ["补充说明"],
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
        self.write_project_file(
            "runtime/context_manifest.json",
            json.dumps(
                {
                    "task_contract": {
                        "task_goal": ["基于 runtime 合同生成任务意图"],
                        "task_scenario": ["当前任务用于验证 facts 默认读取 runtime 合同"],
                        "execution_constraints": ["不得把任务目标当成业务事实"],
                        "read_order": ["先读 resolved", "再读 manifest"],
                        "notes": ["补充说明"],
                    },
                    "references": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
        )

        model = build_facts_model(self.project_id)

        self.assertEqual(len(model.source_files), 2)
        self.assertTrue(model.source_files[0].endswith(f"/projects/{self.project_id}/source/requirement.md"))
        self.assertTrue(model.source_files[1].endswith(f"/projects/{self.project_id}/source/background.md"))
        self.assertTrue(any(unit.heading == "Runtime Task Goal" for unit in model.evidence_units))
        self.assertTrue(
            any(
                unit.source_file.endswith("/runtime/task_card_resolved.json")
                for unit in model.evidence_units
                if unit.heading == "Runtime Task Goal"
            )
        )
        self.assertFalse(any(unit.source_file.endswith("/source/task_card.md") for unit in model.evidence_units))

    def test_facts_model_falls_back_to_task_card_when_runtime_contract_missing(self) -> None:
        self.write_project_file("source/task_card.md", make_task_card(self.project_id))
        self.write_project_file("source/requirement.md", "# Requirement\n\n员工可以查看个人权限。\n")
        self.write_project_file("source/background.md", "# Background\n\n当前流程依赖审批系统。\n")

        model = build_facts_model(self.project_id)

        self.assertTrue(any(unit.heading == "Runtime Contract Fallback" for unit in model.evidence_units))
        self.assertTrue(any(unit.source_file.endswith("/source/task_card.md") for unit in model.evidence_units))
        self.assertTrue(any("Runtime 合同缺失" in gap for gap in model.gaps))

    def test_check_runtime_contract_reports_mismatch_and_missing_read_order(self) -> None:
        self.write_project_file(
            "runtime/task_card_resolved.json",
            json.dumps(
                {
                    "errors": [],
                    "task_goal": ["目标 A"],
                    "task_scenario": ["场景 A"],
                    "execution_constraints": ["约束 A"],
                    "read_order": [],
                    "notes": ["备注 A"],
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
        self.write_project_file(
            "runtime/context_manifest.json",
            json.dumps(
                {
                    "task_contract": {
                        "task_goal": ["目标 B"],
                        "task_scenario": ["场景 A"],
                        "execution_constraints": ["约束 A"],
                        "read_order": [],
                        "notes": ["备注 A"],
                    }
                },
                ensure_ascii=False,
                indent=2,
            ),
        )

        issues: list[tuple[str, str]] = []
        check_runtime_contract(self.project_id, issues)

        self.assertIn(("warning", "task_card_resolved.json 缺少 read_order"), issues)
        self.assertIn(("warning", "context_manifest.json.task_contract 缺少 read_order"), issues)
        self.assertTrue(any("不一致：task_goal" in message for level, message in issues if level == "warning"))


if __name__ == "__main__":
    unittest.main()
