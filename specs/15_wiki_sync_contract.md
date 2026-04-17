# Wiki Sync Contract

## 1. 目标

本合同用于约束 `knowledge/raw/**/*.md` 到 `knowledge/wiki/**/*.md` 的自动同步机制。

正式目标链路：

- 自动检测 raw 变更
- 自动生成同步计划与同步报告
- 自动更新已注册 Wiki 页的托管区块
- 自动重建 `knowledge/wiki/index.md`
- 自动刷新 `knowledge/wiki/overview.md`
- 自动执行 Wiki lint

## 2. 边界

- raw 是真源
- wiki 是编译层，不是镜像层
- 自动同步只允许写回托管区块
- 托管区块外内容视为人工区块，不得覆盖
- 未注册 target page 不得写回
- 未注册 raw 不得写回

## 3. 托管区块

托管区块是允许自动写回的最小同步单元。

约束：

- 仅区块内部可写
- `block_id` 在单页唯一
- BEGIN / END 必须成对
- `source` 必须为仓库相对路径
- `mode` 必须是合同允许值

推荐锚点格式：

```md
<!-- AUTO-SYNC:BEGIN block_id=structure_breakdown source=knowledge/raw/business/permission/15_page_carrier_semantics.md mode=replace_block -->
...auto content...
<!-- AUTO-SYNC:END block_id=structure_breakdown -->
```

## 4. 写回安全规则

- 无锚点不写
- 锚点不闭合不写
- registry 非法不写
- extract 失败不写
- dry-run 不写
- strict 模式下出现 warning 可直接失败

## 5. 不确定信息

同步器不得自由扩写未确认信息。

不确定信息必须保持为：

- `[GAP]`
- `[CONFLICT]`
- `[ASSUMPTION]`

## 6. 验收标准

- 修改已注册 raw 后，统一入口能识别变更
- 已注册 target page 的托管区块能自动更新
- 未注册页不被误更新
- 人工区块不被覆盖
- raw 删除后按策略降级
- `knowledge/wiki/index.md`、`knowledge/wiki/overview.md`、lint 继续通过
