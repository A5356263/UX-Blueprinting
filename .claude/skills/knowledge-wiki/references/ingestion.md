# 知识入库规则

本文件用于承接 `knowledge-ingestion` 的能力复刻。

## 当前前提

- `.claude/skills/knowledge-ingestion` 继续保留
- `knowledge-wiki` 只复刻其能力，不替换旧 skill
- 本文件约束的是 `knowledge-wiki/knowledge/` 下的入库行为

## 核心规则

- 把 `knowledge/raw/**` 当成事实来源
- 把 `knowledge/wiki/summaries/**` 当成路由卡，不当成正式知识
- 用最小但可复用的改动保留有效信息
- 先更新 raw，再刷新 wiki
- 用 `[GAP]`、`[CONFLICT]`、`[QUESTION]` 显式保留不确定性
- 过程残留要隔离，不要把它抄成正式知识

## 入库流程

1. 写入前先读目标区域
2. 从附近的 `README.md`、`knowledge/LLM.md`、`knowledge/wiki/index.md` 和邻近示例判断本地约定
3. 先给输入材料分类，再决定它是可沉淀知识、未决信息、过程残留还是噪音
4. 先决定落点，再优先合并，避免扩散
5. 先更新 raw，再用 `python knowledge/scripts/update_wiki.py --apply` 或 `--only <raw-file-path>` 刷新 wiki
6. 收尾前检查落点、命名、raw-summary 一致性和未决项

## 候选入库扫描

当输入来自 `knowledge/candidates/pending/**`，或涉及菜单、路径、权限、状态、字段、角色、流程、页面入口变化时，不得只更新候选文件中列出的“已知命中文件”。

必须基于以下线索做定向扫描：

- 涉及领域
- 影响对象
- 旧表述线索
- 新表述线索
- 已知命中文件
- 建议更新位置
- `[GAP] / [QUESTION] / [CONFLICT]`

扫描顺序：

1. 读取候选文件
2. 提取涉及领域、影响对象、旧表述线索、新表述线索、已知命中文件
3. 先读取候选文件中明确提到的 raw
4. 扫描涉及领域下的 `knowledge/raw/**`
5. 使用旧表述线索和新表述线索搜索 `knowledge/raw/**`
6. 检查相关 `knowledge/wiki/summaries/**`
7. 形成“必须更新 / 命中但不更新 / 暂不处理”的判断结果
8. 再执行 raw 更新和 wiki 同步

## 禁止事项

- 不要只改 summary，不改 raw
- 不要把 summary 当事实来源
- 不要为了有个地方放内容，就把上传材料整个塞进 `README.md`
- 不要恢复 `source_manifest`、`build_manifest`、旧 `topics`、registry 或额外映射层
- 不要让弱来源静默覆盖强来源
