# LLD｜Generation 推理生成改造具体细节

## 1. 设计范围

本细节设计只覆盖 `packages/generation/` 内部重构，不扩展到：

- task_card
- context_assemble
- validate
- wiki 子系统
- preview

---

## 2. 推荐目录结构

```text
packages/generation/
  core.py
  reasoning/
    schemas.py
    facts_reasoner.py
    business_reasoner.py
    experience_reasoner.py
    renderers.py
```

---

## 3. core.py 新职责

`core.py` 只保留总调度职责：

1. 读取 source / workspace / runtime 输入
2. 调用 facts reasoner
3. 调用 business reasoner
4. 调用 experience reasoner
5. 调用 renderers 写正式产物
6. 更新 provenance

不再承担：

- 关键词表驱动结论
- 固定页面骨架拼装
- 大段模板正文直接拼接

---

## 4. 中间模型定义

## 4.1 facts_model
最小字段建议：

```json
{
  "task_goal": "",
  "actors": [],
  "objects": [],
  "rules": [],
  "states": [],
  "actions": [],
  "exceptions": [],
  "dependencies": [],
  "gaps": [],
  "trace_links": []
}
```

### 作用
- 作为 business 的唯一正式事实输入
- 不直接产出业务立场

---

## 4.2 business_model
最小字段建议：

```json
{
  "review_target": "",
  "change_intent": "",
  "domain_baseline": [],
  "judgments": [],
  "placement_options": [],
  "tradeoffs": [],
  "final_position": {},
  "risk_items": [],
  "open_questions": [],
  "experience_constraints": []
}
```

### judgments
每条判断至少包含：

- `judgment_id`
- `topic`
- `conclusion`
- `evidence`
- `baseline_refs`
- `comparison`
- `remaining_gap`

### final_position
至少包含：

- `position_id`
- `conclusion`
- `reason`
- `impact_to_experience`

---

## 4.3 experience_model
最小字段建议：

```json
{
  "experience_goal": "",
  "flow_loops": [],
  "pages": [],
  "state_matrix": [],
  "copy_contracts": [],
  "risk_protections": [],
  "open_questions": [],
  "trace_links": []
}
```

### flow_loops
每个闭环至少包含：

- `loop_id`
- `loop_name`
- `user_goal`
- `steps`
- `entry`
- `exit`
- `success_result`
- `failure_result`

### steps
每个流程节点至少包含：

- `step_id`
- `user_intent`
- `user_question`
- `required_information`
- `action`
- `state_change`
- `risk_point`
- `page_ref`

### pages
每页至少包含：

- `page_id`
- `page_name`
- `page_type`
- `page_goal`
- `primary_task`
- `secondary_tasks`
- `entry_condition`
- `headline_information`
- `main_information`
- `support_information`
- `states`
- `copy_responsibilities`
- `reading_order`
- `related_flows`

---

## 5. 推理层设计

## 5.1 facts_reasoner
### 输入
- requirement.md
- background.md
- context_manifest.json
- 显式引用 wiki / knowledge

### 输出
- facts_model

### 规则
- 只提取，不判断是否合理
- 缺信息必须进 `gaps`
- 事实必须保持 trace

---

## 5.2 business_reasoner
### 输入
- facts_model
- wiki / knowledge 基线
- business contract

### 输出
- business_model

### 推理步骤
1. 识别本次变更意图
2. 建立领域基线
3. 形成核心判断
4. 做能力归位比较
5. 形成最终立场
6. 输出体验层约束

### 注意
- 不输出页面方案
- 不输出 UI 细节
- 不把体验偏好误写成业务立场

---

## 5.3 experience_reasoner
### 输入
- facts_model
- business_model
- wiki / guideline
- experience contract

### 输出
- experience_model

### 推理步骤
1. 识别核心任务闭环
2. 拆分闭环节点
3. 为节点分配页面承载
4. 生成页面蓝图
5. 生成状态矩阵
6. 生成文案责任
7. 生成风险保护

### 注意
- 先有闭环，再有页面
- 先有页面目标，再有页面内容
- 先有阅读顺序，再有区块表达

---

## 6. 渲染层设计

## 6.1 facts 渲染
保持现有合同章节，但内容来自 facts_model。

## 6.2 business 渲染
推荐改成线性结构：

1. 评审对象与任务边界
2. 方案意图与问题定义
3. 领域基线
4. 核心业务判断链
5. 能力归位比较
6. 最终业务立场
7. 风险与开放问题
8. 对体验层的约束
9. 判断追踪映射

## 6.3 experience 渲染
推荐改成线性结构：

1. 体验目标与边界
2. 任务闭环总览
3. 闭环 A / 闭环 B
4. 页面 / 窗口清单
5. 关键页面蓝图
6. 状态与反馈矩阵
7. 文案合同
8. 风险与保护策略
9. 体验追踪映射

---

## 7. 页面级输出细则

每个关键页面至少要回答：

- 这个页面解决什么问题
- 用户为什么来到这里
- 首屏先看到什么
- 主任务是什么
- 次任务是什么
- 哪些信息必须前置
- 哪些信息可后置
- 当前有哪些状态
- 每个状态如何反馈
- 用户最容易误解什么
- 文案应该承担什么解释责任
- 页面阅读顺序是什么

### reading_order 建议结构
```json
[
  "header",
  "summary",
  "main_task_area",
  "risk_or_limit_note",
  "support_info",
  "footer_actions"
]
```

---

## 8. 状态与流程细则

### 流程必须是闭环
每个任务流至少要交代：

- 起点
- 主动作
- 关键判断点
- 成功结果
- 失败结果
- 下一步

### 状态必须嵌入流程节点
状态不是独立罗列，而应说明：

- 它在哪个节点出现
- 为什么出现
- 用户当下能做什么
- 需要看到什么解释

---

## 9. 文案合同细则

每类文案至少包含：

- `copy_id`
- `scene`
- `goal`
- `must_include`
- `forbidden_style`
- `example_direction`

重点不只是“写什么”，而是：

- 这句文案在解释什么
- 它防止用户误解什么
- 它在流程中承担什么责任

---

## 10. 与检查链路的对齐点

虽然 validate 不负责推理，但 generation 重构后必须保持：

- business judgment 可追溯
- experience 页面 / 流程 / 状态 / 文案仍可被检查
- 页面 ID、流程 ID、判断 ID 不消失
- gap 与 trace 继续保留

---

## 11. 迁移策略

推荐采用“两阶段迁移”：

### 第一阶段
- 保持现有 Markdown 输出结构
- 先把推理本体迁到 model
- 确保 validate 不破

### 第二阶段
- 再优化 business / experience 的阅读结构
- 将网状表述改成更线性的闭环表述

这样可以避免一次性改动过大。

---

## 12. 完成判定

当以下条件成立，可视为 LLD 落地完成：

1. `generation/core.py` 只保留调度
2. 三层中间模型已建立
3. business 不再由固定判断模板直接拼接
4. experience 不再由固定页面骨架直接拼接
5. 页面级输出已覆盖流程、状态、信息结构、阅读顺序、文案责任
6. 输出更利于人类线性阅读
7. 现有 gate / validate / coverage 仍可运行

---

## 13. 一句话细节结论

本次 LLD 的关键不是“再写更多模板”，而是把生成过程拆成“中间模型推理 + Markdown 渲染”两层，并让 business 与 experience 的最终表达从固定章节填充，升级为更适合人读的业务判断链、任务闭环与页面阅读顺序。
