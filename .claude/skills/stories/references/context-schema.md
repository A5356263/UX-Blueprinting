# Stories Context JSON Schema

## 1. 定位

- 正式产物：`spark-output/context/stories.json`
- `skill`：固定为 `stories`
- `version`：固定为 `3.0`
- 人类阅读面：`spark-output/stories.md`

`stories.md` 与 `stories.json` 是同一轮用户故事结论的两个面向：

- Markdown 承载完整任务叙述、章节组织和阅读上下文。
- JSON 承载下游 Skill 直接消费的完整结构化 Story 语义。
- JSON 不是标题索引、Markdown 全文镜像或第二次 Story 分析。
- 两者语义必须一致；JSON 不得新增 Markdown 没有的 Story、优先级、完成标准、设计触点、假设或问题。

## 2. 生成红线

1. JSON 阶段只读取已完成并通过自检的 `stories.md`。
2. 禁止回读上游、原始输入、知识库或会话上下文补充、纠正或重判 Markdown。
3. 只允许按目标字段拆分、结构化改写和不改变原意的简写，禁止拼接成新结论。
4. Markdown 没有明确内容时，单值写 `unknown`，集合写 `[]`。
5. 只有 Markdown 明确标记的假设和待确认问题才能进入对应字段。
6. 禁止使用“略”“同上”“见正文”等占位。
7. 不输出章节映射、Story 引用关系、中间 JSON 或下游专用字段。

## 3. 固定结构

只允许以下字段和层级：

```json
{
  "skill": "stories",
  "version": "3.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/stories.md",
  "source_refs": [],
  "source_mode": "unknown",
  "direction_summary": "unknown",
  "stories": [
    {
      "title": "unknown",
      "granularity": "unknown",
      "persona": "unknown",
      "scenario": "unknown",
      "goal": "unknown",
      "priority": "unknown",
      "source_basis": [],
      "user_story": "unknown",
      "acceptance_criteria": [],
      "design_touchpoints": {
        "pages_or_scenarios": [],
        "component_types": [],
        "states": [],
        "interaction_patterns": []
      },
      "risks_or_validation": [],
      "critical_assumptions": []
    }
  ],
  "out_of_scope": [],
  "open_questions": []
}
```

`stories[]` 不得为空。对象必须保留全部键；数组允许为空，不得生成虚假占位对象。

## 4. 字段写入规则

通用规则：

1. `skill`、`version`、`artifact_md` 按模板固定；`generated_at` 写实际时间或 `unknown`；`project_name`、`source_refs`、`source_mode` 只写 Markdown 已确认内容。
2. `direction_summary` 只承接 `1. 来源与方向` 的正式方向结论，不复制完整论证。
3. 每个业务值必须能指回 Markdown 的明确原意；不得合并不同 Story、完成标准、触点、风险或假设。
4. 保持原结论的确定性；已确认、假设和待确认不得互相转换。
5. 使用简短结构化表述，但不得省略会改变语义的角色、场景、目标、触发条件、数量阈值、适用范围和禁止边界。

### Story 完整覆盖

1. `2. Story 索引` 中的每个 Story 必须按原顺序在 `stories[]` 中出现一次，不得遗漏、重复或新增。
2. `title`、`granularity`、`priority` 与索引保持一致；`persona`、`scenario`、`goal`、`source_basis`、`user_story`、`acceptance_criteria`、`design_touchpoints`、`risks_or_validation` 只承接同一 Story 的正文。
3. Markdown 只有 Story 索引、没有对应详情时，仍保留该 Story 对象；未提供字段写 `unknown` 或 `[]`，不得自行展开详情。
4. `acceptance_criteria[]` 逐项承接全部明确完成标准，不得只选代表项，也不得把待确认问题改写为完成标准。
5. `design_touchpoints` 按页面或场景、组件类型、状态、交互模式分别承接；不得跨类补推或压成自由文本。
6. `critical_assumptions[]` 只接受 Markdown 以“关键假设”或 `critical_assumption` 明确标记的独立条目；没有时必须写 `[]`。禁止把来源依据、成立条件、风险或合理推测改写为假设。
7. `out_of_scope[]` 逐项承接 `4. 不进入 Story 的内容`；`open_questions[]` 逐项承接 `5. 待确认问题`，不得互相转换。

## 5. 明确不进入 JSON

- Story ID、章节锚点、字段与 Markdown 的映射关系。
- Story 标题清单、P0 标题清单、角色清单等可由 `stories[]` 直接读取的重复索引。
- 上游完整论证、知识消费记录、自检结果和运行日志。
- 页面布局、具体文案、旅程阶段、情绪曲线和流失风险。
- 为下游生成的额外关系、排序表或中间模型。

## 6. 下游读取约定

- 下游可将结构完整的 Stories `3.0` JSON 作为正式机器输入。
- JSON 字段为 `unknown`、`[]`，与 Markdown 明显冲突，或需要审计完整任务叙述时，再回读 `stories.md`。
- JSON 缺失的信息不得从会话上下文补齐。
- JSON 与 Markdown 冲突时停止使用冲突字段，回读 Markdown 核对并报告交接错误；不得自行选择或重判。
- 旧 `2.0` JSON 只提供标题级索引，不能替代 Stories Markdown。

## 7. 校验

```bash
node .claude/skills/stories/scripts/validate-context.js spark-output/context/stories.json
```

校验失败时只修 JSON 并重跑；不得反向修改已冻结的 Markdown。
