# HLD｜Knowledge Wiki 轻量化优化方案总纲

## 1. 文档目标

在**不改变 Wiki 为项目独立子系统**这一前提下，将当前 Wiki 从“重编译知识层”切换为“轻量摘要入口层”。

本方案同时覆盖：

- `knowledge/raw/business/**`
- `knowledge/raw/guidelines/**`

本方案不是权限域特例，而是面向不同原始知识类型的**通用轻量 Wiki 方案**。

---

## 2. 现状判断

### 2.1 当前正式定义

当前项目内对 Wiki 的正式定义仍偏向：

- 主项目默认只消费 `knowledge/wiki/`
- Wiki 负责编译正式页、自动回写、健康检查、稳定入口
- Wiki 目录按 `sources / concepts / entities / topics / relations / synthesis` 组织
- 已存在 block 同步、registry、托管区块、dry-run / apply 机制

这套定义会持续带来：

1. raw 与 wiki 的双层维护
2. 对非研发人员不友好的正文页型
3. 高频 raw 变更下的同步治理成本
4. “原始知识维护”与“正式知识编译”边界混乱

### 2.2 本次优化的核心判断

本次优化不再把 Wiki 定义为“二次知识模型主承载层”，而改为：

**raw 的一对一摘要层 + 入口目录层 + 机械状态层**

---

## 3. 新的核心定位

### 3.1 新定位

新的轻量 Wiki 默认只承担：

- 入口
- 导航
- 一对一摘要
- 页面级弱关系
- 机械状态
- 显式问题聚合

### 3.2 默认不再承担的内容

新的默认机制不再承担：

- 自动生成 `concepts / entities / topics / relations / synthesis`
- 自动维护高语义关系网络
- 自动做跨文件知识编译
- 自动把 raw 回写成复杂正文页
- 自动要求所有领域进入页型化建模

### 3.3 物理性移除原则

以下旧结构不做“逻辑降级”，而做**物理性移除**：

- `knowledge/wiki/concepts/`
- `knowledge/wiki/entities/`
- `knowledge/wiki/topics/`
- `knowledge/wiki/relations/`
- `knowledge/wiki/synthesis/`

同时移除与之绑定的默认机制：

- `knowledge/wiki_sync/registry.yaml`
- `knowledge/scripts/sync_wiki_pages.py`
- `specs/15_wiki_sync_contract.md`
- `specs/16_wiki_sync_registry_contract.md`
- `specs/17_wiki_sync_execution_contract.md`

说明：

- 旧内容不再保留在当前运行路径
- 历史追溯依赖 Git 历史
- 新方案不再提供 legacy 兼容层

---

## 4. 目标形态

### 4.1 默认目录

新的默认结构围绕以下对象建立：

- `knowledge/raw/**`：唯一高频维护真源
- `knowledge/wiki/summaries/**`：与 raw 一对一摘要
- `knowledge/wiki/index.md`：总入口
- `knowledge/wiki/overview.md`：机械状态页
- `knowledge/wiki/questions.md`：显式问题池
- `knowledge/wiki/log.md`：维护日志

### 4.2 一对一摘要原则

摘要文件与原始文件保持：

- 同名
- 镜像路径
- 一对一对应

示例：

- `knowledge/raw/business/permission/15_page_carrier_semantics.md`
- `knowledge/wiki/summaries/business/permission/15_page_carrier_semantics.md`

- `knowledge/raw/guidelines/task_type_index.md`
- `knowledge/wiki/summaries/guidelines/task_type_index.md`

### 4.3 弱关系原则

每个摘要页允许保留少量页面级关系，例如：

- related summaries
- 建议继续阅读
- 上游资料
- 相邻主题

约束：

- 关系只表达“阅读邻接”
- 不表达高语义知识图谱关系
- 单页建议 3 到 5 个链接
- 不引入 registry / block sync 级治理

---

## 5. 人与 LLM 的消费方式

### 5.1 默认消费协议

新的默认协议为：

**summary-first + raw-on-demand**

即：

1. 先从 `index.md` 进入
2. 先读对应 summary
3. 不够再回查 raw

### 5.2 何时只读 summary

以下场景通常只读 summary：

- 判断某份资料是否相关
- 快速理解主题范围
- 组装背景上下文
- 找阅读入口
- 看当前 gaps / conflicts

### 5.3 何时必须回查 raw

以下场景必须继续读 raw：

- 需要细节事实
- 需要证据引用
- 需要正式判断
- summary 中存在 `[GAP] / [CONFLICT]`
- summary 无法覆盖任务所需信息

---

## 6. overview 与 questions 的定位

### 6.1 overview

`overview.md` 只做**机械状态板**，不做语义裁决。

只保留这类信息：

- raw 总数
- summary 覆盖数
- 最近更新文件
- 含 `[GAP]` 的摘要数
- 含 `[CONFLICT]` 的摘要数
- 无 summary 的 raw 数
- questions 条目数

### 6.2 questions

`questions.md` 只做**显式未决项聚合**，来源仅限：

- raw 中显式 `[GAP] / [CONFLICT] / [QUESTION]`
- summary 中显式 `[GAP] / [CONFLICT] / [QUESTION]`

不做：

- 自动推断问题
- 自动语义裁决
- 研究型知识编译

---

## 7. 对 business 与 guidelines 的通用适配

### 7.1 business

适用于：

- 按业务域建包
- 文件编号稳定
- 单文件可表达一组业务事实

摘要重点：

- 文件讲什么
- 适用范围
- 关键事实
- 关键对象
- gaps / conflicts
- related summaries

### 7.2 guidelines

适用于：

- 任务入口索引
- 原则正文
- 触发器索引
- 跨业务复用规则

摘要重点：

- 这份原则资料服务什么任务
- 优先阅读什么
- 不适用什么
- 关键原则点
- risks / gaps
- related summaries

---

## 8. Impact Analysis

### 8.1 正向影响

1. 明显降低维护复杂度  
2. 取消 raw -> 正文页 的双层同步压力  
3. 人类阅读路径更接近“目录 + 摘要 + 原文”  
4. 更适合非研发人员维护  
5. 权限与指南可共用同一机制  

### 8.2 负向影响

1. 失去高结构语义页型网络  
2. 失去自动生成 entity / relation 的能力  
3. 某些跨资料知识，需要靠 summary 链接而不是关系页表达  
4. 主项目消费逻辑需要从“只吃 wiki 正文”改为“先 summary，必要时回 raw”  

### 8.3 切换风险

1. 删除旧目录后，现有引用会失效  
2. 旧脚本链路中的 `sync_wiki_pages.py / registry / heavy specs` 必须同时清理  
3. 旧页中的 AUTO-SYNC 锚点需要一并移除  
4. 若主项目仍假设 `concepts / entities / topics / relations` 存在，会直接断链  

### 8.4 风险控制

1. 先完成文档合同改口  
2. 再完成目录与脚本物理删除  
3. 再切换索引、概览、问题池和消费入口  
4. 最后验证 permission 与 guidelines 两类原始知识均可跑通  

---

## 9. 结论

新的轻量 Wiki 不是“弱化版重 Wiki”，而是**物理切换后的新子系统形态**：

- 原始知识维护在 raw
- 默认消费从 summary 进入
- 复杂页型与重同步机制全部移除
- Wiki 保留独立子系统身份，但角色改为“摘要入口系统”
