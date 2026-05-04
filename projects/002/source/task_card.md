# Task Card

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.2
- Task ID: 002
- Task Name: 权限自助申请全链路蓝图
- Domain: permission

## Task Goal

- 基于真实需求文档，构建"员工自助申请权限"从事实提炼到业务判断再到体验转译的全链路蓝图。
- 本次输出服务于权限产品方案评审、实施可行性评审与后续体验方案落地对齐。

## Task Scenario

- 场景：中大型企业希望降低超管集中授权压力，支持员工查看个人权限并发起权限申请，经审批后生效。
- 任务类型：新建任务，从零建立 `projects/002` 身份与产物。
- 执行范围：覆盖 facts / business / experience 全链路，并输出检查结果。

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
3. 生成 facts.md（详见 `specs/08_fact_extraction_contract.md`）→ 运行 `python -m packages gate-facts 002`，通过才能进入下一步
4. 生成 business_blueprint.md（详见 `specs/09_business_blueprint_contract.md`）→ 运行 `python -m packages gate-business 002`，通过才能进入下一步
5. 生成 experience_blueprint.md（详见 `specs/10_experience_blueprint_contract.md`）→ 运行 `python -m packages gate-experience 002`，通过才能进入下一步
6. 运行 `python -m packages validate 002` 和 `python -m packages coverage 002`
7. 运行 `python -m packages archive 002`（产物镜像到 exports/）

## Constraints

- 不得臆造业务事实
- 信息不足处保留 `[GAP]`
- 正式产出必须写入 `workspace/`
- 不得用聊天回复替代正式文档产物
- facts 阶段不得把引用知识提升为当前任务的已确认事实
- business 阶段不得输出 UI 方案或实现方案
- experience 阶段不得输出高保真视觉稿或研发实现细节
- **阶段门禁**：每个阶段必须 gate 通过后才能进入下一阶段。不得在 facts gate 通过前生成 business_blueprint.md，不得在 business gate 通过前生成 experience_blueprint.md。不得一次性写完所有产物再回头补 gate。

## Knowledge

- knowledge/wiki/index.md
- knowledge/wiki/summaries/business/permission/00_domain_overview.md

## Design Guidelines

- knowledge/wiki/summaries/guidelines/README.md

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

## Result Locations

- 执行中结果: projects/002/workspace/
- 归档结果: projects/002/exports/final/

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
- 参考示例：`test/Experience_Blueprint 理想效果.md`

## Notes

- 本任务输入以 `projects/002/source/requirement.md` 为唯一事实来源；知识库仅用于校准与补充判断。
- 若需求中存在未明确审批规则、敏感权限清单或埋点口径，需在产物中显式标记 `[GAP]`。
