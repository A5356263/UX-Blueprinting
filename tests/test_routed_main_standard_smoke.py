from __future__ import annotations

import json
import shutil
import unittest
import uuid
from pathlib import Path

from packages.common import get_project_dir, get_repo_root
from packages.provenance import build_generated_provenance, write_provenance
from packages.routed_main.core import run_routed_main


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _task_card(project_id: str) -> str:
    return f"""
# Task Card

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.3
- Task ID: {project_id}
- Task Name: 跨端标准主链路冒烟
- Domain: 权限管理

## Task Goal

- 验证标准执行模式下的 routed main 可以在跨系统环境稳定完成 facts、business lite 和 experience 主链路。
- 这次输出主要服务于执行中枢稳定性验收，不追求业务方案完整评审。

## Task Scenario

- 这是一个用于 CI 的最小标准项目，只验证 routed main 主链路和跨系统兼容性。
- 当前任务覆盖 facts / business / experience 全链路，business 阶段采用 lite 深度。

## Required Inputs

- projects/{project_id}/source/requirement.md
- projects/{project_id}/source/background.md

## Required Outputs

- projects/{project_id}/workspace/facts.md
- projects/{project_id}/workspace/business_blueprint_lite.md
- projects/{project_id}/workspace/experience_blueprint.md
- projects/{project_id}/workspace/gap_list.md
- projects/{project_id}/workspace/check_report.md
- projects/{project_id}/workspace/check_status.json

## Read Order

1. 先读本文档
2. 再读 `Required Inputs`
3. 生成 facts.md
4. 生成 business_blueprint_lite.md
5. 生成 experience_blueprint.md
6. 运行 validate / coverage

## Constraints

- 不得臆造业务事实。
- 信息不足处保留 `[GAP]`。
- 正式产出必须写入 `workspace/`。
- facts 阶段不得把引用知识直接提升为当前任务已经确认的事实。
- business 阶段不得输出 UI 实现方案。
- experience 阶段不得输出前端技术实现细节。
- `runtime/uxb_route_decision.json` 是执行判断与知识选择唯一来源。

## Templates

- templates/facts.template.md
- templates/business_blueprint_lite.template.md
- templates/experience_blueprint.template.md
- templates/gap_list.template.md
- templates/check_report.template.md

## Checks

- specs/06_check_contract.md
- specs/08_fact_extraction_contract.md
- specs/17_business_blueprint_lite_contract.md
- specs/10_experience_blueprint_contract.md

## Result Locations

- 执行中结果: projects/{project_id}/workspace/
- 运行时产物: projects/{project_id}/runtime/

## Completion Criteria

- 必需输出文件全部存在
- `check_report.md` 已生成
- 无 blocker

## Facts Output Requirements

### Required Sections

- ## 任务概述
- ## 功能范围
- ## 关键业务规则
- ## 状态流转
- ## 异常与边界
- ## 依赖与前置条件
- ## 开放问题与缺口

### Boundary

- 只提取当前任务需要承接的事实、规则、状态、异常和依赖

## Business Output Requirements

### Required Sections

- ## 0. 本次关键业务判断
- ## 1. 一句话结论
- ## 2. 关键业务规则
- ## 3. 边界与风险
- ## 4. 体验承接要求
- ## 5. 升级信号
- ## 6. 待确认问题

### Boundary

- 只保留影响体验承接的关键规则、边界、风险与状态

## Experience Output Requirements

### Required Sections

- ## 0. 本次关键设计判断
- ## 1. 旅程图
- ## 2. 交互流程总览
- ## 3. 主交互流程
- ## 4. 次交互流程
- ## 5. 异常与阻断流程
- ## 6. 页面 / 弹窗 / 抽屉设计
- ## 7. 状态与反馈文案
- ## 8. 待确认问题

### Boundary

- 重点验证业务承接、异常处理、状态反馈和关键文案，不展开高保真视觉

## Notes

- 这是跨系统稳定性 smoke 项目，重点验证真实主链路，不作为业务方案沉淀。
""".strip()


def _facts_md(project_id: str) -> str:
    return f"""
# Facts

## 任务概述

- 这次任务要验证一个员工自助申请权限的标准链路，目标是确认执行中枢在不同系统下都能稳定读取任务卡、路由判断、知识摘要和正式产物。
- 涉及角色包括员工、审批人和权限管理员，其中员工负责提交申请，审批人负责判断是否放行，管理员只在异常或治理场景中介入。
- 主要场景是员工因为临时工作需要申请一个预定义角色包，审批通过后系统自动生效，并把结果同步回员工侧和审批侧。
- 当前事实主要来自 `projects/{project_id}/source/requirement.md` 与 `projects/{project_id}/source/background.md`，并以这两份输入作为正式承接来源。

## 功能范围

- 权限申请入口：员工从权限中心进入申请页，浏览可申请的角色包，查看申请说明、有效期和申请前置条件，再决定是否发起申请。
- 权限申请提交：员工选择角色包、填写申请理由、确认使用范围与时长后提交申请，系统生成申请单并进入待审批状态。
- 审批处理：审批人查看申请详情、判断业务理由与风险是否可接受，执行同意或拒绝，系统记录审批意见并推进后续状态。
- 生效与回收：审批通过后系统自动授予权限，到期后自动回收；若申请被关闭、撤回或被拒绝，则不会进入生效状态。

## 关键业务规则

- 员工只能申请系统已经开放的角色包，不能自由拼装权限，也不能绕过角色包直接点选底层权限。
- 申请必须填写业务理由和使用时长，审批人需要基于理由、角色包风险等级和申请人当前身份做判断。
- 审批通过后由系统自动授权，不允许审批人先同意再让管理员手工补授权，否则状态与实际结果会失去同步。
- 若角色包已关闭、申请人离职、审批链路失效或目标角色包策略发生变化，系统需要阻断继续提交并反馈明确原因。

## 状态流转

- 申请单至少存在待提交、待审批、已通过、已拒绝、已撤回、已关闭、已到期回收这些关键状态。
- 员工提交申请后状态从待提交进入待审批；审批人同意后进入已通过并触发授权；拒绝后进入已拒绝并向员工反馈原因。
- 若员工主动取消或业务方关闭申请，状态会进入已撤回或已关闭，之后不再允许继续审批或继续授权。
- 若权限生效后达到到期时间，系统会自动进入已到期回收，同时保留审计记录和结果反馈。

## 异常与边界

- 如果员工选择的角色包已下线、超出申请范围或与当前身份冲突，系统需要在入口或提交前阻断，并说明不可申请原因。
- 如果审批人在处理时发现申请已撤回、角色包策略已改变或申请单状态落后于实际结果，系统需要提示当前状态异常，避免重复审批。
- 如果自动授权失败、回收失败或状态同步失败，系统必须保留失败状态、通知相关角色，并提供后续补救入口。
- 如果员工中途退出填写页或刷新页面，系统需要明确草稿是否保留，不能让用户误以为已经提交成功。

## 依赖与前置条件

- 依赖组织内已经存在的角色包配置、审批链路配置和自动授权执行能力。
- 依赖权限系统具备状态持久化、授权日志和到期回收机制，否则无法保证状态、规则和结果一致。
- 依赖通知能力把审批结果、异常结果和到期回收结果同步给员工和审批人。

## 开放问题与缺口

- 当前默认有效期是否按角色包配置自动带出，还需要产品确认。
- 审批意见是否允许员工在申请详情页二次查看，需要进一步确认展示范围。
- 若授权执行成功但通知发送失败，是否需要单独暴露中间状态，还需要后续评估。
""".strip()


def _business_lite_md() -> str:
    return """
# 轻量业务蓝图

## 0. 本次关键业务判断

**判断：**

这次适合按轻量业务蓝图承接，因为核心变化集中在“申请、审批、生效、回收”四段标准状态链路，规则、边界、风险已经足以支撑体验承接，不需要展开完整业务蓝图。

**主要影响：**

1. 从管理员集中分配转向员工自助申请，业务入口、状态、审批和结果反馈都需要重新建立闭环。
2. 自动授权取代手工补授权后，状态同步、风险控制和异常补救成为关键规则。
3. 体验承接必须覆盖正常审批、拒绝、关闭、撤回、授权失败和到期回收，不允许只写 happy path。

**建议方案：**

- 保持角色包作为唯一可申请对象，不开放自由拼装权限。
- 审批通过后立即自动授权，并把状态、结果、风险和文案同步给员工与审批人。
- 体验层重点承接申请范围、审批结果、异常状态和补救动作，不把治理细节下放给用户。

**需要重新判断的信号：**

1. 如果后续要支持跨组织审批、按字段级范围申请或多级联动审批，就不再适合当前轻量承接。
2. 如果后续要允许员工自定义权限组合，业务规则、风险和治理边界会明显升级。

## 1. 一句话结论

可以做，但必须把“可申请范围、审批状态、授权结果、异常阻断和反馈文案”当成一个统一业务闭环处理，不能只提供提交入口而缺少后续状态承接。

## 2. 关键业务规则

- 规则一：员工只能申请预定义角色包，申请前必须看到角色包名称、使用范围、有效期和申请说明，不能直接选择底层权限。
- 规则二：申请提交时必须填写明确业务理由和使用时长，审批人依据理由、角色包风险等级和申请人身份做判断，拒绝时需要保留原因文案。
- 规则三：审批同意后系统立即执行授权，状态从待审批进入已通过，再进入已生效；如果授权失败，状态必须显式停在失败态，而不是伪装成已完成。
- 规则四：申请被撤回、关闭、拒绝或到期回收时，都需要有明确状态、规则口径和结果反馈，避免员工误以为权限仍然有效。
- 规则五：任何异常状态都不能跳过审计记录，系统需要保留处理时间、处理人和结果，以便后续治理与复盘。

## 3. 边界与风险

- 边界一：当前只支持申请已有角色包，不支持申请不存在的角色包，也不支持在提交时配置额外数据范围。
- 边界二：当前风险控制以角色包预设风险等级和审批链路为主，不引入复杂策略引擎，但必须守住申请范围与自动授权边界。
- 风险一：如果授权结果和申请状态不同步，员工会在状态上看到“已通过”但实际没有权限，体验层必须暴露异常状态和补救文案。
- 风险二：如果角色包已关闭、审批配置失效或目标对象变化，系统必须在入口、提交前或审批时及时阻断，不能让用户走到无效终点。
- 风险三：如果到期回收失败，权限风险会延伸到治理层，因此需要有清晰告警、结果状态和后续处理责任。

## 4. 体验承接要求

- 角色：员工、审批人、权限管理员三类角色都要有清晰的状态入口，其中管理员主要承接异常治理和补救，不进入主申请链路。
- 流程：体验需要完整覆盖申请入口、填写提交、待审批、审批结果、生效结果、关闭撤回和到期回收这些状态节点。
- 状态：至少要讲清待审批、已通过、已拒绝、已撤回、已关闭、授权失败、已到期回收这些状态的含义、可操作项和反馈文案。
- 异常：必须正式展开角色包关闭、审批失效、授权失败、状态不同步、通知失败和到期回收失败这些异常与阻断。
- 文案：核心反馈文案要区分“申请提交成功”“审批通过但授权失败”“申请被拒绝”“申请已关闭”“权限已到期回收”等结果，不可混写成模糊提示。

## 5. 升级信号

- 如果业务方要求员工在申请时配置更细粒度的数据范围，说明规则复杂度、风险和治理责任已升级，需要回到更完整的业务判断。
- 如果审批链路要支持多级会签、跨组织流转或条件分支，就需要重新评估当前轻量业务承接是否足够。
- 如果异常补救要开放给普通员工而不只是管理员，体验路径和风险边界都需要重新设计。

## 6. 待确认问题

- 默认有效期是否按角色包自动带出，还是允许审批人调整，还需要进一步确认。
- 员工是否能在申请详情页查看完整审批意见，需要结合隐私与治理要求确认。
- 当通知失败但授权成功时，是否要暴露“结果已生效但通知失败”的单独状态，还需要产品决定。
""".strip()


def _experience_md() -> str:
    return """
# Experience Blueprint

## 0. 本次关键设计判断

**判断：**

这次体验方案的关键待确认不是“要不要做申请入口”，而是如何把申请、审批、授权、生效、异常和回收串成一个用户可理解的状态闭环。

**主要影响：**

1. 员工需要在一个连续流程里理解申请条件、审批进度、授权结果和到期结果。
2. 审批人需要快速判断风险，并在异常状态下知道当前是否还能继续操作。
3. 权限管理员只在异常和治理场景介入，因此页面和文案要避免让普通用户承担治理责任。

**建议方案：**

- 在员工侧提供稳定入口、清晰状态和结果反馈，把规则、边界、风险和异常转成用户可理解的文案。
- 在审批侧强调申请理由、风险提示、状态校验和处理结果，避免重复审批和错误审批。
- 在异常流程里显式展示阻断、失败、冲突和补救动作，不把异常吞掉。

**不建议方案：**

- 不建议只提供提交表单而缺少申请详情页、结果页和状态承接。
- 不建议把授权失败、状态不同步等异常只记在后台而不反馈给用户。

**关键待确认：**

1. 员工是否能查看审批意见全文，会影响结果页和详情页的文案层级。
2. 授权成功但通知失败时是否需要单独状态，会影响状态与反馈文案结构。

## 1. 旅程图

- 员工：进入权限中心 -> 识别可申请角色包 -> 填写申请理由与时长 -> 提交申请 -> 查看审批进度 -> 接收审批结果 -> 确认权限是否生效 -> 到期后查看回收结果
- 审批人：接收待审批提醒 -> 查看申请详情与风险提示 -> 判断是否同意 -> 提交审批意见 -> 查看系统处理结果
- 权限管理员：接收异常告警 -> 查看失败原因与影响范围 -> 执行补救处理 -> 回写处理结果

### 旅程缺口

- 若默认有效期规则尚未确认，员工在填写阶段看到的时长提示需要保留待确认口径。
- 若审批意见展示范围未定，结果页需要先按“可查看摘要”保守设计。

## 2. 交互流程总览

- 节点 2.1 申请入口：员工从权限中心进入可申请角色包列表，先理解规则、边界和风险，再决定是否发起申请。
- 节点 2.2 申请填写：员工填写理由、时长并确认状态说明，系统在提交前做范围、状态和异常校验。
- 节点 2.3 待审批：申请提交后进入待审批状态，员工看到进度，审批人看到待处理列表和重点风险信息。
- 节点 2.4 审批结果：审批人同意或拒绝后，系统反馈结果状态、处理文案和下一步动作。
- 节点 2.5 生效与回收：授权成功后提示已生效，到期后提示已回收；若失败则进入异常阻断流程。

## 3. 主交互流程

节点 X1：申请入口

**用户动作：**

员工打开权限中心，进入“可申请角色包”列表，浏览可申请项、范围说明、有效期和申请前置条件。

**系统反馈：**

系统展示角色包名称、适用范围、风险提示和是否可申请；若当前角色包已关闭或与员工身份冲突，入口直接显示阻断状态。

**需要前置解释的信息：**

员工需要知道只能申请角色包、不能自由选择底层权限，以及审批通过后系统会自动授权。

**建议文案：**

“请选择业务需要的角色包。审批通过后系统会自动为你开通权限，到期后自动回收。”

**下一步：**

点击进入申请填写页。

节点 X2：申请填写

**用户动作：**

员工选择角色包，填写申请理由、使用时长，并确认自己理解申请范围、规则、风险和状态变化。

**系统反馈：**

系统实时校验必填项、申请资格、角色包状态和可申请范围；若信息完整，则允许提交；若资格不满足，则在字段和页面顶部同步反馈阻断原因。

**需要前置解释的信息：**

员工需要知道提交后会进入待审批状态，审批通过不等于已经生效，仍要等待系统完成授权。

**建议文案：**

“提交后申请将进入审批流程。审批通过后系统会继续执行授权，请在详情页查看最终生效状态。”

**下一步：**

提交申请并进入申请详情页。

节点 X3：审批处理

**用户动作：**

审批人打开待处理申请，查看角色包、理由、时长、风险提示和当前状态，决定同意或拒绝。

**系统反馈：**

系统在审批动作前再次校验当前申请状态是否仍为待审批；若状态已变化，则阻止继续处理并提示最新状态；若审批成功，则记录意见并开始后续授权或结束流程。

**需要前置解释的信息：**

审批人需要知道审批通过后系统会自动授权，若授权失败会进入异常状态，而不是由审批人继续手工开通。

**建议文案：**

“同意后系统将自动执行授权；如执行失败，系统会记录失败原因并通知相关人员处理。”

**下一步：**

提交审批结果并查看系统反馈。

节点 X4：结果确认

**用户动作：**

员工返回申请详情页查看最新状态，确认是已通过、已拒绝、已关闭、已撤回、已生效还是异常失败。

**系统反馈：**

系统用统一状态口径展示结果、风险、文案和下一步动作；若已生效，则提示到期时间；若被拒绝，则展示拒绝原因；若授权失败，则提供联系管理员或查看处理进度的路径。

**需要前置解释的信息：**

员工需要理解“审批通过”和“权限已生效”是两个连续状态，而不是同一个结果。

**建议文案：**

“审批已通过，系统正在开通权限。若长时间未生效，请查看处理状态或联系管理员。”

**下一步：**

根据状态继续使用权限、等待处理或执行补救动作。

## 4. 次交互流程

- 员工撤回申请：在待审批状态下允许员工主动撤回，撤回后页面更新为已撤回状态，并说明后续不能继续审批。
- 员工查看历史申请：员工可在历史记录中查看角色包、申请理由、状态、结果和到期时间，用于追踪规则和结果。
- 审批人查看已处理记录：审批人可回看自己处理过的申请，核对意见、结果状态和异常处理情况。

## 5. 异常与阻断流程

异常 X1：角色包已关闭

**发生时机：** 员工进入入口或准备提交时  
**触发条件：** 目标角色包已下线、已停用或当前组织不可申请  
**判断依据：** facts 与 business 已确认角色包关闭属于正式阻断规则  
**反馈形式：** 页面顶部阻断提示 + 入口禁用状态  
**系统反馈：** “当前角色包已停止开放申请，请选择其他角色包或联系管理员。”  
**用户下一步：** 返回列表重新选择，或联系管理员确认替代方案

异常 X2：申请状态已变化

**发生时机：** 审批人打开待处理详情并准备操作时  
**触发条件：** 申请已被撤回、关闭或其他人已处理  
**判断依据：** 当前状态与页面打开时缓存状态不一致  
**反馈形式：** 页面级状态提示 + 操作按钮禁用  
**系统反馈：** “当前申请状态已更新，暂时不能继续审批，请刷新后查看最新结果。”  
**用户下一步：** 刷新页面并改为查看最新状态

异常 X3：授权失败

**发生时机：** 审批通过后系统执行自动授权时  
**触发条件：** 自动授权任务失败、目标系统不可用或配置缺失  
**判断依据：** 授权执行结果返回失败态  
**反馈形式：** 结果页异常提示 + 状态标签 + 管理员告警  
**系统反馈：** “审批已通过，但权限开通失败。系统已记录问题并通知管理员处理。”  
**用户下一步：** 员工查看处理进度，管理员进入补救流程

异常 X4：到期回收失败

**发生时机：** 权限到期后系统执行回收  
**触发条件：** 回收执行失败或目标系统未响应  
**判断依据：** 回收任务失败且状态未完成同步  
**反馈形式：** 治理告警 + 详情页风险提示  
**系统反馈：** “权限到期但回收失败，管理员正在处理，请暂勿继续依赖该权限结果。”  
**用户下一步：** 管理员执行补救，员工等待处理结果

## 6. 页面 / 弹窗 / 抽屉设计

**页面：可申请角色包列表**

**页面目标：** 帮助员工识别可申请项、申请规则、边界和风险  
**进入条件：** 员工进入权限中心并具备查看申请入口的资格  
**页面结构：** 列表区、角色包说明区、风险提示区、状态反馈区  
**状态反馈区：** 显示可申请、不可申请、角色包关闭、资料不足等状态  
**异常状态下的结构变化：** 若角色包关闭或不可申请，卡片直接展示原因并禁用主按钮  
**具体文案：** “仅支持申请预定义角色包，审批通过后系统自动开通权限。”  
**按钮：** 主按钮“去申请”，次按钮“查看说明”  
**成功反馈：** 进入填写页时保留所选角色包信息  
**失败反馈：** 若入口受限，展示“当前不可申请”的原因文案

**页面：申请填写页**

**页面目标：** 收集理由、时长并在提交前完成状态和规则校验  
**进入条件：** 员工从列表页点击可申请角色包进入  
**页面结构：** 角色包摘要区、申请表单区、规则说明区、异常提示区  
**状态反馈区：** 字段错误、资格不足、时长超限、资料不全等状态集中呈现  
**异常状态下的结构变化：** 资格不足或角色包关闭时，提交按钮禁用并显示阻断原因  
**具体文案：** “请说明业务理由与使用时长。提交后将进入审批流程。”  
**按钮：** 主按钮“提交申请”，次按钮“取消”  
**成功反馈：** “申请已提交，当前状态为待审批。”  
**失败反馈：** “提交失败，请先补全信息或稍后重试。”

**页面：申请详情页**

**页面目标：** 让员工和审批人查看申请状态、处理结果、异常原因和下一步动作  
**进入条件：** 提交成功后自动跳转，或从历史记录进入  
**页面结构：** 状态摘要区、申请信息区、审批信息区、反馈文案区、后续动作区  
**状态反馈区：** 清晰区分待审批、已通过、已拒绝、已关闭、授权失败、已生效、已回收  
**异常状态下的结构变化：** 授权失败和回收失败时增加风险提示区与补救说明  
**具体文案：** “审批已通过，系统正在开通权限。” / “申请已被拒绝，请查看原因。”  
**按钮：** 依据状态提供“撤回申请”“刷新状态”“联系管理员”等动作  
**成功反馈：** 展示最终生效时间和到期时间  
**失败反馈：** 展示失败原因、风险说明和下一步建议

## 7. 状态与反馈文案

| 状态 | 含义 | 适用对象 | 用户可操作 | 统一反馈口径 |
|---|---|---|---|---|
| 待审批 | 申请已提交，等待审批人处理 | 员工、审批人 | 员工可撤回，审批人可处理 | 申请已提交，正在等待审批 |
| 已通过待生效 | 审批通过，系统正在授权 | 员工、审批人 | 仅可查看状态 | 审批已通过，系统正在开通权限 |
| 已生效 | 权限已成功开通 | 员工 | 可使用权限 | 权限已开通，将在到期后自动回收 |
| 已拒绝 | 审批人拒绝申请 | 员工、审批人 | 员工可查看原因并重新发起 | 申请未通过，请查看拒绝原因 |
| 已撤回 | 员工主动取消申请 | 员工、审批人 | 仅可查看历史 | 申请已撤回，不再进入审批 |
| 已关闭 | 系统或业务方关闭申请 | 员工、审批人 | 仅可查看说明 | 申请已关闭，请根据说明处理 |
| 授权失败 | 审批通过但系统授权失败 | 员工、管理员 | 员工查看处理进度，管理员补救 | 审批已通过，但权限开通失败 |
| 已到期回收 | 权限到期并已完成回收 | 员工、管理员 | 员工可查看结果 | 权限已到期并完成回收 |

## 8. 待确认问题
1. **审批意见展示范围**

   影响：会影响员工结果页和详情页的文案层级，以及是否需要额外的隐私提示。  
   建议确认方：产品 / 业务

2. **通知失败是否独立成态**

   影响：会影响状态与反馈文案的数量，以及员工是否需要看到“结果已生效但通知失败”的中间状态。  
   建议确认方：产品 / 技术

## 附录：设计指南消费说明

| 使用依据 | 转换结果 | 落点 |
|---|---|---|
| 业务摘要强调状态闭环 | 转成结果页、详情页和审批页的状态闭环表达 | 申请详情页、审批详情页 |
| 业务规则强调异常正式承接 | 转成异常与阻断流程，不再只写正常路径 | 异常与阻断流程 |
| 业务边界强调结果同步 | 转成“审批通过不等于已生效”的反馈文案 | 状态与反馈文案 |
""".strip()


def _route_decision(project_id: str) -> dict[str, object]:
    business_summary = "knowledge/wiki/summaries/业务/README.md"
    complexity_summary = ".codex/skills/uxb/references/complexity/00_core_complexity_judgment.md"
    return {
        "schema_version": "uxb_route_decision@4.0",
        "project_id": project_id,
        "created_by": "uxb_ai",
        "confirmed_by_user": True,
        "can_execute_mainline": True,
        "judgment": {
            "demand_type": "stability_smoke",
            "business_depth": "business_blueprint_lite",
            "experience_output": "experience_blueprint",
            "reason": "这是一个标准模式跨系统 smoke 项目，用于验证真实主链路在不同系统上都能稳定承接。",
        },
        "complexity_judgment": {
            "business_change": ["新增员工自助申请与审批授权闭环"],
            "experience_pressure": ["需要显式承接状态、异常、阻断和反馈文案"],
            "uncertainties": ["默认有效期和审批意见展示范围仍需确认"],
        },
        "knowledge_selection": {
            "summary_refs": {
                "business": [business_summary],
                "guideline": [],
                "complexity": [complexity_summary],
            },
            "raw_escalation_plan": [],
            "stage_refs": {
                "facts": {"raw_refs": []},
                "business": {"raw_refs": []},
                "experience": {"raw_refs": []},
            },
            "selection_reasons": [
                {
                    "ref": business_summary,
                    "type": "summary",
                    "used_for_stage": ["facts", "business", "experience"],
                    "reason": "用业务 summary 约束标准模式 smoke 项目的业务范围、状态闭环和异常边界。",
                },
                {
                    "ref": complexity_summary,
                    "type": "summary",
                    "used_for_stage": ["facts"],
                    "reason": "用复杂度参考保证 routed main 仍按 UXB judgment 的稳定入口执行。",
                },
            ],
        },
        "execution": {
            "required_outputs": [
                "facts.md",
                "business_blueprint_lite.md",
                "experience_blueprint.md",
            ],
            "notes": [
                "这个项目只用于跨系统稳定性 smoke，不用于沉淀正式业务方案。",
            ],
        },
    }


class RoutedMainStandardSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = get_repo_root()
        self.project_id = f"_ci_routed_main_smoke_{uuid.uuid4().hex[:8]}"
        self.project_dir = get_project_dir(self.project_id)
        self.addCleanup(shutil.rmtree, self.project_dir, ignore_errors=True)
        self._build_project()

    def _build_project(self) -> None:
        source_dir = self.project_dir / "source"
        workspace_dir = self.project_dir / "workspace"
        runtime_dir = self.project_dir / "runtime"
        for path in (source_dir, workspace_dir, runtime_dir):
            path.mkdir(parents=True, exist_ok=True)

        _write_json(
            self.project_dir / "meta.json",
            {
                "project_id": self.project_id,
                "task_name": "跨端标准主链路冒烟",
                "domain": "权限管理",
                "status": "draft",
                "project_role": "real_project",
                "read_only": False,
                "excluded_from_default_scan": True,
            },
        )
        _write_text(
            source_dir / "requirement.md",
            """
# Requirement

- 目标：验证员工自助申请权限的标准链路能否稳定承接申请、审批、生效、异常和回收。
- 重点：确认跨系统环境下 routed main 可以稳定读取任务卡、装配上下文、通过 gate、写出 validate 与 coverage 结果。
- 约束：本项目只做稳定性 smoke，不追求完整业务扩展。
""",
        )
        _write_text(
            source_dir / "background.md",
            """
# Background

- 组织内已有角色包、审批链路和自动授权能力。
- 现阶段只支持申请预定义角色包，不支持自定义权限组合。
- 后续仍可能补充默认有效期与审批意见展示范围规则。
""",
        )
        _write_text(source_dir / "task_card.md", _task_card(self.project_id))
        _write_text(workspace_dir / "facts.md", _facts_md(self.project_id))
        _write_text(workspace_dir / "business_blueprint_lite.md", _business_lite_md())
        _write_text(workspace_dir / "experience_blueprint.md", _experience_md())
        _write_json(runtime_dir / "uxb_route_decision.json", _route_decision(self.project_id))
        write_provenance(
            self.project_id,
            build_generated_provenance(
                self.project_id,
                "tests.test_routed_main_standard_smoke",
                "seed-routed-main-smoke",
            ),
        )

    def test_run_routed_main_standard_smoke(self) -> None:
        exit_code = run_routed_main(self.project_id, route="auto", skip_preview=True, strict=False)
        self.assertEqual(exit_code, 0)

        runtime_dir = self.project_dir / "runtime"
        workspace_dir = self.project_dir / "workspace"
        report = json.loads((runtime_dir / "routed_main_report.json").read_text(encoding="utf-8"))
        status = json.loads((workspace_dir / "check_status.json").read_text(encoding="utf-8"))
        provenance = json.loads((runtime_dir / "provenance.json").read_text(encoding="utf-8"))

        self.assertEqual(report.get("status"), "passed")
        self.assertEqual(report.get("execution_mode"), "standard")
        self.assertEqual(status.get("status"), "passed")
        command_chain = provenance.get("command_chain", [])
        for command_name in [
            "route-decision",
            "assemble",
            "generate-facts",
            "gate-facts",
            "generate-business-lite",
            "gate-business-lite",
            "generate-experience",
            "gate-experience-lite",
            "validate-lite",
            "coverage-lite",
            "run-routed-main",
        ]:
            self.assertIn(command_name, command_chain)


if __name__ == "__main__":
    unittest.main()
