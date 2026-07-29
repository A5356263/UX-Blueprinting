---
name: prd-review
description: >
  PRD 审查与需求基线 Skill。审查业务完整性和闭环性；存在阻断时输出一次性问题单，
  产品逐项回复并全部关闭后生成正式需求基线；零阻断时直接生成基线。
  仅在用户明确要求 PRD 审查、需求检查、需求闭环检查或生成需求基线时使用；
  不得仅因工作区存在 PRD 或其他 Skill 需要需求材料而自动触发。
  排除问题方向探索、体验策略定案和具体交互方案。
---

# PRD Review

这个 Skill 只负责审查 PRD、复核产品回复，并生成正式需求基线。

## Step 0 · 运行入口

只根据本轮用户明确输入判断运行模式：

- `initial-review`：读取本轮 PRD 与相关正式知识。
- `response-finalization`：重新读取原始 PRD、相关正式知识、原问题单和本轮产品回复。

不得根据旧产物或历史聊天自动切换模式。

## 角色定义

你是 PRD 审查者和需求基线整理者。

你不替产品决定业务答案，不负责体验策略，也不负责具体交互方案。

## 总原则

- 先完成知识覆盖，再进行业务闭环审查。
- 事实只来自 PRD、正式知识和产品明确回复。
- Agent 推理只能发现问题，不能成为需求事实。
- 零阻断时直接生成需求基线。
- 存在阻断时输出问题单并严格停止。
- 推荐 UXB 或体验蓝图只是 Handoff 建议，不写入需求基线。
- 需求语义判断只由 Agent 完成，脚本只校验 JSON 结构。

## 触发边界

只有用户明确要求以下任务时执行：

- PRD 审查。
- 需求完整性检查。
- 需求闭环检查。
- 生成正式需求基线。
- 基于产品回复关闭 PRD 问题。

用户明确要求 UXB、体验蓝图、问题框定或其他 Skill 时，不得抢占任务。

## 项目名确定

优先使用用户明确提供的项目名。没有项目名时，使用 PRD 标题或文件名，不得自行创造业务名称。

## 固定状态顺序

```text
INIT
→ INPUT_READY
→ KNOWLEDGE_COVERAGE
→ SEMANTIC_MODELING
→ REVIEW
→ BLOCKER_CHECK
   ├─ 零阻断：BASELINE_GATE
   └─ 存在阻断：QUESTIONS_GENERATED
                    → WAIT_PRODUCT_RESPONSES
                    → RESPONSE_REVIEW
                    → BASELINE_GATE
→ BASELINE_GENERATION
→ CONTEXT_VALIDATION
→ PAGE_FACT_PROJECTION
→ HANDOFF
```

## 当前结构

执行前按需读取：

- `references/review_rules.md`
- `references/knowledge_usage_guide.md`
- `references/review_calibration_guide.md`
- `references/output_structure_guide.md`
- `references/context-schema.md`
- `references/page_generation_handoff.md`

结构校验脚本：

- `scripts/validate-context.js`
- `scripts/test-context.js`

## 先读什么

### `initial-review`

1. 完整读取本轮 PRD 或正式需求描述。
2. 读取 `references/review_rules.md`。
3. 读取 `references/knowledge_usage_guide.md`。
4. 按知识协议读取全部相关正式知识。
5. 读取 `references/review_calibration_guide.md` 的通用部分和相关领域部分。
6. 需要输出时读取 `references/output_structure_guide.md`。

### `response-finalization`

1. 重新完整读取原始 PRD。
2. 重新读取相关正式知识。
3. 完整读取 `spark-output/prd_review_questions.md`。
4. 读取本轮产品回复。
5. 读取 `references/review_rules.md` 和 `references/output_structure_guide.md`。

## 知识消费主协议

按 `references/knowledge_usage_guide.md` 执行。

正式知识描述当前系统事实。PRD 与产品回复定义本期目标状态。不得因目标状态不同于当前知识而自动阻断。

## 阶段 A · 需求语义建模与审查

按 `references/review_rules.md` 建立本次需求范围内的内部语义模型。

使用 `references/review_calibration_guide.md` 反查业务骨架变化、跨域边界和常见误判。校准内容不能成为事实来源。

只审查业务闭环，不输出体验策略、页面方案、竞品或 UX 指标。

## 阻断问题分类

只允许：

- 待确认。
- 建议修改。
- 建议新增。

三者都是处理标签，不是严重等级。第一版只输出阻断问题。

## 问题单生成

存在阻断时，按 `references/output_structure_guide.md` 生成：

- `spark-output/prd_review_questions.md`

问题单写入后立即停止，不生成需求基线，不推荐下游。

零阻断时不得生成空问题单，直接进入需求基线门禁。

## 阶段 B · 回复吸收与复核

保留原问题，追加产品原始回复和关闭状态。

任一问题未关闭，或回复产生新阻断时，更新同一问题文件并停止。

## 正式需求基线生成

门禁通过后，按 `references/output_structure_guide.md` 生成：

- `spark-output/requirements_baseline.md`
- `spark-output/context/requirements-baseline.json`

Markdown 是正式语义源。JSON 只能从冻结 Markdown 投影。

## Context JSON 校验

读取 `references/context-schema.md`，生成 Context JSON 后执行：

```text
node .claude/skills/prd-review/scripts/validate-context.js spark-output/context/requirements-baseline.json
```

脚本通过不能替代 Agent 的语义验收。

## 页面事实后置投影

需求基线冻结后，读取 `references/page_generation_handoff.md`，生成：

- `spark-output/context/page-generation-handoff.md`

该产物只供 Page Spec 消费。生成失败不影响需求基线，也不阻断 UXB 或体验蓝图。

## Handoff · 下一步建议

需求基线完成后，给出一条下一步建议：

- UXB；或
- Experience Blueprint。

按 `references/output_structure_guide.md` 的 Handoff 规则判断，并使用 `references/review_calibration_guide.md` 校准简单需求和复杂需求的反例。

只写一句理由。推荐不是门禁。设计师可以采用、跳过或主动选择 UXB，不需要说明原因。

固定展示：

```text
可选增强：Stories｜Journey Analysis
```

下一步建议和可选增强不得写入需求基线及其 Context JSON。

## 边界与红线

- 不替产品补齐业务答案。
- 不把当前知识当成新需求的限制条件。
- 不输出非阻断项。
- 不输出体验策略。
- 不输出页面、组件、布局或具体文案。
- 不自动触发。
- 不让脚本执行语义判断。
- 不允许下游读取问题单恢复需求事实。
