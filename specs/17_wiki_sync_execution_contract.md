# Wiki Sync Execution Contract

## 1. 目标

本合同用于约束 Wiki 自动同步执行层、状态文件、报告文件与统一入口编排方式。

## 2. 执行层文件

- `knowledge/scripts/sync_wiki_pages.py`
- `knowledge/scripts/update_wiki.py`
- `knowledge/scripts/auto_update_wiki.py`

## 3. 统一链路

```text
scan_raw.py
  -> build_manifest.py
  -> sync_wiki_pages.py
  -> reindex_wiki.py
  -> refresh_overview.py
  -> lint_wiki.py
```

## 4. 运行模式

### 4.1 dry-run

职责：

- 读取 registry
- 解析 raw
- 生成目标块内容
- 输出 diff 与计划
- 不写回文件

### 4.2 apply

职责：

- 先执行 dry-run
- 校验通过后写回托管块
- 更新 state
- 生成 report

## 5. 状态与报告

状态文件：

- `knowledge/outputs/reports/update_wiki_state.json`
- `knowledge/outputs/reports/wiki_sync_state.json`

同步报告：

- `knowledge/outputs/reports/pending_wiki_updates.md`
- `knowledge/outputs/reports/wiki_sync_report.md`

## 6. CLI 参数

- `--dry-run`
- `--apply`
- `--only <raw-file>`
- `--strict`
- `--domain <name>`

## 7. 不写回类错误

- target page 不存在且 `create_policy=must_exist`
- 锚点缺失
- 锚点不闭合
- registry 非法
- extract_rule 执行失败

## 8. 警告类错误

- raw 变化但无注册映射
- 映射存在但 block 内容未变化
- raw 删除后仅执行降级
