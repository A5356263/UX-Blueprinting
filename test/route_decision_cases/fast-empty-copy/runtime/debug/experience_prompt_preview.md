# Experience Prompt 预览（仅调试）

> 说明：此文件仅用于排查，不参与主链路生成与评审。
> 权威输入：`projects/fast-empty-copy/workspace/facts.md`、`projects/fast-empty-copy/workspace/business_blueprint.md`、`E:/AI设计/体验蓝图构建思路/specs/10_experience_blueprint_contract.md`、`E:/AI设计/体验蓝图构建思路/templates/experience_blueprint.template.md`

## 1. 任务目标

- Protocol Name: UXB Test Task
- Protocol Version: 1.0
- Task ID: fast-empty-copy
- Task Name: 空状态文案微调
- Domain: test
- 优化空状态提示文案，让用户知道当前没有可展示内容。
- 用户进入列表页时，当前筛选条件下没有数据。
- projects/fast-empty-copy/source/requirement.md

## 2. route 判断

- 需求类型：业务流程调整；建议路线：standard；置信度：medium。
- 重点维度：流程承接。
- route 输出建议：重点展开主路径变化、步骤衔接、角色协同和结果回写
- 升级信号：后续发现新增核心业务能力、重构既有模块或改变业务对象关系时，需升级 full。；后续发现多角色协作闭环、权限模型、审批模式或状态机变化时，需升级 full。
- route 判断理由：初判为业务流程调整，主要压力在流程承接，需要保留业务边界判断后再转体验方案。
- 写作规则以对应 specs 中的路线说明要求为准。

## 3. facts 摘要

- 输入来源：source/requirement.md 与 source/background.md。
- 用户进入列表页时，当前条件下没有数据，需要优化空状态提示。
- 仅调整空状态提示内容。
- 不新增列表字段、筛选条件、权限规则或审批动作。
- 当前没有新增业务规则。
- 空状态只说明当前没有可展示内容。
- 页面仍保持原有加载成功后的空结果状态。
- 不新增状态机节点。
- 不处理接口失败、权限不足或数据加载失败。
- 本次只处理无数据结果的提示。
- 依赖现有列表页和现有空状态组件。
- 无阻断问题。

## 4. business 核心判断与承接要求

### business 核心判断
- business_blueprint.md 暂缺或内容不足，请先补齐 business。

## 5. 设计指南导航（按需消费）

- 当前任务未命中显式指南导航，将按业务承接要求保守生成。

## 6. 设计指南消费判断

在输出体验蓝图前，请基于 facts.md 和 business_blueprint.md 判断：
1. 本次业务蓝图中是否出现报错、阻断、校验、状态反馈、审批延迟、批量风险、高风险配置等体验问题。
2. 这些问题是否命中 Design Guidelines 中的具体 summary。
3. 如果命中 summary，必须读取其 source_refs 指向的 raw，并只吸收原则，不暴露大段原文。
4. 体验蓝图不得凭指南替代业务事实；业务事实不足时，只能输出待确认问题或条件型建议。
5. 输出方案时，需要说明反馈时机、反馈形式、用户可见文案和用户下一步。


## 7. 设计原则摘要

- 先写主流程，再补次流程与异常阻断流程。
- 页面/弹窗/抽屉必须写清页面目标、进入条件、操作、状态反馈和异常处理。
- 文案必须给具体草案，不写抽象策略句。
- 禁止重做事实抽取、业务判断或需求全文重读。

## 8. 待确认问题

- 当前暂无显式待确认问题，需在生成时主动暴露不确定项。

## 9. 输出模板要求

- 输出文件：`projects/{project_id}/workspace/experience_blueprint.md`
- 固定章节：
  - `## 1. 交互流程总览`
  - `## 2. 主交互流程`
  - `## 3. 次交互流程`
  - `## 4. 异常与阻断流程`
  - `## 5. 页面 / 弹窗 / 抽屉设计`
  - `## 6. 状态与反馈文案`
  - `## 7. 待确认问题`
