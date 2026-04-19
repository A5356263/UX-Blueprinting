# WBS｜Knowledge Wiki 轻量化优化执行清单

## 1. 执行目标

将当前 Wiki 子系统从“重型自动编译 + block 同步”切换为“轻量入口 + 一对一摘要 + 弱关系 + 机械状态”，并且**物理性移除旧页型与旧同步机制**。

本次执行不包含：

- 保留 `concepts / entities / topics / relations / synthesis` 作为 legacy
- 继续扩展 heavy-sync registry
- 为旧页型建立兼容层

---

## 2. 执行分组

- A. 定义与合同修订
- B. 目录与文件物理调整
- C. 脚本链路重构
- D. permission / guidelines 落地
- E. 弱关系机制落地
- F. 切流与验收

---

## A. 定义与合同修订

### A1. 修订 `knowledge/README.md`
- [ ] 将 Wiki 子系统默认职责改为“维护入口、摘要、弱关系、状态、问题池”
- [ ] 将“主项目默认只消费 `knowledge/wiki/`”改为“主项目先消费 Wiki 入口与摘要，必要时回查 raw”
- [ ] 删除“自动回写正文”作为默认目标的描述
- [ ] 新增 `wiki/summaries/` 目录说明
- [ ] 删除 `concepts / entities / topics / relations / synthesis` 的默认目录说明

### A2. 修订 `knowledge/LLM.md`
- [ ] 将 LLM 角色收缩为“摘要编译器 + 入口维护者 + 健康检查执行者”
- [ ] 删除默认抽 `concept / entity / topic / relation` 的动作
- [ ] 新增 summary-first / raw-on-demand 消费规则
- [ ] 明确 questions 仅聚合显式未决项
- [ ] 明确 overview 仅做机械统计
- [ ] 明确 related summaries 为页面级弱关系

### A3. 修订 `knowledge/wiki/README.md`
- [ ] 新增 `summaries/` 为默认知识页层
- [ ] 删除 `concepts / entities / topics / relations / synthesis` 的默认职责说明
- [ ] 删除“正式知识页网络”表述

### A4. 修订 `specs/07_wiki_contract.md`
- [ ] 将默认页面合同改为 `system + summary`
- [ ] 删除 `Entity / Concept / Topic / Relation` 的默认页型地位
- [ ] 新增 summary 页最小合同
- [ ] 新增 summary 与 raw 一对一关系说明
- [ ] 新增 related summaries 轻关系说明

### A5. 处理 heavy-sync specs
- [ ] 删除 `specs/15_wiki_sync_contract.md`
- [ ] 删除 `specs/16_wiki_sync_registry_contract.md`
- [ ] 删除 `specs/17_wiki_sync_execution_contract.md`
- [ ] 清理所有对这 3 份合同的引用

---

## B. 目录与文件物理调整

### B1. 新建默认目录
- [ ] 新建 `knowledge/wiki/summaries/`
- [ ] 新建 `knowledge/wiki/summaries/business/`
- [ ] 新建 `knowledge/wiki/summaries/guidelines/`

### B2. 物理删除旧页型目录
- [ ] 删除 `knowledge/wiki/concepts/`
- [ ] 删除 `knowledge/wiki/entities/`
- [ ] 删除 `knowledge/wiki/topics/`
- [ ] 删除 `knowledge/wiki/relations/`
- [ ] 删除 `knowledge/wiki/synthesis/`

### B3. 保留系统页
- [ ] 保留 `knowledge/wiki/index.md`
- [ ] 保留 `knowledge/wiki/overview.md`
- [ ] 保留 `knowledge/wiki/questions.md`
- [ ] 保留 `knowledge/wiki/log.md`

### B4. 清理旧模板与引用
- [ ] 评估 `templates/` 是否仍有必要
- [ ] 若无必要，删除与旧页型绑定的模板文件
- [ ] 清理 `index.md` 中旧目录段落
- [ ] 清理 README / docs 中旧目录示例

---

## C. 脚本链路重构

### C1. 重构 `update_wiki.py`
- [ ] 从编排链中移除 `sync_wiki_pages.py`
- [ ] 将统一链路改为：
  - `scan_raw.py`
  - `build_manifest.py`
  - `build_summaries.py`
  - `reindex_wiki.py`
  - `refresh_overview.py`
  - `refresh_questions.py`
  - `lint_wiki.py`

### C2. 新增摘要构建脚本
- [ ] 新增 `knowledge/scripts/build_summaries.py`
- [ ] 支持 raw -> summary 一对一镜像生成
- [ ] 支持 `business` 与 `guidelines`
- [ ] 支持 `--dry-run`
- [ ] 支持 `--only`
- [ ] 支持 `--apply`

### C3. 删除 heavy-sync 机制
- [ ] 删除 `knowledge/scripts/sync_wiki_pages.py`
- [ ] 删除 `knowledge/wiki_sync/registry.yaml`
- [ ] 清理 `auto_update_wiki.py` 中对 heavy-sync 的依赖
- [ ] 清理 `pending_wiki_updates.md` 中 registry 语义

### C4. 重构 `reindex_wiki.py`
- [ ] 默认只索引 `summaries/`
- [ ] 不再索引 `concepts / entities / topics / relations / synthesis`
- [ ] index 结构改为按 raw 镜像路径呈现摘要入口

### C5. 重构 `refresh_overview.py`
- [ ] 改为纯机械统计
- [ ] 统计 raw 总数
- [ ] 统计 summary 覆盖数
- [ ] 统计 `[GAP] / [CONFLICT] / [QUESTION]`
- [ ] 统计无 summary 的 raw
- [ ] 删除“冲突已解决 / 页面健康度”之类语义裁决字段

### C6. 新增或重构 `refresh_questions.py`
- [ ] 新增 `knowledge/scripts/refresh_questions.py`
- [ ] 从 raw / summary 中聚合显式 `[GAP] / [CONFLICT] / [QUESTION]`
- [ ] 输出统一问题池
- [ ] 不做推断式问题生成

### C7. 重构 `lint_wiki.py`
- [ ] 删除 AUTO-SYNC 锚点检查
- [ ] 删除 registry block 检查
- [ ] 新增 raw-summary 一对一映射检查
- [ ] 新增 summary 头部字段检查
- [ ] 新增 related summaries 链接存在性检查

---

## D. permission / guidelines 落地

### D1. permission 覆盖
- [ ] 为 `knowledge/raw/business/permission/*.md` 生成对应摘要
- [ ] 摘要路径镜像到 `knowledge/wiki/summaries/business/permission/*.md`
- [ ] 抽取关键事实、关键对象、gaps、related summaries

### D2. guidelines 覆盖
- [ ] 为 `knowledge/raw/guidelines/**/*.md` 生成对应摘要
- [ ] 摘要路径镜像到 `knowledge/wiki/summaries/guidelines/**/*.md`
- [ ] 适配索引型 raw 与正文型 raw

### D3. 原始入口页适配
- [ ] 在 `index.md` 中分别建立 business 与 guidelines 入口区
- [ ] 保证两类原始知识都能从总入口到达

---

## E. 弱关系机制落地

### E1. Summary 页面关系区
- [ ] 在 summary 页中新增“相关摘要 / 建议继续阅读”
- [ ] 控制在 3 到 5 个链接
- [ ] 只表达阅读邻接，不表达知识图谱关系

### E2. 关系生成策略
- [ ] 先支持人工维护 related summaries
- [ ] 再支持按目录与索引规则给出候选
- [ ] 不引入 registry / block sync

---

## F. 切流与验收

### F1. 物理删除验收
- [ ] 仓库中不存在 `knowledge/wiki/concepts/`
- [ ] 仓库中不存在 `knowledge/wiki/entities/`
- [ ] 仓库中不存在 `knowledge/wiki/topics/`
- [ ] 仓库中不存在 `knowledge/wiki/relations/`
- [ ] 仓库中不存在 `knowledge/wiki/synthesis/`
- [ ] 仓库中不存在 `knowledge/wiki_sync/registry.yaml`
- [ ] 仓库中不存在 `knowledge/scripts/sync_wiki_pages.py`
- [ ] 仓库中不存在 `specs/15/16/17`

### F2. 功能验收
- [ ] 改动任意 raw 后，可自动更新同名 summary
- [ ] `index.md` 可自动更新
- [ ] `overview.md` 可自动更新
- [ ] `questions.md` 可自动更新
- [ ] 无 heavy-sync 报告、registry、block 写回残留

### F3. 消费验收
- [ ] LLM 可先从 index 进入
- [ ] LLM 可先读 summary
- [ ] 需要细节时可继续回 raw
- [ ] permission 与 guidelines 两类路径都可跑通

---

## 3. 结论

本次执行不是“收缩旧机制”，而是**物理切换到新机制**：

- 删除旧页型目录
- 删除旧同步机制
- 建立 summary 为核心的新默认链路
