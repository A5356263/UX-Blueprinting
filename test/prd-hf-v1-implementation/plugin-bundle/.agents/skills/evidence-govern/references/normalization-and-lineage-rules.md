read_frequency: always
execution_critical: true

# Normalization and Lineage Rules

## 当前生产者

只适配当前 Registry 版本：

- Objective 4.0.0
- Subjective 4.0.0
- Experience Heuristic 4.0.0

不读取 Registry 未登记或没有真实适配器的旧证据处理产物。

## 最小源字段

每条上游 Evidence 至少能解析：

```text
source_item_id
claim_summary 或 observation_ref
scope
time_window
source_attribution
evidence_form
lineage
privacy_status
manual_review_required
allowed_uses
forbidden_uses
```

可选：

```text
scene.where
scene.what
scene.operation
scene.who_redacted
```

不新增 `governance_projection` 中间包。

## ID

`evidence_id` 是一次具体观察的稳定 ID，由以下内容确定性生成：

```text
producer skill
source item ref
claim type
claim summary
scope
time window
```

输出格式：

```text
ev_<sha256 前 16 位>
```

`lineage_fingerprint` 是规范化源 Item 的完整 SHA-256。完全相同来源重复运行必须得到相同 Fingerprint。

## Comparison Key

只在指标/问题定义、业务对象、任务环节、单位口径和核心范围充分时生成。新时间窗口产生新 Evidence ID，但可共享 `comparison_key`。

`comparison_key` 只表示可比较，不表示支持或冲突。

## 缺失

- 缺 source ID 或来源引用：保持 `candidate`，禁止正式发布。
- 缺隐私状态：按 `needs_review` 处理，进入 `restricted` 生命周期并排入人工复核。
- 上游标记 `manual_review_required=true`：在绑定的 Review Decision 获批前，消费者访问和 Handoff 不得放行。
- 下游只能缩小 `allowed_uses`、扩大 `forbidden_uses`，不得放宽上游限制。
- 缺时间：不可做跨时间比较。
- 缺 who：不可做实体或分群匹配。
- 缺 operation：可匹配现象，但降低链接置信度。
- 缺全部场景：保留单条证据，不形成跨源互证。

只限制受影响 Item，不阻断整个包。

## 排除

上游 Findings、比较结果、Knowledge Candidate、Validation Request 和报告正文都不能转成 Canonical Evidence Item，除非上游正式 Schema 已将其提升为 `evidence_items[]`。
