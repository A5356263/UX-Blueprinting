# Experience Blueprint Context JSON Schema

## 1. 定位与版本

- 产物：`spark-output/context/experience-blueprint.json`
- `skill`：固定为 `experience-blueprint`
- `version`：固定为 `4.0`
- `experience_blueprint.md` 是给人阅读的完整体验设计文档。
- 本 JSON 是同一轮蓝图结论的结构化机器面，不是摘要、索引或第二次推理。
- ASCII 页面图只保留在 Markdown `§6`；JSON 通过 `markdown_heading` 指向对应标题。
- 禁止承担泳道图模型、坐标、关系边、覆盖清单或下游执行状态。

## 2. 完整结构

```json
{
  "skill": "experience-blueprint",
  "version": "4.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/experience_blueprint.md",
  "source_refs": [],
  "upstream_contract": {
    "mode": "uxb-mode",
    "requirements_baseline_refs": [
      "spark-output/requirements_baseline.md",
      "spark-output/context/requirements-baseline.json"
    ],
    "uxb_refs": [
      "spark-output/uxb_output.md",
      "spark-output/context/uxb.json"
    ]
  },
  "critical_design_judgments": [
    {
      "judgment": "示例判断",
      "impacts": ["示例影响"],
      "recommended_approach": "示例建议方案",
      "not_recommended": "示例不建议方案及原因",
      "open_question": "unknown"
    }
  ],
  "journey_consumption": [
    {
      "type": "信心最低点",
      "finding": "示例发现",
      "source_stage": "示例角色 / 阶段",
      "blueprint_target": "示例蓝图落点"
    }
  ],
  "interaction_overview": [
    {
      "name": "示例主路径",
      "path_type": "主路径",
      "steps": ["进入示例页面", "点击示例按钮"],
      "branches": ["示例条件 → 示例反馈"]
    }
  ],
  "main_flow": [
    {
      "name": "示例节点",
      "user_action": "示例用户动作",
      "system_feedback": "示例系统反馈",
      "pre_explanations": ["示例前置说明"],
      "copy_suggestions": ["示例文案"],
      "next_step": "示例下一步"
    }
  ],
  "sub_flows": [
    {
      "name": "示例次流程",
      "trigger_condition": "示例触发条件",
      "user_action": "示例用户动作",
      "system_feedback": "示例系统反馈",
      "pre_explanations": [],
      "copy_suggestions": [],
      "next_step": "示例下一步"
    }
  ],
  "exceptions": [
    {
      "name": "示例异常",
      "timing": "示例发生时机",
      "trigger_condition": "示例触发条件",
      "basis": "示例判断依据",
      "feedback_type": "InlineError",
      "system_feedback": "示例系统反馈",
      "user_next_step": "示例用户下一步",
      "recovery_path": "示例恢复路径"
    }
  ],
  "surfaces": {
    "pages": [
      {
        "name": "示例页面",
        "goal": "示例目标",
        "entry_condition": "示例进入条件",
        "markdown_heading": "6.1 示例页面",
        "structure_notes": ["示例区域与层级说明"],
        "fields": ["示例字段"],
        "validation_rules": ["示例校验规则"],
        "state_feedback": ["示例状态反馈"],
        "exception_structure_changes": ["示例异常结构变化"],
        "copy_items": ["示例文案"],
        "buttons": ["示例按钮"],
        "success_feedback": ["示例成功反馈"],
        "failure_feedback": ["示例失败反馈"]
      }
    ],
    "modals": [],
    "drawers": []
  },
  "states": [
    {
      "state": "示例状态",
      "meaning": "示例含义",
      "applies_to": "示例适用对象",
      "user_actions": ["示例可用操作"],
      "feedback": "示例统一反馈口径"
    }
  ],
  "feedbacks": [
    {
      "scenario": "示例场景",
      "type": "Toast",
      "copy": "示例反馈文案"
    }
  ],
  "open_questions": [
    {
      "question": "示例问题",
      "impact": "示例影响",
      "owner": "示例确认方"
    }
  ],
  "upstream_trace": [
    {
      "upstream_judgment": "示例上游判断",
      "experience_meaning": "示例体验含义",
      "design_decision": "示例设计决策",
      "blueprint_target": "示例正文落点"
    }
  ]
}
```

## 3. 固定写入规则

1. 先完成并自检 `experience_blueprint.md`，再开始 JSON。
2. JSON 阶段只读取这份冻结 Markdown；不得回读上游、知识库、原始需求或会话补充。
3. 只做字段归位和显式列表拆分；不得概括、改写、合并、补全或重新判断。
4. 只允许去除 Markdown 标记、表格符号、列表序号和首尾空白。
5. 条件、限制、否定词、阈值、变量、例外和恢复方式必须保留。
6. 单值缺失写 `unknown`；集合缺失写 `[]`。不得为了填满字段猜测。
7. `source_refs[]` 只写 Markdown 头部明确列出的真实来源；未列出时写 `[]`。
8. 写入前按章节建立当次核对清单；清单不落盘，不生成 ID 或映射文件。
9. 写入后核对 Markdown 正式条目数与 JSON 对应对象数；数量不一致时只修正投影遗漏，不返回正文重新推理。

### 3.1 上游合同

`mode` 只允许：

- `baseline-mode`
- `uxb-mode`
- `framing-mode`

`baseline-mode`：

- `requirements_baseline_refs` 固定包含需求基线 Markdown 与 JSON。
- `uxb_refs` 使用空数组。

`uxb-mode`：

- `requirements_baseline_refs` 固定包含需求基线 Markdown 与 JSON。
- `uxb_refs` 固定包含 UXB Markdown 与 JSON。

独立 `framing-mode`：

- 只在用户明确选择 Problem Framing 独立入口时使用。
- `requirements_baseline_refs` 和 `uxb_refs` 使用空数组。
- Problem Framing 正式路径写入 `source_refs`。

不得用旧 UXB `5.0` 路径组合冒充 `uxb-mode`。

## 4. 逐章承接

| Markdown | JSON | 承接要求 |
|---|---|---|
| `§0` | `critical_design_judgments[]` | 每条判断、影响、建议、不建议及待确认逐项保留 |
| `§1` | `journey_consumption[]` | 每个消费项、来源阶段和蓝图落点逐项保留 |
| `§2` | `interaction_overview[]` | 每条路径、动作步骤和显式分支逐项保留 |
| `§3` | `main_flow[]` | 每个节点及其五类信息逐项保留 |
| `§4` | `sub_flows[]` | 每个次流程及其显式信息逐项保留 |
| `§5` | `exceptions[]` | 每个异常的发生、条件、依据、反馈、下一步和恢复逐项保留 |
| `§6` | `surfaces.*[]` | 每个载体的全部非 ASCII 设计事实逐项保留；ASCII 本体留在 Markdown |
| `§7` | `states[]`、`feedbacks[]` | 每行独立状态和反馈逐项保留 |
| `§8` | `open_questions[]` | 每个问题、影响和确认方逐项保留 |
| `§9` | `upstream_trace[]` | 上游承接追踪逐项保留；知识读取日志不重复写入 |

`§9` 中形成的设计决策必须已经落入 `§0-§8`；如果只存在于知识消费日志，Markdown 尚未收口，禁止进入 JSON 阶段。

## 5. 页面载体字段

- `markdown_heading`：对应 Markdown 标题原文，仅用于定位 ASCII，不承担业务引用关系。
- `structure_notes[]`：ASCII 外明确写出的区域、层级、顺序和结构说明。
- `fields[]`：表单字段、展示字段及其显式说明。
- `validation_rules[]`：字段校验、提交前校验和提交失败条件。
- `state_feedback[]`：加载、空状态、处理中、已关闭及其他显式状态反馈。
- `exception_structure_changes[]`：按钮置灰、入口隐藏、阻断弹窗、字段错误等显式结构变化。
- `copy_items[]`、`buttons[]`、`success_feedback[]`、`failure_feedback[]`：对应载体章节中显式列出的全部条目。

## 6. 禁止字段与内容

禁止写入：

- `source_status`
- 任意 `*_id`
- `source_anchor`、`md_anchor`
- `end_type`、`end_target`
- ID 形式的 `applies_to`
- ASCII 字符图及其转写布局树
- `lanes`、`nodes`、`edges`、坐标、连线、`coverage_manifest`
- 下游消费状态或完成标记

## 7. 校验

```bash
node .claude/skills/experience-blueprint/scripts/validate-context.js spark-output/context/experience-blueprint.json
```

校验器只检查 JSON 结构、字段类型、固定值和禁止字段。它不读取 Markdown、不判断设计质量，也不能替代逐章数量与原文保真核对。

退出码非 `0` 时必须修复并重跑。
