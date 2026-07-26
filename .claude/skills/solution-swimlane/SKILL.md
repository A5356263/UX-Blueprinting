---
name: solution-swimlane
description: >
  从正式体验蓝图 Markdown 或可选 Context JSON 中抽取角色、责任、业务动作、系统处理、条件、交接、主次流程、异常、恢复与待确认项，生成确定性的单文件 HTML/SVG 方案协同泳道图。用户要求方案协同图、业务泳道图、跨角色流程主图、需求宣讲主图，或要求将 experience_blueprint.md 转为泳道图时使用。不用于需求分析、用户旅程、页面原型、页面动作清单或建设阶段图。
---

# Solution Swimlane

把体验蓝图转换为最小语义草稿，由脚本补全机械字段并稳定输出 HTML。不要建立来源清单或逐字段对账；只允许在当次执行记录中建立一次紧凑 P/S/E 覆盖清单。

## 文件边界

只读取：

```text
spark-output/experience_blueprint.md
spark-output/context/experience-blueprint.json
```

第二个文件可缺失。只写入：

```text
spark-output/solution-swimlane/solution_swimlane.html
spark-output/solution-swimlane/.work/semantic-draft.json
spark-output/solution-swimlane/.work/semantic-model.json
spark-output/solution-swimlane/.work/validation.json
```

不得修改输入、其他 Skill、`shared-workflow/`、项目配置或其他输出。不得调用 `shared-workflow/generate-progress-preview.js`。
如果本轮操作修改到其他 Skill，立即停止，不得继续修复、回退或扩展，并报告具体路径。

## 执行门禁

- 自动生成总耗时达到 180 秒时停止并报告超时。
- 只使用本次读取的正式输入，忽略历史对话中的项目、角色和流程。
- Markdown 只完整读取一次，同时记录原文明示的 P/S/E 编号和标题；不得为了确认历史印象重新读取。
- 语义草稿只完整生成一次。
- 规范化失败时只允许依据完整错误列表修正一次 JSON 语法、字段、ID、引用或关系顺序，不得重新读取和抽取全文。
- 修正不得创建原文没有的业务关系；出口不明确时使用 `pending` 和 `open_questions`。
- 第二次规范化仍失败时立即停止。
- 模型通过后只渲染一次；渲染或 HTML 校验失败时不得重新抽取语义。
- 局部信息不完整时使用 `pending` 和 `open_questions`，不得阻断其余已确认流程。
- 默认不得启动浏览器、HTTP 服务、`npx serve` 或安装依赖。
- 覆盖门禁通过后不得重新讨论主流程定义、为同一路径提出多个候选方案或重新生成整份草稿。
- 禁止使用“再想一下”“重新考虑”“也许可以跳过”等开放式反思循环；发现漏项时只补对应路径。

必须按以下顺序执行，不得跳过、调换或返回上一步重新生成：

```text
选择输入
→ 完整读取一次并记录 P/S/E 编号
→ 直接建立最小语义模型
→ 输出一次紧凑 P/S/E 覆盖清单
→ 执行覆盖门禁
→ 写入最小语义草稿
→ 执行一次草稿必填项检查
→ 规范化语义模型
→ 模型校验
→ HTML 渲染
→ HTML 校验
→ 成功后删除 .work
```

## 1. 选择输入

1. Markdown 存在时，以 Markdown 为唯一权威业务语义来源。
2. JSON 只补充 Markdown 未表达且不冲突的结构化流程信息。
3. 同一事实冲突时采用 Markdown，并把冲突写入 `open_questions`。
4. JSON 的项目名或业务范围与 Markdown 明示内容不一致时，忽略整份 JSON 并报告警告。
5. 只有 JSON 时，仅当能识别泳道、业务节点和一条完整主流程才继续。
6. 两个输入均不存在、无法识别泳道或无法形成主流程时停止。

## 2. 抽取语义

完整读取 Markdown，不按章节白名单截断。

### 2.1 有效信息

只抽取会改变图结构或流程含义的信息：

| 语义 | 判断问题 | 模型位置 |
|---|---|---|
| 参与方 | 谁执行或承担责任？ | `lanes` |
| 业务动作 | 角色完成什么完整任务？ | `nodes` |
| 系统处理 | 系统自动校验、计算、写入或通知什么？ | `nodes` |
| 顺序 | 下一步是什么？ | `edges` |
| 条件 | 在什么条件下走不同路径？ | `decision` + `conditional` |
| 交接 | 任务或结果交给谁？ | `handoff` |
| 结果 | 流程完成、失败或终止后得到什么？ | `result` / `end` |
| 异常 | 出错后如何恢复、回流或终止？ | `exception` / `return` / `terminate` |

### 2.2 节点与泳道粒度

- 一个节点只表达一个可独立评审的业务任务或系统处理。
- 连续、同角色且没有独立分支价值的细步骤必须合并。
- 页面点击、字段填写、按钮、Toast 和提示文案只能进入节点摘要，不得独立成节点。
- 页面级动作只有在改变跨角色业务流转时才能提升为节点。
- 同一任务中的角色动作与系统处理必须拆开。
- 角色别名语义和责任均相同时必须合并；责任不同则分开。
- 系统自动行为必须进入系统泳道，不得归给人工角色。
- 节点 `summary` 只有在补充 `label` 未表达的业务信息时才写；否则省略。
- 草稿不得写 `source_refs`。

### 2.3 流程分类

- `main`：从明确开始到主要业务结果的核心成功路径，必须且只能有一条。
- `secondary`：编辑、查看、撤销、关闭等非核心任务，必须结束或回到主流程。
- `exception`：失败、超时、驳回、无权限或其他异常，必须具有恢复、终止或 `pending` 出口。
- 只在 `flows[].edge_ids` 中维护流程归属和关系顺序；脚本推导 `node_ids` 与反向 `flow_ids`。
- 每条流程的后一条关系必须从前一条关系的终点继续，不得跳跃、并排或重复端点。
- 只有主流程创建显式 `start` 和 `end`。次流程与异常流程复用真实触发节点，以真实结果、恢复、终止或 `pending` 结束。
- 总业务仍继续时使用 `result`，不得在流程中途使用 `end`。
- 不得只画异常提示而遗漏恢复、回流或终止方式。

### 2.4 不确定信息

- 角色、关系端点或恢复方式无法由原文确认时不得猜测。
- 已知存在但细节不清的步骤必须使用 `pending` 节点。
- 不确定节点或关系必须使用 `certainty: "uncertain"`。
- 只有答案会改变泳道、节点、关系端点或方向、流程归属、条件分支、恢复、回流、终止或 `pending` 出口时，才写入 `open_questions`。
- 页面文案、字段展示、视觉样式、按钮、Toast、提示语、秒级或分钟级耗时，以及不改变节点和关系的交互细节不得进入 `open_questions`。
- 不确定内容可以在节点 `summary` 中完整表达时，不得同时创建 `open_questions`。
- 合法待确认项必须同时写明具体问题、结构影响、关联元素和临时表达。
- 局部不确定不得阻断其他已确认流程。

### 2.5 排除内容

背景、旅程分析、设计判断、页面布局、控件、字段、按钮、Toast、视觉草图、知识消费记录、上游追踪、统计结论和建设阶段本身不得进入模型。

章节名不是过滤依据。如果上述章节包含真实角色、动作、条件、交接、结果或异常，只抽取有效语义。

### 2.6 P/S/E 覆盖门禁

完整读取 Markdown 时，只记录原文明示的 P/S/E 编号和标题，不得自行创造编号。建立模型后，在当次执行记录中输出一次紧凑清单；清单不得写入文件、模型或 HTML。

每个编号必须且只能使用以下一种格式：

```text
S4｜已制图｜secondary-records
X1｜因无结构变化跳过｜仅描述按钮颜色，不产生动作、处理、状态、分支、交接或出口
```

“已制图”后必须填写已存在或即将写入草稿的 `flow.id`。多个编号合并到同一流程时可以填写同一个 `flow.id`。

只有同时满足以下全部条件，才能标记为“因无结构变化跳过”：

1. 没有新增或改变角色任务；
2. 没有新增或改变系统处理；
3. 没有新增或改变业务状态或结果；
4. 没有新增或改变条件或分支；
5. 没有新增或改变跨角色交接；
6. 没有新增或改变异常、恢复、回流、终止或待处理出口。

任意一项不满足都必须标记为“已制图”。不得使用“不是主流程”“只是查看信息”“没有修改数据”“发生频率低”“可以写进摘要”或“对主图价值不高”作为跳过理由。

覆盖门禁必须确认：

1. 每个原文明示编号恰好出现一次；
2. 每条“已制图”路径引用的 `flow.id` 存在于待写入草稿的流程中；
3. 每条跳过理由明确说明六项结构均未变化；
4. 查看类路径只要包含角色动作或系统展示结果，就不得跳过；
5. 异常路径不得停在提示或通知，原文明示恢复、回流、人工处理或终止时必须完整表达。

门禁发现漏项时，只补该路径的节点、关系和流程映射，不得重新读取 Markdown、重新分析已完成路径或重建整份模型。

## 3. 写入最小语义草稿

创建固定目录 `spark-output/solution-swimlane/.work/`，完整读取
[semantic-model-schema.md](references/semantic-model-schema.md)，将结果一次写入
`spark-output/solution-swimlane/.work/semantic-draft.json`。

硬规则：

- 使用草稿版本 `1.1`。
- 只写草稿契约定义的业务语义字段。
- 不得写 `source_refs`。
- 不得在节点、关系中写 `flow_ids`，不得在流程中写 `node_ids` 或 `default_visible`。
- 流程只写按实际行进顺序排列的 `edge_ids`。
- 节点 `summary` 没有补充信息时省略，由脚本逐字复制 `label`。
- 已确认节点和关系省略 `certainty`；只有不确定元素显式写 `certainty: "uncertain"`。
- 不得出现 `coverage_manifest`、`coverage_rules`、`source_inventory`、`source_item_ids` 或 `source_selectors`。
- 端点或恢复方式不明确时使用 `certainty: "uncertain"` 并补充待确认项；不得猜测。
- 相同语义使用稳定、简短的英文小写连字符 ID。

草稿完成后只执行一次以下检查，修正发现的确定性缺项后立即进入规范化，不得继续业务讨论：

1. 每个 `edge.label` 是非空字符串；
2. 每个 P/S/E 编号在覆盖清单中恰好出现一次；
3. 每条“已制图”路径引用的 `flow.id` 存在；
4. 每条流程至少包含一条关系；
5. 每条关系的 `from`、`to` 节点存在；
6. 每条 `open_questions` 均通过第 2.4 节的结构影响门禁。

## 4. 规范化并校验模型

先执行：

```text
node <skill-root>/scripts/normalize-semantic-model.js --draft spark-output/solution-swimlane/.work/semantic-draft.json --out spark-output/solution-swimlane/.work/semantic-model.json
```

规范化脚本负责补全 `summary`、`source_refs: []`、`certainty`、`node_ids`、`flow_ids` 和 `default_visible`。Agent 不得手工补全这些机械字段。

再执行：

```text
node <skill-root>/scripts/validate-semantic-model.js --model spark-output/solution-swimlane/.work/semantic-model.json --report spark-output/solution-swimlane/.work/validation.json
```

首次规范化或校验失败时一次读取全部错误，只允许修正一次草稿结构并重新规范化、校验。若仍失败，保留 `.work`、报告错误并停止，不覆盖已有 HTML。

## 5. 渲染并校验 HTML

执行：

```text
node <skill-root>/scripts/render-solution-swimlane.js --model spark-output/solution-swimlane/.work/semantic-model.json --template <skill-root>/assets/solution-swimlane.template.html --out spark-output/solution-swimlane/solution_swimlane.html
```

随后执行：

```text
node <skill-root>/scripts/validate-semantic-model.js --model spark-output/solution-swimlane/.work/semantic-model.json --html spark-output/solution-swimlane/solution_swimlane.html --report spark-output/solution-swimlane/.work/validation.json
```

渲染器必须负责布局、连线、流程切换、缩放、打印和 SVG 导出。Agent 不得手写 HTML 或 SVG。

## 6. 视觉检查

默认跳过本节。只有用户明确要求“浏览器检查”时，才读取
[visual-rules.md](references/visual-rules.md) 并检查一次：

- 泳道、节点、标签和箭头可读；
- 连线不穿过节点正文；
- 主、次、异常流程可以切换；
- `pending` 与不确定关系可辨认；
- 长中文不截断；
- 缩放、打印和 SVG 导出可用。

浏览器不可用时报告“未执行视觉检查”并结束，不得启动本地服务器替代。视觉问题只允许修正一次渲染实现或样式，不得改变已校验的业务语义。

## 完成

只有模型校验和 HTML 校验均通过，才逐个删除 `.work` 中的
`semantic-draft.json`、`semantic-model.json`、`validation.json`，再删除空的 `.work` 目录。禁止递归删除
`spark-output/solution-swimlane/`。清理后确认正式 HTML 存在，再报告完成并返回：

```text
spark-output/solution-swimlane/solution_swimlane.html
```

## 资源

- `references/semantic-model-schema.md`：语义模型 2.0 完整字段契约。
- `references/visual-rules.md`：HTML/SVG 布局与交互规则。
- `scripts/normalize-semantic-model.js`：最小草稿校验与机械字段补全。
- `scripts/validate-semantic-model.js`：模型与 HTML 轻量校验。
- `scripts/render-solution-swimlane.js`：确定性布局与单文件 HTML 渲染。
- `scripts/test-solution-swimlane.js`：语义模型和渲染回归测试。
