from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.experience_preview.build_preview_model import build_preview_model
from packages.experience_preview.render_html import write_preview_site


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def _business_md() -> str:
    return """
# 业务蓝图

## 1. 一句话结论

保持原有审批域能力，补上员工自助申请和状态承接。
"""


def _experience_md() -> str:
    return """
# 体验蓝图

## 0. 本次关键设计判断

本次重点不是新增复杂页面，而是稳定承接申请、审批和结果反馈。

## 1. 旅程图

- 管理员：进入配置 → 开启申请 → 保存策略
- 员工：发现缺权限 → 发起申请 → 等待结果

### 旅程缺口

- 入口位置仍需确认

## 2. 交互流程总览

**分角色交互流程：**

- 管理员：进入配置 → 节点 2.1 开启能力 → 发布生效
- 员工：查看权限 → 节点 2.2 提交申请 → 查看结果

**异常流程重点：**

- 审批人缺失

## 3. 主交互流程

### 员工提交申请

员工在权限页选择可申请项并提交说明。

### 审批人处理申请

审批人查看申请详情并完成同意或拒绝。

## 4. 次交互流程

### 查看申请记录

员工可以查看已提交申请及审批结果。

## 5. 异常与阻断流程

### 审批人缺失

提交时若无审批人，需阻断并提示联系管理员。

## 6. 页面 / 弹窗 / 抽屉设计

### 我的权限页

包含权限列表、申请入口和申请记录区。

### 申请弹窗

包含可申请项、原因输入和提交按钮。

## 7. 状态与反馈文案

| 状态 | 含义 | 适用对象 | 用户可操作 | 统一反馈口径 |
|---|---|---|---|---|
| 审批中 | 申请已提交 | 员工 | 等待处理 | 审批中，请等待审批人处理 |
| 已通过 | 审批完成并生效 | 员工 | 前往使用 | 审批已通过，权限已生效 |

- 审批中
- 已通过

## 8. 待确认问题

1. **员工入口位置**

   影响：会影响主流程起点。
   建议确认方：产品

## 附录：设计指南消费说明

### 1. 设计指南消费

| 使用依据 | 转换结果 | 落点 |
|---|---|---|
| 反馈可见性原则 | 统一状态口径 | 状态与反馈文案 |
"""


class ExperiencePreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="uxb-preview-test-"))
        self.projects_dir = self.temp_dir / "projects"
        self.project_id = "preview-stability"
        workspace = self.projects_dir / self.project_id / "workspace"
        _write_text(workspace / "business_blueprint.md", _business_md())
        _write_text(workspace / "experience_blueprint.md", _experience_md())
        self.env_patch = patch.dict(os.environ, {"UXB_PROJECTS_DIR": str(self.projects_dir)})
        self.env_patch.start()

    def tearDown(self) -> None:
        self.env_patch.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_build_preview_model_assigns_stable_components(self) -> None:
        model = build_preview_model(self.project_id)
        sections = {section["section_key"]: section for section in model["experience"]["sections"]}

        self.assertEqual(sections["journey"]["component"], "journey-section")
        self.assertEqual(sections["flow-overview"]["component"], "flow-overview-section")
        self.assertEqual(sections["main-flow"]["component"], "main-flow-section")
        self.assertEqual(len(sections["main-flow"]["subsections"]), 2)
        self.assertEqual(sections["page-structure"]["component"], "page-structure-section")
        self.assertEqual(len(model["experience"]["pages"]), 2)
        self.assertEqual(len(model["experience"]["state_rows"]), 2)
        self.assertIn("旅程缺口", sections["journey"]["body_html"])
        self.assertEqual(len(model["experience"]["interaction_summary"]["rows"]), 2)

    def test_build_preview_model_parses_bold_role_summary_rows(self) -> None:
        workspace = self.projects_dir / self.project_id / "workspace"
        _write_text(
            workspace / "experience_blueprint.md",
            """
# 体验蓝图

## 2. 交互流程总览

**管理员配置流程：**
进入权限管理 → 开启申请能力 → 发布生效

**员工申请流程：**
查看已有权限 → 提交申请 → 查看结果

**异常流程重点：**

- 审批人缺失
""",
        )

        model = build_preview_model(self.project_id)
        rows = model["experience"]["interaction_summary"]["rows"]

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["role"], "管理员配置流程")
        self.assertEqual(rows[0]["nodes"][0]["name"], "进入权限管理")
        self.assertEqual(rows[1]["role"], "员工申请流程")
        self.assertEqual(rows[1]["nodes"][-1]["name"], "查看结果")

    def test_rendered_preview_keeps_self_contained_layout_and_component_shells(self) -> None:
        model = build_preview_model(self.project_id)
        preview_dir = self.projects_dir / self.project_id / "runtime" / "preview"
        preview_dir.mkdir(parents=True, exist_ok=True)

        write_preview_site(preview_dir, model)
        html = (preview_dir / "index.html").read_text(encoding="utf-8")

        self.assertIn('class="tab-btn active" data-panel="business"', html)
        self.assertIn('class="tab-btn" data-panel="experience"', html)
        self.assertIn('data-section-key="journey"', html)
        self.assertIn('data-section-key="flow-overview"', html)
        self.assertIn('data-section-key="main-flow"', html)
        self.assertIn("state-feedback-table-wrap", html)
        self.assertIn("journey-visual", html)
        self.assertIn("summary-visual", html)
        self.assertIn(".summary-path {\n  display: flex;\n  align-items: center;\n  gap: 8px;\n  flex-wrap: nowrap;", html)
        self.assertIn(".journey-path-nodes {\n  display: flex;\n  align-items: center;\n  gap: 8px;\n  flex-wrap: nowrap;", html)
        self.assertNotIn('<div class="summary-role">异常流程重点</div>', html)
        self.assertNotIn('<span class="summary-step">审批人缺失</span>', html)
        self.assertIn("异常流程重点", html)
        self.assertIn("审批人缺失", html)
        self.assertNotIn("<link ", html)
        self.assertNotIn("https://", html)
        self.assertNotIn("http://", html)


if __name__ == "__main__":
    unittest.main()
