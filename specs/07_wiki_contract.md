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

- `source_path`
- `domain`
- `summary_role: light_route_card`
- `updated_at`

## Summary 正文结构

建议固定为：

1. 定位
2. 触发信号
3. 稳定结论
4. 已知缺口

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
