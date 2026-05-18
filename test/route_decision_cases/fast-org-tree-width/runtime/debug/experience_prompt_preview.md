# Experience Prompt 预览（仅调试）

> 说明：此文件仅用于排查，不参与主链路生成与评审。
> 权威输入：`projects/fast-org-tree-width/workspace/facts.md`、`projects/fast-org-tree-width/workspace/business_blueprint.md`、`E:/AI设计/体验蓝图构建思路/specs/10_experience_blueprint_contract.md`、`E:/AI设计/体验蓝图构建思路/templates/experience_blueprint.template.md`

## 1. 任务目标

- Protocol Name: UXB Test Task
- Protocol Version: 1.0
- Task ID: fast-org-tree-width
- Task Name: 组织树宽度拖动
- Domain: test
- 优化组织树宽度展示，让长部门名称更容易查看。
- 用户在组织架构页面查看层级较深的部门名称。
- projects/fast-org-tree-width/source/requirement.md

## 2. route 判断

- 需求类型：布局交互优化；建议路线：fast；置信度：unknown。
- 重点维度：布局交互。
- route 输出建议：重点展开默认状态、交互边界、极限状态、响应方式和偏好记忆。
- route 判断理由：这次主要影响组织树的页面表现和交互边界，不改变权限、审批、数据范围或业务规则，适合按局部体验优化处理。
- 写作规则以对应 specs 中的路线说明要求为准。

## 3. facts 摘要

- 输入来源：source/requirement.md 与 source/background.md。
- 组织架构页面左侧组织树在层级较深时，部门名称容易被截断。
- 用户希望拖动组织树区域宽度，并在本浏览器内记忆默认宽度。
- 支持组织树区域宽度调整。
- 支持页面刷新后恢复本浏览器内默认宽度。
- 不要求跨设备同步。
- 不新增组织、成员、角色或权限能力。
- 不改变组织数据、成员数据或权限规则。
- 不新增业务状态。
- 仅涉及界面展示宽度的本地记忆。
- 需要定义最小宽度、最大宽度、长名称展示和窗口缩小时的响应方式。
- 依赖现有组织架构页面和左侧组织树。

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
