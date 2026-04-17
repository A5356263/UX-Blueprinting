# Wiki 合同

## 目标

定义 `knowledge/wiki/` 中页面的正式页面类型、结构合同与显式标记规则。

## 页面类型

当前定义五类页面：

- Entity Page
- Concept Page
- Topic Page
- Relation Page
- Index Page

## 路径建议

- `knowledge/wiki/entities/<slug>.md`
- `knowledge/wiki/concepts/<slug>.md`
- `knowledge/wiki/topics/<slug>.md`
- `knowledge/wiki/relations/<slug>.md`
- `knowledge/wiki/index.md`

## 通用页面合同

所有 Wiki 页面建议包含以下栏目：

1. 文件定位
2. 结论
3. 适用范围与边界
4. 主体内容
5. 关键关系
6. 证据与来源
7. 关联页面
8. 缺口与冲突
9. 变更记录

## 标记规范

允许使用以下标记：

- `[GAP]`
- `[CONFLICT]`
- `[ASSUMPTION]`
- `[DEPRECATED]`

要求：

- `[GAP]` 必须说明缺失的是什么
- `[CONFLICT]` 必须指出冲突双方或冲突来源
- `[ASSUMPTION]` 不得伪装成最终结论

## 与主链路的边界

Wiki 页面承担：

- 长期知识沉淀
- 跨任务复用
- 概念统一
- 上下文压缩

Wiki 页面不承担：

- 替代 `facts.md`
- 替代业务蓝图
- 替代体验蓝图
- 替代视觉设计稿
