---
name: knowledge-ingestion
description: Safely ingest non-standard materials into this repository's knowledge system without polluting the source of truth. Use when Codex needs to merge help-center articles, product docs, operation guides, FAQ, screenshot or video analysis, meeting notes, requirement drafts, or external references into `knowledge/` while preserving the repository's Chinese naming, raw-as-source, and summary-first routing protocol.
---

# 知识入库

只有在先弄清仓库里哪里是事实来源、哪里只是过程残留之后，才开始做知识入库。

## 使用流程

1. 写入前先读目标区域。
2. 从附近的 `README.md`、`knowledge/README.md`、`knowledge/LLM.md`、`knowledge/wiki/index.md`、相关 `specs/` 和邻近示例里判断本地约定。
3. 先给输入材料分类，再决定它是可沉淀知识、未决信息、过程残留还是噪音。
4. 先决定落点，再优先合并，避免扩散。
5. 先更新 raw，再用 `python knowledge/scripts/update_wiki.py --apply` 或 `--only <raw-file-path>` 刷新 wiki。
6. 收尾前检查落点、命名、raw-summary 一致性和未决项。

## 按需读取这些参考文件

- 需要确认 `knowledge/` 结构、命名协议、summary 元数据契约和 `source_refs` 规则时，读 [references/knowledge-protocol.md](references/knowledge-protocol.md)。
- 需要按输入类型处理帮助中心、操作指南、FAQ、截图、视频、会议纪要或需求草稿时，读 [references/input-adaptation.md](references/input-adaptation.md)。
- 收尾前，以及任务容易放错位置或违反约束时，读 [references/validation.md](references/validation.md)。

## 核心规则

- 把 `knowledge/raw/**` 当成事实来源。
- 把 `knowledge/wiki/summaries/**` 当成路由卡，不当成正式知识。
- 用最小但可复用的改动保留有效信息。
- 用 `[GAP]`、`[CONFLICT]`、`[QUESTION]` 显式保留不确定性。
- 过程残留要隔离，不要把它抬成正式知识。

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
- 还剩哪些 `[GAP]`、`[CONFLICT]`、`[QUESTION]`
