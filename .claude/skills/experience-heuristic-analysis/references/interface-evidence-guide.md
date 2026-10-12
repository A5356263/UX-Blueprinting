# 界面证据与场景描述指南

按需用于逐项登记来源、判断材料能力、定位 Finding 和生成 Scene Descriptor。

## 来源能力

| source type | 可支持 | 不能支持 |
| --- | --- | --- |
| `screenshot` | 可见布局、层级、文案、遮挡、裁切、静态状态 | 键盘、屏幕阅读器、真实点击、动态顺序 |
| `prototype` / `flow` / `blueprint` | 路径、分支、状态和设计预期 | 真实实现和用户行为 |
| `frontend_code` | 代码中可证明的结构、语义、状态和 token 线索 | 最终渲染、真实设备与用户行为 |
| `dom` / `a11y` | 实际结构、语义关系、名称和状态线索 | 视觉层级、真实辅助技术表现 |
| `runtime` | 实际交互后的状态变化、反馈和错误线索 | 发生率、满意度和业务影响 |
| `design_guideline` / `design_system` | 规范依据 | 界面已经实现该规则 |
| `business_rule` | 业务判断依据 | 界面问题本身 |

页面源码与运行证据冲突时，以运行证据描述现状，保留源码差异为实现线索。

## Source Manifest

来源分三类：

- 证据来源：截图、原型、Figma 导出、前端代码、DOM、A11Y、runtime、flow、blueprint；
- 情境来源：Brief、Stories、设计规范、设计系统、业务规则；
- 用户描述：只能帮助定位范围，不能单独支撑 Evidence Promotion。

每项来源记录：

```text
source_id
source_type
source_ref
acquisition = user_provided | tool_collected | explicit_upstream
status = loaded | partially_loaded | unreadable
observable_capabilities[]
limitations[]
fingerprint
sensitivity
privacy_status
redaction_applied
disclosure_limitations[]
```

链接、Figma、浏览器、DOM、A11Y 或 runtime 只有实际读取或实际采集后才可登记为 loaded。

`source_ref` 使用工作区相对路径或不含凭证的 opaque ref。不得保存本机绝对路径、`file://`、编辑器 URI 或带 token、secret、signature、key、credential、auth 参数的 URL。

## Finding 定位

只填写材料实际支持的字段：页面或流程、任务节点、位置、状态、route、component path、selector、aria label、截图区域或证据路径。禁止补造不可见定位。

## Scene Descriptor

Promoted Evidence 使用：

```text
where.product_area
where.page_or_flow
where.journey_step
where.state
what.business_object
what.interface_element
operation.user_goal
operation.user_action
source_attribution.source_refs[]
evidence_form[]
matching_policy = automatic_candidate | manual_only
```

`where`、`what`、`operation` 三组中至少两组可识别，才允许 `automatic_candidate`；否则使用 `manual_only`。未知信息写 `unknown`，不得猜测。

## 工具声明

不得声称已运行浏览器、Figma、自动化审计、截图模型或辅助技术，除非本轮工具真实执行且结果已登记。技能不内置这些依赖。
