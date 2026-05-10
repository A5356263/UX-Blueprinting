# Wiki 合同

## 目标

定义 `knowledge/wiki/` 的轻量页面结构、summary 合同与系统页边界。

## 页面类型

当前默认页面类型只有两类：

- System Page
- Summary Page

## 路径建议

- `knowledge/wiki/index.md`
- `knowledge/wiki/overview.md`
- `knowledge/wiki/questions.md`
- `knowledge/wiki/log.md`
- `knowledge/wiki/summaries/<relative_path_under_raw>.md`

## Summary 最小合同

每个 summary 至少包含以下头部字段：

- `page_id`
- `page_type: summary`
- `source_path`
- `source_group`
- `status`
- `confidence`
- `updated_at`
- `source_refs`
- `related_summaries`

## Summary 正文结构

建议固定为：

1. 这份原始资料讲什么
2. 适用范围 / 不适用范围
3. 关键事实
4. 关键术语 / 关键对象
5. 当前缺口 / 冲突 / 问题
6. 相关摘要 / 建议继续阅读

## 一对一镜像规则

summary 与 raw 必须保持：

- 同名
- 镜像路径
- 一对一对应

映射规则：

```text
knowledge/raw/业务/权限管理/15_页面载体语义.md
-> knowledge/wiki/summaries/业务/权限管理/15_页面载体语义.md
```

## 弱关系规则

`related_summaries` 仅表达阅读邻接关系。

约束：

- 单页建议 3 到 5 个链接
- 只链接存在的 summary
- 不表达 entity / relation / topic 级知识图谱关系

## 标记规范

允许使用以下显式标记：

- `[GAP]`
- `[CONFLICT]`
- `[QUESTION]`
- `[ASSUMPTION]`
- `[DEPRECATED]`

要求：

- `[GAP]` 必须说明缺失的是什么
- `[CONFLICT]` 必须指出冲突双方或冲突来源
- `[QUESTION]` 必须保留为未决项，不得伪装成结论
- `[ASSUMPTION]` 不得伪装成最终结论

## 系统页边界

### `index.md`

只做导航，默认只索引 `summaries/`。

### `overview.md`

只做机械统计，不做语义裁决。

### `questions.md`

只聚合 raw / summary 中显式出现的 `[GAP] / [CONFLICT] / [QUESTION]`。

### `log.md`

只做维护留痕。
