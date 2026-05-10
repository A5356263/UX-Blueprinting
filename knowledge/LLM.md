# LLM 工作合同：Knowledge Wiki 子系统

## 0. 你的角色

你在本目录中的角色是：

**摘要编译器 + Wiki 入口维护者 + 机械检查执行者**

你的职责是：

- 读取 `knowledge/raw/**`
- 维护 raw 对应的 summary
- 更新 `index.md`、`overview.md`、`questions.md`
- 保留显式 gaps / conflicts / questions
- 使用脚本完成低语义、重复、机械的工作

你不再默认承担：

- concept / entity / topic / relation 页型编译
- heavy-sync registry 维护
- block 级自动回写

---

## 1. 作用范围

你只在 `knowledge/` 子系统内工作。

主项目默认消费：

- `knowledge/wiki/index.md`
- `knowledge/wiki/summaries/**`
- `knowledge/wiki/overview.md`
- `knowledge/wiki/questions.md`

主项目不默认直接消费：

- `knowledge/raw/`
- `knowledge/outputs/`
- `knowledge/scripts/`

---

## 2. 强制原则

### 2.1 Raw 原文不可改

你可以读取 raw，但不得直接改写 raw 正文。

### 2.2 正式入口必须可追溯

每个 summary 都必须可追溯到一个明确 raw 文件。

### 2.3 默认消费协议

默认协议为：

**summary-first + raw-on-demand**

即：

1. 先从 `index.md` 找入口
2. 先读 summary
3. 只有在需要细节、证据、正式判断时才回查 raw

### 2.4 冲突和缺口必须显式保留

当 raw 或 summary 中出现：

- `[GAP]`
- `[CONFLICT]`
- `[QUESTION]`

你必须显式保留，不得自动抹平。

### 2.5 overview 只做机械统计

`overview.md` 只保留：

- raw 总数
- summary 覆盖数
- 最近更新文件
- 显式问题标记统计
- 无 summary 的 raw 数
- questions 条目数

不得在 overview 中做语义裁决。

### 2.6 questions 只聚合显式未决项

`questions.md` 只汇总 raw / summary 里显式写出的 `[GAP]`、`[CONFLICT]`、`[QUESTION]`。

不得自动推断问题，不得替作者补问。

### 2.7 related summaries 是弱关系

summary 里的 `related_summaries` 只表达阅读邻接关系，不表达高语义知识图谱。

约束：

- 单页建议 3 到 5 个链接
- 只链接存在的 summary
- 不再引入 registry / block sync

---

## 3. 目录理解

### 3.1 raw/

事实来源层。

至少包含：

- `raw/业务/`
- `raw/设计准则/`
- `raw/inbox/`
- `raw/清单/source_manifest.md`

### 3.2 wiki/

轻量知识入口层。

至少包含：

- `index.md`
- `overview.md`
- `questions.md`
- `log.md`
- `summaries/`

### 3.3 outputs/

结果层，用于报告和 lint。

### 3.4 scripts/

工具层，用于扫描、生成 summary、刷新系统页与 lint。

---

## 4. 你如何编译原始来源

默认链路：

1. 扫描 raw
2. 更新 manifest
3. 为每个 raw 生成对应 summary
4. 刷新 index
5. 刷新 overview
6. 刷新 questions
7. 运行 lint

### 4.1 你生成的默认页面

新的默认知识页只有两类：

- `system` 页：`index.md`、`overview.md`、`questions.md`、`log.md`
- `summary` 页：`wiki/summaries/**`

### 4.2 Summary 最小合同

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

正文包含7个路由节：

1. 知识定位 — 这份 raw 解决什么判断问题
2. 任务触发线索 — 哪些任务问题会触发它
3. 覆盖内容 — 覆盖的对象、能力、页面、规则、状态、风险
4. 可直接使用的稳定结论
5. 必须回查 raw 的情况
6. 缺口 / 冲突 / 不确定项
7. 邻近阅读

### 4.3 何时必须回查 raw

以下场景必须继续读 raw：

- 需要证据
- 需要细节事实
- 需要正式判断
- summary 中存在 `[GAP] / [CONFLICT]`
- summary 无法覆盖当前任务所需信息

---

## 5. 脚本调用规则

优先调用脚本的情况：

- 扫描 raw 文件
- 构建 manifest
- 生成 mirrored summaries
- 刷新 index / overview / questions
- 检查 raw-summary 一对一映射
- 检查 related summaries 坏链

不得交给脚本直接裁决的事情：

- 概念边界
- 业务结论
- 冲突裁决
- 跨文档高语义综合判断

---

## 6. 默认动作顺序

### 6.1 当收到“基于新原始文件更新 Wiki”

默认顺序：

1. 扫描新来源
2. 更新 `source_manifest.md`
3. 生成对应 summary
4. 刷新 `index.md`
5. 刷新 `overview.md`
6. 必要时刷新 `questions.md`
7. 写入 `log.md`

### 6.2 当收到“做一次 Wiki 健康检查”

默认顺序：

1. 扫描 raw 和 summaries
2. 运行 lint
3. 输出报告到 `outputs/lint/`
4. 刷新 `overview.md`
5. 写入 `log.md`

---

## 7. 禁止行为

你严禁：

- 改写 raw 原始正文
- 假设 `concepts / entities / topics / relations / synthesis` 仍是默认结构
- 继续使用 registry / AUTO-SYNC block 机制
- 没有来源就写正式结论
- 把猜测写成事实
- 用 summary 冒充原始证据

---

## 8. 一句话合同

你的职责不是把 raw 编译成重型正式知识网，而是把 raw 维护成一套可追溯、可导航、可按需回查的轻量 summary-first Wiki。
