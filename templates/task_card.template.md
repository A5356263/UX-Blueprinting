# Task Card

## Protocol

- Protocol Name：Cross-AI Task Card
- Protocol Version：v0.2
- Task ID：{{TASK_ID}}
- Task Name：{{TASK_NAME}}
- Domain：{{DOMAIN}}

## Task Goal

- 用一句话说明本任务要解决什么问题
- 说明本次输出主要服务于哪类评审、设计或重构工作

## Task Scenario

- 描述本次任务场景
- 说明这是新建、补充、校对、重构还是审查任务
- 说明本次任务主要落在：facts / business / experience 的哪一层，或覆盖全链路

## Required Inputs

- projects/{{TASK_ID}}/source/requirement.md
- projects/{{TASK_ID}}/source/background.md

## Required Outputs

- projects/{{TASK_ID}}/workspace/facts.md
- projects/{{TASK_ID}}/workspace/business_blueprint.md
- projects/{{TASK_ID}}/workspace/experience_blueprint.md
- projects/{{TASK_ID}}/workspace/gap_list.md
- projects/{{TASK_ID}}/workspace/check_report.md
- projects/{{TASK_ID}}/workspace/check_status.json

## Read Order

1. 先读本文件
2. 再读 `Required Inputs`
3. facts 阶段仅做 input-first extraction（输入优先提取）
4. business 阶段在 facts 基础上引入业务知识做 review（评审）
5. experience 阶段在 business 基础上引入 guideline（设计指南）做 translation（转译）
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
- knowledge/wiki/summaries/{{DOMAIN}}/**

## Wiki

- knowledge/wiki/index.md
- knowledge/wiki/summaries/{{DOMAIN}}/**

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

- 执行中结果：projects/{{TASK_ID}}/workspace/
- 归档结果：projects/{{TASK_ID}}/exports/final/

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

- mode：input-first extraction
- knowledge role：calibration only
- forbidden：
  - promote unconfirmed knowledge as confirmed task facts
  - replace task inputs with wiki / knowledge summaries

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

- mode：facts-first judgment
- knowledge role：baseline establishment
- forbidden：
  - replace facts with knowledge-only conclusions
  - output UI / implementation decisions in business blueprint

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

- mode：business-first translation
- knowledge role：business semantic guard + guideline-based derivation
- forbidden：
  - rewrite business rules in experience blueprint
  - output high-fidelity visual specs or implementation details

## Notes

- 当前为模板占位，可按任务补充
- 若任务明确只做到某一阶段，可在 `Task Scenario` 中标注并在 `Required Outputs` 中裁剪，但必须保持协议可解析
