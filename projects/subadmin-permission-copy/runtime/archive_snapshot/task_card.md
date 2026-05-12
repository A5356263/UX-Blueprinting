# Task Card

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.2
- Task ID: subadmin-permission-copy
- Task Name: 子管理员支持复制
- Domain: 权限管理

## Task Goal

- 为子管理员模式新增「复制」能力，允许权限管理员将已有子管理员的「可授权组织」和「可授权功能」批量复制给最多 200 名用户
- 解决集团型客户批量配置子管理员时重复勾选效率低的问题
- 输出完整业务蓝图和体验蓝图，服务于产品评审和研发实现

## Task Scenario

- 新建任务
- 基于已确认的需求文档和诊断咨询结论，输出全链路正式产物（facts → business → experience）
- 全链路覆盖

## Required Inputs

- projects/subadmin-permission-copy/source/requirement.md
- projects/subadmin-permission-copy/source/background.md

## Required Outputs

- projects/subadmin-permission-copy/workspace/facts.md
- projects/subadmin-permission-copy/workspace/business_blueprint.md
- projects/subadmin-permission-copy/workspace/experience_blueprint.md
- projects/subadmin-permission-copy/workspace/gap_list.md
- projects/subadmin-permission-copy/workspace/check_report.md
- projects/subadmin-permission-copy/workspace/check_status.json

## Read Order

1. 先读本文件
2. 再读 `Required Inputs`
3. 生成 facts.md（详见 `specs/08_fact_extraction_contract.md`）→ 运行 `python -m packages gate-facts subadmin-permission-copy`，通过才能进入下一步
4. 生成 business_blueprint.md（详见 `specs/09_business_blueprint_contract.md`）→ 运行 `python -m packages gate-business subadmin-permission-copy`，通过才能进入下一步
5. 生成 experience_blueprint.md（详见 `specs/10_experience_blueprint_contract.md`）→ 运行 `python -m packages gate-experience subadmin-permission-copy`，通过才能进入下一步
6. 运行 `python -m packages validate subadmin-permission-copy` 和 `python -m packages coverage subadmin-permission-copy`
7. 运行 `python -m packages archive subadmin-permission-copy`（产物镜像到 exports/）

## Constraints

- 不得臆造业务事实
- 信息不足处保留 `[GAP]`
- 正式产出必须写入 `workspace/`
- 不得用聊天回复替代正式文档产物
- facts 阶段不得把引用知识提升为当前任务的已确认事实
- business 阶段不得输出 UI 方案或实现方案
- experience 阶段不得输出高保真视觉稿或研发实现细节
- **阶段门禁**：每个阶段必须 gate 通过后才能进入下一阶段

## Knowledge

- knowledge/wiki/index.md

## Wiki

- knowledge/wiki/index.md

## Design Guidelines

- knowledge/wiki/index.md

## Knowledge Consumption Policy

### Primary Knowledge Entry

- knowledge/wiki/index.md

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

## Result Locations

- 执行中结果: projects/subadmin-permission-copy/workspace/
- 归档结果: projects/subadmin-permission-copy/exports/final/

## Completion Criteria

- 必需输出文件全部存在
- `check_report.md` 已生成
- 无 blocker

## Facts Output Requirements

产出规范见 `specs/08_fact_extraction_contract.md` 和 `templates/facts.template.md`。

核心要求：
- 用自然语言理解和重述需求，不切碎原文，不填表，不用 ID 编号
- 禁止把引用知识提升为当前任务的已确认事实
- 信息不足处保留 `[GAP]`

## Business Output Requirements

产出规范见 `specs/09_business_blueprint_contract.md` 和 `templates/business_blueprint.template.md`。

核心要求：
- 用业务分析师的自然语言做判断，不复制 facts 碎片
- 禁止输出 UI 方案或实现方案
- 方案承接要求必须具体、可执行

## Experience Output Requirements

产出规范见 `specs/10_experience_blueprint_contract.md` 和 `templates/experience_blueprint.template.md`。

核心要求：
- 每个交互节点写清用户动作、系统反馈、前置解释、具体文案、下一步
- 文案必须是可直接展示的文本，禁止元指令
- 禁止输出高保真视觉稿或研发实现细节

## Notes

- 基于已确认的需求文档和诊断咨询结论（10 个不明确事项中 1-7 已采纳，8-10 按现状不动）
- 双管理员互审完整审批规则留待产品补充，蓝图阶段按状态模型设计
