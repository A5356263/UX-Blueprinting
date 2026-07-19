# Context JSON 与 Solution Swimlane 优化实施计划

## 0. 文档定位

本文是本轮优化的唯一实施计划，面向后续执行 Agent。

执行 Agent 必须按本文规定的范围、顺序和验收门禁实施，不得把“减少 JSON 输出成本”理解为删减业务语义，也不得借本轮优化重写无关 Skill。

本计划基于两类证据形成：

1. `bench/8` 中代表性 Skill 的产物分层方式。
2. 当前项目的真实 Skill、正式产物、执行日志和下游读取关系。

核心判断：

- Markdown 或 HTML 承载完整的人类可读结果。
- Context JSON 只承载下游必须稳定读取的结构。
- 生成器内部 JSON 只作为临时编译模型，不冒充正式业务产物。
- JSON 是否精简，由真实消费者决定，不按统一字段数量强行裁剪。

---

## 1. 最终目标

本轮只完成两项主体优化：

1. Context JSON 生成与 schema 管理优化。
2. `solution-swimlane` 生成成本与稳定性优化。

完成后应达到：

- 内网 LLM 不再重复生成大段与 Markdown 相同的解释性内容。
- 下游仍能稳定识别业务范围、角色、流程、状态、异常和恢复关系。
- `solution-swimlane` 不因 JSON 精简而减少节点、关系、流程或来源覆盖。
- Skill 主文件减少大段 schema 占用，但 Agent 不会跳过 schema。
- 所有正式 JSON 都有确定性校验，不依赖 Agent 自我判断“看起来正确”。
- 当前页面原型和泳道图的语义完整度不低于优化前。

---

## 2. 本轮范围

### 2.1 必须修改

#### JSON 生产与消费

- `.claude/skills/uxb/`
- `.claude/skills/journey-analysis/`
- `.claude/skills/experience-blueprint/`
- `.claude/skills/page-spec/`

#### 泳道生成

- `.claude/skills/solution-swimlane/`

#### 必要的跨 Skill 消费契约

- `experience-blueprint` 对 UXB JSON 的读取规则
- `page-spec` 对 Experience Blueprint JSON 的读取规则
- `solution-swimlane` 对 Experience Blueprint JSON 的读取与来源清单生成规则
- 只在确有字段解析时修改 `shared-workflow/`；仅检查文件存在时不得无理由修改

### 2.2 本轮明确不修改

- 不做会话上下文隔离。
- 不改变 Journey 的业务字段和分析颗粒度。
- 不改写 UXB、Journey、Experience Blueprint、Page Spec 的 Markdown 正文方法论。
- 不重做页面原型能力。
- 不把 Page Spec 改成按需输出。
- 不新增独立 SVG 正式产物。
- 不输出 Solution Swimlane Markdown。
- 不输出 Solution Swimlane 正式业务 JSON。
- 不批量迁移所有其他 Skill 的 Context JSON。
- 不因本轮优化重构 `board`、`edge`、`stories`、`problem-framing`、`product-analysis` 等无关 Skill。
- 不覆盖或改写当前 `spark-output/` 中的基线产物，除非进入最终回归测试且用户明确允许重新生成。

### 2.3 关于“所有 schema 是否都迁出”的决定

建立全项目规范：

> 凡正式输出 Context JSON 的 Skill，最终都应把详细 schema 放入 Skill 自己的 `references/`，并通过确定性脚本校验。

但不在本轮一次性迁移所有 Skill。

本轮迁移：

- `uxb`
- `journey-analysis`
- `experience-blueprint`
- `page-spec`

原因：

- 这四个 Skill 位于当前正式主链。
- 三个需要同步精简 JSON。
- Journey 虽不精简字段，但迁出 schema 后可验证统一方案不会破坏完整模型。
- 其他 Skill 未完成消费者审计，批量迁移会扩大回归范围。

后续其他 Skill 按同一规范逐个迁移，不得仅为目录形式统一而一次性修改。

### 2.4 文件级改动矩阵

执行 Agent 必须以本表为文件范围基线。表中未列出的文件，只有在测试证明其直接消费了变更字段时才允许修改，并必须在最终交付中说明证据。

| Skill | 必改文件 | 新增文件 | 允许的改动 |
|---|---|---|---|
| `uxb` | `.claude/skills/uxb/SKILL.md` | `references/context-schema.md`、`scripts/validate-context.js`、`tests/fixtures/` | 移出 schema、增加强门禁、输出 v2 紧凑 JSON |
| `journey-analysis` | `.claude/skills/journey-analysis/SKILL.md`、`scripts/validate_context.js` | `references/context-schema.md`、`tests/fixtures/` | 移出 schema、增加强门禁；业务字段不得精简 |
| `experience-blueprint` | `.claude/skills/experience-blueprint/SKILL.md` | `references/context-schema.md`、`scripts/validate-context.js`、`tests/fixtures/` | 移出 schema、增加强门禁、输出 v2 紧凑 JSON |
| `page-spec` | `.claude/skills/page-spec/SKILL.md` | `references/context-schema.md`、`scripts/validate-context.js`、`tests/fixtures/` | 移出 schema、增加强门禁、输出 v2 索引 JSON |
| `solution-swimlane` | `SKILL.md`、`references/semantic-extraction.md`、`references/validation-rules.md`、`references/visual-rules.md`、`assets/solution-swimlane.template.html`、现有相关 scripts | `references/diagram-model-schema.md`、`scripts/prepare-semantic-input.js`、必要测试 fixture | 缩小 LLM 草稿、脚本物化覆盖、适配 Blueprint v1/v2、移除 SVG 导出 |

消费方修改边界：

- `journey-analysis/SKILL.md`：只修改 UXB v1/v2 字段读取映射，不改旅程分析方法。
- `experience-blueprint/SKILL.md`：只修改 UXB v1/v2 字段读取映射及自己的 JSON 输出。
- `page-spec/SKILL.md`：只修改 Blueprint v1/v2 读取和自己的 JSON 输出，不改页面规格正文结构。
- `solution-swimlane/scripts/build-source-inventory.js`：只修改 Blueprint v1/v2 解析和来源分层，不改变正式输入边界。
- `shared-workflow/generate-progress-preview.js`：如果仍只检查文件存在，不修改。
- `shared-workflow/skill-graph.json` 与 `shared-workflow/next-skill.md`：本轮不修改。

测试 fixture 统一放在各自 Skill 内，不放入 `spark-output/`：

```text
<skill-root>/tests/fixtures/context.valid.json
<skill-root>/tests/fixtures/context.invalid.missing-field.json
<skill-root>/tests/fixtures/context.invalid.extra-field.json
<skill-root>/tests/fixtures/context.invalid.reference.json
```

如果某类错误不适用于该 Skill，可不创建对应 fixture；但必须在测试文件中说明为什么不适用。

---

## 3. 当前基线与已验证事实

### 3.1 当前 JSON 规模

当前测试产物：

| 产物 | 当前大小 | 本轮处理 |
|---|---:|---|
| `spark-output/context/uxb.json` | 约 19.7 KB | 精简 |
| `spark-output/context/journey-analysis.json` | 约 10.6 KB | 结构不变，只迁 schema |
| `spark-output/context/experience-blueprint.json` | 约 26.8 KB | 精简 |
| `spark-output/context/page-spec.json` | 约 16.7 KB | 精简 |

文件大小只用于观察，不作为删除字段的首要依据。

### 3.2 Page Spec 的真实消费情况

当前执行日志显示：

```text
读取 spark-output/page_spec.md
生成 spark-output/子管理员复制_页面原型.html
```

当前页面原型生成没有读取 `page-spec.json`。

全仓当前也没有正式下游 Skill 逐字段消费 `page-spec.json`；进度面板只用文件存在性判断状态。

因此：

- `page_spec.md` 是当前页面生成的完整事实源。
- `page-spec.json` 应改为索引与覆盖检查模型。
- 不允许继续在 JSON 中完整复制结构图、文案池、流程和状态正文。

### 3.3 `bench/8` 提供的定位参考

- `prd`：完整内容在 Markdown，JSON 只保存章节摘要和范围。
- `brief`：完整可视产物与紧凑 Context JSON 分离。
- `journey`：下游需要逐阶段遍历，因此保留完整阶段结构。
- `stories`、`sitemap`：JSON 是可执行结构，保留必要业务对象。
- `flow-web`：正式代码包含完整细节，JSON 只保存流程、屏幕、组件和文件索引。
- `extract`：Token 本身就是机器数据，因此允许较重 JSON。

本项目采用相同思想，但不复制其模板代码。

---

## 4. Schema 外置规范

### 4.1 文件位置

每个本轮 Skill 新增自己的 schema 文件：

```text
.claude/skills/uxb/references/context-schema.md
.claude/skills/journey-analysis/references/context-schema.md
.claude/skills/experience-blueprint/references/context-schema.md
.claude/skills/page-spec/references/context-schema.md
```

每个文件必须包含：

1. schema 版本。
2. 完整 JSON 结构。
3. 字段说明。
4. 必填与可空规则。
5. 枚举值。
6. 字段来源。
7. 不允许出现的重复内容。
8. 正确示例。
9. 最小错误示例。
10. 对应校验命令。

不允许：

- 把 schema 放到多层嵌套目录。
- 让 `context-schema.md` 再跳转到第二个 schema 文件才能理解完整结构。
- 在 `SKILL.md` 和 schema 文件中维护两份完整 JSON 模板。
- 用“参考以下结构”“尽量遵守”之类弱约束。

### 4.2 `SKILL.md` 必须保留的硬提示

详细 schema 虽然迁出，但以下门禁必须直接留在每个 `SKILL.md` 中，且放在“Context JSON 写入”步骤之前：

```markdown
## ⛔ Context JSON 生成门禁

写入 Context JSON 前，必须完整读取：

`references/context-schema.md`

硬规则：

1. 未完整读取该文件，禁止开始生成 Context JSON。
2. 禁止凭记忆重建 schema，禁止沿用旧 JSON 结构。
3. 禁止从 Markdown 机械复制整段正文填充 JSON。
4. 只能写入 schema 明确允许的字段；不得新增、删除、改名或改变字段类型。
5. Markdown 必须先完成并通过本 Skill 自检，再从已确认内容映射 JSON。
6. 写盘后必须运行指定校验脚本。
7. 校验失败时必须修复并重跑；校验未通过不得进入 Handoff，不得宣告 Skill 完成。
8. schema 文件缺失或无法读取时，停止 JSON 生成并明确报告，禁止临时自创结构。
```

该提示不得被压缩成一句：

```text
按 references/context-schema.md 输出 JSON。
```

上面这种写法属于不合格实现，因为无法阻止 Agent 跳读、凭记忆重建或直接复制 Markdown。

### 4.3 校验脚本

每个本轮 Skill 必须有可直接运行的校验入口：

```text
.claude/skills/uxb/scripts/validate-context.js
.claude/skills/journey-analysis/scripts/validate_context.js
.claude/skills/experience-blueprint/scripts/validate-context.js
.claude/skills/page-spec/scripts/validate-context.js
```

Journey 保留现有脚本名，避免无必要的路径迁移。

校验至少覆盖：

- JSON 可解析。
- 根字段集合正确。
- 必填字段存在。
- 字段类型正确。
- 枚举值合法。
- ID 非空且唯一。
- 引用的 ID 存在。
- 不允许额外字段。
- 正式产物路径正确。
- 版本号正确。
- 对应完整结果不得使用空数组伪装完成。

只有 schema 文件而没有可执行校验，视为本轮任务未完成。

---

## 5. UXB JSON 优化

### 5.1 定位

`uxb_output.md` 是完整需求定案。

`uxb.json` 是面向 Journey、Experience Blueprint 等下游的业务交接模型，不是 UXB 正文镜像。

### 5.2 必须保留

- 元数据与 `artifact_md`
- 业务场景摘要
- 需求是否成立及关键前提
- 业务范围
- 角色与职责
- 功能闭环
  - 输入
  - 处理
  - 输出
  - 结果
  - 边界
- 业务规则
  - 触发条件
  - 结果
  - 不满足时处理
- 状态
  - 状态含义
  - 系统结果
  - 用户下一步
- 异常
  - 触发条件
  - 系统处理
  - 恢复方式
- 体验蓝图承接要求
- 约束
- 缺口与待确认问题

### 5.3 移出 JSON

- 原始需求长篇复述
- 完整成立性论证过程
- 与 Markdown 相同的关键判断长文
- 知识消费过程明细
- 非下游必需的推荐与不推荐论述
- 纯解释性段落

### 5.4 下游适配

必须检查并更新：

- `journey-analysis` 的 UXB 读取映射
- `experience-blueprint` 的 UXB 读取映射

下游不得要求从紧凑 JSON 恢复完整论证；需要叙述性判断时继续读取 `uxb_output.md`。

### 5.5 正确结果

- 下游不读 Markdown，也能恢复角色、范围、功能、规则、状态、异常和承接要求的结构骨架。
- 下游同时读取 Markdown 时，能获得完整判断依据。
- JSON 中没有大段重复 UXB 正文。

### 5.6 错误结果

- 只保留项目名和一句摘要。
- 删除状态、异常或恢复路径。
- 将功能压缩为功能名称列表。
- 把体验蓝图承接要求合并成一句泛化描述。
- 为了缩小文件而删除下游正在读取的字段。

---

## 6. Journey JSON 处理

### 6.1 决定

Journey 本轮不精简业务结构。

继续保留：

- 旅程主题
- readiness
- 阶段
- 行动
- 触点
- 痛点
- 情绪与信心
- 流失风险
- 机会
- 证据
- 关键转折
- 骨架降级结果
- 用户补充

### 6.2 本轮只做

- 把完整 JSON 模板迁移到 `references/context-schema.md`。
- 在 `SKILL.md` 中加入强制读取门禁。
- 让现有 `validate_context.js` 与外置 schema 的字段定义一致。
- 补充正确与错误 fixture。

### 6.3 禁止

- 不因“统一紧凑 JSON”而删除阶段详情。
- 不把证据、流失风险或机会只保留为统计数。
- 不改变当前 Full / Skeleton 降级逻辑。

---

## 7. Experience Blueprint JSON 优化

### 7.1 定位

`experience_blueprint.md` 是完整体验设计方案。

`experience-blueprint.json` 是下游结构索引，供：

- `page-spec` 定位流程、载体、状态和异常。
- `solution-swimlane` 建立来源索引。

它不直接承担泳道图 `lanes / nodes / edges` 模型生成。

### 7.2 必须保留

- 元数据、版本和来源
- 来源模式
- 关键设计判断的短结构
- 主流程
  - 稳定节点 ID
  - 节点名称
  - 用户动作
  - 系统反馈
  - 状态变化
  - 下一步
  - Markdown 来源锚点
- 次流程
  - 稳定流程 ID
  - 名称
  - 触发条件
  - 核心动作
  - 系统反馈
  - 下一步或结束方式
  - Markdown 来源锚点
- 异常
  - 稳定异常 ID
  - 发生时机
  - 触发条件
  - 系统反馈
  - 用户下一步
  - 恢复路径或明确终止
  - Markdown 来源锚点
- 页面、弹窗、抽屉的轻量索引
  - ID
  - 名称
  - 类型
  - 目标
  - 入口条件
  - Markdown 来源锚点
- 状态索引
- 待确认问题

### 7.3 移出 JSON

- 完整 ASCII 结构图
- 页面区域详细正文
- 按钮清单
- 长文案和提示文案
- 成功与失败反馈长描述
- 旅程消费长篇复述
- 知识消费过程
- 上游映射的重复解释
- 页面结构与 Markdown 完全相同的正文

### 7.4 不增加的负担

Experience Blueprint 不负责直接输出：

- 泳道
- 图节点
- 图关系
- 流程着色
- 坐标
- 连线
- coverage manifest

这些属于 `solution-swimlane` 的下游编译职责。

禁止为了方便泳道图，把体验蓝图 JSON 改造成第二份 `diagram-model.json`。

### 7.5 兼容策略

- 新输出版本升为 `2.0`。
- `page-spec` 与 `solution-swimlane` 在迁移期同时接受旧 `1.0` 和新 `2.0`。
- 新生产者只输出 `2.0`。
- 不自动重写当前已有 `experience-blueprint.json`。

---

## 8. Page Spec JSON 优化

### 8.1 定位

`page_spec.md` 是页面生成的唯一完整事实源。

`page-spec.json` 只负责：

- 生成范围索引
- 实体定位
- 实体关系
- Markdown 锚点
- 覆盖数量
- 未决问题
- Edge 消费追踪

### 8.2 固定输出规则

Page Spec 仍然每次固定输出：

```text
spark-output/page_spec.md
spark-output/context/page-spec.json
```

不得改成用户按需选择 JSON。

### 8.3 紧凑 JSON 必须保留

```json
{
  "skill": "page-spec",
  "version": "2.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/page_spec.md",
  "source_refs": [],
  "page_summary": {
    "product_domain": "unknown",
    "page_type": "unknown",
    "user_role": "unknown",
    "core_task": "unknown"
  },
  "generation_scope": {
    "generate": [],
    "reference_only": [],
    "do_not_generate": []
  },
  "entities": [
    {
      "entity_id": "unknown",
      "name": "unknown",
      "type": "unknown",
      "generate_mode": "generate",
      "md_anchor": "unknown"
    }
  ],
  "entity_relationships": [],
  "coverage": {
    "pages": 0,
    "entities": 0,
    "flows": 0,
    "validation_rules": 0,
    "states": 0,
    "exceptions": 0,
    "result_states": 0,
    "copy_items": 0,
    "template_variables": 0
  },
  "open_questions": [],
  "edge_consumed": false,
  "edge_trace": []
}
```

上述字段名是本轮锁定契约。执行 Agent 不得自行增删、改名或改变层级。

如实施时发现字段与现有消费者存在无法兼容的冲突，必须停止该阶段，列出：

1. 冲突字段。
2. 当前消费者路径。
3. 不兼容原因。
4. 最小调整方案。

未经用户确认不得修改本节契约。

### 8.4 从 JSON 删除

- `structure_ascii`
- 完整 `regions`
- 完整 `list_fields`
- 完整 `key_actions`
- 完整 `main_interaction_flow`
- 完整 `validation_rules`
- 完整 `states`
- 完整 `exception_recovery`
- 完整 `result_states`
- `copy_pool`
- 模板变量详细解释

这些内容继续完整保留在 `page_spec.md`。

### 8.5 页面生成约束

任何生成 HTML 页面原型的 Agent 必须：

1. 读取完整 `page_spec.md`。
2. 只把 `page-spec.json` 用于定位范围和执行覆盖检查。
3. 不得只读紧凑 JSON 直接生成页面。
4. 生成前对照 `coverage`，确认 MD 中对应项目未被漏读。

如果未来页面生成器希望只读 JSON，必须另行设计页面生成专用结构，不得静默扩大当前 Context JSON。

---

## 9. Solution Swimlane 优化

### 9.1 正式输入与输出

正式输入保持：

```text
spark-output/experience_blueprint.md
spark-output/context/experience-blueprint.json
```

正式输出只保留：

```text
spark-output/solution-swimlane/solution_swimlane.html
```

不新增：

- 正式 Markdown
- 正式 `diagram-model.json`
- 独立 SVG 文件

HTML 继续使用内联 SVG 作为绘图技术。

移除：

- 工具栏中的“导出 SVG”
- 对“导出 SVG 控件存在”的校验要求
- 独立 SVG 导出函数和相关无用代码

保留打印能力。

### 9.2 当前问题

当前泳道图质量合格，但中小需求仍需要较长生成时间。

主要负担不是 HTML 渲染，而是：

- LLM 需要处理过多原始来源项。
- LLM 需要生成较大的覆盖映射。
- 草稿中存在可由脚本确定的重复来源处置。
- 完整来源覆盖与图语义模型混在同一次生成中。

### 9.3 优化后的内部流水线

```text
完整蓝图 MD + 紧凑蓝图 JSON
→ 完整 source-inventory
→ 确定性语义候选预处理
→ LLM 只生成 lanes / nodes / edges / flows
→ 脚本物化全部覆盖
→ 模型校验
→ HTML 渲染
→ DOM 与几何校验
```

### 9.4 完整来源清单仍必须保留

不得删除 `source-inventory.json` 的全量审计能力。

优化方式不是少枚举来源，而是把来源分层：

- `diagram_candidates`
  - 角色
  - 角色任务
  - 系统处理
  - 改变走向的条件
  - 主流程关系
  - 次流程触发与回接
  - 异常发生、处理和恢复
- `auto_detail`
  - 页面布局
  - 字段说明
  - 示例文案
  - 不改变流程的反馈细节
- `auto_excluded`
  - 视觉草图
  - 重复容器
  - 纯分析说明
  - 非语义元数据

完整 inventory 继续参与最终对账。

LLM 只消费 `diagram_candidates` 和必要上下文；`auto_detail`、`auto_excluded` 由脚本按稳定规则物化覆盖记录。

### 9.5 新增确定性预处理

新增：

```text
.claude/skills/solution-swimlane/scripts/prepare-semantic-input.js
```

职责：

1. 读取完整 `source-inventory.json`。
2. 按稳定来源路径和内容类型分类。
3. 输出 `<temp-dir>/semantic-input.json`。
4. 为可确定的详情与排除项生成 `auto_coverage_rules[]`。
5. 不判断具体业务关系端点。
6. 不自动合并语义不同的节点。

禁止脚本根据关键词猜测：

- 谁审批
- 谁发起
- 哪个异常回到哪个节点
- 哪两个任务是同一任务

这些仍由正式蓝图证据与语义抽取决定。

### 9.6 LLM 草稿最小结构

LLM 只生成：

- `lanes`
- `nodes`
- `edges`
- `flows`
- `open_questions`
- 图元素对应的 `source_selectors`

LLM 不生成：

- 完整 `coverage_manifest`
- 每个页面字段的排除说明
- 每条文案的重复处置
- 像素坐标
- DOM
- SVG path
- 几何验证报告

### 9.7 内部模型 schema 外置

将 `semantic-extraction.md` 中的大段 `diagram-model` JSON 模板迁出到：

```text
.claude/skills/solution-swimlane/references/diagram-model-schema.md
```

`solution-swimlane/SKILL.md` 必须加入同等级硬门禁：

```markdown
生成 `diagram-draft.json` 前，必须完整读取：

- `references/semantic-extraction.md`
- `references/diagram-model-schema.md`
- `references/validation-rules.md`

未完整读取任一文件，禁止生成模型。
禁止凭记忆重建字段，禁止自行删除 lanes、nodes、edges、flows 或来源选择器。
```

### 9.8 语义完整性红线

优化不得减少：

- 正式角色或系统处理方
- 主流程任务
- 系统处理节点
- 条件分支
- 次流程
- 异常流程
- 异常恢复或终止
- 状态变化形成的业务关系
- 明确回流关系

不得设定“最多几十个节点”或“最多几十条关系”。

图元素数量由正式蓝图决定，不由性能目标决定。

### 9.9 视觉能力必须保持

- 严格横向泳道。
- “全部”位于流程选择区首位。
- 默认高亮主流程。
- 主流程、次流程、异常流程使用明显不同的卡片和连线颜色。
- 聚焦流程时非当前节点、连线和标签保持低透明度。
- 聚焦流程不放大可见线宽。
- 共同端点关系允许复用共同线段。
- 无共同端点关系不得共享无法辨认的长线段。
- 标签不得遮挡节点正文或其他标签。
- 回流使用底部独立路由区。
- 回流增多时自动增加画布高度和安全边距。
- 工具栏在文档流中占据真实高度。
- 1920×1080 下优先展示更多有效信息。
- 缩放、适应、重置、信息抽屉、打印和收起能力保留。

---

## 10. 实施顺序

必须按以下顺序执行，不得并行修改生产者和消费者后跳过中间验证。

### 阶段 0：冻结基线

1. 记录当前四份 Context JSON 的字段树和大小。
2. 记录当前页面原型生成只读取 `page_spec.md` 的事实。
3. 从当前泳道 HTML 提取：
   - lane ID 集合
   - node ID 集合
   - edge ID 集合
   - flow ID 集合
   - 节点标签
   - 关系端点和标签
4. 保存为回归期望，不修改正式业务产物。

验证：

- 基线数据可由脚本重复读取。
- 不是只记录数量，必须记录完整 ID 与关系集合。

### 阶段 1：只迁移 schema，不改变 JSON 输出

1. 为四个主链 Skill 新建 `references/context-schema.md`。
2. 把现有完整 schema 原样迁入。
3. 在 `SKILL.md` 加入强制门禁。
4. 补齐校验脚本。
5. 用当前正式 JSON 验证。

验证：

- 迁移前后 JSON 字段和内容不变。
- SKILL 中不再保留完整 JSON 模板。
- schema 缺失时测试必须失败。
- 校验失败时 Handoff 门禁生效。

### 阶段 2：优化 UXB JSON

1. 定义 UXB `2.0` 紧凑 schema。
2. 修改 UXB 生成规则。
3. 更新 Journey 和 Experience Blueprint 的消费映射。
4. 增加 v1/v2 兼容读取测试。
5. 运行当前 UXB 基线回归。

验证：

- 角色、范围、功能、规则、状态、异常、承接要求集合不减少。
- JSON 不再包含长篇分析正文。

### 阶段 3：优化 Experience Blueprint JSON

1. 定义 Blueprint `2.0` 紧凑 schema。
2. 移除页面详细结构和重复解释。
3. 保留流程、异常、状态、载体索引与 Markdown 锚点。
4. 更新 Page Spec 和 Solution Swimlane 的 v1/v2 读取。
5. 更新 source inventory 解析。

验证：

- 主流程、次流程、异常和恢复关系不减少。
- Page Spec 可从 MD 恢复完整页面规格。
- Solution Swimlane 能构建与基线相同的语义集合。

### 阶段 4：优化 Page Spec JSON

1. 定义 Page Spec `2.0` 索引 schema。
2. 将完整页面内容留在 MD。
3. 生成覆盖统计。
4. 修改 Page Spec 的校验规则。
5. 明确页面原型生成必须读取 MD。

验证：

- 当前页面原型基于同一 MD 重新生成时，信息完整度不下降。
- JSON 覆盖统计与 MD 实际数量一致。
- JSON 不包含完整文案池和 ASCII。

### 阶段 5：优化 Solution Swimlane

1. 新增语义候选预处理脚本。
2. 缩小 LLM 草稿范围。
3. 外置内部 diagram model schema。
4. 更新 coverage materialization。
5. 更新 validator。
6. 移除独立 SVG 导出功能与对应验证。
7. 保持现有视觉能力。

验证：

- 完整来源仍全部有唯一处置。
- LLM 不再生成完整覆盖清单。
- 模型和 HTML 校验全部通过。
- 与基线的 lane/node/edge/flow 语义集合一致。

### 阶段 6：全链回归

执行：

```text
UXB
→ Journey
→ Experience Blueprint
→ Page Spec
→ HTML 页面原型
→ Solution Swimlane
```

验证每个节点：

- 正式产物存在。
- JSON 校验通过。
- 下游成功读取。
- 没有新增 `unknown` 掩盖字段丢失。
- 没有因 schema 版本变化进入错误降级模式。

---

## 11. 测试设计

### 11.1 Schema 正向测试

每个 Skill 至少提供一个最小合法 fixture：

- 所有必填字段存在。
- ID 唯一。
- 引用有效。
- 可空字段使用合法空值。

### 11.2 Schema 反向测试

每个 Skill 至少覆盖：

- 缺根字段
- 多余字段
- 错误类型
- 非法枚举
- 重复 ID
- 引用不存在
- 完整结果使用空核心数组
- 版本错误
- 正式产物路径错误

### 11.3 消费兼容测试

必须覆盖：

- UXB v1 → Experience Blueprint
- UXB v2 → Experience Blueprint
- Blueprint v1 → Page Spec
- Blueprint v2 → Page Spec
- Blueprint v1 → Solution Swimlane
- Blueprint v2 → Solution Swimlane

### 11.4 语义集合回归

不能只比较计数。

必须比较：

```text
lane IDs + names
node IDs + labels + lane IDs
edge IDs + from + to + labels + types
flow IDs + node IDs + edge IDs + flow types
exception recovery targets
```

任一集合减少或关系端点改变，测试失败。

### 11.5 页面完整度回归

至少检查：

- 本次新增与修改功能全部存在。
- 页面、弹窗、抽屉范围正确。
- 关键交互可执行。
- 常规状态存在。
- 本次新增与修改功能的规则和异常有表达。
- 不要求前端原型模拟依赖真实后端数据的完整状态。

### 11.6 性能观察

记录优化前后：

- JSON 文件大小
- JSON 字符串值数量
- 与 Markdown 完全重复的字符串比例
- Solution Swimlane 草稿输入项数量
- LLM 生成的 JSON 行数
- 内网实际执行时间，由用户环境最终验证

性能目标是明显减少重复输出，不设置会迫使删除业务语义的硬字节上限。

如果体积下降与语义完整冲突，以语义完整为优先。

---

## 12. 完成标准

只有全部满足才能宣布本轮优化完成：

### Schema

- [ ] 四个主链 Skill 的详细 schema 已移至独立文件。
- [ ] 四个 `SKILL.md` 都保留强制读取与校验门禁。
- [ ] schema 文件丢失时不会凭记忆继续生成。
- [ ] 每个正式 JSON 都有可执行校验。

### JSON

- [ ] UXB JSON 已紧凑化且业务交接语义不丢失。
- [ ] Journey JSON 结构未被精简。
- [ ] Blueprint JSON 已紧凑化且流程、异常、状态、载体索引完整。
- [ ] Page Spec JSON 已变为索引与覆盖模型。
- [ ] Page Spec 仍固定输出 MD + JSON。
- [ ] 所有改动过的生产者输出版本明确。
- [ ] 所有真实消费者支持迁移期版本。

### Solution Swimlane

- [ ] 正式产物仍只有单文件 HTML。
- [ ] 内联 SVG 保留。
- [ ] 独立 SVG 导出功能已移除。
- [ ] 内部 JSON 只写临时目录。
- [ ] LLM 不再生成完整覆盖清单。
- [ ] 完整 source inventory 仍参与最终对账。
- [ ] 模型校验与 HTML 校验通过。
- [ ] 角色、节点、关系、流程、异常恢复集合与基线一致。
- [ ] 现有流程聚焦、颜色区分、紧凑布局和回流空间能力未退化。

### 回归

- [ ] 当前测试需求全链执行成功。
- [ ] 页面原型的信息完整度不低于优化前。
- [ ] 泳道图没有少节点、少关系、少流程。
- [ ] 无消费者因字段变化读取失败。
- [ ] 未修改本轮范围外的 Skill。

---

## 13. 什么是好的实现

好的实现具备以下特征：

- JSON 变小是因为删除重复叙述，不是删除业务对象。
- MD 和 JSON 职责清楚，不再维护两份完整正文。
- Agent 在写 JSON 前必须读 schema，写完必须跑脚本。
- 下游明确知道何时读 JSON、何时回到 MD。
- `solution-swimlane` 的 LLM 只处理必须进行语义判断的部分。
- 全量来源由脚本审计，任何遗漏都能被发现。
- schema 升级有版本、有兼容期、有回归测试。
- 所有修改都能追溯到本计划的目标。

---

## 14. 什么是错误的实现

以下任一行为都视为失败：

- 把 JSON 精简成项目名、摘要和文件路径。
- 删除角色、规则、状态、异常、恢复路径或流程关系。
- 为了让泳道更快而设置固定节点上限。
- 让 Experience Blueprint 直接生成泳道 lanes/nodes/edges。
- Page Spec JSON 精简后，页面生成 Agent 改成只读 JSON。
- 把 schema 移出后，只在 SKILL 中写一句弱提示。
- schema 文件缺失时凭记忆继续输出。
- 只有 schema 文档，没有确定性校验脚本。
- 只比较优化前后的节点数量，不比较关系端点和语义。
- 将内部临时 JSON 写入 `spark-output/` 作为正式产物。
- 继续保留独立 SVG 导出，却声称已经取消 SVG 成本。
- 为统一目录结构而批量修改所有无关 Skill。
- 顺手重构当前已工作的页面原型或 shared-workflow。

---

## 15. 实施结束后的交付清单

执行 Agent 最终必须交付：

1. 修改文件清单。
2. 四份外置 Context schema。
3. 四个 Context JSON 校验入口。
4. 三份紧凑 JSON 契约说明：
   - UXB
   - Experience Blueprint
   - Page Spec
5. Solution Swimlane 新内部流水线说明。
6. 正向与反向测试结果。
7. v1/v2 消费兼容测试结果。
8. 当前测试需求的语义集合回归结果。
9. 优化前后 JSON 规模与重复度对比。
10. 未验证项与需要在内网补测的实际耗时。

不得只报告“已精简”“已通过”，必须给出可复验的文件路径、命令和集合对账结果。
