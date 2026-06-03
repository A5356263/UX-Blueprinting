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
- `knowledge/templates/`

---

## 2. 强制原则

### 2.1 Raw 原文不可改

你可以读取 raw，但不得直接改写 raw 正文。

这里的“不得直接改写 raw 正文”适用于 Wiki 编译、summary 维护和系统页刷新场景。
如果是知识入库、知识清理或用户确认后的 raw 更新，应遵循 `.codex/skills/knowledge-ingestion` 的流程：先判断、先规划、先确认，再更新 raw 并刷新 wiki。

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

### 2.7 轻路由卡不承担邻接图谱

轻路由卡只负责帮助 AI 判断这份 raw 值不值得继续读。

不要为了“补全关系”再恢复独立的邻接关系字段、registry 或 block sync。

---

## 3. 目录理解

### 3.1 raw/

事实来源层。

至少包含：

- `raw/业务/`
- `raw/设计准则/`
- `raw/inbox/`

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

### 3.5 templates/

知识入库模板层。

它只服务：

- 知识入库
- 新领域建档
- 编号结构参考
- README 模板生成

它不属于正式 raw，不生成 summary，不进入 index，也不参与主链路默认知识消费。

---

## 4. 你如何编译原始来源

默认链路：

1. 扫描 raw
2. 为每个 raw 生成对应 summary
3. 刷新 index
4. 刷新 overview
5. 刷新 questions
6. 运行 lint

### 4.1 你生成的默认页面

新的默认知识页只有两类：

- `system` 页：`index.md`、`overview.md`、`questions.md`、`log.md`
- `summary` 页：`wiki/summaries/**`

### 4.2 Summary 最小合同

每个 summary 至少包含：

- `source_path`
- `domain`
- `summary_role: light_route_card`
- `updated_at`

正文包含 4 个路由节：

1. 定位 — 这份 raw 主要解决什么判断
2. 触发信号 — 什么场景下值得升级读这份 raw
3. 稳定结论 — 可以直接复用的稳定判断
4. 已知缺口 — 当前还没覆盖或还没确认的点

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
- 生成 mirrored summaries
- 刷新 index / overview / questions
- 检查 raw-summary 一对一映射
- 检查 `source_path` 已失效的 orphan summary
- 用户确认后清理 orphan summary
- 统计 summary 1-4 语义节缺失状态

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
2. 生成对应 summary
3. 刷新 `index.md`
4. 刷新 `overview.md`
5. 必要时刷新 `questions.md`
6. 写入 `log.md`

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

---

## 9. Summary 语义填充触发协议

当用户说“填充 <域> 的 summary”或类似表述时，按以下步骤执行：

1. 读取 `knowledge/outputs/reports/pending_semantic_summaries.md`
2. 筛选仍包含轻路由卡占位内容且属于目标域的 summary
3. 对每个目标 summary：
   - 从头部元数据中的 `source_path` 读取对应 raw
   - 基于 raw 实际内容填写以下 4 个语义节：
     - `## 定位`
     - `## 触发信号`
     - `## 稳定结论`
     - `## 已知缺口`
4. 目标域全部完成后，运行：
   `python knowledge/scripts/refresh_semantic_summary_report.py`

执行约束：

- 逐域推进，一次只处理一个域
- 不修改 raw 原文
- 保持原文 meaning，不补写 raw 中没有的推测性结论
- 保留显式的 `[GAP]`、`[CONFLICT]`、`[QUESTION]`

### 9.1 正式填充前原则

在执行 Summary 语义填充前，先遵守以下原则：

1. **以 raw 为唯一事实源**
   - 只依据当前 summary 对应 `source_path` 指向的 raw 填写
   - 不混入其他 raw、外部常识、历史记忆或主观补全
   - 若某结论未在当前 raw 中出现，就不能写成稳定结论

2. **summary 是路由卡，不是复述稿**
   - 第 1-4 节的目标是帮助后续 AI 判断“这份 raw 解决什么问题、什么时候该读、能直接拿走什么”
   - 不按原文顺序机械复述，不把正文改写成长篇摘要
   - 优先提炼判断入口、适用场景、边界、依赖和稳定结论

3. **优先写判断价值，不优先写信息覆盖率**
   - 如果 raw 信息很多，先提炼最影响任务判断的内容
   - 第 1 节写“这份 raw 解决什么判断问题”
   - 第 2 节写“什么任务会触发读取”
   - 第 3 节写“覆盖了哪些对象、能力、页面、规则、状态、风险”
   - 第 4 节写“哪些结论可以被后续任务稳定复用”

4. **稳定结论必须可直接复用**
   - 只写跨场景仍成立的事实、约束、前置关系、互斥关系、失败结果、边界规则
   - 不把举例、说明性话术、局部操作细节拔高成通用结论
   - 遇到“仅目录结构”“仅待采集说明”这类 raw，第 4 节应诚实写出其可复用结论有限，而不是硬凑业务结论

5. **显式保留不确定性，不主动补洞**
   - `[GAP]` 表示缺口，不能自行补齐
   - `[CONFLICT]` 表示冲突，不能替作者裁决
   - `[QUESTION]` 表示未决项，不能自动转成事实
   - 若 raw 本身是“帮助文档现状”与“真源待核对”的对照材料，summary 必须保留这种“待融合 / 待核对”属性

6. **按统一视角组织第 3 节覆盖内容**
   - 默认优先从以下维度组织：对象、能力、页面/路径、规则、状态、风险、上游依赖
   - 不要求每篇都覆盖全部维度，但要优先使用这一组视角
   - 避免有的 summary 写成页面清单，有的写成概念散文，导致跨域不可比

7. **先识别 raw 类型，再决定写法**
   - `README.md`：重点写目录作用、阅读顺序、维护原则、子域边界，不误写成业务规则页
   - `00_领域概述.md`：重点写领域定义、核心问题、上下游依赖、典型使用对象
   - `10-15` 这类能力/场景/路径文件：重点写任务入口、页面承载、场景触发条件、链路边界
   - `20-25` 这类契约/规则文件：重点写前置规则、覆盖规则、互斥关系、失败结果、治理约束
   - `50_常见问题.md`：重点写高频问答主题、例外、限制、常见排查点，不误写成完整规则总表
   - 仅目录型或采集未完成型文件：重点写覆盖范围、当前缺口、可用于导航但不足以做完整判断

8. **区分“业务真源”与“帮助文档现状”**
   - 有些 raw 记录的是目标业务模型，有些记录的是帮助中心现有口径
   - 若文件定位是“现有表述提取”“差异对照”“供进一步融合”，summary 必须把它写成对照材料，而不是最终真源
   - 遇到旧口径、迁移中口径或待核对口径，优先写“可作为核对输入”，不要写成最终规则

9. **设计准则类文件要写成原则卡，不要写成业务卡**
   - 对 `knowledge/raw/设计准则/**`，第 1 节应写它解决什么体验判断问题
   - 第 2 节应写会在哪类设计任务中触发
   - 第 3 节应写原则、触发场景、推导输出、自检问句、反模式、取舍提示
   - 第 4 节应写可复用的设计判断结论，而不是业务配置建议

10. **遇到列表密集型 raw 时先抽结构，再抽结论**
   - 如预算排查清单、字段清单、审批类型枚举、支付方式矩阵等，不要逐条搬运
   - 先抽出该文件提供的判断框架，再挑选高复用结论进入第 4 节
   - 只在确有价值时保留关键枚举，不把 summary 写成原始表格的镜像

11. **域内保持写法一致**
   - 同一 domain 内的 summary 应尽量使用一致的视角和句式密度
   - 同类文件之间优先保持同一抽象层级
   - 如果某域已形成写法样板，后续文件应优先向样板对齐，而不是每篇自由发挥
