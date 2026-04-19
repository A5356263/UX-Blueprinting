# LLD｜Knowledge Wiki 轻量化优化技术细节

## 1. 技术目标

将当前 Wiki 自动维护链路从：

```text
raw -> registry -> block sync -> compiled wiki pages
```

切换为：

```text
raw -> mirrored summary -> system pages -> raw on demand
```

并保留一个轻关系层：

```text
summary -> related summaries (weak links)
```

本次技术方案同时要求：

- 物理删除旧页型目录
- 物理删除 heavy-sync 机制
- 不提供 legacy 兼容路径

---

## 2. 目录方案

### 2.1 新默认目录结构

```text
knowledge/
  raw/
    business/
      permission/
    guidelines/

  wiki/
    index.md
    overview.md
    questions.md
    log.md

    summaries/
      business/
        permission/
          *.md
      guidelines/
        *.md
        principles/
          */principles.md
```

### 2.2 需物理删除的目录

```text
knowledge/wiki/concepts/
knowledge/wiki/entities/
knowledge/wiki/topics/
knowledge/wiki/relations/
knowledge/wiki/synthesis/
```

### 2.3 需物理删除的 heavy-sync 文件

```text
knowledge/wiki_sync/registry.yaml
knowledge/scripts/sync_wiki_pages.py
specs/15_wiki_sync_contract.md
specs/16_wiki_sync_registry_contract.md
specs/17_wiki_sync_execution_contract.md
```

### 2.4 路径映射规则

原始文件与摘要文件采用**镜像路径**：

```text
summary_path = knowledge/wiki/summaries/<relative_path_under_raw>
```

示例：

```text
knowledge/raw/business/permission/10_capability_map.md
-> knowledge/wiki/summaries/business/permission/10_capability_map.md

knowledge/raw/guidelines/task_type_index.md
-> knowledge/wiki/summaries/guidelines/task_type_index.md
```

约束：

- 仅处理 `.md`
- `raw/manifests/**` 不进入 summary 镜像
- `raw/inbox/**` 可选进入 `summaries/inbox/**`
- summary 文件名与 raw 完全一致

---

## 3. Summary 页面合同

### 3.1 头部字段

每个 summary 至少包含：

- `page_id`
- `page_type: summary`
- `source_path`
- `source_group`
- `status`
- `confidence`
- `updated_at`
- `source_refs`
- `related_summaries`

### 3.2 正文结构

建议固定为：

1. 这份原始资料讲什么
2. 适用范围 / 不适用范围
3. 关键事实
4. 关键术语 / 关键对象
5. 当前缺口 / 冲突 / 问题
6. 相关摘要 / 建议继续阅读

### 3.3 页面示例

```md
# 15_page_carrier_semantics

- page_id: PG-SUMMARY-BIZ-PERM-0015
- page_type: summary
- source_path: knowledge/raw/business/permission/15_page_carrier_semantics.md
- source_group: business
- status: active
- confidence: medium
- updated_at: 2026-04-18
- source_refs: [knowledge/raw/business/permission/15_page_carrier_semantics.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/13_route_map.md
  - knowledge/wiki/summaries/business/permission/31_experience_translation_requirements.md

## 1. 资料摘要
...

## 2. 适用范围 / 非适用范围
...

## 3. 关键事实
...

## 4. 关键术语 / 关键对象
...

## 5. 当前缺口 / 冲突 / 问题
- [GAP] ...
- [QUESTION] ...

## 6. 相关摘要
- ...
```

---

## 4. 构建脚本设计

### 4.1 `build_summaries.py`

职责：

- 扫描 `knowledge/raw/**/*.md`
- 忽略 `raw/manifests/**`
- 为每个 raw 构建同名 summary
- 支持 dry-run / apply / only
- 生成 summary 构建报告

CLI：

```text
python knowledge/scripts/build_summaries.py --dry-run
python knowledge/scripts/build_summaries.py --apply
python knowledge/scripts/build_summaries.py --only knowledge/raw/business/permission/15_page_carrier_semantics.md
```

### 4.2 摘要抽取策略

第一版只做**轻抽取**：

- 取标题
- 取前部定位段
- 取显式列表项
- 取显式 `[GAP] / [CONFLICT] / [QUESTION]`
- 生成相关摘要候选

不做：

- entity 抽取
- relation 编译
- 复杂知识建模
- 多文件综合裁决

### 4.3 related summaries 生成

第一版优先级：

1. 人工指定字段
2. 同目录相邻文件
3. index 中相邻入口
4. 同一 raw 包内被显式提及的文件名

约束：

- 单页最多 5 个
- 不做评分图谱
- 不生成独立关系页

---

## 5. 系统页脚本设计

### 5.1 `reindex_wiki.py`

输入：

- `knowledge/wiki/summaries/**`

输出：

- `knowledge/wiki/index.md`

结构建议：

```text
# Knowledge Wiki Index

## business
### permission
- [00_domain_overview](summaries/business/permission/00_domain_overview.md)
- ...

## guidelines
- [task_type_index](summaries/guidelines/task_type_index.md)
- ...
```

### 5.2 `refresh_overview.py`

输入：

- raw 总文件数
- summary 总文件数
- 显式 `[GAP] / [CONFLICT] / [QUESTION]`

输出：

- `knowledge/wiki/overview.md`

只保留机械字段，不做语义裁决。

### 5.3 `refresh_questions.py`

输入：

- raw
- summaries

抽取：

- `[GAP]`
- `[CONFLICT]`
- `[QUESTION]`

输出：

- `knowledge/wiki/questions.md`

问题项最小字段：

- `question_id`
- `source_path`
- `summary_path`（可空）
- `question_type`
- `text`
- `updated_at`

---

## 6. 统一编排入口

### 6.1 新链路

```text
scan_raw.py
  -> build_manifest.py
  -> build_summaries.py
  -> reindex_wiki.py
  -> refresh_overview.py
  -> refresh_questions.py
  -> lint_wiki.py
```

### 6.2 `update_wiki.py` 修改点

需要：

- 删除 `sync_wiki_pages.py` 步骤
- 删除 `--domain` 等 heavy-sync 透传语义
- 将报告改为：
  - changed raw
  - updated summaries
  - index refresh
  - overview refresh
  - questions refresh
  - lint result

### 6.3 `auto_update_wiki.py` 修改点

需要：

- 触发新链路
- 不再依赖 registry / block sync
- 仅关注 raw -> summary 更新

---

## 7. lint 设计

### 7.1 删除旧检查

移除：

- AUTO-SYNC 锚点检查
- registry block 检查
- managed block 一致性检查

### 7.2 新增检查

新增：

- 每个 raw 是否有对应 summary
- summary 头部字段是否完整
- `source_path` 是否存在
- `related_summaries` 是否存在坏链
- `index.md` 是否仅索引 summaries
- `overview.md / questions.md` 是否可生成

---

## 8. 迁移与删除顺序

### 8.1 顺序

1. 修订合同与 README  
2. 新建 `summaries/`  
3. 构建全部 summary  
4. 切换 `index / overview / questions / lint` 到新链路  
5. 删除 heavy-sync 文件  
6. 删除旧页型目录  
7. 删除文档中的旧引用  

### 8.2 删除方式

要求直接删除，不做保留目录：

- `git rm knowledge/wiki/concepts`
- `git rm knowledge/wiki/entities`
- `git rm knowledge/wiki/topics`
- `git rm knowledge/wiki/relations`
- `git rm knowledge/wiki/synthesis`
- `git rm knowledge/wiki_sync/registry.yaml`
- `git rm knowledge/scripts/sync_wiki_pages.py`
- `git rm specs/15_wiki_sync_contract.md`
- `git rm specs/16_wiki_sync_registry_contract.md`
- `git rm specs/17_wiki_sync_execution_contract.md`

历史回溯依赖 Git。

---

## 9. 验收标准

### 9.1 结构验收

- 仓库中不存在旧页型目录
- 仓库中不存在 heavy-sync registry / script / specs
- `knowledge/wiki/` 默认只保留：
  - `summaries/`
  - `index.md`
  - `overview.md`
  - `questions.md`
  - `log.md`

### 9.2 行为验收

- 改动任意 raw 后，同名 summary 会更新
- index 自动更新
- overview 自动更新
- questions 自动更新
- permission 与 guidelines 两类 raw 都可被覆盖

### 9.3 消费验收

- LLM 默认从 index 进入
- 先读 summary
- 必要时回 raw
- 不再依赖 entity / relation / topic 页型
