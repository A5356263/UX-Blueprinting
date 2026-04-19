# Memory Layer Flow

## 是什么

Memory Layer 是当前执行中枢之上的质量经验沉淀层。

它负责把通过样例、失败模式、repair 结果与 capability 使用经验提炼成：

- pattern
- failure_mode
- capability_insight
- preference 骨架

## 为什么不放进 wiki

`knowledge/wiki/` 是独立知识子系统，负责概念统一、跨任务知识复用与上下文压缩。

Memory Layer 不直接写进 wiki，原因是：

- memory 沉淀的是质量经验，不是知识正文
- memory 需要区分项目级候选与长期 accepted 条目
- memory 需要明确保留 candidate / accepted 状态
- quality preference 不应和 wiki 词条混在一起

因此首轮长期 memory 固定放在顶层：

```text
memory/
```

## 长期层与项目层分别在哪里

长期层：

```text
memory/
  index.json
  patterns/
  failure_modes/
  preferences/
  capability_insights/
```

项目级运行层：

```text
projects/<project-id>/runtime/memory/
  extracted_memory_candidates.json
  accepted_memory_items.json
  memory_trace.json
```

用户查看入口：

```text
projects/<project-id>/workspace/memory_summary.md
```

## 如何提取 candidate

在任务已通过正式检查，或 Repair Loop 已闭环后，运行：

```bash
python -m packages memory-extract <project-id>
```

该命令会：

- 从 `task_card_resolved.json` 读取 domain / wiki 证据
- 从 `check_status.json` 提取通过样例与失败模式线索
- 从 `runtime/remediation/issue_index.json` 提取 repair 相关经验
- 在 `runtime/memory/` 中生成 candidate 与 trace

## 如何接受进入长期层

运行：

```bash
python -m packages memory-accept <project-id>
```

当前首轮实现会把可直接复用的 pattern / failure_mode / capability_insight 写入顶层 `memory/`，并刷新：

- `memory/index.json`
- `projects/<project-id>/runtime/memory/accepted_memory_items.json`

## 如何查看摘要

运行：

```bash
python -m packages memory-summary <project-id>
```

然后查看：

- `projects/<project-id>/workspace/memory_summary.md`

该摘要至少回答：

- 本次新增的通用模式
- 本次新增的领域模式
- 本次识别的失败模式
- 本次新增的 capability insight
- 哪些进入长期 memory
- 哪些仍只是候选
- 当前 preference 骨架在哪里

## 如何后续补充 preferences

主观偏好不由 AI 自动填写，只预建骨架：

- `memory/preferences/quality_preferences.md`
- `memory/preferences/preference_rules.yaml`

后续应由项目维护者手动补充：

- 更偏好的判断追踪深度
- 更偏好的状态矩阵完整度
- 不接受的写法
- 风险容忍度

## 已验证样例

当前已用 `examples/positive/real-self-apply-v1/` 验证以下链路：

- 能生成 memory candidate
- 能把一条 generic pattern 接受到长期 memory
- 能把一条 permission domain pattern 接受到长期 memory
- 能生成 `workspace/memory_summary.md`

## 一句话原则

先从项目结果提炼可复用经验，再决定哪些进入长期层；memory 只沉淀质量经验，不复制整篇任务正文。
