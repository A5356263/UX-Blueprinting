---
name: edge
description: >
  异常态设计 Skill。读取已完成的体验蓝图或用户明确指定的目标页面，按状态矩阵补齐异常态、空状态、加载态和边界状态，输出结构化状态设计结果。
  仅在用户明确要求异常态、边界状态、空状态或异常流程补全时使用；不得在体验蓝图完成后自动触发。
  排除：主交互方案（用 experience-blueprint）、页面规格提取（用 page-spec）、设计完整性走查（用 check）。
---

# Edge

这个 skill 负责在主流程设计完成后，补齐异常态、空状态、加载态、权限态、边界数据态和离线态。

它的目标不是检查“有没有问题”，而是主动把容易漏掉的状态设计出来，给后续走查、页面规格或页面生成直接使用。
它默认产出的不是“异常态大全”，而是“当前任务真正需要的异常态补丁”。

它在链路中的定位是：

- 默认不强制进入主链
- 在需要补状态覆盖时作为可选补强层调用
- 输出结果默认供 `page-spec`、`check` 或后续页面生成吸收
- 保留独立运行能力，但独立运行也不默认展开成大型专项报告

## Step 0 · 运行入口

### Step 0.1 · 本 Skill 产物状态

执行本 Skill 前，只检查本 Skill 对应正式产物是否存在。

正式产物：
- `spark-output/edge_output.md`
- `spark-output/context/edge.json`

只允许检查文件是否存在；禁止读取产物正文、禁止解析 JSON 内容、禁止根据已有产物改变当前任务类型。

若任一正式产物存在，先输出以下状态提示，然后继续执行本 Skill 的入口规则：

```text
检测到本 Skill 已有正式产物（已产出）。
```

该提示只表示状态，不代表采取任何处理动作。

禁止：
- 读取产物正文
- 解析 JSON 内容
- 根据已有产物改变当前任务类型
- 根据已有产物执行下游
- 根据已有产物询问处理方式
- 根据已有产物推断用户意图

### Step 0.2 · 上游读取与模式判断

启动后按以下顺序读取：

1. 按当前 `SKILL.md` 的规则确认本 Skill 自身位置和输入边界
2. 读取 `spark-output/context/experience-blueprint.json`
3. 读取 `spark-output/experience_blueprint.md`
4. 如需知识补充，从 `knowledge-wiki` 的 `knowledge/wiki/index.md` 进入实际入口；业务知识先按领域 README 选择正式文件，index 明确直达的单一设计知识直接进入，再按顶部导航只读命中的反馈、报错、异常、恢复或状态章节；不得预设目录层级或遍历 raw

- 停止条件：命中局部知识后不得停止；问题涉及的主体、动作、条件、例外、结果及已触发依赖均有正式依据后再输出
- 封闭枚举：仅以完整正式清单作答；未命中完整清单时，不得把局部事实表述为全集
- 输出边界：以上仅作内部检查，不展示读取过程或检查项；证据不足影响正确性时，只说明必要边界

这是链路消费型 skill，默认承接 `spark-output/` 中的上游产物属于正式工作流。

上游读取硬门禁：

- Blueprint `3.0` JSON 是结构化设计事实的机器面；重点消费目标载体相关的 `exceptions`、`states`、`feedbacks`、流程和页面状态事实。
- JSON 不包含 ASCII 和完整设计叙述，链路模式仍必须实际完整读取 `experience_blueprint.md`。
- `interaction_overview`、关键判断、旅程消费和上游追踪不用于替代本 Skill 现有状态矩阵分析。
- 即使蓝图刚在同一会话生成、当前上下文仍保留内容，也不得替代本次文件读取。
- 重点章节只决定二次核对优先级，不是正文白名单。
- JSON 与 Markdown 冲突时停止使用冲突字段并报告交接错误；不得静默选择任一侧或自行修复。
- 只有 JSON 而没有 Markdown 时，不得进入链路模式或据此补齐状态、异常、恢复和文案。
- 蓝图未读完前，不得进入状态矩阵分析或生成正式 Edge 产物。

如果存在 `page-spec` 消费需求，`edge` 的输出应被视为状态补丁层，而不是新的主设计源。

降级规则：

- 如果 Blueprint `3.0` JSON 与 Markdown 同时存在，先从 JSON 读取结构化状态、异常和反馈，再以完整 Markdown 补充语境并核对一致性
- 如果 JSON 缺失但 `experience_blueprint.md` 存在，则从 Markdown 中提取目标页面、主流程和异常段落
- 如果只有 JSON 或两个文件都缺失，不进入链路模式，转为独立模式并向用户确认目标范围
- 如果知识库不可用，继续执行，但不要伪造知识消费结果

### Step 0.3 · 独立模式确认

没有体验蓝图上游时，先向用户确认：

1. 要穷举的页面、流程或模块
2. 平台类型：Web / Mobile / 多端
3. 是否有重点关注状态类型

独立模式下仍按同一套状态矩阵输出，只是不依赖上游文件。
如果目标范围明显过大（如页面过多、模块边界过宽、同时覆盖多个不相干流程），先要求用户收窄范围或分批处理，避免一次性产出失控。


## 角色定义

Edge 负责：

- 识别需要补充异常态的页面、流程或节点
- 按 6 类状态矩阵系统性穷举
- 为每个需要的状态补充设计描述、文案建议和用户下一步
- 标出必须补但当前缺失的关键状态

Edge 不负责：

- 重新做业务判断
- 重写主流程设计
- 做视觉风格方案
- 做实现验收
- 取代 `experience-blueprint` 或 `page-spec` 成为主规格

## 输出哲学

`edge` 有两种使用姿态，但只有一套收紧后的输出原则：

- **独立模式**：可以单独成立，帮助用户补齐目标页面 / 流程的异常态
- **主链模式**：作为 `experience-blueprint` 之后的状态补丁层，被 `page-spec`、`check` 或页面生成阶段吸收

无论哪种模式，都遵循以下原则：

- 首要目标不是“把所有异常态讲全”，而是“把本次任务真正需要补的异常态讲清”
- 默认产出补丁型结果，而不是第二份完整设计稿
- 只有会影响下游生成、状态恢复、关键文案或结构判断的状态，才值得展开

## 范围收敛规则

执行前必须先收紧本次补强边界：

- 只对**本次目标实体**做完整异常态补强
- 对“只引用不生成”的页面或外围关联页面，最多保留影响说明，不完整展开
- 对承载页 / 父页面，只在它直接影响当前主实体状态时补充必要异常态
- 不因发现关联页面而自动扩大异常态范围
- 不因状态矩阵完整性诉求而把与本次任务无关的页面一起拉入

## 状态矩阵

执行前必须阅读：

- `references/state-matrix.md`

固定检查 6 类状态：

- 空状态
- 加载状态
- 错误状态
- 边界数据
- 权限状态
- 离线状态

要求：

- 每一类都要明确给出“适用 / 不适用 / 待确认”
- 不允许只列 checklist，不给设计描述
- 发现 must 状态缺失时，必须进入 `critical_missing`

## 默认展开策略

为防止信息量失控，默认按以下规则控制展开深度：

- `must` 状态默认展开
- `should` 状态默认压缩表达，只有在满足以下任一条件时才展开：
  - 会改变页面结构
  - 会改变用户恢复路径
  - 会改变关键状态文案
  - 会直接影响 `page-spec` 生成
- `nice-to-have` 默认不展开，只进入汇总或待后续补强

这里的“展开”指写出完整的设计描述、用户出口、文案建议和落位建议；“压缩表达”指只保留状态名、适用理由和是否建议后续补充。

## 执行流程

### Step 1：确定目标范围

- 如果读到了体验蓝图上游，先整理出页面 / 弹窗 / 抽屉 / 关键节点列表
- 如果没有完整上游，则基于用户输入确认本次范围
- 优先只锁定本次真正要生成、要补强或要校验的实体，不把外围引用页默认纳入完整穷举
- 输出前先说明本次穷举覆盖了哪些页面和平台

### Step 2：逐屏穷举异常态

对每个目标页面，按 `references/state-matrix.md` 逐类判断：

- 哪些状态是 must
- 哪些状态是 should
- 哪些可以记为 nice-to-have
- 仅对需要展开的状态写设计描述、反馈方式、文案建议、用户下一步

对每条展开状态，额外标注建议下游吸收位置：

- `状态表现`
- `异常恢复`
- `文案池`
- `待确认项`

### Step 3：收敛关键缺口

整理：

- `critical_missing`
- must / should / nice-to-have 数量
- 每类状态的覆盖情况
- 哪些状态被完整展开，哪些仅压缩记录

如果存在 blocker 级缺口，要在 Markdown 报告里单列“必须优先补齐”。

### Step 4：写入结果

输出到：

- `spark-output/edge_output.md`
- `spark-output/context/edge.json`

输出规则补充：

- 如果宿主支持文件系统，先检查并创建 `spark-output/` 与 `spark-output/context/`，再写入产物

`edge.json` 至少包含：

- `skill`
- `version`
- `generated_at`
- `project_name`
- `source_mode`
- `targets[]`
- `states_matrix[]`
- `coverage`
- `critical_missing[]`

写入失败不阻断完成，但必须明确提示。

## 输出要求

Markdown 报告至少包含：

- 本次范围
- 总览统计
- 关键缺失
- 关键状态补丁
- 可压缩吸收的状态

Markdown 默认不是“逐屏每态全文展开报告”，而是“异常态补丁报告”。
除非用户明确要求全量展开，否则不要把所有 `should` / `nice-to-have` 状态逐条展开成大文档。

输出定位要求：

- `edge_output.md` 是补强层结果，不是新的页面主规格
- `edge.json` 默认供 `page-spec`、`check` 或页面生成阶段按需吸收
- 不要求下游完整复写 `edge` 全文，只吸收与目标页面直接相关的状态补丁
- `edge_output.md` 默认应更像“补丁说明书”，而不是“完整异常态专项设计稿”

JSON 要求：

- `states_matrix[].screen`
- `states_matrix[].screen_id`
- `states_matrix[].states[]`
- `states_matrix[].states[].state_type`
- `states_matrix[].states[].required`
- `states_matrix[].states[].severity`
- `states_matrix[].states[].design_description`
- `states_matrix[].states[].fallback_behavior`
- `states_matrix[].states[].visual_hint`
- `states_matrix[].states[].copy_hint`
- `states_matrix[].states[].target_section`

`target_section` 只用于标记建议注入位置，可选值为：

- `状态表现`
- `异常恢复`
- `文案池`
- `待确认项`

它是下游消费提示，不代表 `edge` 有权改写主规格结构。

Markdown 建议结构：

```markdown
# Edge 异常态补丁：{项目名}

## 1. 本次覆盖范围
## 2. 状态覆盖总览
## 3. 必须优先补齐
## 4. 关键状态补丁
## 5. 可压缩吸收的状态
## 6. 不进入本次生成的待确认项
```

`关键状态补丁` 默认只展开关键项，每条至少包含：

- 适用页面 / 实体
- 状态类型
- 为什么需要
- UI / 交互补丁
- 文案补丁
- 用户出口 / 恢复路径
- 建议注入章节（`target_section`）

## Context JSON 写入

正式产物生成后，按固定结构写入 `spark-output/context/edge.json`。

固定结构：

```json
{
  "skill": "edge",
  "version": "1.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/edge_cases.md",
  "source_refs": [],
  "read_sections": [],
  "source_mode": "unknown",
  "scope": {
    "targets": [],
    "included": [],
    "excluded": []
  },
  "overview_stats": {
    "targets_count": 0,
    "states_count": 0,
    "critical_missing_count": 0,
    "compressible_count": 0
  },
  "targets": [
    {
      "screen_id": "unknown",
      "screen_name": "unknown",
      "source": "unknown"
    }
  ],
  "states_matrix": [
    {
      "screen": "unknown",
      "screen_id": "unknown",
      "states": [
        {
          "state_type": "unknown",
          "required": "unknown",
          "severity": "unknown",
          "design_description": "unknown",
          "fallback_behavior": "unknown",
          "visual_hint": "unknown",
          "copy_hint": "unknown",
          "target_section": "unknown"
        }
      ]
    }
  ],
  "coverage": {
    "covered": [],
    "missing": [],
    "not_applicable": []
  },
  "critical_missing": [
    {
      "screen_id": "unknown",
      "state_type": "unknown",
      "reason": "unknown",
      "impact": "unknown",
      "suggested_fix": "unknown"
    }
  ],
  "compressible_states": [
    {
      "state_type": "unknown",
      "can_be_absorbed_by": "unknown",
      "reason": "unknown"
    }
  ],
  "open_questions": [
    {
      "question": "unknown",
      "impact": "unknown"
    }
  ]
}
```

硬规则：

- 字段固定，不得新增、删除或改名。
- 只填入本 Skill 正式 Markdown 已产出的信息；缺失信息写 `unknown`、空数组，或进入 `open_questions[]`。
- 不得为了填满 JSON 编造信息。
- `states_matrix[].states[]` 是核心，不得压缩成统计数。
- `critical_missing[]` 必须保留影响和建议修复。
- JSON 不复制 Markdown 全文。
- 写入失败不阻断完成，但应在输出中提示。

## Handoff · 固定下一步

固定输出：

```text
异常态已完成。当前没有固定下一步推荐。
你可以停在这里。
```

**硬规则：正式产物写入并校验通过后，必须执行 `node shared-workflow/generate-progress-preview.js`；失败仅告警，不得阻断 Handoff。**

## 边界

- 不把 Edge 写成主流程蓝图的重做版本
- 不为了凑满 25 个子类型而强行编造业务状态
- 不把“未确认”写成“已确定需要”
- 不输出 marker、dashboard 或其他已暂缓执行的 chain 机制
- 不要求每次主链都必须调用 Edge
- 不把 Edge 产物伪装成替代 `page-spec` 的页面生成契约
- 不为了显得完整而默认展开所有 `should` / `nice-to-have`
- 不因发现关联页面而自动扩大本次异常态范围
- 不把状态穷举能力误用成页面方案重写能力
