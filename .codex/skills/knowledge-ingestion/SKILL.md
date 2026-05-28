---
name: knowledge-ingestion
description: Safely ingest non-standard materials into this repository's knowledge system without polluting the source of truth. Use when Codex needs to merge help-center articles, product docs, operation guides, FAQ, screenshot or video analysis, meeting notes, requirement drafts, or external references into `knowledge/` while preserving the repository's Chinese naming, raw-as-source, and summary-first routing protocol.
---

# 知识入库

只有先弄清仓库里哪里是事实来源、哪里只是过程残留之后，才开始做知识入库。

## 使用流程

1. 写入前先读目标区域。
2. 从附近的 `README.md`、`knowledge/README.md`、`knowledge/LLM.md`、`knowledge/wiki/index.md`、相关 `specs/` 和邻近示例里判断本地约定。
3. 先给输入材料分类，再决定它是可沉淀知识、未决信息、过程残留还是噪音。
4. 先决定落点，再优先合并，避免扩散。
5. 先更新 raw，再用 `python knowledge/scripts/update_wiki.py --apply` 或 `--only <raw-file-path>` 刷新 wiki。
6. 收尾前检查落点、命名、raw-summary 一致性和未决项。

## 入库前 summary 状态检查

执行知识入库前，先读取：

`knowledge/outputs/reports/pending_semantic_summaries.md`

检查：

- `pending_generate`
- `pending_review`

如果二者均为 0，说明当前 summary 语义填充状态可作为入库判断参考。

如果存在待生成或待复核 summary：

- 不自动更新全部 summary。
- 先判断本次入库涉及领域是否命中待处理 summary。
- 如果命中，必须在最终汇报中说明风险。
- 如果影响本次入库判断，应先处理相关 summary 或暂停入库。

注意：

- 这里不是新增 `semantic_stale`。
- 这里不是自动补全所有 summary。
- 这里只是入库前的健康检查。

## 定向影响面扫描

当输入材料来自 `知识候选区/**`，或涉及菜单、路径、权限、状态、字段、角色、流程、页面入口变化时，不得只更新候选文件中列出的“已知命中文件”。

必须基于以下线索做定向扫描：

- 涉及领域
- 影响对象
- 旧表述线索
- 新表述线索
- 已知命中文件
- 建议更新位置
- `[GAP] / [QUESTION] / [CONFLICT]`

扫描顺序：

1. 读取候选文件。
2. 提取涉及领域、影响对象、旧表述线索、新表述线索、已知命中文件。
3. 先读取候选文件中明确提到的 raw。
4. 扫描涉及领域下的 `knowledge/raw/**`。
5. 使用旧表述线索和新表述线索搜索 `knowledge/raw/**`。
6. 检查相关 `knowledge/wiki/summaries/**`。
7. 如搜索结果命中邻近领域，再扩展读取邻近领域的 README、领域概述和命中文件。
8. 形成“必须更新 / 命中但不更新 / 暂不处理”的判断结果，用于执行与最终汇报。
9. 再执行 raw 更新和 wiki 同步。

候选文件提供的是扫描种子，不是完整更新边界。
这些判断结果只需要在任务结束时向用户汇报，不需要额外生成清单文件。

## 扫描范围控制

不要默认全库通读。

优先扫描：

1. 候选文件明确写出的涉及领域。
2. 候选文件明确写出的已知命中文件。
3. 旧表述线索命中的文件。
4. 新表述线索命中的文件。
5. 相关领域的 README、`00_领域概述`、同目录相关能力文件。
6. 被 summary `related_summaries` 指向的邻近文件。

只有在以下情况才扩大范围：

- 旧表述线索在多个领域命中。
- 变更涉及平台级菜单、全局入口、权限、组织、成员、审批等高复用基础能力。
- 候选文件中明确出现跨领域影响。
- 初始领域扫描发现明显外部依赖。

## 按需读取这些参考文件

- 需要确认 `knowledge/` 结构、命名协议、summary 元数据契约和 `source_refs` 规则时，读 [references/knowledge-protocol.md](references/knowledge-protocol.md)。
- 需要按输入类型处理帮助中心、操作指引、FAQ、截图、视频、会议纪要、需求草稿或知识候选区文件时，读 [references/input-adaptation.md](references/input-adaptation.md)。
- 收尾前，以及任务容易放错位置或违反约束时，读 [references/validation.md](references/validation.md)。

## 核心规则

- 把 `knowledge/raw/**` 当成事实来源。
- 把 `knowledge/wiki/summaries/**` 当成路由卡，不当成正式知识。
- 用最小但可复用的改动保留有效信息。
- 用 `[GAP]`、`[CONFLICT]`、`[QUESTION]` 显式保留不确定性。
- 过程残留要隔离，不要把它抄成正式知识。

## 禁止事项

- 不要只改 summary，不改 raw。
- 不要重建 `source_manifest`、`build_manifest`、旧 `wiki/topics`、registry 层或命名映射表。
- 不要为了有个地方放内容，就把上传材料整个塞进 `README.md`。
- 不要为了让编号看起来整齐就批量造文件。
- 不要让弱来源静默覆盖强来源。

## 最终汇报

简要说明：

- 合并了什么
- 跳过或暂缓了什么
- 是否执行了 wiki 同步
- 新增了哪些文件
- 哪些文件属于“必须更新 / 命中但不更新 / 暂不处理”
- 还剩哪些 `[GAP]`、`[CONFLICT]`、`[QUESTION]`
## Health Check Trigger

When this skill is used for knowledge ingestion, raw deletion sync, knowledge cleanup, or large-module ingestion, do a lightweight health check first:

1. Run `python knowledge/scripts/prune_orphan_summaries.py --dry-run`
2. If orphan summaries exist, list:
   - summary path
   - missing `source_path`
   - suggested action
3. Do not delete immediately; wait for user confirmation
4. After confirmation, run `python knowledge/scripts/update_wiki.py --apply --prune-orphans`
5. Then re-check `knowledge/outputs/reports/pending_semantic_summaries.md`
6. If summary sections 1-4 are semantically missing, only prompt; do not auto-fill by default

## Large Module Ingestion Trigger

When the new material cannot be merged stably into an existing domain, or a new business domain is needed:

1. Read `knowledge/raw/业务/README.md`
2. Read the target domain README or a nearby example
3. Read `knowledge/templates/业务知识入库/`
4. Distinguish:
   - `README.md`: template-directory guide
   - `README.template.md`: new-domain README template
5. Output a short ingestion plan before writing raw
6. Only write raw after user confirmation, then refresh wiki
