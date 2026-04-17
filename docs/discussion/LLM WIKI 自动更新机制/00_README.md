# Wiki 自动更新体系优化文档（目录）

## 文档列表

- [01_HLD_Wiki自动更新体系总设计.md](./01_HLD_Wiki自动更新体系总设计.md)
- [02_Impact_Analysis_Wiki自动更新体系影响分析.md](./02_Impact_Analysis_Wiki自动更新体系影响分析.md)
- [03_WBS_Wiki自动更新实施清单.md](./03_WBS_Wiki自动更新实施清单.md)
- [04_LLD_Wiki自动更新详细设计.md](./04_LLD_Wiki自动更新详细设计.md)

## 适用范围

用于在现有 `knowledge/wiki/` 子系统上补齐：

`RAW 改动 -> 自动检测 -> 自动报告 -> 自动重建索引 -> 自动更新具体 Wiki 页`

## 当前基线

现有统一入口已具备以下能力：

- 扫描 `knowledge/raw/**/*.md`
- 重建 `source_manifest.generated.md`
- 重建 `knowledge/wiki/index.md`
- 刷新 `knowledge/wiki/overview.md`
- 输出 `pending_wiki_updates.md`
- 执行基础 lint

当前缺失能力：

- 将 raw 变化稳定编译到 `topics/`、`entities/`、`concepts/`、`relations/` 等具体 Wiki 页
- 只更新托管区块并保留人工区块
- 基于 registry 做 1:N 映射与增量同步
- 记录同步状态、生成同步报告、支持 dry-run / apply
