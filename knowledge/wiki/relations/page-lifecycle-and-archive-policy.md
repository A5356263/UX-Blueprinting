# 页面生命周期与归档策略

- page_id: PG-RELATION-0002
- page_type: relation
- canonical_name: 页面生命周期与归档策略
- aliases: [page-lifecycle-policy]
- status: stable
- confidence: medium
- source_refs: [SRC-BIZ-0001, SRC-GDL-0001]
- related_pages:
  - knowledge/wiki/archive/archive-index.md
  - knowledge/wiki/log.md
  - knowledge/wiki/questions.md
  - knowledge/wiki/templates/synthesis-template.md
- created_at: 2026-04-09
- updated_at: 2026-04-09

## 关系结论

- 页面状态应遵循 `draft -> stable -> deprecated -> archived` 的主路径，不建议跳级。
- `deprecated` 用于“仍可阅读但不再建议消费”，`archived` 用于“退出默认消费索引，仅归档保留”。
- `archive/` 是归档承接层，不是草稿池或临时输出池。

## 触发条件

- 进入 `draft`：
  - 新建页面但来源尚在补证
  - 结构已成型但冲突未裁决
- 进入 `stable`：
  - `source_refs` 完整且可追溯
  - 关键边界已写清，冲突已显式标注
  - 已纳入 `index.md` 可稳定导航
- 进入 `deprecated`：
  - 页面结论被新页面替代
  - 页面结构仍有参考价值但不再作为默认口径
  - 需要在原页标明替代页
- 进入 `archived`：
  - 页面已不再被主项目默认消费
  - 内容仅用于历史追踪或审计
  - 已在 `archive/archive-index.md` 登记入口

## 执行动作

- 当状态从 `stable` 变更为 `deprecated`：
  - 更新页面状态字段
  - 在页面顶部标注替代页
  - 写入 `wiki/log.md`
- 当状态从 `deprecated` 变更为 `archived`：
  - 页面移动到 `wiki/archive/` 或在归档索引登记
  - 从默认索引导航中下架
  - 写入 `wiki/log.md` 并提供 rollback_hint

## 风险控制

- 未写日志不得执行批量归档。
- 未给出替代页不得直接将稳定页标为 `deprecated`。
- 有未裁决冲突时，不应以归档方式掩盖争议。
