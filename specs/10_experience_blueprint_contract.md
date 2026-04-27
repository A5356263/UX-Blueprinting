# 体验蓝图构建合同（主链路收缩版）

## 目标

本合同定义体验阶段最小闭环：基于 `facts.md` 与 `business_blueprint.md` 生成 `experience_blueprint.md`。

体验阶段必须优先承接 Business Blueprint 的方案承接要求，并结合设计原则输出可评审体验方案。

## 阶段定位

体验阶段负责把业务判断与方案承接要求转译为体验表达，重点回答：

- 用户如何完成主任务
- 次流程如何进入与回退
- 异常/阻断如何反馈与恢复
- 页面/弹窗/抽屉如何承载信息与操作
- 状态与反馈文案如何解释系统语义

体验阶段不负责视觉高保真、前端实现、接口设计与研发架构。

## 输入与输出

- 输入：
  - `projects/<project-id>/workspace/facts.md`
  - `projects/<project-id>/workspace/business_blueprint.md`
  - 可选：`projects/<project-id>/workspace/gap_list.md`
- 输出：
  - `projects/<project-id>/workspace/experience_blueprint.md`
  - 调试可选：`projects/<project-id>/runtime/debug/experience_prompt_preview.md`（不参与主链路）

## 承接边界

- 必须承接 Business 的：
  - 推荐业务方案
  - 必须守住的规则和边界
  - 主要风险与保护策略
  - 方案承接要求
  - 待确认问题
- 不得绕开 `business_blueprint.md` 重新做业务判断。
- 不得仅依据 facts 摘要生成保守体验方案。

## experience_blueprint 结构

必须包含以下固定章节：

- `## 1. 体验结论`
- `## 2. 主交互流程`
- `## 3. 次交互流程`
- `## 4. 异常与阻断流程`
- `## 5. 页面 / 弹窗 / 抽屉设计`
- `## 6. 状态与反馈文案`
- `## 7. 待确认问题`
- `## 附录：依据与追踪`

## 质量要求

- 主流程、次流程、异常流程都要可评审，不能只写 happy path。
- 页面章节需说明承载目标、进入条件、关键操作与结果去向。
- 状态文案必须可直接给用户展示，避免机器化提示语。
- 待确认问题应暴露真实不确定项并说明影响。

## 失败条件

- `experience_blueprint.md` 缺失。
- 固定章节缺失。
- 未承接 business 的推荐方案/规则边界/风险保护/方案承接要求。
- 缺少主流程、页面设计或异常阻断内容。

## 同步约束

以下内容必须与本合同一致：

- `templates/experience_blueprint.template.md`
- `packages/generation/core.py`
- `packages/validate/core.py`
- `packages/generation/*`
- `packages/mainline.py`
