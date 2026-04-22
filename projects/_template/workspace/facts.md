# Facts

## 任务意图

- 任务目标：当前任务需要先判断再生成，并把输出建立在当前输入与命中知识之上。
- 任务边界：本次聚焦 generation 内部生成逻辑，不扩展到高保真视觉与实现细节。
- 输出用途：为 business judgment 与 experience translation 提供可追踪、可回链的当前任务事实。

## 事实来源说明

- 主输入：
  - E:/AI设计/体验蓝图构建思路/projects/_template/source/requirement.md
  - E:/AI设计/体验蓝图构建思路/projects/_template/source/background.md
- 显式引用：
- none
- 知识校准命中：
- none
- 使用边界：
  - facts 阶段坚持 input-first extraction，知识只做术语与边界校准，不替代当前任务事实

## 术语与对象边界

| term_id | 术语 | 当前任务中的含义 | 边界说明 | 来源 |
| --- | --- | --- | --- | --- |
| T-01 | 生成链路 | 当前任务需要先判断再生成，并把输出建立在当前输入与命中知识之上。 | 当前任务中的直接承接对象，需要与其上下游关系分开理解。 | projects/_template/source/task_card.md |
| T-02 | 任务边界 | 本次聚焦 generation 内部生成逻辑，不扩展到高保真视觉与实现细节。 | 当前任务中的直接承接对象，需要与其上下游关系分开理解。 | projects/_template/source/task_card.md |
| T-03 | 当前任务 | 当前任务属于 generation 内部的结构升级与生成质量优化。 | 当前任务中的直接承接对象，需要与其上下游关系分开理解。 | projects/_template/source/task_card.md |
| T-04 | 当前状态 | 当前状态是待补充，信息不足时需要保持保守输出并显式保留 gap。 | 当前任务中的直接承接对象，需要与其上下游关系分开理解。 | projects/_template/source/task_card.md |

## 角色与对象清单

### 角色清单

| actor_id | 角色 | 角色类型 | 当前职责 / 影响 | 来源 |
| --- | --- | --- | --- | --- |
| A-01 | 当前任务评审角色 | 任务相关角色 | 当前任务需要先判断再生成，并把输出建立在当前输入与命中知识之上。 | projects/_template/source/task_card.md |
| A-02 | 设计评审角色 | 任务相关角色 | 当前任务属于 generation 内部的结构升级与生成质量优化。 | projects/_template/source/task_card.md |

### 对象清单

| object_id | 对象 | 对象类型 | 当前任务中的说明 | 来源 |
| --- | --- | --- | --- | --- |
| O-01 | 生成链路 | 任务相关对象 | 当前任务需要先判断再生成，并把输出建立在当前输入与命中知识之上。 | projects/_template/source/task_card.md |
| O-02 | 任务边界 | 任务相关对象 | 本次聚焦 generation 内部生成逻辑，不扩展到高保真视觉与实现细节。 | projects/_template/source/task_card.md |
| O-03 | 当前任务 | 任务相关对象 | 当前任务属于 generation 内部的结构升级与生成质量优化。 | projects/_template/source/task_card.md |
| O-04 | 当前状态 | 任务相关对象 | 当前状态是待补充，信息不足时需要保持保守输出并显式保留 gap。 | projects/_template/source/task_card.md |
| O-05 | 知识引用 | 任务相关对象 | 当前没有显式知识引用，判断只能以 source 输入为主，并把知识缺口作为 dependency gap 暴露。 | projects/_template/source/task_card.md |

## 原子事实清单

### Actor Facts
- none

### Object Facts
- F-O01: 当前任务需要先判断再生成，并把输出建立在当前输入与命中知识之上。 (source: EV-S01)
- F-O02: 本次聚焦 generation 内部生成逻辑，不扩展到高保真视觉与实现细节。 (source: EV-S02)
- F-O03: 当前任务属于 generation 内部的结构升级与生成质量优化。 (source: EV-S03)

### State Facts
- F-S01: 当前状态是待补充，信息不足时需要保持保守输出并显式保留 gap。 (source: EV-S04)

### Action Facts
- F-AC01: 当前任务需要先判断再生成，并把输出建立在当前输入与命中知识之上。 (source: EV-S01)
- F-AC02: 当前任务属于 generation 内部的结构升级与生成质量优化。 (source: EV-S03)

### Rule Facts
- F-R01: 本次聚焦 generation 内部生成逻辑，不扩展到高保真视觉与实现细节。 (source: EV-S02)

### Exception Facts
- F-E01: 当前状态是待补充，信息不足时需要保持保守输出并显式保留 gap。 (source: EV-S04)
- F-E02: 当前没有显式知识引用，判断只能以 source 输入为主，并把知识缺口作为 dependency gap 暴露。 (source: EV-S05)

### Dependency Facts
- F-D01: 当前任务属于 generation 内部的结构升级与生成质量优化。 (source: EV-S03)
- F-D02: 当前没有显式知识引用，判断只能以 source 输入为主，并把知识缺口作为 dependency gap 暴露。 (source: EV-S05)

### Scope Facts
- F-SC01: 本次聚焦 generation 内部生成逻辑，不扩展到高保真视觉与实现细节。 (source: EV-S02)

## 规则矩阵

| rule_id | 规则名称 | trigger（触发条件） | subject（作用对象） | precondition（前置条件） | result（结果） | failure / block（失败或拦截） | source_ref |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-01 | Task Boundary规则 | Task Boundary | 任务边界 | 当前证据中涉及的前置条件成立后才可继续执行。 | 本次聚焦 generation 内部生成逻辑，不扩展到高保真视觉与实现细节。 | 当前状态是待补充，信息不足时需要保持保守输出并显式保留 gap。 | EV-S02 |

## 状态模型

| state_id | 状态 | 进入条件 | 退出条件 | 阻断条件 | 说明 | source_ref |
| --- | --- | --- | --- | --- | --- | --- |
| S-01 | 待补充 | Fallback State | 完成当前状态对应的动作或进入下一个结果态。 | 命中当前证据中的限制、异常或依赖缺失时进入阻断。 | 当前状态是待补充，信息不足时需要保持保守输出并显式保留 gap。 | EV-S04 |

## 动作与流程事实

| flow_id | 发起角色 | 动作 | 前置条件 | 后续动作 / 结果 | 备注 | source_ref |
| --- | --- | --- | --- | --- | --- | --- |
| FL-01 | 当前任务评审角色 | 生成 生成链路 | Task Goal | 当前任务需要先判断再生成，并把输出建立在当前输入与命中知识之上。 | 从当前输入直接抽取，未做模板补全：EV-S01 | EV-S01 |
| FL-02 | 设计评审角色 | 生成 当前任务 | Task Scenario | 当前任务属于 generation 内部的结构升级与生成质量优化。 | 从当前输入直接抽取，未做模板补全：EV-S03 | EV-S03 |

## 异常与拦截清单

| exception_id | 场景 | 触发条件 | 系统结果 / 提示 | 影响对象 | source_ref |
| --- | --- | --- | --- | --- | --- |
| EX-01 | 待补充 | Fallback State | 当前状态是待补充，信息不足时需要保持保守输出并显式保留 gap。 | 当前任务评审角色 | EV-S04 |
| EX-02 | 异常场景2 | Fallback Knowledge Boundary | 当前没有显式知识引用，判断只能以 source 输入为主，并把知识缺口作为 dependency gap 暴露。 | 当前任务评审角色 | EV-S05 |

## 依赖清单

| dependency_id | 依赖项 | 类型 | 当前作用 | 当前确认度 | source_ref |
| --- | --- | --- | --- | --- | --- |
| DEP-01 | 当前任务 | 任务依赖 | 当前任务属于 generation 内部的结构升级与生成质量优化。 | 推断 | EV-S03 |
| DEP-02 | 知识引用 | 知识 / 上下文 / 外部依赖 | 当前没有显式知识引用，判断只能以 source 输入为主，并把知识缺口作为 dependency gap 暴露。 | 显式提及 | EV-S05 |

## 范围与非范围

### 本次明确范围
- IN-01: 本次聚焦 generation 内部生成逻辑，不扩展到高保真视觉与实现细节。

### 本次明确非范围 / 暂不展开
- OUT-01: 当前输入没有要求进入高保真视觉设计与实现细节。

## 已知约束
- C-01: 事实层以 source 输入为主，知识只做术语与边界校准。
- C-02: 当前输入不足时保留 gap，不用通用模板句替代真实事实。

## 开放问题与缺口

### Open Questions
- none

### Gaps
- GAP-01: 当前状态是待补充，信息不足时需要保持保守输出并显式保留 gap。
- GAP-02: 当前没有显式知识引用，判断只能以 source 输入为主，并把知识缺口作为 dependency gap 暴露。
- GAP-03: 当前没有读取到可用的显式知识引用，当前只能依赖 source 输入做保守推断。

## 追踪映射

| fact_or_unit_id | 类型 | 对应原文位置 | 主要来源文件 | 备注 |
| --- | --- | --- | --- | --- |
| F-O01 | fact | Task Goal:0 | projects/_template/source/task_card.md | 当前任务需要先判断再生成，并把输出建立在当前输入与命中知识之上。 |
| F-O02 | fact | Task Boundary:0 | projects/_template/source/task_card.md | 本次聚焦 generation 内部生成逻辑，不扩展到高保真视觉与实现细节。 |
| F-O03 | fact | Task Scenario:0 | projects/_template/source/task_card.md | 当前任务属于 generation 内部的结构升级与生成质量优化。 |
| F-S01 | fact | Fallback State:0 | projects/_template/source/task_card.md | 当前状态是待补充，信息不足时需要保持保守输出并显式保留 gap。 |
| F-AC01 | fact | Task Goal:0 | projects/_template/source/task_card.md | 当前任务需要先判断再生成，并把输出建立在当前输入与命中知识之上。 |
| F-AC02 | fact | Task Scenario:0 | projects/_template/source/task_card.md | 当前任务属于 generation 内部的结构升级与生成质量优化。 |
| F-R01 | fact | Task Boundary:0 | projects/_template/source/task_card.md | 本次聚焦 generation 内部生成逻辑，不扩展到高保真视觉与实现细节。 |
| F-E01 | fact | Fallback State:0 | projects/_template/source/task_card.md | 当前状态是待补充，信息不足时需要保持保守输出并显式保留 gap。 |
| F-E02 | fact | Fallback Knowledge Boundary:0 | projects/_template/source/task_card.md | 当前没有显式知识引用，判断只能以 source 输入为主，并把知识缺口作为 dependency gap 暴露。 |
| F-D01 | fact | Task Scenario:0 | projects/_template/source/task_card.md | 当前任务属于 generation 内部的结构升级与生成质量优化。 |
| F-D02 | fact | Fallback Knowledge Boundary:0 | projects/_template/source/task_card.md | 当前没有显式知识引用，判断只能以 source 输入为主，并把知识缺口作为 dependency gap 暴露。 |
| F-SC01 | fact | Task Boundary:0 | projects/_template/source/task_card.md | 本次聚焦 generation 内部生成逻辑，不扩展到高保真视觉与实现细节。 |
