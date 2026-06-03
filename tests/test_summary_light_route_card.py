from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from packages.generation.reasoning.knowledge_loader import _classify_note
from packages.knowledge_consumption.summary_parser import parse_summary_metadata


REPO_ROOT = Path(__file__).resolve().parents[1]


class SummaryLightRouteCardTests(unittest.TestCase):
    def test_parse_summary_metadata_infers_source_group_from_source_path(self) -> None:
        text = """# 可用性
- source_path: knowledge/raw/设计准则/可用性.md
- domain: 设计准则
- summary_role: light_route_card
- updated_at: 2026-06-03

## 定位
用于路由。
## 触发信号
- 需要判断可用性时

## 稳定结论
- 可直接复用
## 已知缺口
- 暂无
"""
        metadata = parse_summary_metadata(text)
        self.assertEqual(metadata.get("source_group"), "guideline")
        self.assertEqual(metadata.get("source_path"), "knowledge/raw/设计准则/可用性.md")
        self.assertEqual(metadata.get("summary_role"), "light_route_card")
        self.assertNotIn("page_type", metadata)
        self.assertNotIn("source_refs", metadata)
        self.assertNotIn("confidence", metadata)

    def test_classify_light_route_card_by_path(self) -> None:
        text = """# 组织架构

- source_path: knowledge/raw/业务/组织架构/10_组织架构设计.md
- domain: 组织架构
- summary_role: light_route_card
- updated_at: 2026-06-03
"""
        note_type = _classify_note("knowledge/wiki/summaries/业务/组织架构/10_组织架构设计.md", text)
        self.assertEqual(note_type, "business")

    def test_build_summaries_dry_run_succeeds(self) -> None:
        command = [
            sys.executable,
            str(REPO_ROOT / "knowledge" / "scripts" / "build_summaries.py"),
            "--dry-run",
            "--only",
            "knowledge/raw/业务/权限管理/15_页面载体语义.md",
        ]
        result = subprocess.run(command, cwd=str(REPO_ROOT / "knowledge"), capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("summary_count=1", result.stdout)

    def test_lint_wiki_succeeds_with_light_route_cards(self) -> None:
        command = [sys.executable, str(REPO_ROOT / "knowledge" / "scripts" / "lint_wiki.py")]
        result = subprocess.run(command, cwd=str(REPO_ROOT / "knowledge"), capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)


if __name__ == "__main__":
    unittest.main()
