# UXB Context JSON Schema

## 1. 定位

- 正式产物：`spark-output/context/uxb.json`
- `skill`：固定为 `uxb`
- `version`：固定为 `5.0`
- 人类阅读面：`spark-output/uxb_output.md`

`uxb_output.md` 与 `uxb.json` 是同一轮已冻结 UXB 定案结论的两个面向：

- Markdown 承载完整论证、背景、业务解释和章节衔接。
- JSON 承载下游 Skill 直接消费的结构化结论。
- JSON 不是摘要、索引、Markdown 全文镜像或第二次分析。
- 两者语义必须一致；JSON 不得新增 Markdown 没有的事实、边界、规则、状态、异常或处理方式。

## 2. 生成红线

1. JSON 阶段只读取已冻结且已通过自检的 `uxb_output.md`。
2. 禁止回读原始需求、知识库或会话上下文补充、纠正或重判 Markdown。
3. 只允许结构化改写和不改变原意的简写，禁止为了填满字段进行推导。
4. Markdown 没有明确内容时，单值写 `unknown`，集合写 `[]`，未决事项进入 `open_questions[]`。
5. 禁止使用“略”“同上”“见正文”等占位。
6. `§9` 或 `[GAP]` 中的事项不得改写为确定规则、状态、异常或处理结果。
7. 不输出字段与 Markdown 章节的映射、ID、引用表或中间 JSON。

## 3. 固定结构

只允许以下字段和层级：

```json
{
  "skill": "uxb",
  "version": "5.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/uxb_output.md",
  "source_refs": [],
  "key_design_judgments": [
    {
      "judgment": "unknown",
      "impact": "unknown",
      "recommended_approach": "unknown",
      "not_recommended": "unknown",
      "open_question": "unknown"
    }
  ],
  "input_summary": {
    "raw_request": "unknown",
    "confirmed_facts": [],
    "explicit_constraints": [],
    "missing_information": []
  },
  "business_scenario_judgment": {
    "scenario": "unknown",
    "role": "unknown",
    "task": "unknown",
    "value": "unknown"
  },
  "viability_judgment": {
    "is_valid": "unknown",
    "reason": "unknown",
    "blocking_issues": [],
    "assumptions": []
  },
  "business_boundary": {
    "in_scope": [],
    "out_of_scope": [],
    "boundary_reason": []
  },
  "roles": [
    {
      "name": "unknown",
      "type": "unknown",
      "responsibility": "unknown",
      "needs": []
    }
  ],
  "features": [
    {
      "name": "unknown",
      "input": "unknown",
      "process": "unknown",
      "output": "unknown",
      "result": "unknown",
      "boundary": "unknown"
    }
  ],
  "business_rules": [
    {
      "rule": "unknown",
      "trigger": "unknown",
      "result": "unknown",
      "fallback": "unknown"
    }
  ],
  "states": [
    {
      "state": "unknown",
      "meaning": "unknown",
      "system_result": "unknown",
      "user_next_step": "unknown"
    }
  ],
  "exceptions": [
    {
      "exception": "unknown",
      "trigger": "unknown",
      "handling": "unknown",
      "recovery": "unknown"
    }
  ],
  "experience_handoff_requirements": [
    {
      "requirement": "unknown",
      "business_judgment": "unknown",
      "experience_impact": "unknown",
      "must_address": [],
      "do_not_rejudge": []
    }
  ],
  "constraints": {
    "hard_constraints": [],
    "dependencies": [],
    "do_not_do": [],
    "safety_or_business_boundaries": []
  },
  "open_questions": [
    {
      "question": "unknown",
      "impact": "unknown",
      "owner": "unknown",
      "level": "unknown"
    }
  ]
}
```

数组允许为空；不得为通过校验而生成虚假占位对象。

## 4. 字段写入规则

通用规则：

1. `skill`、`version`、`artifact_md` 按模板固定；`generated_at` 写实际时间或 `unknown`；`project_name` 和 `source_refs` 只写已确认名称与真实输入路径。
2. 每个业务值必须能指回 Markdown 的明确原意；允许按目标字段拆分和简写，但不得把多个分散表述拼成 Markdown 中不存在的新结论。
3. 对象必须保留模板中的全部键；数组按独立结论逐项填写，不合并不同角色、功能、规则、状态、异常或承接要求，也不生成虚假占位对象。
4. 保持原结论的确定性：已确认、假设和待确认不得互相转换；字段没有明确内容时，单值写 `unknown`、集合写 `[]`，只有 `§9` 或显式 `[GAP]` 才能进入 `open_questions[]`。
5. 使用简短结构化表述，但不得省略会改变语义的角色、触发条件、数量阈值、处理结果、适用范围和禁止边界。

高风险字段：

- `key_design_judgments[]` 只承接 `§0` 已冻结的判断、影响、推荐、不建议和待确认，不新增体验方案。
- `viability_judgment` 保留 Markdown 已有成立口径、原因和阻断；只有 Markdown 以“假设”或“前提”明确列出的独立条目才能进入 `assumptions[]`，没有时必须写 `[]`。禁止把依赖项、成立条件、方案判断或合理推测改写为假设。
- `features[]` 必须保留输入、处理、输出、结果和边界；未明确的字段写 `unknown`，不得推导后端机制。
- `business_rules[]`、`states[]`、`exceptions[]` 分开填写；兜底、处理或恢复未明确时写 `unknown`，不得互相补推或自行创建待确认问题。
- `experience_handoff_requirements[]` 只承接 `§7`；`must_address` 与 `do_not_rejudge` 保持数组并逐项保留，不得压成一句话或提前生成蓝图方案。
- `open_questions[]` 保留问题、影响、确认方和层级，不得在 JSON 中作答；层级未标明时写 `unknown`。

### 显式结构覆盖

`open_questions[]` 按以下顺序核对：

1. 先承接 `§9 待确认问题`。
2. 再逐项核对冻结 Markdown 全文中显式标记的 `[GAP]`。
3. `[GAP]` 与 `§9` 的讨论对象和待确认决策均相同时，不重复写入；不得仅因内容相关就合并。
4. 未被 `§9` 覆盖的 `[GAP]` 必须写入 `open_questions[]`。
5. 只使用 Markdown 已明确写出的内容；`impact`、`owner`、`level` 未明确时写 `unknown`。

禁止把未标记为 `[GAP]` 的风险、假设、建议或判断错误影响转成问题，禁止在 JSON 中回答 `[GAP]`，也不得为补齐字段回读原始需求或自行推导。

`constraints` 只从以下明确列表逐项承接：

| JSON 字段 | 允许来源 |
|---|---|
| `hard_constraints[]` | `§1`、`§8` 中以“明确约束”“硬约束”等标题或标签列出的独立条目，包括其中明确表达“禁止”“不可”的事项 |
| `dependencies[]` | `§8` 中以“依赖项”等标题或标签列出的独立条目 |
| `do_not_do[]` | `§4`、`§8` 中以“不做什么”“不新增”“不改变”等标题、标签或条目前缀列出的独立条目 |
| `safety_or_business_boundaries[]` | `§8` 中以“安全边界”“业务边界”等标题或标签明确列出的独立条目 |

只有出现在上述明确结构中的独立条目才能写入；相同条目只保留一项，不得合并不同结论，并保留会改变语义的对象、条件和否定词。对应结构没有明确内容时使用 `[]`；没有明确安全或业务边界时，`safety_or_business_boundaries[]` 必须为 `[]`。禁止从 `§2 最大不确定性`、`§3 系统代价`、推荐能力形态、体验建议或普通正文推导约束，也不得把“建议、不建议、可能、风险”改写为“必须、不可、不做”。

## 5. 明确不进入 JSON

- `read_sections`、`knowledge_trace` 及其他知识消费明细。
- 长篇背景、成立性论证和章节衔接文字。
- Markdown 目录、章节锚点和逐章映射。
- 自检结果、Handoff 推荐和页面事实交接。
- Preview、进度状态、Git 信息和运行日志。
- 页面、泳道、图节点、关系边、坐标和覆盖清单。
- 为一致性校验产生的 ID、引用、映射表或中间模型。

## 6. 下游读取约定

- 下游默认读取本 JSON 建立 UXB 正式机器上下文。
- JSON 字段为 `unknown`、`[]`，与 Markdown 明显冲突，或下游需要审计完整论证时，才回读 `uxb_output.md`。
- JSON 缺失的信息不得从会话上下文补齐。
- JSON 与 Markdown 冲突时停止使用冲突字段，回读 Markdown 核对并报告交接错误；不得自行选择或重判。

## 7. 校验

写盘后必须运行：

```bash
node .claude/skills/uxb/scripts/validate-context.js spark-output/context/uxb.json
```

退出码非 `0` 时只修正 JSON 结构并重跑；不得反向修改已冻结的 Markdown。校验未通过不得进入 Handoff。
