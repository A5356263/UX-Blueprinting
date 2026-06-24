---
name: edge
description: 异常态 Skill。读取体验蓝图产出或用户指定的目标页面，按 6 类 25 子类型状态矩阵穷举异常态，输出结构化状态设计结果。
---

# Edge

这个 skill 负责在主流程设计完成后，补齐异常态、空状态、加载态、权限态、边界数据态和离线态。

它的目标不是检查“有没有问题”，而是主动把容易漏掉的状态设计出来，给后续走查或页面设计直接使用。

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

## 上游读取协议

启动后按以下顺序读取：

1. 读取 `_shared/skill-graph.json`，确认自己的位置和下游
2. 读取 `spark-output/context/experience-blueprint.json`
3. 读取 `spark-output/experience_blueprint.md`
4. 如有需要，补读 `knowledge-wiki` 中与反馈、报错、异常态相关的知识

降级规则：

- 如果存在 `experience-blueprint.json`，优先用 JSON 提取页面、流程、状态和异常线索
- 如果 JSON 缺失但 `experience_blueprint.md` 存在，则从 Markdown 中提取目标页面、主流程和异常段落
- 如果两个文件都缺失，不阻断执行，转为独立模式并向用户确认目标范围
- 如果知识库不可用，继续执行，但不要伪造知识消费结果

## 独立模式

没有体验蓝图上游时，先向用户确认：

1. 要穷举的页面、流程或模块
2. 平台类型：Web / Mobile / 多端
3. 是否有重点关注状态类型

独立模式下仍按同一套状态矩阵输出，只是不依赖上游文件。

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

## 执行流程

### Step 1：确定目标范围

- 如果读到了体验蓝图上游，先整理出页面 / 弹窗 / 抽屉 / 关键节点列表
- 如果没有完整上游，则基于用户输入确认本次范围
- 输出前先说明本次穷举覆盖了哪些页面和平台

### Step 2：逐屏穷举异常态

对每个目标页面，按 `references/state-matrix.md` 逐类判断：

- 哪些状态是 must
- 哪些状态是 should
- 哪些可以记为 nice-to-have
- 每个状态的设计描述、反馈方式、文案建议、用户下一步

### Step 3：收敛关键缺口

整理：

- `critical_missing`
- must / should / nice-to-have 数量
- 每类状态的覆盖情况

如果存在 blocker 级缺口，要在 Markdown 报告里单列“必须优先补齐”。

### Step 4：写入结果

输出到：

- `spark-output/edge_output.md`
- `spark-output/context/edge.json`

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
- 按页面展开的状态矩阵
- 每个状态的设计描述 / 用户出口 / 文案建议

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

## 交接

完成后：

1. 读取 `_shared/next-skill.md` 交接话术模板
2. 读取 `_shared/skill-graph.json` 中 id 为 `edge` 的 `next_hint`
3. 如果 `next_hint.preferred` 为空，按终端节点口径输出
4. 如果 `next_hint.preferred` 非空，按标准三层结构输出

## 边界

- 不把 Edge 写成主流程蓝图的重做版本
- 不为了凑满 25 个子类型而强行编造业务状态
- 不把“未确认”写成“已确定需要”
- 不输出 marker、dashboard 或其他已暂缓执行的 chain 机制
