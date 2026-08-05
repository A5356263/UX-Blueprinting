# UXB Context 9.0 JSON Schema

## 快速导航

- [1. 定位](#1-定位)
- [2. 生成顺序](#2-生成顺序)
- [3. 固定根结构](#3-固定根结构)
- [4. 体验决定](#4-体验决定)
- [5. 跨任务体验约束](#5-跨任务体验约束)
- [6. 来源承接](#6-来源承接)
- [7. 投影规则](#7-投影规则)
- [8. 结构校验边界](#8-结构校验边界)

## 1. 定位

- 正式 Markdown：spark-output/uxb_output.md
- Context JSON：spark-output/context/uxb.json
- skill：固定为 uxb
- version：固定为 9.0

Markdown 是唯一正式语义源。JSON 只投影已经确认并冻结的 Markdown。

## 2. 生成顺序

只有正式 Markdown 冻结后，才能读取本文件并生成 JSON。

生成时：

1. 读取冻结后的 UXB Markdown。
2. 从 §1 投影体验决定。
3. 从真实存在的 §2 投影跨任务体验约束。
4. 从 §3 投影来源承接。
5. 运行结构校验。
6. 由 Agent 核对 Markdown 与 JSON 的语义一致性。

禁止：

- 回读需求基线、知识库、聊天记录或内部任务覆盖结果补 JSON。
- 用 schema 要求 Markdown 增加字段。
- 在 JSON 中重新概括、改写或扩展体验决定。
- 保存候选体验问题、未选择方向和内部比较过程。
- 保存页面、组件、布局和最终文案。

## 3. 固定根结构

    {
      "skill": "uxb",
      "version": "9.0",
      "generated_at": "2026-08-04T00:00:00+08:00",
      "project_name": "项目名称",
      "artifact_md": "spark-output/uxb_output.md",
      "decisions": [],
      "cross_cutting_constraints": [],
      "upstream_trace": []
    }

根字段全部必填。不得新增其他根字段。

字段规则：

- skill：固定为 uxb。
- version：固定为 9.0。
- generated_at：非空 ISO 8601 时间字符串。
- project_name：非空字符串。
- artifact_md：固定为 spark-output/uxb_output.md。
- decisions：体验决定数组，可以为空。
- cross_cutting_constraints：跨任务体验约束数组，可以为空。
- upstream_trace：来源数组，可以为空。

## 4. 体验决定

每个对象直接对应 Markdown §1 中的一条体验决定。

### 4.1 最小对象

    {
      "id": "ED-001",
      "task": "对应任务",
      "roles": ["涉及角色"],
      "decision": "Markdown 中已确认的体验决定"
    }

必填字段：

- id：ED-001 格式，在 decisions 内唯一。
- task：非空字符串，沿用 Markdown 中的任务名称。
- roles：非空字符串数组。
- decision：非空字符串，保持 Markdown 决定正文的语义和范围。

### 4.2 可选字段

    {
      "business_objects": ["Markdown 中直接出现的业务对象"],
      "states": ["Markdown 中直接出现的状态"],
      "conditions": ["Markdown 中直接出现的适用条件"],
      "additional_constraints": ["Markdown 中直接出现的额外约束"],
      "source_refs": ["Markdown 中直接关联的来源编号"]
    }

可选字段规则：

- 字段出现时必须是非空字符串数组。
- 数组不得为空，不得包含空字符串。
- Markdown 没有直接内容时省略字段。
- 不得从正式输入或知识库补充可选字段。

一条 Markdown 决定只生成一个 decisions 对象。不要因为它同时涉及信息、状态和恢复而拆成多个 JSON 对象。

## 5. 跨任务体验约束

每个对象直接对应 Markdown §2 中的一条跨任务体验约束。

    {
      "id": "CC-001",
      "constraint": "跨任务、跨角色或跨系统共同遵守的体验约束",
      "applies_to": ["适用任务或角色"]
    }

字段全部必填：

- id：CC-001 格式，在 cross_cutting_constraints 内唯一。
- constraint：非空字符串。
- applies_to：非空字符串数组。

Markdown 没有 §2 时，cross_cutting_constraints 使用空数组。不要从 §1 再次提炼一套约束。

## 6. 来源承接

每个对象直接对应 Markdown §3 中的一项来源。

    {
      "id": "UT-001",
      "source_type": "正式输入",
      "source_name": "真实来源名称",
      "source_path": "真实路径",
      "used_for": ["ED-001"]
    }

必填字段：

- id：UT-001 格式，在 upstream_trace 内唯一。
- source_type：非空字符串。
- source_name：非空字符串。
- used_for：非空字符串数组。

可选字段：

- source_path：真实路径存在时输出非空字符串。用户直接提供完整正文且没有路径时省略。

source_type 不使用固定枚举。沿用 Markdown 对来源的真实分类，例如正式输入、业务知识、设计准则或交互模式。

used_for 只记录 Markdown 已写明的决定编号或判断范围。不得根据 JSON 对象关系补写来源用途。

## 7. 投影规则

- JSON 数组顺序与 Markdown 对应内容顺序一致。
- 角色、任务、对象和状态名称沿用 Markdown。
- id 只用于 UXB 本轮 Context 内识别，不作为跨 Skill 固定外键。
- 不使用章节号、行号或固定路径建立语义绑定。
- 没有对应内容时使用空数组或省略可选字段。
- 不生成空字符串、空可选数组和占位对象。
- JSON 中每条非元数据内容都必须能在 Markdown 中找到直接来源。
- JSON 校验失败时只修 JSON。
- Markdown 结论错误时返回 UXB 体验决定阶段并重新确认。

## 8. 结构校验边界

脚本可以校验：

- JSON 是否可解析。
- 根字段和对象字段是否存在。
- 是否包含未知字段。
- 字段类型。
- 固定值。
- 字符串和数组是否为空。
- id 格式及数组内唯一性。

脚本不能校验：

- 体验问题是否真实。
- 体验决定是否具体或合理。
- 是否越界到页面方案。
- Markdown 与 JSON 是否语义一致。
- JSON 内容是否忠实投影 Markdown。
- 是否应该执行 UXB。

这些内容由 Agent 验收。
