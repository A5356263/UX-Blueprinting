---
name: solution-swimlane
description: >
  方案协同泳道图 Skill。只读取正式体验蓝图 Markdown 与 Context JSON，将已确认的角色任务、系统处理、主流程、次流程、异常、条件和回流编译为经过来源覆盖校验的单文件 HTML + 内联 SVG。
  当用户要求方案协同图、业务泳道图、需求宣讲主图、跨角色流程主图，或明确要求把 experience_blueprint.md 与 experience-blueprint.json 转成 HTML/SVG 泳道图时使用。
  不用于前置需求分析、用户旅程分析、页面动作级交互图、页面原型、仅凭自然语言直接画图，或已有/一期/二期建设阶段图。
---

# Solution Swimlane

把正式体验蓝图压缩成产品、设计和开发共同评审的跨角色方案主图。保持语义可追踪；任何节点、关系或来源覆盖缺口都必须阻断正式输出。

## 固定输入与输出

只读取：

```text
spark-output/experience_blueprint.md
spark-output/context/experience-blueprint.json
```

只正式输出：

```text
spark-output/solution-swimlane/solution_swimlane.html
```

不要读取 UXB、旅程、原始需求或知识库补全缺失语义。输入不足时报告缺口，不生成伪完整图。

## 执行流程

### 1. 检查输入

确认两个正式输入均存在。读取 Blueprint `3.0` JSON 中的主流程、次流程、异常和状态，读取 Markdown 补充角色、条件、先后关系、系统处理和不确定性。

上游读取硬门禁：

- Blueprint `3.0` JSON 是结构化设计事实的机器面；必须接受无 ID、无 anchor、无 `end_target` 的字段结构，不得生成版本转换文件。
- 主图语义重点消费 `main_flow`、`sub_flows`、`exceptions`、`states`；`interaction_overview` 只作重复总览排除，页面载体、文案、反馈和分析追踪不提升为主图元素。
- JSON 不能替代 Markdown 中的角色、条件语境、系统处理语境和完整叙述；必须实际完整读取 `experience_blueprint.md`。
- 即使蓝图刚在同一会话生成、当前上下文仍保留内容，也不得替代本次文件读取。
- 重点章节只决定二次核对优先级，不是正文白名单。
- JSON 与 Markdown 冲突时停止生成并报告交接错误；不得静默选择任一侧或自行修复。
- 只有 JSON、Markdown 缺失或 Markdown 未读完时，不得建立源清单、图模型或正式 HTML。
- Agent 实际读取 Markdown 与确定性脚本解析源清单是两道独立门禁，不能相互替代。

如两者冲突、无法识别至少一个角色与系统处理方、无法形成闭合主流程，停止。

### 2. 建立完整源清单

在系统临时目录创建本轮工作目录，执行：

```bash
node <skill-root>/scripts/build-source-inventory.js \
  --md spark-output/experience_blueprint.md \
  --json spark-output/context/experience-blueprint.json \
  --out <temp-dir>/source-inventory.json
```

不要手工删减源清单。

### 3. 生成语义图模型

完整读取：

- `references/semantic-extraction.md`
- `references/validation-rules.md`

根据两个正式输入和完整源清单生成 `<temp-dir>/diagram-model.json`。

先生成只包含图元素、精确 `source_selectors[]` 和必要 `coverage_rules[]` 的 `<temp-dir>/diagram-draft.json`，再执行：

```bash
node <skill-root>/scripts/materialize-coverage.js \
  --inventory <temp-dir>/source-inventory.json \
  --draft <temp-dir>/diagram-draft.json \
  --out <temp-dir>/diagram-model.json
```

物化前必须先保证选择器按语义类型互不重叠，并完整覆盖主流程、次流程、异常和状态。脚本预检失败时会一次报告全部跨类型冲突，并汇总未显式处置的流程源项；应按完整报告批量修正草稿，不得只修第一项后反复试跑。

硬规则：

- 每个源项必须且只能有一个覆盖记录。
- 每个必画角色、节点、关系和流程必须映射到真实图元素。
- 同义归并必须保留全部 `source_item_ids[]`。
- 无法可靠确定的关系写为 `blocked`；不要猜测端点。
- 不把页面、按钮、字段、Toast 和建设阶段默认提升为主图节点或图例。

### 4. 先校验模型

```bash
node <skill-root>/scripts/validate-solution-swimlane.js \
  --inventory <temp-dir>/source-inventory.json \
  --model <temp-dir>/diagram-model.json \
  --report <temp-dir>/model-validation.json
```

校验失败时修复模型；如果缺口来自正式输入，停止并报告，不修改上游。

### 5. 渲染单文件 HTML

模型校验通过后，完整读取 `references/visual-rules.md`，再执行：

```bash
node <skill-root>/scripts/render-solution-swimlane.js \
  --inventory <temp-dir>/source-inventory.json \
  --model <temp-dir>/diagram-model.json \
  --template <skill-root>/assets/solution-swimlane.template.html \
  --out spark-output/solution-swimlane/solution_swimlane.html
```

渲染器使用严格横向泳道。流程选择区首位固定为“全部”，但默认仍高亮主流程；次流程和异常流程通过同一 HTML 内的流程选择器切换。切换与总览聚焦只能降噪，不能删除节点或关系。

### 6. 校验最终 HTML

```bash
node <skill-root>/scripts/validate-solution-swimlane.js \
  --inventory <temp-dir>/source-inventory.json \
  --model <temp-dir>/diagram-model.json \
  --html spark-output/solution-swimlane/solution_swimlane.html \
  --report <temp-dir>/html-validation.json
```

只有模型校验与 HTML 校验全部通过，才可宣告完成。

### 7. 视觉检查

在浏览器打开正式 HTML，至少检查：

- 泳道、节点和箭头可读；
- 中文长文本没有溢出或截断；
- 连线不穿过节点正文；
- “显示全部”时允许具有共同端点的关系复用共同线段；无共同端点的关系不得共享长线段，关系标签不得遮挡节点或其他标签；
- “全部”位于流程选择区首位；全部视角默认突出主流程，次流程与异常流程标签按需显示；
- 全部视角悬停或键盘聚焦任一关系时，对应完整流程的节点、关系和标签同步高亮，其他流程降噪；
- 选择或聚焦具体流程时，可见业务线保持正常线宽，透明命中轨道不得显示颜色或箭头，非当前节点与关系降至低透明度；
- 回流关系使用泳道下方的独立动态路由区，随回流数量增加画布高度，并保留底部安全边距；
- 主流程、每条次流程和每条异常流程都可切换；
- 缩放、适应画布、打印和导出 SVG 可用；
- 工具栏在文档流中占据真实高度，保持单行且可收起，不得覆盖画布；
- 节点详情、待确认项和校验信息默认不占据画布布局空间；
- 1920×1080 视口在正文保持最小可读的前提下，应优先展示更多时间列和完整泳道；不得用大面积空白替代有效信息；
- 主流程、次流程和异常流程的按钮、卡片与连接线具有一致且明显不同的类别颜色；
- 流程切换前后节点和关系总数不变。

视觉检查只能发现布局问题，不能替代脚本完整性校验。

## 失败关闭

遇到以下任一情况，不覆盖已有正式 HTML：

- `blocked_total > 0`
- `unmapped_total > 0`
- 必画来源集合与模型覆盖集合不相等
- 模型与 SVG DOM 的泳道、节点或关系集合不相等
- 关系端点不存在
- 异常没有恢复目标或明确终止
- MD 与 JSON 冲突且无法从正式蓝图内裁决

## 完成口径

输出：

```text
方案协同图已完成并通过完整性校验：
spark-output/solution-swimlane/solution_swimlane.html

当前没有固定下一步推荐。
你可以停在这里。
```

正式产物写入并校验通过后，执行：

```bash
node shared-workflow/generate-progress-preview.js
```

刷新失败只告警，不得把已通过校验的方案协同图判为失败。

## 资源

- `references/semantic-extraction.md`：角色、任务、系统动作、主次异常流程和来源覆盖规则。
- `references/visual-rules.md`：严格横向泳道、HTML/SVG 和交互规则。
- `references/validation-rules.md`：模型契约、四层对账和失败条件。
- `assets/solution-swimlane.template.html`：无业务内容的自包含 HTML 模板。
- `scripts/build-source-inventory.js`：确定性枚举 MD 与 JSON 全部源项。
- `scripts/materialize-coverage.js`：展开来源选择器并物化完整覆盖清单。
- `scripts/render-solution-swimlane.js`：确定性布局并生成正式 HTML。
- `scripts/validate-solution-swimlane.js`：校验来源、模型与 SVG DOM。
- `scripts/test-solution-swimlane.js`：故障注入回归测试。
