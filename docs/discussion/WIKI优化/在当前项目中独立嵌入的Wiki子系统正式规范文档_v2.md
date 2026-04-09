# 在当前项目中独立嵌入的 Wiki 子系统正式规范文档 v2

> 用途：本规范用于指导 AI 在当前项目中把 `knowledge/` 改造为一个独立维护、独立演化、但被主项目稳定消费的 Wiki 子系统。
>
> 本文档是**嵌入式 Wiki 子系统规范**，不是通用知识库规范，也不是主项目执行规范。
> 它只约束 Wiki 子系统自身的目录、文件、页型、维护机制、脚本协作方式，以及 AI 的改造步骤。
>
> 本文档默认使用 `LLM.md` 作为 AI 合同文件名。若后续接入其他模型，可替换文件名，但合同职责不变。

---

## 0. 目标与边界

### 0.1 目标

本 Wiki 子系统的目标不是单纯做知识管理，而是为当前项目提供一套**可持续维护、可追溯、可复用**的正式知识层，供主项目稳定消费，用于支撑：

- 业务蓝图生成
- 体验蓝图生成
- 事实对齐
- 领域知识复用
- 设计指南与业务知识的统一编译

### 0.2 子系统定位

本 Wiki 子系统嵌入在当前项目中，但逻辑上独立。

它的职责是：

- 吸收原始来源
- 编译正式 Wiki 页面
- 做自我检查
- 做合法性检查
- 做自动更新
- 做自动回写
- 用脚本辅助 AI 执行通用任务

它**不是**主项目执行中枢的一部分。

### 0.3 主项目与 Wiki 子系统的关系

主项目与 Wiki 子系统分工如下：

#### 主项目负责
- 接收需求
- 读取任务输入
- 消费 `knowledge/wiki/` 正式知识页
- 生成业务蓝图与体验蓝图
- 输出项目产物

#### Wiki 子系统负责
- 管理原始来源
- 维护正式知识页
- 记录日志
- 做健康检查
- 做回写与归档
- 提供稳定知识入口

### 0.4 非目标

以下内容不属于本规范目标：

- 不定义主项目的任务执行模式
- 不把 Wiki 后台维护逻辑塞进 `packages` 主执行中枢
- 不要求主项目直接消费 Raw
- 不要求主项目直接消费 Outputs
- 不要求所有逻辑都由大模型完成
- 不依赖单一工具或单一模型品牌

---

## 1. 子系统总原则

### 1.1 正式消费原则

主项目默认只消费：

- `knowledge/wiki/`

主项目不应默认直接消费：

- `knowledge/raw/`
- `knowledge/outputs/`
- `knowledge/scripts/`

只有在 Wiki 正式页不足、且经显式指令允许时，才可以触发 Wiki 子系统维护流程，而不是让主项目主链路自行回查 Raw。

### 1.2 原始来源原则

Raw 是事实来源层。

规则：

- 允许 AI 读取
- 不允许 AI 直接改写原始正文
- 不允许用 AI 总结覆盖原始文件
- 可以补充清单、索引、关联信息
- 不可以篡改原始事实

### 1.3 正式知识原则

Wiki 是正式知识层。

规则：

- 面向长期复用
- 面向主项目消费
- 面向持续更新
- 面向结构化关系网络
- 不保存一次性闲聊
- 不保存未经核实的推测性结论

### 1.4 输出分层原则

Outputs 是结果层，不是事实层，也不是正式知识层。

规则：

- 回答、报告、图表、检查报告先进入 Outputs
- 只有稳定、可复用、可追溯的内容才允许回写到 Wiki
- Outputs 不直接替代正式 Wiki 页面

### 1.5 脚本协作原则

Wiki 子系统允许使用通用脚本辅助 AI 工作，以降低 token 消耗，并提高稳定性。

脚本适合负责：

- 扫描目录
- 生成来源清单
- 检查坏链
- 检查孤立页
- 检查命名冲突
- 统计健康指标
- 生成 lint 报告
- 刷新 overview

脚本不负责最终知识判断，不负责替代 AI 的语义编译工作。

### 1.6 重要操作留痕原则

Wiki 子系统的所有重要动作必须留痕，包括：

- ingest（摄入，导入新来源）
- update（更新，更新正式页）
- lint（体检，健康检查）
- write-back（回写，把高价值输出回写到 Wiki）
- archive（归档，归入历史）
- manual override（人工覆盖，人工修正）

---

## 2. 外显目录结构

## 2.1 子系统根目录

Wiki 子系统在当前项目中以 `knowledge/` 作为根目录。

推荐结构如下：

```text
knowledge/
  raw/
    business/
    guidelines/
    inbox/
    manifests/
      source_manifest.md

  wiki/
    index.md
    overview.md
    log.md
    questions.md
    sources/
    concepts/
    entities/
    topics/
    relations/
    synthesis/
    templates/
    archive/

  outputs/
    answers/
    reports/
    diagrams/
    lint/

  scripts/
    scan_raw.py
    build_manifest.py
    lint_wiki.py
    refresh_overview.py
    reindex_wiki.py

  README.md
  LLM.md
```

---

## 2.2 强制目录

以下目录为强制存在：

- `knowledge/raw/`
- `knowledge/wiki/`
- `knowledge/outputs/`
- `knowledge/scripts/`

### 2.3 强制系统文件

以下文件为强制存在：

- `knowledge/README.md`
- `knowledge/LLM.md`
- `knowledge/raw/manifests/source_manifest.md`
- `knowledge/wiki/index.md`
- `knowledge/wiki/overview.md`
- `knowledge/wiki/log.md`
- `knowledge/wiki/questions.md`

### 2.4 目录职责说明

#### raw/
原始来源层。

用于保存：
- 业务知识真源
- 设计指南真源
- 后续新增原始文件
- 尚未归档的新资料

#### wiki/
正式知识层。

用于保存：
- 来源摘要页
- 概念页
- 实体页
- 主题页
- 关系页
- 综合页
- 模板页
- 归档页
- 系统页

#### outputs/
结果层。

用于保存：
- 查询回答
- 专题总结
- 图表与图解
- lint 报告

#### scripts/
工具层。

用于保存：
- 通用脚本
- lint 脚本
- 刷新索引脚本
- 刷新 overview 脚本
- manifest 生成脚本

#### README.md
给人看的系统说明书。

#### LLM.md
给 AI 看的系统合同文件。

---

## 3. 系统文件职责

### 3.1 README.md

`README.md` 面向人类维护者。

必须至少写清楚：

- 这个 Wiki 子系统是什么
- 它和主项目的边界
- 目录结构说明
- 哪些内容属于 Raw
- 哪些内容属于正式 Wiki
- 哪些内容属于 Outputs
- Scripts 做什么、不做什么
- 如何触发 Wiki 维护
- 如何查看日志与健康状态

### 3.2 LLM.md

`LLM.md` 面向 AI。

它是 Wiki 子系统的工作合同。

必须至少写清楚：

- AI 的角色
- AI 不得改写 Raw 原文
- AI 如何 ingest
- AI 如何 update Wiki
- AI 如何做 lint
- AI 如何做 write-back
- AI 如何记录 log
- AI 何时允许调用 scripts
- AI 何时必须停止并标记冲突/缺口

### 3.3 文件名说明

`LLM.md` 不是特定厂商绑定文件名。

如果未来使用其他模型，可改名为：
- `AI.md`
- `AGENT.md`
- `SYSTEM.md`

但职责保持一致。

---

## 4. Raw 层规范

### 4.1 Raw 的职责

Raw 层只负责一件事：

**保存事实来源。**

### 4.2 Raw 的来源分类

基于当前项目，Raw 至少分为：

- `raw/business/`：业务知识真源
- `raw/guidelines/`：设计指南、设计原则、规范真源
- `raw/inbox/`：新进原始文件临时入口
- `raw/manifests/`：来源清单

### 4.3 Raw 的允许状态

Raw 可以是以下两种状态：

#### A. 已分类归档
例如：
- 业务资料已放入 `business/`
- 指南资料已放入 `guidelines/`

#### B. 临时堆放
如果新资料还没整理好，允许先放进：
- `raw/inbox/`

但不允许长期只依赖 inbox 运转。

### 4.4 Raw 的最低要求

每份原始来源至少要满足：

- 知道它是什么
- 知道它来自哪里
- 知道它属于业务还是指南
- 知道它是否完整
- 能被加入来源清单

### 4.5 source_manifest.md（来源清单）

`source_manifest.md` 是 Raw 层总表。

每条记录至少包含：

- `source_id`
- `title`
- `path`
- `source_group`（business / guidelines / inbox）
- `source_type`
- `date`
- `status`（完整 / 残缺 / 待确认 / 过期）
- `notes`

### 4.6 原始层命名建议

推荐格式：

`[日期可选]_[来源类型]_[简短标题]`

例如：
- `2026-04-01_doc_permission-scope.md`
- `guideline_page-carrier-semantics.md`
- `note_experience-principles.md`

---

## 5. Wiki 正式层规范

### 5.1 Wiki 的职责

Wiki 层承载正式知识页面，是主项目唯一默认消费层。

### 5.2 正式页分类

Wiki 正式页分为以下几类：

#### A. 系统页
- `index.md`
- `overview.md`
- `log.md`
- `questions.md`

#### B. 内容页
- `sources/`：来源摘要页
- `concepts/`：概念页
- `entities/`：实体页
- `topics/`：主题页
- `relations/`：关系页
- `synthesis/`：综合页
- `templates/`：模板页
- `archive/`：归档页

### 5.3 正式页基本要求

每个正式页至少必须：

- 可追溯到来源
- 有稳定标题
- 有页型
- 有最小元数据
- 有相关页面链接
- 被纳入至少一个索引或主题入口
- 不混合多个页型而失去可读性

### 5.4 元数据最低要求

建议每个正式页头部包含：

```yaml
page_id: PG-CONCEPT-0001
page_type: concept
canonical_name: 示例概念
aliases: []
status: stable
confidence: medium
source_refs: [SRC-0001]
related_pages: []
created_at: 2026-04-09
updated_at: 2026-04-09
owner: ai
review_state: unreviewed
freshness: current
```

### 5.5 页面状态值

推荐状态值：

- `draft`：草稿
- `stable`：稳定
- `disputed`：有争议
- `deprecated`：已废弃
- `archived`：已归档

### 5.6 页面分类说明

#### 来源摘要页
压缩单份来源，为后续正式页提供基础。

#### 概念页
定义稳定术语，统一口径。

#### 实体页
描述可单独指认的对象。

#### 主题页
组织多个概念、实体和来源，形成专题视角。

#### 关系页
描述区别、关系、依赖与边界。

#### 综合页
承接高价值 outputs 的回写，沉淀跨来源结论。

---

## 6. Outputs 层规范

### 6.1 Outputs 的职责

Outputs 用于承载用户可消费成果，但默认不直接进入正式 Wiki。

### 6.2 Outputs 分类

至少包含：

- `answers/`
- `reports/`
- `diagrams/`
- `lint/`

### 6.3 Output 最低元数据

每个 output 至少包含：

- `output_id`
- `output_type`
- `title`
- `prompt_or_question`
- `based_on_pages`
- `based_on_sources`
- `generated_at`
- `writeback_candidate`

### 6.4 Output 与 Wiki 的边界

- Output 面向“这次消费”
- Wiki 面向“长期复用”
- Output 可以临时
- Wiki 必须稳定

### 6.5 回写条件

只有满足以下条件的 output 才允许回写：

- 不是一次性闲聊
- 具备复用价值
- 有明确来源或明确推导链
- 没有明显未裁决事实争议
- 能找到合适承接页型

---

## 7. Scripts 层规范

### 7.1 Scripts 的职责

Scripts 是 AI 的辅助工具层，用于处理通用、重复、低语义任务。

### 7.2 Scripts 适合做的事情

包括但不限于：

- 扫描 Raw 文件
- 建立或刷新 source manifest
- 检查坏链
- 检查孤立页
- 检查命名冲突
- 检查 alias 冲突
- 统计页数和来源数
- 刷新 overview
- 生成 lint 报告
- 重建索引

### 7.3 Scripts 不适合做的事情

Scripts 不负责：

- 定义概念边界
- 裁决事实冲突
- 生成正式知识结论
- 决定某条结论是否应进入正式 Wiki

### 7.4 脚本调用原则

AI 可以调用 scripts，但必须遵守：

- 先判断是否属于通用任务
- 能用脚本完成的通用检查，优先用脚本
- 脚本结果由 AI 解释，不直接等于正式结论
- 脚本运行后的关键结果要写入 log 或 output

### 7.5 推荐脚本

建议至少提供以下脚本骨架：

- `scan_raw.py`
- `build_manifest.py`
- `lint_wiki.py`
- `refresh_overview.py`
- `reindex_wiki.py`

---

## 8. 内部过渡逻辑规范

### 8.1 过渡逻辑不再外显为目录

本版本中，Transition（过渡层，过渡处理层）仍然存在，但不再要求显式目录。

它是 Wiki 子系统的内部构建逻辑，而不是对主项目暴露的正式目录。

### 8.2 内部过渡逻辑的职责

当 AI 处理新 Raw 来源时，必须在内部完成以下动作：

- 生成来源摘要
- 提取候选概念
- 提取候选实体
- 提取候选主题
- 建立别名映射
- 暴露冲突
- 暴露缺口
- 判断是否可进入正式 Wiki

### 8.3 内部过渡逻辑的输出去向

内部过渡逻辑的结果最终落在以下位置：

- 来源摘要进入 `wiki/sources/`
- 正式概念进入 `wiki/concepts/`
- 正式实体进入 `wiki/entities/`
- 正式主题进入 `wiki/topics/`
- 正式关系进入 `wiki/relations/`
- 高价值综合结果进入 `wiki/synthesis/`
- 暂不成熟的问题进入 `wiki/questions.md`
- 操作过程进入 `wiki/log.md`

### 8.4 何时必须先走内部过渡逻辑

出现以下任一情况时，禁止直接写正式 Wiki 页：

- 同一对象多命名混乱
- 来源分散且无清单
- 事实与意见混杂
- 冲突很多
- 边界不清
- 来源缺失严重

---

## 9. 持续维护机制

### 9.1 自我检查机制

Wiki 子系统必须具备自我检查能力。

至少检查：

- orphan pages（孤立页，没人链接或不链接别人）
- broken links（坏链，链接失效）
- duplicate pages（重复页）
- naming inconsistency（命名不一致）
- alias collisions（别名冲突）
- stale pages（过时页）
- missing source refs（缺来源）
- unresolved conflicts（未解决冲突）
- unresolved gaps（未解决缺口）

### 9.2 合法性机制

正式 Wiki 页必须满足：

- 有来源支撑
- 可追溯
- 不得把猜测写成事实
- 冲突必须显式标注
- Raw 原文不可改写
- 无法确认的内容必须进入 questions 或 gaps，而不是写成正式结论

### 9.3 自动更新机制

当新 Raw 来源进入时，Wiki 子系统应支持自动更新：

- 注册来源
- 更新 manifest
- 生成来源摘要
- 找到受影响的正式页
- 更新页内容
- 更新 index / overview / questions
- 记录日志

### 9.4 自动回写机制

当 outputs 中出现高质量成果时，Wiki 子系统应支持自动回写：

- 判断是否具备复用价值
- 判断是否可追溯
- 判断是否存在未裁决争议
- 找到合适承接页型
- 更新正式页或新建 synthesis 页
- 记录 log

### 9.5 日志机制

所有重要动作都必须写入 `wiki/log.md`。

每条日志至少包含：

- `log_id`
- `timestamp`
- `action_type`
- `operator`
- `touched_files`
- `summary`
- `reason`
- `risk_level`
- `rollback_hint`

### 9.6 总览机制

`wiki/overview.md` 必须定期刷新。

至少展示：

- 页面总数
- 来源总数
- 最近更新
- 未解决冲突数
- 未解决缺口数
- 孤立页数
- 过时页数
- 待回写 outputs 数量

---

## 10. 与当前项目的嵌入关系

### 10.1 嵌入方式

Wiki 子系统嵌入在当前项目中，推荐直接以 `knowledge/` 作为独立系统根。

### 10.2 与 packages 的边界

`packages` 主执行中枢不应承担以下职责：

- Wiki ingest
- Wiki lint
- Wiki write-back
- manifest 构建
- source 扫描
- Wiki 自我维护脚本执行

这些都属于 `knowledge/` 子系统内部能力。

### 10.3 主项目消费方式

主项目默认只消费：

- `knowledge/wiki/`

而不消费：

- `knowledge/raw/`
- `knowledge/outputs/`
- `knowledge/scripts/`

### 10.4 真源映射关系

对当前项目而言：

- 业务知识真源 = `knowledge/raw/business/`
- 设计指南真源 = `knowledge/raw/guidelines/`
- 正式知识消费层 = `knowledge/wiki/`

---

## 11. AI 改造项目的具体步骤

> 本节用于直接指导 AI 改造当前项目中的 `knowledge/` 目录。

### 第 1 步：建立目录骨架

先确保以下目录与文件存在：

```text
knowledge/
  raw/
    business/
    guidelines/
    inbox/
    manifests/
      source_manifest.md

  wiki/
    index.md
    overview.md
    log.md
    questions.md
    sources/
    concepts/
    entities/
    topics/
    relations/
    synthesis/
    templates/
    archive/

  outputs/
    answers/
    reports/
    diagrams/
    lint/

  scripts/

  README.md
  LLM.md
```

### 第 2 步：迁移现有真源

将现有知识真源按语义归入：

- 业务真源 → `knowledge/raw/business/`
- 设计指南真源 → `knowledge/raw/guidelines/`

如果存在新进但未整理来源，放入：

- `knowledge/raw/inbox/`

### 第 3 步：补齐来源清单

创建并维护：

- `knowledge/raw/manifests/source_manifest.md`

为已有原始来源分配 `source_id`，补齐：
- 标题
- 路径
- 分组
- 类型
- 状态
- 备注

### 第 4 步：建立 Wiki 系统页

创建并补充：

- `knowledge/wiki/index.md`
- `knowledge/wiki/overview.md`
- `knowledge/wiki/log.md`
- `knowledge/wiki/questions.md`

### 第 5 步：建立正式页目录

创建并确认以下目录存在：

- `knowledge/wiki/sources/`
- `knowledge/wiki/concepts/`
- `knowledge/wiki/entities/`
- `knowledge/wiki/topics/`
- `knowledge/wiki/relations/`
- `knowledge/wiki/synthesis/`
- `knowledge/wiki/templates/`
- `knowledge/wiki/archive/`

### 第 6 步：建立 Outputs 目录

创建并确认以下目录存在：

- `knowledge/outputs/answers/`
- `knowledge/outputs/reports/`
- `knowledge/outputs/diagrams/`
- `knowledge/outputs/lint/`

### 第 7 步：建立 Scripts 骨架

至少建立以下脚本文件骨架：

- `knowledge/scripts/scan_raw.py`
- `knowledge/scripts/build_manifest.py`
- `knowledge/scripts/lint_wiki.py`
- `knowledge/scripts/refresh_overview.py`
- `knowledge/scripts/reindex_wiki.py`

### 第 8 步：编写 README.md

在 `knowledge/README.md` 中写清：

- 子系统定位
- 目录说明
- 主项目如何消费 Wiki
- 哪些目录不应被主项目直接消费
- 如何触发 Wiki 维护

### 第 9 步：编写 LLM.md

在 `knowledge/LLM.md` 中写清：

- AI 角色
- Raw 不可改
- 如何 ingest
- 如何 update
- 如何 lint
- 如何 write-back
- 如何记录 log
- 何时调用脚本
- 何时停止并标记冲突/缺口

### 第 10 步：初始化正式 Wiki 内容

按以下顺序初始化：

1. `wiki/sources/`：先为重要来源生成来源摘要
2. `wiki/concepts/`：提炼稳定概念
3. `wiki/entities/`：补实体页
4. `wiki/topics/`：补主题页
5. `wiki/relations/`：补关系边界页
6. `wiki/synthesis/`：沉淀综合页
7. 更新 `index.md`
8. 更新 `overview.md`
9. 更新 `log.md`

### 第 11 步：建立首次健康检查能力

运行或准备：

- manifest 检查
- 链接检查
- 孤立页检查
- 缺来源检查
- overview 刷新

将检查结果写入：

- `knowledge/outputs/lint/`
- 必要时更新 `knowledge/wiki/overview.md`
- 必要时记录到 `knowledge/wiki/log.md`

---

## 12. AI 维护动作默认顺序

### 12.1 当收到“基于新原始文件更新 Wiki”

默认顺序：

1. 扫描新来源
2. 注册 source_id
3. 更新 source_manifest
4. 生成来源摘要
5. 识别受影响正式页
6. 做内部过渡判断
7. 更新或新建正式页
8. 更新 index / overview / questions
9. 写入 log

### 12.2 当收到“做一次 Wiki 健康检查”

默认顺序：

1. 扫描 wiki 全部页面
2. 运行脚本辅助检查
3. 输出 lint 结果
4. 标记严重级别
5. 刷新 overview
6. 写入 log

### 12.3 当收到“把某个 outputs 回写进 Wiki”

默认顺序：

1. 判断 output 是否具备复用价值
2. 判断是否可追溯
3. 判断是否有未解决事实争议
4. 找到承接页型
5. 更新正式页或新建 synthesis 页
6. 写入 log

---

## 13. 禁止行为清单

AI 严禁：

- 改写 Raw 原始正文
- 让主项目默认直接消费 Raw
- 让主项目默认直接消费 Outputs
- 把 Wiki 维护逻辑塞进 `packages` 主执行中枢
- 把 scripts 当成正式知识判断器
- 把猜测写成正式知识
- 没有来源就下定义
- 抹掉冲突只保留单一口径
- 不写日志直接大改 Wiki
- 把一次性问答直接当正式页

---

## 14. 完成标准

### 14.1 可用状态

当以下条件同时满足时，Wiki 子系统达到“可用”状态：

- `knowledge/` 子系统目录完整
- README 与 LLM 合同存在
- Raw 来源层可用
- source_manifest 可用
- Wiki 系统页可用
- 正式页目录完整
- Outputs 目录完整
- Scripts 骨架存在
- 主项目可默认消费 `knowledge/wiki/`

### 14.2 稳定状态

当以下条件同时满足时，Wiki 子系统达到“稳定”状态：

- 关键来源已有来源摘要
- 核心概念、实体、主题、关系页已建立
- index / overview / log / questions 已运转
- lint 可执行
- 自动更新机制可执行
- 自动回写机制可执行
- scripts 与 AI 协作稳定
- 主项目与 Wiki 子系统边界清楚

---

## 15. 推荐最小模板

### 15.1 来源摘要页模板

```md
# 标题

- page_id:
- source_id:
- source_type:
- path:
- one_sentence_summary:
- core_points:
- mentioned_terms:
- mentioned_entities:
- touched_topics:
- scope_boundary:
- open_questions:
- source_refs:
- created_at:
- updated_at:
```

### 15.2 概念页模板

```md
# 标题

- page_id:
- canonical_name:
- aliases:
- one_sentence_definition:
- detailed_definition:
- scope:
- non_scope:
- related_concepts:
- common_misunderstandings:
- source_refs:
- related_pages:
- status:
- confidence:
- gaps:
- conflicts:
- created_at:
- updated_at:
```

### 15.3 Output 模板

```md
# 标题

- output_id:
- output_type:
- title:
- prompt_or_question:
- based_on_pages:
- based_on_sources:
- generated_at:
- writeback_candidate:
- summary:
```

---

## 16. 版本信息

- document_version: v2
- status: draft-for-use
- intended_use: AI project refactor instruction / wiki subsystem governance
