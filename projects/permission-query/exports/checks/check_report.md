# Check Report｜人读说明版

> 本文件是 `projects/permission-query/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 11
- info_count: 7

## Output Status

- projects/permission-query/workspace/facts.md: present
- projects/permission-query/workspace/business_blueprint.md: present
- projects/permission-query/workspace/experience_blueprint.md: present
- projects/permission-query/workspace/gap_list.md: present
- projects/permission-query/workspace/check_report.md: present
- projects/permission-query/workspace/check_status.json: present

## Blockers

- none

## Warnings

- experience gate 状态为 warning
- experience_blueprint.md 旅程图列表存在，但未形成可解析的角色路径结构
- facts gate 状态为 warning
- 承接检查：business_blueprint.md 已把“信息过载风险：通过渐进式信息披露和默认折叠缓解”列为需要保护的风险，但 experience_blueprint.md 还没有把它转成用户可见规则、提示或保护动作。
- 承接检查：business_blueprint.md 已把“子管理员越界查询：显式提示管理边界”列为必须处理的异常，但 experience_blueprint.md 还没有写清触发时机、反馈文案或用户下一步。
- 承接检查：business_blueprint.md 明确要求主流程闭环包含“三个查询维度的完整查询-查看结果-查看详情的闭环...”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。
- 承接检查：business_blueprint.md 明确要求主流程闭环包含“查询结果到配置页的导航跳转（查询发现异常后去修复...”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。
- 承接检查：business_blueprint.md 明确要求主流程闭环包含“查询结果导出流程”，但 experience_blueprint.md 还没有把这一段转成清晰的用户流程、系统反馈或结果去向。
- 承接检查：business_blueprint.md 要求解释“可见性截断提示（子管理员的管理范围边界）”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- 承接检查：business_blueprint.md 要求解释“权限来源（直接授予/角色授予/叠加）”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。
- 承接检查：business_blueprint.md 要求解释“权限颗粒度层级关系（功能权限、数据权限等类型区分...”，但 experience_blueprint.md 的状态与反馈文案还没有把状态含义、用户动作和页面反馈写完整。

## Infos

- business gate 状态：passed
- 自然语言承接检查：主流程闭环覆盖：0/3
- 自然语言承接检查：异常与阻断覆盖：3/4
- 自然语言承接检查：状态与反馈覆盖：1/4
- 自然语言承接检查：角色路径覆盖：4/4
- 自然语言承接检查：设计指南装配：3 条
- 自然语言承接检查：风险保护承接：2/3

## 自然语言承接检查

- 角色路径覆盖：4/4
- 主流程闭环覆盖：0/3
- 异常与阻断覆盖：3/4
- 状态与反馈覆盖：1/4
- 风险保护承接：2/3
- 设计指南装配：3 条

## Machine Status

- 机器可读状态文件：`projects/permission-query/workspace/check_status.json`
