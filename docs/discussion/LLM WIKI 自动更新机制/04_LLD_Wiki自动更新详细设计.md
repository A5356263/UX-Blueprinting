# LLD：Wiki 自动更新详细设计

## 1. 目录设计

```text
specs/
  15_wiki_sync_contract.md
  16_wiki_sync_registry_contract.md
  17_wiki_sync_execution_contract.md
knowledge/
  wiki_sync/
    registry.yaml
  scripts/
    sync_wiki_pages.py
    update_wiki.py
  outputs/
    reports/
      wiki_sync_report.md
      wiki_sync_state.json
```

## 2. Registry 结构

```yaml
version: 1

domains:
  permission:
    enabled: true
    mappings:
      - raw_source: knowledge/raw/business/permission/15_page_carrier_semantics.md
        target_page: knowledge/wiki/topics/page-carrier-semantics-map.md
        page_type: topic
        block_id: structure_breakdown
        sync_mode: replace_block
        extract_rule: permission.page_group_inventory
        deletion_policy: mark_gap
        create_policy: must_exist
        source_mode: single_source
        priority: 100
```

## 3. Block 模型

### 3.1 Block 元数据

- `block_id`
- `source`
- `mode`
- `managed_by=wiki_sync`

### 3.2 Block 类型

- `replace_block`
- `merge_unique_list`
- `status_only`
- `append_log`

首版只建议正式支持：

- `replace_block`
- `merge_unique_list`

## 4. 托管锚点规则

### 4.1 语法

```md
<!-- AUTO-SYNC:BEGIN block_id=evidence_sources source=knowledge/raw/business/permission/15_page_carrier_semantics.md mode=merge_unique_list -->
...
<!-- AUTO-SYNC:END block_id=evidence_sources -->
```

### 4.2 校验规则

- BEGIN / END 必须成对
- block_id 必须一致
- block_id 在单页唯一
- source 必须是相对路径
- mode 必须在合同允许列表内

## 5. 状态文件设计

```json
{
  "version": 1,
  "items": [
    {
      "raw_path": "knowledge/raw/business/permission/15_page_carrier_semantics.md",
      "raw_hash": "sha256:...",
      "target_page": "knowledge/wiki/topics/page-carrier-semantics-map.md",
      "block_id": "structure_breakdown",
      "output_hash": "sha256:...",
      "last_sync_status": "applied",
      "synced_at": "2026-04-17T10:00:00Z"
    }
  ]
}
```

## 6. 同步流程

### 6.1 计划阶段

1. 加载 registry
2. 读取 `update_wiki_state.json` / `wiki_sync_state.json`
3. 扫描 changed raw
4. 根据 registry 生成 update plan
5. 校验 target page / block / mode

### 6.2 编译阶段

1. 读取 raw 内容
2. 按 `extract_rule` 抽取结构化结果
3. 生成目标 block 文本
4. 进行规范化输出

### 6.3 写回阶段

1. 定位 target page
2. 精确匹配 BEGIN/END
3. 仅替换块内内容
4. 写回前生成 diff
5. 成功后更新 state

### 6.4 收尾阶段

1. 输出 `wiki_sync_report.md`
2. 触发 `reindex_wiki.py`
3. 触发 `refresh_overview.py`
4. 触发 `lint_wiki.py`

## 7. 抽取规则设计

### 7.1 抽取规则命名

格式：

`<domain>.<semantic_output>`

示例：

- `permission.page_group_inventory`
- `permission.evidence_sources`
- `permission.gap_summary`
- `permission.upstream_downstream_links`

### 7.2 抽取输出约束

抽取器输出必须是结构化中间结果，不直接自由生成整页文本。

推荐中间结构：

```json
{
  "page_groups": [],
  "page_names": [],
  "gaps": [],
  "sources": []
}
```

## 8. 错误处理

### 8.1 不写回类错误

- target page 不存在且 `create_policy=must_exist`
- 锚点缺失
- 锚点不闭合
- registry 非法
- extract_rule 执行失败

### 8.2 警告类错误

- raw 变化但无注册映射
- 映射存在但 block 内容未变化
- raw 删除后仅执行降级

## 9. Lint 细则

### 9.1 页面级

- 页面是否包含 `source_refs`
- page_type 是否存在
- 状态字段是否合法

### 9.2 同步级

- registry 声明的 target page 是否存在
- registry 声明的 block_id 是否存在
- 同一 target page 的 block_id 是否冲突
- source 与 registry 是否匹配

## 10. update_wiki.py 修改点

### 10.1 Steps 顺序

```python
steps_order = [
    "scan_raw.py",
    "build_manifest.py",
    "sync_wiki_pages.py",
    "reindex_wiki.py",
    "refresh_overview.py",
    "lint_wiki.py",
]
```

### 10.2 状态写入

- 原 `update_wiki_state.json` 继续保留总运行时间
- 新 `wiki_sync_state.json` 记录 block 级同步状态

## 11. 默认策略建议

### 11.1 create_policy

- `must_exist`
- `create_if_missing`

默认：`must_exist`

### 11.2 deletion_policy

- `mark_gap`
- `deprecated`
- `clear_block_keep_page`
- `skip_with_warning`

默认：`mark_gap`

### 11.3 source_mode

- `single_source`
- `multi_source_aggregate`

默认：`single_source`

## 12. 正式建议

- 一次性完成合同、registry、同步内核、状态文件、报告、lint 扩展
- 首版按全域通用架构实现，不为某个 raw 写特例
- 后续新增领域只补 registry 与页面锚点，不再改方法论

## 13. 本次修订说明

- spec 路径从 `knowledge/specs` 修正为根目录 `specs/`
- spec 文件拆分为 `specs/15_wiki_sync_contract.md`、`specs/16_wiki_sync_registry_contract.md`、`specs/17_wiki_sync_execution_contract.md`
- index 表述从 `indices/` 修正为现有 `knowledge/wiki/index.md`
