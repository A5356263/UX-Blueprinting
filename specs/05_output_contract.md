# 输出合同

## 目标

定义项目主链路产物与检查产物的最小结构合同，并确保 `specs/08`、`specs/09`、`specs/10` 升级后的阶段输出在主链路中保持一致。

## 正式输出位置

执行中产物：

- `projects/<project-id>/workspace/facts.md`
- `projects/<project-id>/workspace/business_blueprint.md`
- `projects/<project-id>/workspace/experience_blueprint.md`
- `projects/<project-id>/workspace/gap_list.md`
- `projects/<project-id>/workspace/check_report.md`
- `projects/<project-id>/workspace/check_status.json`

预览产物：

- `projects/<project-id>/runtime/preview/`

## facts.md

必须至少符合 `specs/08_fact_extraction_contract.md`，并包含：

- `1. 核心需求事实`
- `2. 功能范围`
- `3. 关键业务规则`
- `4. 状态流转`
- `5. 异常与边界`
- `6. 依赖与前置条件`
- `7. GAP / 待确认`

## business_blueprint.md

必须至少符合 `specs/09_business_blueprint_contract.md`，并包含：

- `评审对象与任务边界`
- `领域基线`
- `方案意图与变更类型`
- `合理性判断`
- `底层逻辑一致性判断`
- `管理策略一致性判断`
- `能力归位判断`
- `价值、成本与认知负担评估`
- `备选路径比较`
- `最终业务立场`
- `关键规则与依赖影响`
- `风险与反模式`
- `开放问题与缺口`
- `判断追踪映射`

## experience_blueprint.md

必须至少符合 `specs/10_experience_blueprint_contract.md`，并包含：

- `体验目标与任务边界`
- `体验推导依据`
- `信息架构总览`
- `任务流蓝图`
- `页面 / 窗口清单`
- `关键页面蓝图`
- `区块布局示意`
- `内容与信息优先级合同`
- `状态与反馈矩阵`
- `文案合同`
- `风险、疑惑点与保护策略`
- `开放问题与缺口`
- `体验追踪映射`

体验蓝图不得再被压缩为“只写体验要求”的摘要型说明。

## check_report.md

必须包含：

- `Summary`
- `Output Status`
- `Blockers`
- `Warnings`
- `Infos`
- `Coverage Check`
- `Machine Status`

## check_status.json

必须包含：

- `task_id`
- `status`
- `has_blocker`
- `blocker_count`
- `warning_count`
- `info_count`
- `completed_outputs`
- `missing_outputs`
- `issues`
- `metrics`

## 失败条件

- 任一必需输出缺失
- 任一输出未落在规定位置
- `business_blueprint.md` 或 `experience_blueprint.md` 仍停留在旧摘要式结构
- 模板、gate、validate 与 `specs/09`、`specs/10` 的最小结构要求不一致
- 检查双产物缺失或状态不一致
