# Journey Analysis Context JSON Schema

## 1. 定位

- 正式产物：`spark-output/context/journey-analysis.json`
- `skill`：固定为 `journey-analysis`
- `version`：固定为 `3.0`
- 人类阅读面：`spark-output/journey_analysis.md`

`journey_analysis.md` 与 `journey-analysis.json` 是同一轮旅程分析结论的两个面向：

- Markdown 承载完整旅程叙述、章节组织和阅读上下文。
- JSON 承载下游 Skill 直接消费的完整结构化旅程语义。
- JSON 不是摘要索引、Markdown 全文镜像或第二次旅程分析。
- 两者语义必须一致；JSON 不得新增 Markdown 没有的角色、阶段、转折、痛点、风险、机会、来源或缺口。

## 2. 生成红线

1. JSON 阶段只读取已完成并通过自检的 `journey_analysis.md`。
2. 禁止回读上游、原始输入、知识库或会话上下文补充、纠正或重判 Markdown。
3. JSON 只做字段归位和显式列表拆分，不得概括、改写或压缩业务文本。每个字段必须保留 Markdown 对应内容中的全部独立判断、限定条件、括号说明、示例、枚举、阈值、适用范围和禁止边界。
4. Markdown 没有明确内容时，单值写 `unknown`，集合写 `[]`。
5. 只有 Markdown 明确写出的阶段转折、来源和缺口才能进入对应字段。
6. 禁止使用“略”“同上”“见正文”等占位。
7. 不输出章节映射、阶段 ID、中间 JSON 或下游专用字段。

## 3. 固定结构

只允许以下字段和层级：

```json
{
  "skill": "journey-analysis",
  "version": "3.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/journey_analysis.md",
  "source_refs": [],
  "mode": "unknown",
  "result_level": "unknown",
  "journeys": [
    {
      "role": "unknown",
      "role_type": "主线角色",
      "summary": "unknown",
      "stages": [
        {
          "name": "unknown",
          "goal": "unknown",
          "actions": [],
          "touchpoints": [],
          "user_voice": "unknown",
          "confidence": "unknown",
          "confidence_reason": "unknown",
          "pain_points": [],
          "dropout_risk": "unknown",
          "opportunities": []
        }
      ],
      "key_transitions": [
        {
          "from": "unknown",
          "to": "unknown",
          "trigger": "unknown"
        }
      ]
    }
  ],
  "source_trace": [
    {
      "conclusion": "unknown",
      "source_type": "unknown",
      "source": "unknown"
    }
  ],
  "gaps": [
    {
      "gap": "unknown",
      "impact": "unknown",
      "suggested_source": "unknown"
    }
  ]
}
```

`journeys[]` 不得为空，每个旅程的 `stages[]` 不得为空。对象必须保留全部键；允许 `key_transitions[]`、`source_trace[]` 和 `gaps[]` 为空，不得生成虚假占位对象。

## 4. 字段写入规则

通用规则：

1. `skill`、`version`、`artifact_md` 按模板固定；`generated_at` 写实际时间或 `unknown`；`project_name`、`source_refs`、`mode`、`result_level` 只写 Markdown 头部已确认内容。
2. 每个业务值必须能直接指回 Markdown 的唯一对应内容，不得合并不同角色、阶段、来源或缺口。
3. 保持原结论的确定性和来源类型；原文提取、用户补充、规则推导、未提供不得互相转换。
4. 只允许删除 Markdown 的加粗标记、表格符号、列表序号和字符串首尾空白，将明确编号的多个条目拆成数组，以及删除用户心声最外层的展示引号。
5. 除上一条白名单外，不得删除、替换、概括或重新组织任何业务文本；任何角色限定、条件、括号说明、示例、枚举、阈值、风险等级、适用范围或禁止边界被删除，都视为 JSON 投影失败。
6. `role`、`summary`、`name`、`goal`、`user_voice`、`confidence`、`confidence_reason`、`dropout_risk`、`source_trace[]` 和 `gaps[]` 必须完整承接对应 Markdown 单元，不得摘要化。
7. `actions[]`、`touchpoints[]`、`pain_points[]` 和 `opportunities[]` 只允许按 Markdown 的明确条目拆分；每个数组条目内部必须保留完整文本。
8. 写盘前逐字段回看 Markdown：JSON 每个业务字符串必须覆盖对应 Markdown 单元的全部语义成分；发现内容缩短时，只有确认被删除内容属于第 4 条格式白名单才允许保留，否则恢复对应 Markdown 原文。

### 角色与阶段完整覆盖

1. Markdown 中每个“主线角色旅程”或“支持角色旅程”按原顺序在 `journeys[]` 中出现一次，不得遗漏、重复或新增。
2. `role_type` 只允许按章节标题写 `主线角色` 或 `支持角色`；`role` 与 `summary` 承接同一角色章节。
3. 每个角色下的全部阶段按原顺序进入该角色的 `stages[]`，不得把同名阶段合并、移动到其他角色或平铺到根级。
4. 每个阶段固定承接 `name`、`goal`、`actions`、`touchpoints`、`user_voice`、`confidence`、`confidence_reason`、`pain_points`、`dropout_risk`、`opportunities`。
5. `actions[]`、`touchpoints[]`、`pain_points[]`、`opportunities[]` 逐项承接全部明确条目，不得只选代表项。
6. `dropout_risk` 保留 Markdown 的风险等级、触发情形和结果，不拆分成额外对象。

### 转折、来源与缺口

1. `key_transitions[]` 只承接 Markdown 明确写出的阶段转折；`from`、`to`、`trigger` 必须能直接指回同一条转折。
2. Markdown 未明确输出阶段转折时写 `[]`。禁止根据阶段顺序、动作或常识自行生成转折。
3. `source_trace[]` 逐行承接“来源说明”的结论、来源类型和具体来源，不得新增来源或提高来源确定性。
4. `gaps[]` 逐行承接“缺口说明”的缺口、影响和建议补充来源，不得把痛点、机会或合理推测改写为缺口。
5. 不从缺口自行改写 `open_questions`；下游需要追问时直接消费 `gaps[]`。

## 5. 明确不进入 JSON

- 角色、阶段、低信心阶段等可由 `journeys[]` 直接读取的重复索引。
- Markdown 章节锚点、阶段 ID、字段与 Markdown 的映射关系。
- readiness 过程、补问过程、自检结果和运行日志。
- 下游章节提示、蓝图落点、页面方案或额外关系模型。
- Markdown 未明确输出的阶段转折和开放问题。

## 6. 下游读取约定

- 下游可将结构完整的 Journey `3.0` JSON 作为正式机器输入。
- JSON 字段为 `unknown`、`[]`，与 Markdown 明显冲突，或需要审计完整旅程叙述时，再回读 `journey_analysis.md`。
- JSON 缺失的信息不得从会话上下文补齐。
- JSON 与 Markdown 冲突时停止使用冲突字段，回读 Markdown 核对并报告交接错误；不得自行选择或重判。
- 旧 `2.0` JSON 只提供旅程摘要索引，不能替代 Journey Markdown。

## 7. 校验

```bash
node .claude/skills/journey-analysis/scripts/validate_context.js spark-output/context/journey-analysis.json
```

校验失败时只修 JSON 并重跑；不得反向修改已冻结的 Markdown。
