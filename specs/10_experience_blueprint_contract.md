# 体验蓝图构建合同（主链路收缩版）

## 目标

本合同定义体验阶段的最小闭环：基于 `facts.md` 与 `business_blueprint.md`，直接产出 `experience_blueprint.md`。  
不再依赖中间拼装产物，确保主链路更短、职责更清晰。

## 阶段定位

体验阶段负责把业务判断转译为可评审的交互蓝图，重点回答：

- 用户如何完成主任务
- 次流程如何进入与回退
- 异常/阻断如何反馈与恢复
- 页面/弹窗/抽屉如何承载信息与操作
- 状态与反馈文案如何解释系统语义

本阶段不负责视觉高保真、前端实现、接口设计与研发架构。

## 输入与输出

- 输入：
  - `projects/<project-id>/workspace/facts.md`
  - `projects/<project-id>/workspace/business_blueprint.md`
  - 可选：`projects/<project-id>/workspace/gap_list.md`
- 输出：
  - `projects/<project-id>/workspace/experience_blueprint.md`
  - `projects/<project-id>/runtime/experience_blueprint_input.md`（供生成参考）

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

- 主流程与异常流程都必须可读、可评审，不得只写 happy path。
- 页面章节必须说明承载目标、进入条件、关键操作与结果去向。
- 状态文案必须是可展示给用户的表达，不得保留机器化提示语。
- 待确认问题不能为空清单化“无”，应暴露真实不确定项。
- 附录需给出依据来源与承接关系，但不要求复杂追踪矩阵。

## 失败条件

- `experience_blueprint.md` 缺失。
- 固定章节缺失。
- 缺少主流程、页面设计或异常阻断内容。
- 文档只含抽象口号，无法支持评审。

## 同步约束

以下内容必须与本合同保持一致：

- `templates/experience_blueprint.template.md`
- `packages/mainline.py`
- `packages/__main__.py`
- `packages/generation/*`
- `packages/validate/*`
- `packages/experience_preview/*`
