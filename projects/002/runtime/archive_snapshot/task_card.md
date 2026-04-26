# Task Card

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.2
- Task ID: 002
- Task Name: 员工自助申请与查询权限能力设计
- Domain: permission

## Task Goal

- 基于 `test/权限需求文档.md` 的真实需求，从零建立“员工自助申请与查询权限能力设计”的当前任务身份，并生成 facts、business、experience 正式产物。
- 本次输出主要服务于权限域产品方案评审、业务判断收敛与体验蓝图构建。

## Task Scenario

- 当前任务场景是企业权限管理从“管理员统一分配”扩展为“员工可自助查询权限、申请权限，并在审批通过后自动生效”的真实产品方案设计。
- 本次任务属于新任务从零建模，不是旧项目重跑，不是历史产物复制，也不是只校对已有结果。
- 本次任务覆盖 facts / business / experience 全链路。

## Required Inputs

- projects/002/source/requirement.md
- projects/002/source/background.md

## Required Outputs

- projects/002/workspace/facts.md
- projects/002/workspace/business_blueprint.md
- projects/002/workspace/experience_blueprint.md
- projects/002/workspace/gap_list.md
- projects/002/workspace/check_report.md
- projects/002/workspace/check_status.json

## Read Order

1. 先读本文件
2. 再读 `Required Inputs`
3. facts 阶段只做 input-first extraction
4. business 阶段在 facts 基础上引入业务知识做 review
5. experience 阶段在 business 基础上引入 guideline 做 translation
6. 最后按 `Templates` 产出结果并按 `Checks` 自检

## Constraints

- 不得臆造业务事实
- 信息不足处保留 `[GAP]`
- 正式产出必须写入 `workspace/`
- 不得用聊天回复替代正式文档产物
- facts 阶段不得把引用知识提升为当前任务的已确认事实
- business 阶段不得输出 UI 方案或实现方案
- experience 阶段不得输出高保真视觉稿或研发实现细节

## Knowledge

- knowledge/wiki/index.md
- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/11_task_scenarios.md
- knowledge/wiki/summaries/business/permission/20_decision_chain_contract.md
- knowledge/wiki/summaries/business/permission/24_governance_state_model.md
- knowledge/wiki/summaries/business/permission/31_experience_translation_requirements.md
- knowledge/wiki/summaries/business/permission/32_copy_and_explanation_strategy.md
- knowledge/wiki/summaries/guidelines/governance.md
- knowledge/wiki/summaries/guidelines/information_architecture.md
- knowledge/wiki/summaries/guidelines/usability.md

## Wiki

- knowledge/wiki/index.md
- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/31_experience_translation_requirements.md

## Knowledge Consumption Policy

### Primary Knowledge Entry

- knowledge/wiki/index.md
- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/31_experience_translation_requirements.md

### Fallback Source

- knowledge/raw/business/permission/

### Fallback Conditions

- 命中 `[GAP]`
- 命中 `[CONFLICT]`
- 摘要页未覆盖当前任务所需的对象、规则、审批链或页面承载语义

### Disallowed Broad References

- 不允许默认整目录装配到 context bundle

## Templates

- templates/facts.template.md
- templates/business_blueprint.template.md
- templates/experience_blueprint.template.md
- templates/gap_list.template.md
- templates/check_report.template.md

## Checks

- specs/06_check_contract.md
- specs/08_fact_extraction_contract.md
- specs/09_business_blueprint_contract.md
- specs/10_experience_blueprint_contract.md

## Platform Optimizations

- skills/skill_requirements_refine.md
- skills/skill_blueprint_build.md

## Result Locations

- 执行中结果: projects/002/workspace/
- 归档结果: projects/002/exports/final/

## Completion Criteria

- 必需输出文件全部存在
- `check_report.md` 已生成
- 无 blocker

## Facts Output Requirements

### Required Sections

- 任务意图
- 事实来源说明
- 术语与对象边界
- 角色与对象清单
- 原子事实清单
- 规则矩阵
- 状态模型
- 动作与流程事实
- 异常与拦截清单
- 依赖清单
- 范围与非范围
- 开放问题与缺口
- 追踪映射

### Recommended ID Prefixes

- F
- C
- R
- S
- A
- EX
- D
- SC
- OQ
- GAP

### Boundary

- mode: input-first extraction
- knowledge role: calibration only
- forbidden: promote unconfirmed knowledge as confirmed task facts
- forbidden: replace task inputs with wiki or knowledge summaries

## Business Output Requirements

### Required Sections

- 评审对象与任务边界
- 领域基线
- 方案意图与变更类型
- 合理性判断
- 底层逻辑一致性判断
- 管理策略一致性判断
- 能力归位判断
- 价值、成本与认知负担评估
- 备选路径比较
- 最终业务立场
- 关键规则与依赖影响
- 风险与反模式
- 开放问题与缺口
- 判断追踪映射

### Recommended ID Prefixes

- J
- BL
- POS
- OPT
- RSK
- AP
- OQ
- GAP

### Boundary

- mode: facts-first judgment
- knowledge role: baseline establishment
- forbidden: replace facts with knowledge-only conclusions
- forbidden: output UI or implementation decisions in business blueprint

## Experience Output Requirements

### Required Sections

- 体验目标与任务边界
- 体验推导依据
- 信息架构总览
- 任务流蓝图
- 页面 / 窗口清单
- 关键页面蓝图
- 区块布局示意
- 内容与信息优先级合同
- 状态与反馈矩阵
- 文案合同
- 风险、疑惑点与保护策略
- 开放问题与缺口
- 体验追踪映射

### Recommended ID Prefixes

- EXP
- OQ
- GAP

### Boundary

- mode: business-first translation
- knowledge role: business semantic guard + guideline-based derivation
- forbidden: rewrite business rules in experience blueprint
- forbidden: output high-fidelity visual specs or implementation details

## Notes

- 当前任务输入真源为 `test/权限需求文档.md` 的真实复制件。
- 本次任务必须从当前输入重新建立任务身份，不得默认沿用历史任务产物。
- 如输入文档存在歧义、缺失或冲突，必须在正式产物中显式暴露为 gap，不得自行补齐为既定事实。
