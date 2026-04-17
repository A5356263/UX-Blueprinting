# Wiki Sync Registry Contract

## 1. 目标

本合同用于约束 `knowledge/wiki_sync/registry.yaml` 的正式结构与允许值。

## 2. Registry 角色

- registry 是自动同步白名单
- registry 描述 raw -> target page -> block 的映射关系
- 未注册映射不得写回 Wiki 页

## 3. 每条映射必含字段

- `raw_source`
- `target_page`
- `page_type`
- `block_id`
- `sync_mode`
- `extract_rule`
- `deletion_policy`
- `create_policy`
- `source_mode`
- `priority`

## 4. 路径约束

- `raw_source` 必须是仓库相对路径
- `target_page` 必须是仓库相对路径
- `target_page` 应指向现有 `knowledge/wiki/**/*.md`
- index 系统页继续沿用 `knowledge/wiki/index.md`

## 5. sync_mode

首版正式支持：

- `replace_block`
- `merge_unique_list`

说明：

- `replace_block`：整块替换为本次编译内容
- `merge_unique_list`：合并块内 Markdown 列表并去重

## 6. deletion_policy

首版允许：

- `mark_gap`
- `deprecated`
- `clear_block_keep_page`
- `skip_with_warning`

默认建议：

- `mark_gap`

## 7. create_policy

允许值：

- `must_exist`
- `create_if_missing`

默认建议：

- `must_exist`

## 8. source_mode

允许值：

- `single_source`
- `multi_source_aggregate`

默认建议：

- `single_source`
