# HLD：Wiki 自动更新体系总设计

## 1. 目标

在现有 Wiki 子系统上补齐正式同步链路，使用户仅修改 `knowledge/raw/**/*.md` 后，执行统一入口即可完成：

- 变更检测
- 同步计划生成
- 具体 Wiki 页托管区块更新
- `knowledge/wiki/index.md` 重建
- `knowledge/wiki/overview.md` 刷新
- lint 校验
- 同步状态与报告输出

## 2. 设计结论

### 2.1 总体策略

采用：

- **托管区块同步**
- **registry 配置驱动**
- **统一同步内核**
- **统一入口编排**
- **增量状态记录**
- **失败不写回**

不采用：

- 整页全量重写
- 针对单一 raw 的特例脚本
- 无锚点的模糊覆盖
- 无报告直接写回

### 2.2 架构定位

系统分为 4 层：

1. **真源层**：`knowledge/raw/**/*.md`
2. **同步规则层**：`specs/15_wiki_sync_contract.md` + `specs/16_wiki_sync_registry_contract.md` + `specs/17_wiki_sync_execution_contract.md` + `knowledge/wiki_sync/registry.yaml`
3. **同步执行层**：`knowledge/scripts/sync_wiki_pages.py`
4. **消费层**：`knowledge/wiki/**/*.md`

### 2.3 设计原则

- raw 是真源
- wiki 是编译层，不是镜像层
- 自动更新只允许 block 级写回
- block 必须有托管锚点
- target page 必须在 registry 白名单中
- 不确定信息保留 `[GAP] / [CONFLICT] / [ASSUMPTION]`
- raw 删除默认不删 wiki 页，只做降级
- 统一入口先 dry-run，可选择 apply

## 3. 目标链路

```text
scan_raw.py
  -> build_manifest.py
  -> sync_wiki_pages.py
  -> reindex_wiki.py
  -> refresh_overview.py
  -> lint_wiki.py
```

## 4. 核心对象

### 4.1 托管区块

定义：允许自动写回的最小同步单元。

约束：

- 仅块内可写
- 块外人工内容不可写
- block_id 在单页内唯一

### 4.2 托管锚点

推荐格式：

```md
<!-- AUTO-SYNC:BEGIN block_id=structure_breakdown source=knowledge/raw/business/permission/15_page_carrier_semantics.md mode=replace_block -->
...auto content...
<!-- AUTO-SYNC:END block_id=structure_breakdown -->
```

### 4.3 Registry 映射

每条映射描述：

- `raw_source`
- `target_page`
- `page_type`
- `block_id`
- `sync_mode`
- `extract_rule`
- `deletion_policy`
- `create_policy`
- `priority`

## 5. 正式产物

### 5.1 新增文件

- `specs/15_wiki_sync_contract.md`
- `specs/16_wiki_sync_registry_contract.md`
- `specs/17_wiki_sync_execution_contract.md`
- `knowledge/wiki_sync/registry.yaml`
- `knowledge/scripts/sync_wiki_pages.py`
- `knowledge/outputs/reports/wiki_sync_report.md`
- `knowledge/outputs/reports/wiki_sync_state.json`

### 5.2 修改文件

- `knowledge/scripts/update_wiki.py`
- 需纳入托管同步的 Wiki 页模板
- `knowledge/scripts/lint_wiki.py`

## 6. 运行模式

### 6.1 dry-run

职责：

- 读取 registry
- 解析 raw
- 生成目标块内容
- 输出 diff 与计划
- 不写回文件

### 6.2 apply

职责：

- 先执行 dry-run
- 校验通过后写回托管块
- 更新 state
- 生成 report

## 7. 非目标

本次不做：

- 视觉稿生成
- 页面结构图渲染
- 主链路产物替代
- 自由文本 AI 改写全页
- 自动裁决业务冲突

## 8. 验收标准

- 修改任意已注册 raw 后，统一入口能识别变更
- 已注册 target page 的托管区块被自动更新
- 未注册 page 不被误更新
- 人工区块不被覆盖
- raw 删除后页面按策略降级
- `knowledge/wiki/index.md`、`knowledge/wiki/overview.md`、lint 继续通过

## 9. 本次修订说明

- spec 路径从 `knowledge/specs` 修正为根目录 `specs/`
- spec 文件拆分为 `specs/15_wiki_sync_contract.md`、`specs/16_wiki_sync_registry_contract.md`、`specs/17_wiki_sync_execution_contract.md`
- index 表述从 `indices/` 修正为现有 `knowledge/wiki/index.md`
