# 界面证据 DSL 规范

建模阶段使用本文件。建模只描述输入证据中可证明的内容，不包含评价或建议。证据可以来自浏览器 DOM、Accessibility Tree、运行时状态、computed style、交互后的状态差异或截图。

## 自动生成流程

DSL 必须由系统自动生成，用户不需要手写。生成时把“主证据”和“提示词上下文”分开处理：

- Browser mode：`DOM + Accessibility Tree + runtime + computed style + prompt_context -> Page/Flow/Interaction DSL`。
- Screenshot mode：`screenshot + prompt_context -> Page/Flow/Interaction DSL`。
- Mixed mode：`DOM/Accessibility/runtime + screenshot + prompt_context -> Page/Flow/Interaction DSL`。

提示词上下文包括 `user`、`task`、`interface_capabilities`、`expected_result`。这些字段只用于解释任务语境、用户意图和验收目标；不能把提示词中提到的能力直接当成已观察到的组件。只有当 DOM、Accessibility、runtime 或截图证据支持时，才可写入 `regions`、`components`、`forms`、`navigation` 或 `feedback_elements`。

当提示词与证据冲突时：

- DSL 中优先记录可验证证据。
- 将冲突写入 `uncertain`。
- UCATS 评分按可验证证据降置信度处理。

## 输入解析

对每个页面或状态抽取：

- 来源元数据：URL/路由、DOM 快照 id、Accessibility 快照 id、截图 id、已知视口尺寸、设备类型、方向、时间戳/顺序。
- 任务上下文：目标用户、任务、界面能力、预期结果；缺失项标记为 `uncertain`。
- DOM/Accessibility：可见文本、role、accessible name、ARIA 状态、焦点、表单值、禁用/选中/展开状态、语义层级。
- Runtime：加载、错误、成功、空状态、权限、网络或交互后的状态变化；仅记录可观察事件。
- Screenshot：清晰/模糊/裁切/局部/遮挡，以及任何可读性限制；仅在截图或像素证据存在时使用视觉结论。
- 可见文本：主要标题、标签、导航、按钮、字段标签、辅助文案、错误文案、表头、空状态、状态文本。
- 布局区域：页头、导航、侧边栏、主区域、工具栏、筛选区、列表/表格、表单、模态框/抽屉、页脚。
- 组件：控件、卡片、表格、图表、标签页、步骤条、搜索、筛选、警告、toast、加载器、分页、对话框。
- 优先级线索：DOM 顺序、可访问性层级、主操作位置、按钮类型、状态与截图中的视觉层级。
- 可访问性线索：role/name 缺失、label 绑定、键盘焦点、ARIA 状态、目标尺寸风险、文本尺寸风险；对比度仅在有 computed style 或视觉证据时记录。
- 未知项：隐藏状态、屏幕外内容、不可见的 hover/focus 行为、后端规则、不可读的精确文案。

## 证据规则

每条观察应包含证据：

- `source_ref`：稳定来源 id，例如 `dom_1`、`a11y_1`、`runtime_1` 或 `image_1`。
- `source_type`：`dom|accessibility|runtime|screenshot|context`。
- `screenshot_ref`：截图 id 或文件名；没有截图时使用 `null`。
- `dom_ref`：DOM 快照 id；不可用时使用 `null`。
- `selector`：稳定 CSS selector、测试 id 或 DOM path；不可用时使用 `null`。
- `region_ref`：稳定区域 id，例如 `r_main` 或 `r_filter_bar`。
- `component_ref`：稳定组件 id，例如 `btn_submit`。
- `bbox`：用于自动化时的近似归一化边界 `[x, y, w, h]`，范围为 `0` 到 `1`。不可用时使用 `null`。
- `quote`：短可见文本或 accessible name；若证据为纯视觉证据则为 `null`。
- `certainty`：`high`、`medium` 或 `low`。

不要引用不可见的实现细节。如果某个结论依赖隐藏行为、视觉模型不可用的像素判断或后端规则，将其加入 `uncertain`。

## Page DSL

```json
{
  "page_id": "p1",
  "page_name": "可见或推断的页面名",
  "page_type": "info|form|list|dashboard|checkout|settings|auth|other",
  "business_scenario": "已知或 uncertain",
  "user_goal": "已知或 uncertain",
  "task_context": {
    "user": "已知或 uncertain",
    "task": "已知或 uncertain",
    "interface_capabilities": ["已知能力或 uncertain"],
    "expected_result": "已知或 uncertain"
  },
  "generation": {
    "method": "auto_from_browser_and_prompt|auto_from_screenshot_and_prompt|auto_from_mixed_and_prompt",
    "evidence_sources": ["dom_1", "a11y_1", "runtime_1", "image_1"],
    "context_fields_used": ["user", "task", "interface_capabilities", "expected_result"],
    "context_only_claims": ["提示词提到但界面证据未证明的能力"],
    "conflicts": []
  },
  "source": {
    "mode": "browser|screenshot|mixed",
    "dom_ref": "dom_1",
    "accessibility_ref": "a11y_1",
    "runtime_ref": "runtime_1",
    "screenshot_ref": "image_1",
    "device_class": "desktop|mobile|tablet|unknown",
    "viewport": {"width": null, "height": null},
    "quality": ["clear"],
    "order": 1
  },
  "regions": [
    {"id": "r_main", "name": "主内容区", "role": "main", "bbox": [0.2, 0.1, 0.7, 0.8], "children": ["tbl_orders"]}
  ],
  "components": [
    {
      "id": "btn_primary",
      "type": "button|link|input|select|table|card|chart|tab|modal|alert|toast|loader|nav|other",
      "label": "提交",
      "role": "button",
      "accessible_name": "提交",
      "selector": "[data-testid='submit']",
      "state": "default|disabled|selected|loading|error|success|unknown",
      "visibility": "visible|partially_visible|hidden|unknown",
      "bbox": [0.7, 0.85, 0.16, 0.06],
      "actions": ["submit_form"],
      "text": ["提交"],
      "evidence": "image_1:r_main:btn_primary"
    }
  ],
  "forms": [
    {
      "id": "form_profile",
      "fields": [{"id": "fld_email", "label": "邮箱", "type": "text|select|checkbox|radio|date|file|unknown", "required": "visible|not_visible|unknown", "validation_visible": false}],
      "submit_component": "btn_primary",
      "error_messages_visible": []
    }
  ],
  "navigation": [{"id": "nav_home", "type": "tab|menu|breadcrumb|link|stepper", "label": "首页", "target": "unknown", "state": "selected"}],
  "feedback_elements": [{"id": "alert_error", "type": "toast|modal|inline|loading|empty|error|success", "content": "可见文案", "trigger": "visible|inferred|unknown"}],
  "visual_priority": [{"rank": 1, "component_ref": "btn_primary", "reason": "位置/颜色/尺寸/文案"}],
  "accessibility_notes": [{"type": "contrast|target_size|text_size|focus|semantics|unknown", "evidence": "image_1:r_main:btn_primary", "certainty": "medium"}],
  "uncertain": ["精确校验行为在截图中不可见。"]
}
```

## Flow DSL

仅在有多张截图、多 DOM 状态、多路由、交互状态差异，或用户提供了有序任务时使用。

```json
{
  "task_name": "完成结账",
  "task_goal": "已知或 uncertain",
  "screens": ["p1", "p2"],
  "steps": [
    {"id": "s1", "page_ref": "p1", "visible_state": "购物车确认", "user_action": "点击结账", "input": [], "output": "结账页面", "time_estimate": "unknown", "uncertain": []}
  ],
  "transitions": [{"from": "p1", "to": "p2", "condition": "点击主 CTA 后", "certainty": "medium"}],
  "decision_nodes": [{"id": "d1", "condition": "选择支付方式", "branches": ["银行卡", "PayPal"], "certainty": "medium"}],
  "dependencies": [{"type": "account|network|payment|permission|data|unknown", "desc": "可见或推断"}],
  "potential_blockers": ["可见阻塞点或 uncertain 推断"],
  "potential_dropoff_points": ["步骤或页面引用"],
  "uncertain": []
}
```

## Interaction DSL

当 DOM、Accessibility、runtime 或截图展示加载、错误、成功、空状态、禁用、模态框或确认等状态时使用。

```json
{
  "interaction_id": "i_submit",
  "trigger_action": "点击提交",
  "visible_states": ["default", "failure"],
  "system_feedback": [{"type": "inline_error", "timing": "提交后", "content_template": "必填字段"}],
  "state_sequence": ["default", "failure"],
  "loading_behavior": "不可见",
  "success_feedback": "不可见",
  "failure_feedback": {"message": "必填字段", "recovery_options": ["编辑字段"]},
  "recovery_path": ["识别字段", "编辑值", "重新提交"],
  "uncertain": ["加载时机在截图中不可见。"]
}
```
