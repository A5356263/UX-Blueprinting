# WBS：Wiki 自动更新实施清单

## 1. 交付包 A：规则层

### A1. 新增 Wiki 同步合同

- 输出：
  - `specs/15_wiki_sync_contract.md`
  - `specs/16_wiki_sync_registry_contract.md`
  - `specs/17_wiki_sync_execution_contract.md`
- 内容：
  - 同步目标
  - 真源 / 编译层边界
  - 托管区块定义
  - 托管锚点格式
  - sync_mode 定义
  - deletion_policy 定义
  - 写回安全规则

### A2. 新增 Registry

- 输出：`knowledge/wiki_sync/registry.yaml`
- 内容：
  - domain 分组
  - raw -> page -> block 映射
  - extract_rule
  - create_policy
  - deletion_policy
  - priority

## 2. 交付包 B：执行层

### B1. 新增同步脚本

- 输出：`knowledge/scripts/sync_wiki_pages.py`
- 能力：
  - 读取 registry
  - 识别变更 raw
  - 解析 raw
  - 生成 block 内容
  - dry-run diff
  - apply 写回
  - 输出 report / state

### B2. 扩展统一入口

- 修改：`knowledge/scripts/update_wiki.py`
- 动作：
  - 在 `build_manifest.py` 后插入 `sync_wiki_pages.py`
  - 支持 dry-run / apply / strict 透传

## 3. 交付包 C：状态与报告

### C1. 新增状态文件

- 输出：`knowledge/outputs/reports/wiki_sync_state.json`
- 字段：
  - raw_path
  - raw_hash
  - target_page
  - block_id
  - last_sync_hash
  - last_sync_status
  - synced_at

### C2. 新增同步报告

- 输出：`knowledge/outputs/reports/wiki_sync_report.md`
- 内容：
  - changed raw
  - planned updates
  - applied updates
  - skipped updates
  - warnings
  - errors

## 4. 交付包 D：页面改造

### D1. 改造 Wiki 页模板

- 动作：在允许自动同步的页面插入托管锚点
- 范围：
  - `topics/*.md`
  - `concepts/*.md`
  - `entities/*.md`
  - `relations/*.md`
  - 现有 `knowledge/wiki/index.md`

### D2. 建立 block 原型

- 原型：
  - `evidence_sources`
  - `coverage_and_gaps`
  - `structure_breakdown`
  - `related_entries`
  - `upstream_downstream_links`

## 5. 交付包 E：校验层

### E1. 扩展 lint

- 修改：`knowledge/scripts/lint_wiki.py`
- 新增检查：
  - BEGIN / END 锚点完整性
  - block_id 唯一性
  - registry target page 存在性
  - registry block_id 与页面锚点一致性

### E2. 增量一致性检查

- 检查项：
  - raw_hash 是否变化
  - target_page 对应块是否已同步
  - state 与实际页面内容是否一致

## 6. 交付包 F：运行参数

### F1. CLI 参数

- `--dry-run`
- `--apply`
- `--only <raw-file>`
- `--strict`
- `--domain <name>`

## 7. 推荐实施顺序

1. A1
2. A2
3. B1
4. D1
5. C1
6. C2
7. B2
8. E1
9. E2
10. F1

## 8. 完成定义

- 合同存在且可被脚本消费
- registry 能描述至少一个 domain 的完整映射
- sync_wiki_pages.py 支持 dry-run / apply
- update_wiki.py 能一键编排完整链路
- 目标 Wiki 页仅更新托管区块
- 报告、状态、lint 可追踪

## 9. 本次修订说明

- spec 路径从 `knowledge/specs` 修正为根目录 `specs/`
- spec 文件拆分为 `specs/15_wiki_sync_contract.md`、`specs/16_wiki_sync_registry_contract.md`、`specs/17_wiki_sync_execution_contract.md`
- index 表述从 `indices/` 修正为现有 `knowledge/wiki/index.md`
