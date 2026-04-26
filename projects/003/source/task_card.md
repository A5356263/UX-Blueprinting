# Task Card

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.2
- Task ID: 003
- Task Name: 员工自助申请与查询权限能力设计
- Domain: permission

## Task Goal

- 解决企业员工权限分配效率低下的问题，通过支持员工自助申请和查询权限来分散权限管理工作
- 本次输出服务于产品功能设计和用户体验设计评审

## Task Scenario

- 本次任务场景：基于权限需求文档，设计员工自助申请权限的功能方案
- 这是新建任务，需要从零开始建立完整的功能设计方案
- 本次任务覆盖全链路：从事实提取到业务蓝图再到体验设计

## Required Inputs

- projects/003/source/requirement.md
- projects/003/source/background.md

## Required Outputs

- projects/003/workspace/facts.md
- projects/003/workspace/business_blueprint.md
- projects/003/workspace/experience_blueprint.md
- projects/003/workspace/gap_list.md
- projects/003/workspace/check_report.md
- projects/003/workspace/check_status.json

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

## Wiki

- knowledge/wiki/index.md
- knowledge/wiki/summaries/business/permission/00_domain_overview.md

## Knowledge Consumption Policy

### Primary Knowledge Entry

- knowledge/wiki/index.md
- knowledge/wiki/summaries/business/permission/00_domain_overview.md

### Fallback Source

- knowledge/raw/business/permission/

### Fallback Conditions

- 命中 `[GAP]`
- 命中 `[CONFLICT]`
- 摘要页未覆盖当前任务需要的对象、规则或路径

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

- 执行中结果: projects/003/workspace/
- 归档结果: projects/003/exports/final/

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

- 当前为模板占位，可按任务补充
- 若任务明确只做到某一阶段，可在 `Task Scenario` 中标注并在 `Required Outputs` 中裁剪，但必须保持协议可解析
