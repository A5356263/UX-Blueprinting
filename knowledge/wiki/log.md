# Knowledge Wiki Log

## LOG-2026-04-09-0001

- log_id: LOG-2026-04-09-0001
- timestamp: 2026-04-09T00:00:00+08:00
- action_type: ingest
- operator: ai
- touched_files:
  - knowledge/raw/business/*
  - knowledge/raw/guidelines/*
  - knowledge/raw/manifests/source_manifest.md
- summary: 完成既有业务与指南真源向 raw 层归位，并初始化来源清单。
- reason: 按 Wiki 子系统 v2 规范完成改造步骤 1-3。
- risk_level: medium
- rollback_hint: 可从 git 还原 `knowledge/raw/` 与 `source_manifest.md` 到改造前状态。

## LOG-2026-04-09-0002

- log_id: LOG-2026-04-09-0002
- timestamp: 2026-04-09T00:00:00+08:00
- action_type: update
- operator: ai
- touched_files:
  - knowledge/README.md
  - knowledge/LLM.md
  - knowledge/wiki/index.md
  - knowledge/wiki/overview.md
  - knowledge/wiki/questions.md
- summary: 初始化 Wiki 系统页与子系统合同文件。
- reason: 按 Wiki 子系统 v2 规范完成改造步骤 4、8、9。
- risk_level: low
- rollback_hint: 可从 git 还原对应系统文件。

## LOG-2026-04-09-0003

- log_id: LOG-2026-04-09-0003
- timestamp: 2026-04-09T00:00:00+08:00
- action_type: lint
- operator: ai
- touched_files:
  - knowledge/scripts/scan_raw.py
  - knowledge/scripts/build_manifest.py
  - knowledge/scripts/lint_wiki.py
  - knowledge/scripts/refresh_overview.py
  - knowledge/scripts/reindex_wiki.py
- summary: 建立 scripts 骨架并提供最小可执行检查能力。
- reason: 按 Wiki 子系统 v2 规范完成改造步骤 7、11。
- risk_level: low
- rollback_hint: 删除脚本骨架并恢复先前目录状态。

## LOG-2026-04-09-0004

- log_id: LOG-2026-04-09-0004
- timestamp: 2026-04-09T00:30:00+08:00
- action_type: update
- operator: ai
- touched_files:
  - knowledge/wiki/concepts/*
  - knowledge/wiki/entities/permission-detail-view.md
  - knowledge/wiki/topics/*
  - knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md
  - knowledge/wiki/index.md
- summary: 为核心 Wiki 内容页补齐 page_id/page_type/source_refs 等元数据，并修正原始来源路径到 raw 层。
- reason: 推进 Wiki 从可用状态进入稳定状态，提升可追溯性与长期维护能力。
- risk_level: low
- rollback_hint: 可按文件粒度回滚本批内容页头部元数据与来源路径修正。

## LOG-2026-04-09-0005

- log_id: LOG-2026-04-09-0005
- timestamp: 2026-04-09T00:40:00+08:00
- action_type: lint
- operator: ai
- touched_files:
  - knowledge/scripts/reindex_wiki.py
  - knowledge/wiki/index.md
  - knowledge/wiki/overview.md
  - knowledge/outputs/lint/latest_lint_report.md
- summary: 扩展重建索引脚本纳入 indices，并完成重建与健康检查，missing_source_refs 归零。
- reason: 完善独立 Wiki 体系的索引可达性与自检闭环。
- risk_level: low
- rollback_hint: 可回滚脚本和系统页到上一版本并重跑脚本恢复。

## LOG-2026-04-09-0006

- log_id: LOG-2026-04-09-0006
- timestamp: 2026-04-09T01:10:00+08:00
- action_type: update
- operator: ai
- touched_files:
  - knowledge/wiki/topics/permission-domain-index.md
  - knowledge/wiki/index.md
  - knowledge/wiki/concepts/*
  - knowledge/wiki/entities/permission-detail-view.md
  - knowledge/wiki/topics/*
  - knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md
  - knowledge/scripts/reindex_wiki.py
  - knowledge/wiki/index.md
- summary: 对齐 v2 规范目录，移除 `wiki/indices/`，将权限域索引页迁移至 `wiki/topics/` 并批量修复链接。
- reason: 消除目录结构与规范定义差异，降低后续维护与脚本分叉风险。
- risk_level: low
- rollback_hint: 可恢复 `wiki/indices/` 并将索引页迁回原目录后重跑 reindex 脚本。

## LOG-2026-04-09-0007

- log_id: LOG-2026-04-09-0007
- timestamp: 2026-04-09T01:40:00+08:00
- action_type: update
- operator: ai
- touched_files:
  - knowledge/wiki/synthesis/permission-configuration-chain-synthesis.md
  - knowledge/wiki/synthesis/governance-mode-synthesis.md
  - knowledge/wiki/archive/archive-index.md
  - knowledge/wiki/templates/synthesis-template.md
  - knowledge/scripts/reindex_wiki.py
  - knowledge/wiki/questions.md
- summary: 补齐首批 synthesis 综合页、archive 索引页与 synthesis 模板，并扩展索引脚本覆盖 templates/archive。
- reason: 推进 Wiki 从结构完整进入知识闭环完整，补齐长期维护页型能力。
- risk_level: low
- rollback_hint: 可按新增页逐个回滚，脚本回滚后重建 index 即可恢复。

## LOG-2026-04-09-0008

- log_id: LOG-2026-04-09-0008
- timestamp: 2026-04-09T02:00:00+08:00
- action_type: update
- operator: ai
- touched_files:
  - knowledge/wiki/relations/page-lifecycle-and-archive-policy.md
  - knowledge/wiki/templates/archive-record-template.md
  - knowledge/wiki/questions.md
  - knowledge/scripts/reindex_wiki.py
- summary: 补齐页面生命周期与归档策略规则页，并新增 archive 记录模板。
- reason: 建立 deprecated/archived 分级规则和触发条件，完善归档治理机制。
- risk_level: low
- rollback_hint: 可回滚新增规则页与模板，再重建 index 恢复前状态。

## LOG-2026-04-09-0009

- log_id: LOG-2026-04-09-0009
- timestamp: 2026-04-09T02:20:00+08:00
- action_type: update
- operator: ai
- touched_files:
  - knowledge/wiki/entities/data-authorization-page.md
  - knowledge/wiki/entities/query-by-role-result-view.md
  - knowledge/wiki/entities/query-by-permission-result-view.md
  - knowledge/wiki/entities/query-by-feature-result-view.md
  - knowledge/wiki/topics/data-permission-gaps-backlog.md
  - knowledge/wiki/questions.md
- summary: 搭建数据权限相关骨架页，覆盖数据授权页与三类查询结果承接页，并新增待补清单。
- reason: 在 Raw 细节未补齐前先建立正式承接骨架，确保后续可增量填充且不破坏体系结构。
- risk_level: low
- rollback_hint: 可删除新增骨架页并重建 index 恢复到上一状态。

## LOG-2026-04-09-0010

- log_id: LOG-2026-04-09-0010
- timestamp: 2026-04-09T02:35:00+08:00
- action_type: update
- operator: ai
- touched_files:
  - knowledge/wiki/topics/data-permission-gaps-backlog.md
- summary: 明确数据权限边界，确认“概念与关系已具备，当前仅缺页面架构层真源信息”。
- reason: 对齐当前维护范围，避免误判为概念层缺失，便于后续 Raw 定向补充。
- risk_level: low
- rollback_hint: 可回滚 backlog 页最后一次改动并重建索引。

## LOG-2026-04-09-0011

- log_id: LOG-2026-04-09-0011
- timestamp: 2026-04-09T03:00:00+08:00
- action_type: update
- operator: ai
- touched_files:
  - knowledge/scripts/update_wiki.py
  - knowledge/outputs/reports/pending_wiki_updates.md
  - knowledge/outputs/reports/update_wiki_state.json
- summary: 新增 Wiki 总开关编排器，串联机械更新链路并自动产出 AI 待处理清单。
- reason: 将子系统从“多脚本手动触发”升级为“一键编排+语义待办输出”的可持续维护模式。
- risk_level: low
- rollback_hint: 回滚编排器并继续使用单脚本手动执行链路。

## LOG-2026-04-09-0012

- log_id: LOG-2026-04-09-0012
- timestamp: 2026-04-09T03:20:00+08:00
- action_type: update
- operator: ai
- touched_files:
  - knowledge/scripts/auto_update_wiki.py
  - knowledge/scripts/run_auto_update_wiki.ps1
  - knowledge/scripts/install_wiki_autoupdate_task.ps1
  - knowledge/scripts/uninstall_wiki_autoupdate_task.ps1
  - knowledge/README.md
  - knowledge/LLM.md
- summary: 新增无人值守自动更新守护脚本与系统任务安装脚本，且补齐子系统运行说明与 AI 消费入口。
- reason: 在不改主链路、不进入 packages 的前提下，实现 Wiki 子系统内部自动触发与可持续维护。
- risk_level: low
- rollback_hint: 卸载系统任务并删除新增脚本，恢复为手动运行 update_wiki.py。

## LOG-2026-04-09-0013

- log_id: LOG-2026-04-09-0013
- timestamp: 2026-04-09T03:35:00+08:00
- action_type: manual override
- operator: ai
- touched_files:
  - knowledge/scripts/install_wiki_autoupdate_task.ps1
  - knowledge/scripts/uninstall_wiki_autoupdate_task.ps1
  - knowledge/scripts/auto_update_wiki.py
  - knowledge/README.md
- summary: 为自动触发安装脚本增加权限不足降级策略（启动项回退），并避免 manifests 变更触发循环更新。
- reason: 提升无人值守在普通权限环境中的可用性与稳定性，防止守护进程自触发抖动。
- risk_level: low
- rollback_hint: 回滚安装脚本与监听脚本到前一版本，改回纯计划任务方案。
## LOG-2026-04-18-0001

- log_id: LOG-2026-04-18-0001
- timestamp: 2026-04-18T23:55:00+08:00
- action_type: migration
- operator: ai
- touched_files:
  - knowledge/README.md
  - knowledge/LLM.md
  - knowledge/wiki/README.md
  - knowledge/wiki/index.md
  - knowledge/wiki/overview.md
  - knowledge/wiki/questions.md
  - knowledge/wiki/summaries/**
  - knowledge/scripts/build_summaries.py
  - knowledge/scripts/refresh_questions.py
  - knowledge/scripts/reindex_wiki.py
  - knowledge/scripts/refresh_overview.py
  - knowledge/scripts/lint_wiki.py
  - knowledge/scripts/update_wiki.py
  - knowledge/scripts/auto_update_wiki.py
  - knowledge/scripts/sync_wiki_pages.py
  - knowledge/wiki_sync/registry.yaml
  - specs/07_wiki_contract.md
  - specs/15_wiki_sync_contract.md
  - specs/16_wiki_sync_registry_contract.md
  - specs/17_wiki_sync_execution_contract.md
- summary: 将 Knowledge Wiki 从重型 compiled page 加 registry sync 机制迁移为 summary-first 轻量入口机制，并物理移除旧页型目录与 heavy-sync 文件。
- reason: 对齐 2026-04-18 的轻量化方案，统一为 raw -> summary -> system pages 的默认链路。
- risk_level: medium
- rollback_hint: 如需回退，只能依赖 Git 历史恢复旧目录、旧脚本与旧 specs；当前仓库不再保留 legacy 兼容层。
