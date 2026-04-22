# Generation 真正推理式生成优化方案（正式版｜非兼容）

## 1. 文档目的

本方案用于承接当前已完成的“推理式架构骨架”阶段，进一步把 `generation` 从：

- 有中间模型、但结论仍大量预设
- 有 reasoner、但仍保留固定判断 / 固定页面 / 固定风险 / 固定文案

升级为：

- **真正由当前输入和命中知识动态驱动**
- **先判断，再生成**
- **不再保留旧固定逻辑**
- **不做兼容模式**

本次方案是**非兼容版改造**，核心要求是：

**旧模板逻辑、旧固定判断、旧固定页面骨架、旧固定风险项，不再保留为兼容分支。**

---

## 2. 当前阶段判断

当前系统已经完成：

- `facts_model / business_model / experience_model` 三层中间模型
- `core.py` 从单体模板器变为编排层
- 推理层与渲染层已经分开
- `business` / `experience` 已经不再直接由一个大模板函数硬拼

但当前仍未完成真正推理式生成，主要问题是：

1. `facts_reasoner.py` 仍偏关键词抽取 + 保底推断
2. `business_reasoner.py` 仍存在大量固定 judgment / fixed option / fixed position
3. `experience_reasoner.py` 仍存在固定页面、固定流程、固定状态、固定文案合同
4. 知识库尚未真正参与“命中后影响结论”的动态推导
5. 现在更像“有推理骨架的生成器”，还不是“真正动态推理生成器”

---

## 3. 本次改造目标

本次改造完成后，必须达到：

1. `facts` 由当前任务输入动态抽取，不再依赖固定角色词表和固定事实句式
2. `business` 由当前任务事实 + 命中知识动态推导，不再内置固定 judgment 和固定 final position
3. `experience` 由当前任务闭环、页面承载、状态变化、信息优先级、文案责任动态推导，不再内置固定页面骨架
4. 知识库真正进入“影响判断链”，不再只是可接入位
5. 渲染层只负责输出 Markdown，不再承担结论生成职责
6. preview 继续跟随正式蓝图输出，但不反向驱动 generation
7. 旧固定逻辑全部移除，不保留兼容模式

---

## 4. 非目标

本次不做以下事项：

- 不改主链路阶段顺序
- 不改 task_card / context_assemble 的职责
- 不把 validate 变成推理器
- 不让 preview 直接决定页面与流程
- 不引入高保真视觉生成
- 不保留旧模板逻辑的 fallback 分支
- 不做“双模式共存”

---

## 5. 正式决策

### 5.1 不保留兼容模式
本次改造明确要求：

- 删除旧固定 judgment
- 删除旧固定页面骨架
- 删除旧固定状态与固定文案模板
- 删除旧式保底结论分支
- 不再保留“如果推不出来就回到旧模板”的逻辑

### 5.2 只保留一种生成方式
改造完成后，`generation` 内部只允许：

**输入 -> 动态推理 -> 中间模型 -> 渲染输出**

不允许：

**输入 -> 固定规则结论 -> 渲染输出**

### 5.3 规则只保留边界规则，不保留预设答案
允许保留：

- 阶段边界
- 证据要求
- 缺口保留规则
- 输出结构要求
- trace 要求
- 编号要求

不允许保留：

- 固定页面集合
- 固定流程集合
- 固定业务立场
- 固定风险项
- 固定文案集合
- 固定 final position

---

## 6. 核心改造思路

## 6.1 facts：从关键词提取改为任务事实建模
`facts_reasoner.py` 必须从当前项目 source 输入中，动态抽取：

- 任务目标
- 角色
- 对象
- 规则
- 状态
- 动作
- 依赖
- 异常
- gap

### 要求
- 不再使用固定角色映射作为主逻辑
- 不再默认生成一整套固定事实编号内容
- facts 的每条事实都应来自当前输入，而不是默认句式
- 信息不足时进入 `gaps`，而不是自动补成通用事实

---

## 6.2 business：从固定 judgment 改为动态业务判断
`business_reasoner.py` 必须基于：

- 当前 `facts_model`
- 当前项目命中的 wiki / knowledge
- 当前业务基线

动态生成：

- 领域基线
- 核心判断
- 能力归位比较
- trade-off
- 最终业务立场
- 对体验层的约束

### 要求
- 删除固定 `J-xx`
- 删除固定 `OPT-xx`
- 删除固定 `final_position`
- 删除固定 `risk_items`
- 每次业务立场必须由当前事实与命中知识推出来
- 不能把“上一次对 generation 的结论”写死为这一次的结论

---

## 6.3 experience：从固定页面骨架改为任务闭环与页面推导
`experience_reasoner.py` 必须基于：

- 当前 `facts_model`
- 当前 `business_model`
- 当前命中的 guideline / wiki / business knowledge

动态生成：

- 任务闭环
- 流程节点
- 页面 / 窗口承载
- 页面级目标
- 页面内信息结构
- 页面状态
- 文案责任
- 风险保护

### 要求
- 删除固定 `P-01 / P-02 / P-03`
- 删除固定 `TF-01 / TF-02`
- 删除固定 `ST-01 ~ ST-04`
- 删除固定 `COPY-01 ~ COPY-03`
- 页面数量、流程数量、页面名称、状态数量、文案合同数量，都必须由当前任务动态生成
- 页面结构必须承接任务闭环，而不是先假定页面再往里填内容

---

## 7. 知识驱动要求

## 7.1 知识必须参与结论，不只是参与引用
当前问题之一是知识只像“可接入位”，没有真正驱动判断。

本次要求：

- facts：知识只做补充解释，不替代 source
- business：知识必须参与“基线建立”和“判断比较”
- experience：知识必须参与“承载方式、信息优先级、状态解释、文案责任”判断

### 不允许
- 只在最终 trace 里引用知识
- 结论先写好，再补知识来源
- 知识页存在，但不影响最终判断

---

## 7.2 命中知识必须可见
每个核心判断都应至少能说明：

- 命中了哪些知识
- 这些知识影响了哪个判断
- 如果没有这些知识，结论哪里会不稳定

---

## 8. 线性输出要求

## 8.1 business 蓝图
后续业务蓝图必须更适合人读，应按线性判断链输出：

1. 问题与意图
2. 领域基线
3. 核心业务判断
4. 能力归位比较
5. 最终业务立场
6. 风险与开放问题
7. 对体验层的约束

## 8.2 experience 蓝图
后续体验蓝图必须按线性任务闭环输出：

1. 任务闭环总览
2. 闭环 A / 闭环 B
3. 每个闭环的流程节点
4. 每个节点承接的页面
5. 页面级蓝图
6. 状态与反馈矩阵
7. 文案合同
8. 风险与保护策略

## 8.3 页面级表达
每个关键页面至少要明确：

- 页面目标
- 用户为什么来这里
- 首屏先看什么
- 主任务 / 次任务
- 页面状态
- 信息结构
- 阅读顺序
- 风险点
- 文案责任

---

## 9. 文件改动建议

## 9.1 必改文件
- `packages/generation/reasoning/facts_reasoner.py`
- `packages/generation/reasoning/business_reasoner.py`
- `packages/generation/reasoning/experience_reasoner.py`
- `packages/generation/reasoning/schemas.py`
- `packages/generation/reasoning/renderers.py`
- `packages/generation/core.py`

## 9.2 联动检查文件
- `templates/business_blueprint.template.md`
- `templates/experience_blueprint.template.md`
- `packages/validate/*`
- `packages/gate-*/*`
- `packages/experience_preview/build_preview_model.py`
- `packages/experience_preview/render_html.py`

### 说明
preview 不需要先重构，但需要确认新蓝图结构仍能被稳定消费。

---

## 10. 实施顺序

### Step 1
先删旧固定逻辑：
- 固定 judgment
- 固定页面
- 固定状态
- 固定文案
- 固定结论

### Step 2
重做 facts 动态抽取逻辑

### Step 3
重做 business 动态判断逻辑

### Step 4
重做 experience 动态页面与流程推导逻辑

### Step 5
调整 renderers，使其只消费 model，不补业务结论

### Step 6
联调 validate / gate / preview

### Step 7
用真实任务做第一轮回归测试

---

## 11. 验收标准

完成后，至少满足：

1. `facts_reasoner.py` 不再依赖固定角色/对象/事实模板
2. `business_reasoner.py` 不再存在固定 judgment / final position / placement option
3. `experience_reasoner.py` 不再存在固定页面、固定流程、固定状态、固定文案集合
4. 每次输出都能体现当前输入差异，而不是大体相同
5. 命中知识会显式影响业务判断和体验判断
6. business / experience 更适合人类线性阅读
7. preview 能继续跟随新蓝图结构输出
8. 旧逻辑已删除，不存在兼容 fallback

---

## 12. 风险与控制

## 风险 1：删掉固定逻辑后，短期输出会不稳定
### 控制
允许输出更“空”，但不允许回退到旧模板；信息不足必须显式进 gap。

## 风险 2：推理自由度提高后，文档结构变散
### 控制
固定输出章节与最小字段，但不固定内部结论。

## 风险 3：知识接入后仍然只是装饰
### 控制
把“知识如何影响判断”列入正式检查项。

## 风险 4：preview 跟不上新结构
### 控制
先保持蓝图章节稳定，再逐步优化 preview 消费逻辑。

---

## 13. 一句话决策

本次优化的正式决策是：

**在保留现有主链路与模块职责分离的前提下，彻底删除 generation 内部旧固定逻辑，不保留兼容模式；将 facts、business、experience 全部改造成由当前输入与命中知识动态驱动的真正推理式生成。**
