# 输出组织

## 1. 输出目录

统一输出到：

```text
help/
```

推荐结构：

```text
help/
├── README.md
├── _indexes/
│   ├── module-tree.md
│   ├── business-flows.md
│   ├── rules-index.md
│   └── dependency-map.md
├── _collection/
│   ├── coverage.md
│   ├── failed-items.md
│   └── process-log.md
├── assets/
│   ├── images/
│   └── videos/
└── modules/
    ├── module-a/
    │   ├── README.md
    │   └── article-name.md
    └── module-b/
        ├── README.md
        └── article-name.md
```

要求：

- 文章正文放到 `help/modules/`
- 顶层总目录放到 `help/README.md`
- 索引放到 `help/_indexes/`
- 采集过程记录放到 `help/_collection/`
- 图片和视频资源放到 `help/assets/`

## 2. 必备索引

采集完成后生成：

- `help/_indexes/module-tree.md`：帮助中心原始模块层级
- `help/_indexes/business-flows.md`：业务动作与页面映射
- `help/_indexes/rules-index.md`：页面明确写出的规则
- `help/_indexes/dependency-map.md`：前置、依赖和影响关系

## 3. 采集日志

采集日志只放在 `help/_collection/`。

### coverage.md

记录：

- 已访问模块
- 已访问文章
- 已识别图片
- 已识别视频
- 未访问入口
- 失败入口

### failed-items.md

推荐表格：

```md
| 类型 | 所属模块 | 页面 | 失败原因 | 已保留信息 | 建议补充 |
|---|---|---|---|---|---|
```

### process-log.md

记录关键采集过程说明，不要污染文章正文。
