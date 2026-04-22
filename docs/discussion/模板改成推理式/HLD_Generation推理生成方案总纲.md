# HLD｜Generation 从模板生成改为推理生成方案总纲

## 1. 目标

本方案用于将当前 `generation` 从“固定模板填充”升级为“基于输入与知识的分层推理生成”。

升级后目标：

- 不再先假定固定页面骨架、固定流程骨架、固定判断骨架
- 先形成事实、业务、体验三层中间推理结果，再渲染正式文档
- 同时提升 `business_blueprint.md` 与 `experience_blueprint.md`
- 输出更适合人读的线性蓝图，而不是网状堆叠说明
- 保持现有主链路不变，保持模块职责分离

---

## 2. 当前问题

当前 `generation` 的主要问题不是“没有结构”，而是“先有结构壳，再往里填内容”。

表现为：

- facts / business / experience 主要由固定章节驱动
- business judgment 仍偏保底评审模板
- experience 仍偏固定页面骨架与固定区块表达
- 文档可过检查，但对复杂任务不够贴合
- 对人类阅读不够友好，流程、页面、状态、文案之间缺少线性闭环

---

## 3. 本次升级的核心决策

### 3.1 保持主链路不变
不新增正式阶段，不改主链路顺序，仍保持：

- facts
- business
- experience
- gate / validate / coverage / archive / preview

### 3.2 只重构 generation 内核
本次主改动只落在 `packages/generation/` 内部：

- 先推理
- 再渲染

不把推理职责扩散到：

- task_card
- context_assemble
- validate
- wiki 子系统
- preview

### 3.3 business 与 experience 同时改
- `facts` 只做轻度升级，继续保持结构化提取定位
- `business` 从“固定评审模板”改为“业务判断生成”
- `experience` 从“固定页面模板”改为“任务流与页面蓝图生成”

### 3.4 输出改成更适合人读的线性蓝图
后续蓝图表达应以线性理解为主：

- 业务蓝图：按“业务判断链”展开
- 体验蓝图：按“任务闭环”展开
- 页面蓝图：按“页面阅读顺序”展开

---

## 4. 升级后的总体架构

```text
source + wiki + knowledge + guideline
        ↓
facts reasoning
        ↓
facts model
        ↓
business reasoning
        ↓
business model
        ↓
experience reasoning
        ↓
experience model
        ↓
markdown renderer
        ↓
facts.md / business_blueprint.md / experience_blueprint.md
```

---

## 5. 新的生成原则

## 5.1 规则只约束边界，不替代结论
允许保留：

- 阶段边界
- 证据要求
- 输出结构要求
- 最小颗粒度要求

不允许写死：

- 固定页面数量
- 固定流程数量
- 固定业务立场
- 固定体验结论

## 5.2 固定输出壳，不固定内部结论
可以固定：

- 文档必须有哪些章节
- 每类章节最少要覆盖哪些信息

不能固定：

- 每次都必须是同一种页面集合
- 每次都必须是同一种流程形态
- 每次都必须落到同一种信息结构

## 5.3 先做中间模型，再渲染文档
Markdown 不再是推理本体，只是最终承载层。

---

## 6. 业务蓝图升级方向

升级后 `business_blueprint.md` 应回答：

- 这次需求到底要解决什么业务问题
- 该需求是否合理
- 是否符合领域底层逻辑
- 是否符合治理与管理策略
- 能力应该独立、并入、降级还是不做
- 代价与收益是否匹配
- 最终业务立场是什么

推荐按线性“判断链”输出：

1. 问题与变更意图
2. 领域基线
3. 核心判断
4. 取舍比较
5. 最终业务立场
6. 风险与缺口
7. 对体验层的输入约束

---

## 7. 体验蓝图升级方向

升级后 `experience_blueprint.md` 不只回答“有哪些页面”，还必须回答：

- 一个或几个完整任务闭环是什么
- 每个闭环节点用户在看什么、做什么、为什么会犹豫
- 信息在流程不同节点应该如何表达
- 哪些页面承接哪个流程节点
- 页面中的状态、注意点、信息结构、阅读顺序如何组织
- 文案在什么节点承担解释责任

推荐按线性“任务闭环”输出：

1. 任务闭环总览
2. 闭环 A / 闭环 B
3. 每个闭环对应页面
4. 页面级蓝图
5. 状态与反馈矩阵
6. 文案合同
7. 风险保护与开放问题

---

## 8. 推荐文件结构

```text
packages/generation/
  core.py
  reasoning/
    facts_reasoner.py
    business_reasoner.py
    experience_reasoner.py
    renderers.py
    schemas.py
```

职责建议：

- `core.py`：总调度
- `facts_reasoner.py`：facts 中间模型生成
- `business_reasoner.py`：business 中间模型生成
- `experience_reasoner.py`：experience 中间模型生成
- `renderers.py`：Markdown 渲染
- `schemas.py`：中间模型结构定义

---

## 9. 非目标

本次不做：

- 不重构 Wiki 子系统
- 不改 task_card 协议
- 不改主链路阶段顺序
- 不引入高保真视觉生成
- 不让 preview 反向决定蓝图
- 不把 validate 变成推理器

---

## 10. 验收标准

升级完成后，至少满足：

1. `generation` 不再预设固定页面骨架
2. `business_blueprint.md` 由业务判断驱动，而不是模板填空
3. `experience_blueprint.md` 由任务闭环与页面推导驱动，而不是固定页面模板
4. facts / business / experience 都存在中间模型
5. 输出更适合人读，能顺着“业务判断 -> 任务流程 -> 页面阅读”理解
6. 现有主链路、validate、preview 仍能工作
7. 模块职责分离不被破坏

---

## 11. 一句话决策

本次升级的正式决策是：

**保持主链路不变，只重构 `generation` 内核；将当前“模板填充式生成”升级为“分层推理后渲染”的生成模式，同时重构 business 与 experience 的生成逻辑，并将蓝图表达重心改为更适合人读的线性判断链、任务闭环与页面阅读顺序。**
