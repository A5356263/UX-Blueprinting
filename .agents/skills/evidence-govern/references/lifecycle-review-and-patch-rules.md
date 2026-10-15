read_frequency: on_demand
execution_critical: true

# Lifecycle, Review and Patch Rules

## Evidence 生命周期

```text
candidate
released
restricted
superseded
archived
```

- `candidate`：已标准化但未完成发布判断。
- `released`：可按消费者权限使用。
- `restricted`：只允许有限用途。
- `superseded`：被更新或更准确证据替代，保留追溯。
- `archived`：退出活跃工作流，只供历史追溯。

## 变化信号

```text
strengthened
weakened
stable
resolved
stale
contradicted
```

信号只描述变化。`resolved` 不删除历史证据；`stale` 不自动归档；`contradicted` 先进入审核或限制。

## Evidence Patch

动作：

```text
release
amend
restrict
supersede
archive
retain
```

## Baseline

生命周期：

```text
proposed
active
stale
superseded
archived
```

动作：

```text
activate
amend
mark_stale
supersede
archive
retain
```

Objective 计算全部 Baseline 数值。Govern 只治理版本和生命周期。Archive 只追加获准版本。

## 审核状态

```text
not_required
pending
approved
rejected
```

- `pending`、`rejected` 不得持久化。
- `not_required`、`approved` 可以进入 Archive Handoff，但 Evidence Govern 自身不写 Store。
- Review Decision 只能引用现有未关闭 Review ID。
- Outcome Patch 只能提出变化和 Patch，不能直接更新生命周期。

## Patch 安全

- 所有 Patch `applied=false`；持久化由 Evidence Archive 执行。
- 修正历史证据时创建新 Evidence ID，并用 `supersedes_ref` 指向旧证据。
- Mapping、指标、旅程、分群、粒度或时区变化不得静默更新 Baseline。
- Evidence Archive 只追加，不覆盖历史记录。
