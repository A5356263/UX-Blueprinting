from __future__ import annotations

import unittest

from packages.task_card_resolve.core import resolve_task_card


class TaskCardContractTests(unittest.TestCase):
    def test_resolve_task_card_keeps_slim_contract(self) -> None:
        text = """# 任务卡片

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.3
- Task ID: demo-task
- Task Name: Demo Task
- Domain: demo

## Required Inputs

- projects/demo-task/source/requirement.md
- projects/demo-task/source/background.md

## Required Outputs

- projects/demo-task/workspace/facts.md

## Constraints

- 不得臆造业务事实
- 信息不足时保留 [GAP]

## Templates

- templates/facts.template.md

## Checks

- specs/08_fact_extraction_contract.md
"""
        resolved = resolve_task_card(text, "demo-task")

        self.assertEqual(resolved["errors"], [])
        self.assertNotIn("task_goal", resolved)
        self.assertNotIn("task_scenario", resolved)
        self.assertNotIn("read_order", resolved)
        self.assertNotIn("notes", resolved)
        self.assertEqual(resolved["required_inputs"], [
            "projects/demo-task/source/requirement.md",
            "projects/demo-task/source/background.md",
        ])
        self.assertEqual(resolved["required_outputs"], ["projects/demo-task/workspace/facts.md"])


if __name__ == "__main__":
    unittest.main()
