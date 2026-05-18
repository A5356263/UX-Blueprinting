from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


CASES = [
    {
        "id": "input-validation-fast-checked-filter-view",
        "expected": "fast",
        "title": "功能权限已勾选筛选查看",
        "source": "快捷查看功能权限",
        "goal": "在功能权限设置页增加只看已勾选权限的快捷筛选。",
        "scenario": "管理员配置功能权限时，权限树层级较深，希望快速查看当前已勾选项。",
        "requirement": "本需求是局部体验优化和布局交互优化，只增加已勾选筛选入口、空状态说明和清空筛选反馈。不新增权限规则，不改变授权范围，不改变审批、数据范围、状态机或业务对象关系。",
        "facts": ["筛选只影响当前页面展示。", "已勾选状态仍以原权限树数据为准。", "空状态需要说明当前筛选条件下没有已勾选权限。"],
        "risks": ["不能让用户误以为权限被取消。"],
    },
    {
        "id": "input-validation-fast-checked-filter-copy",
        "expected": "fast",
        "title": "功能权限已勾选筛选文案",
        "source": "快捷查看功能权限",
        "goal": "优化已勾选筛选的提示语和无结果说明。",
        "scenario": "管理员打开筛选后没有匹配结果，需要知道是筛选无结果而不是权限加载失败。",
        "requirement": "本需求主要是文案与信息表达优化，只补充提示语、tooltip 和空状态解释。沿用现有权限树、保存按钮、半选状态和接口异常反馈，不新增功能能力，不改变权限范围、审批流程或状态机。",
        "facts": ["提示语需要区分筛选无结果和加载失败。", "筛选关闭后回到原权限树展示。"],
        "risks": ["文案不能暗示用户拥有更多权限。"],
    },
    {
        "id": "input-validation-fast-self-permission-help",
        "expected": "fast",
        "title": "自助权限申请说明微调",
        "source": "自助权限申请",
        "goal": "在员工自助申请入口补充可申请范围说明。",
        "scenario": "员工进入自助申请页前，需要理解哪些权限可申请、哪些需要联系管理员。",
        "requirement": "本需求只做入口说明、提示语和空状态微调，不新增自助申请能力，不改变审批范围、审批模式、授权规则、数据范围或状态机。当前只要求帮助员工理解现有入口。",
        "facts": ["说明展示在现有入口附近。", "不改变申请提交、审批或授权结果。"],
        "risks": ["说明不能替代审批规则。"],
    },
    {
        "id": "input-validation-standard-subadmin-copy-basic",
        "expected": "standard",
        "title": "子管理员权限复制基础能力",
        "source": "子管理员权限复制",
        "goal": "支持把一个子管理员的可授权组织和功能权限复制给多个目标用户。",
        "scenario": "超级管理员为同岗位人员批量配置子管理员权限。",
        "requirement": "在既有子管理员授权能力上扩展复制能力，涉及批量选择、复制预览、目标用户校验、部分成功和失败反馈。需要明确权限范围、数据范围、授权规则和异常处理，但不重构权限模型，不新增审批模式。",
        "facts": ["复制来源是已有子管理员。", "目标用户可以多选。", "复制结果需要区分成功、失败和跳过。"],
        "risks": ["不能复制超过当前操作者可授权范围的权限。"],
    },
    {
        "id": "input-validation-standard-subadmin-copy-validation",
        "expected": "standard",
        "title": "子管理员权限复制校验反馈",
        "source": "子管理员权限复制",
        "goal": "补齐子管理员权限复制过程中的校验、阻断和结果反馈。",
        "scenario": "复制前后需要识别目标用户不可用、权限范围不一致和部分权限复制失败。",
        "requirement": "本需求是业务流程调整和既有能力扩展。需要校验来源权限、目标用户状态、授权范围、数据范围和部分失败处理；需要结果回写和审计记录。不新增自助申请，不改变审批模式或权限模型。",
        "facts": ["复制前要预校验。", "复制后要展示明细结果。", "失败项不能静默忽略。"],
        "risks": ["部分成功需要避免管理员误判全部完成。"],
    },
    {
        "id": "input-validation-standard-checked-filter-editing",
        "expected": "standard",
        "title": "功能权限筛选编辑态保护",
        "source": "快捷查看功能权限",
        "goal": "在已勾选筛选开启时保护未保存编辑状态。",
        "scenario": "管理员勾选或取消权限后切换筛选，需要明确未保存变更是否仍保留。",
        "requirement": "在既有功能权限设置能力上增加筛选与编辑态的规则，涉及未保存变更、半选状态、清空筛选和保存前校验。需要业务规则和状态反馈，但不新增权限对象、不改变审批或数据范围。",
        "facts": ["筛选切换不应丢失未保存勾选。", "半选状态需要保持一致。"],
        "risks": ["筛选隐藏未保存变更时需要给出可见反馈。"],
    },
    {
        "id": "input-validation-standard-permission-query-user-role",
        "expected": "standard",
        "title": "权限查询用户角色维度",
        "source": "权限查询",
        "goal": "支持按用户和角色维度查询权限归属。",
        "scenario": "管理员需要定位某个用户拥有权限的来源角色和可见范围。",
        "requirement": "在既有权限查询能力上扩展用户、角色和权限来源维度，涉及查询条件、结果归属、导出限制、数据范围和敏感信息保护。需要业务边界判断，但暂不新增审批流程或权限模型重构。",
        "facts": ["查询结果需要标明权限来源。", "导出受当前管理员数据范围限制。"],
        "risks": ["不能暴露当前操作者无权查看的用户或权限。"],
    },
    {
        "id": "input-validation-standard-self-permission-low",
        "expected": "standard",
        "title": "低完整度自助权限申请澄清",
        "source": "自助权限申请",
        "goal": "把低完整度自助权限申请需求整理成可评估的业务边界。",
        "scenario": "需求只说明员工希望自助申请权限，但审批人、可申请范围和生效方式不清楚。",
        "requirement": "当前需求信息不完整，但涉及业务流程调整、申请提交、审批范围、状态反馈和权限授予边界。需要先输出轻量业务蓝图澄清规则和待确认问题，不直接进入完整新增能力设计。",
        "facts": ["员工希望发起申请。", "可申请权限范围、审批人和生效时机缺失。"],
        "risks": ["如果审批模式和授权范围确认后涉及新增核心能力，需要升级 full。"],
    },
    {
        "id": "input-validation-full-subadmin-copy-approval",
        "expected": "full",
        "title": "子管理员权限复制双管理员审批",
        "source": "子管理员权限复制",
        "goal": "评估子管理员权限复制是否需要双管理员审批和审计闭环。",
        "scenario": "复制动作可能批量放大授权范围，需要在高风险组织中引入审批治理。",
        "requirement": "本需求涉及权限与治理风险、审批治理、审计、敏感数据范围和状态机。需要新增审批模式、复制申请状态、审批通过后生效、拒绝和撤回流程，并处理部分失败、越权拦截和审计追踪。",
        "facts": ["复制可能批量影响多个目标用户。", "高风险权限需要审批后才生效。"],
        "risks": ["直接复制可能造成越权授权和审计缺口。"],
    },
    {
        "id": "input-validation-full-permission-query-multidimension",
        "expected": "full",
        "title": "权限维度多维查询",
        "source": "权限查询",
        "goal": "设计用户、角色、权限、OA 表单和报表的多维权限查询能力。",
        "scenario": "管理员需要从不同业务对象反查权限来源、可见范围、审批链路和导出依据。",
        "requirement": "本需求是功能新增和权限治理能力建设，涉及权限模型、数据范围、敏感查询、导出审计、对象关系重构、状态异常和跨维度结果解释。需要完整业务蓝图和体验蓝图。",
        "facts": ["查询维度包括用户、角色、权限、OA 表单、报表。", "结果需要解释来源和可见范围。"],
        "risks": ["多维查询可能暴露敏感权限结构。"],
    },
    {
        "id": "input-validation-full-self-permission-high",
        "expected": "full",
        "title": "员工自助权限申请完整能力",
        "source": "自助权限申请",
        "goal": "设计员工自助申请权限的完整业务和体验闭环。",
        "scenario": "员工选择可申请权限并提交，审批人处理后权限自动生效或拒绝。",
        "requirement": "本需求是新增核心业务能力，涉及员工申请、管理员配置可申请范围、审批模式、审批状态机、自动授权、生效回写、撤回、拒绝、通知、审计和异常补救。需要完整链路。",
        "facts": ["员工是申请方。", "审批人处理申请。", "管理员配置可申请范围。"],
        "risks": ["可申请范围和审批模式不清会导致越权申请。"],
    },
    {
        "id": "input-validation-full-self-permission-mode-conflict",
        "expected": "full",
        "title": "自助权限申请模式冲突",
        "source": "自助权限申请",
        "goal": "处理自助权限申请与既有双管理员审批、权限变更审批的模式冲突。",
        "scenario": "企业可能同时启用多种权限审批方式，员工申请可能与管理员授权流程交叉。",
        "requirement": "本需求涉及功能新增、审批模式冲突、状态机重构、在途申请关闭策略、授权结果回写和审计治理。需要明确不同模式优先级、关闭后的在途审批处理、失败补救和通知规则。",
        "facts": ["可能存在双管理员审批和员工自助申请并存。", "关闭模式时可能仍有在途申请。"],
        "risks": ["模式冲突会造成重复审批或绕过审批。"],
    },
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def route_for(case: dict[str, object]) -> str:
    route_path = ROOT / str(case["id"]) / "runtime" / "route_decision.json"
    if route_path.exists():
        try:
            route = json.loads(route_path.read_text(encoding="utf-8")).get("route")
            if route in {"fast", "standard", "full"}:
                return str(route)
        except json.JSONDecodeError:
            pass
    return str(case["expected"])


def route_outputs(cid: str, route: str | None) -> list[str]:
    outputs = [
        f"projects/{cid}/workspace/facts.md",
        f"projects/{cid}/workspace/experience_blueprint.md",
        f"projects/{cid}/workspace/check_report.md",
        f"projects/{cid}/workspace/check_status.json",
    ]
    if route == "fast":
        outputs.insert(1, f"projects/{cid}/workspace/business_note.md")
    elif route == "standard":
        outputs.insert(1, f"projects/{cid}/workspace/business_blueprint_lite.md")
    elif route == "full":
        outputs.insert(1, f"projects/{cid}/workspace/business_blueprint.md")
        outputs.insert(3, f"projects/{cid}/workspace/gap_list.md")
    else:
        outputs[1:1] = [
            f"projects/{cid}/workspace/business_note.md",
            f"projects/{cid}/workspace/business_blueprint_lite.md",
            f"projects/{cid}/workspace/business_blueprint.md",
        ]
    return outputs


def task_card(case: dict[str, object], route: str | None = None) -> str:
    cid = str(case["id"])
    output_lines = "\n".join(f"- {item}" for item in route_outputs(cid, route))
    return f"""
# Task Card

## Protocol

- Protocol Name: UXB Test Task
- Protocol Version: 1.0
- Task ID: {cid}
- Task Name: {case["title"]}
- Domain: permission

## Task Goal

- {case["goal"]}

## Task Scenario

- {case["scenario"]}

## Required Inputs

- projects/{cid}/source/requirement.md
- projects/{cid}/source/background.md

## Required Outputs

{output_lines}

## Constraints

- 只依据 source 中的真实需求片段和背景，不引入无来源的新业务范围。
- 按 route_decision 的实际路线输出对应正式产物，不能用聊天回复替代正式文档。

## Knowledge

## Wiki

## Design Guidelines

## Templates

- templates/facts.template.md
- templates/business_note.template.md
- templates/business_blueprint_lite.template.md
- templates/business_blueprint.template.md
- templates/experience_blueprint.template.md

## Checks

- specs/16_business_note_contract.md
- specs/17_business_blueprint_lite_contract.md
- specs/09_business_blueprint_contract.md
- specs/10_experience_blueprint_contract.md
- specs/18_routed_main_contract.md

## Result Locations

- facts: projects/{cid}/workspace/facts.md
- business_note: projects/{cid}/workspace/business_note.md
- business_lite: projects/{cid}/workspace/business_blueprint_lite.md
- business: projects/{cid}/workspace/business_blueprint.md
- experience: projects/{cid}/workspace/experience_blueprint.md

## Completion Criteria

- routed-main 能按 auto 路线完成到最终检查产物。
- 产物必须承接当前需求正文中的关键边界，不外扩判断维度。

## Facts Output Requirements

### Required Sections

- 任务概述

### Boundary

- 不输出体验方案。

## Business Output Requirements

### Required Sections

- 路线对应业务产物

### Boundary

- 不越过 route_decision 的业务深度。

## Experience Output Requirements

### Required Sections

- 交互流程总览

### Boundary

- 不输出前端实现方案。
"""


def source_requirement(case: dict[str, object]) -> str:
    return f"""
# {case["title"]}

## 输入来源

- input 需求集合：{case["source"]}

## 需求正文

{case["requirement"]}

## 关键事实

{chr(10).join(f"- {item}" for item in case["facts"])}

## 风险与边界

{chr(10).join(f"- {item}" for item in case["risks"])}

## 期望判断

- 人工期望路线：{case["expected"]}
- 本章节只用于验收说明，不作为模型路线判断依据。
"""


def background(case: dict[str, object]) -> str:
    return f"""
# Background

本样本来自 input 目录中的 {case["source"]} 需求族，用于阶段三 run-routed-main 严格验收。

验收关注点：

- source/task_card.md 是否能完成 assemble。
- route_decision 是否能写出实际路线。
- routed-main 是否能根据实际路线消费对应业务产物。
- workspace/check_status.json 是否能写出最终机器状态。
"""


def facts(case: dict[str, object]) -> str:
    return f"""
# Facts

## 任务概述

- 输入来源：source/requirement.md 与 source/background.md，需求族为 {case["source"]}。
- 任务目标：{case["goal"]}
- 使用场景：{case["scenario"]}

## 功能范围

{chr(10).join(f"- {item}" for item in case["facts"])}
- 本样本只覆盖当前需求片段，不外扩到其他权限管理能力。

## 关键业务规则

- 权限：需要保持当前操作者可授权或可查询范围。
- 数据范围：结果、筛选、复制或申请都不能越过当前可见范围。
- 审批：如需求未明确新增审批，则只保留现有审批边界；如需求明确审批治理，则进入完整链路判断。
- 状态机：需要区分成功、失败、部分成功、无结果、在途和已关闭等状态。
- 业务对象关系：用户、角色、权限、组织、表单、报表和申请记录之间的关系不能混淆。

## 状态流转

- 初始：用户进入相关权限页面或申请入口。
- 操作中：用户筛选、复制、查询或提交申请。
- 结果：系统给出成功、无结果、失败、部分成功或待审批反馈。

## 异常与边界

{chr(10).join(f"- {item}" for item in case["risks"])}
- 异常需要给出可见原因和下一步，不静默吞掉失败。

## 依赖与前置条件

- 依赖现有账号、组织、角色、权限和审批配置。
- 依赖当前操作者的数据范围与授权范围。

## 开放问题与缺口

- 是否已有统一审计字段和导出限制需要进一步确认。
"""


def business_note(case: dict[str, object], route: str) -> str:
    return f"""
# 业务依据摘要

## 0. 路线说明

- 执行路线：{route}。
- 采用业务依据摘要的原因：当前需求主要是局部体验、文案或展示优化，不改变核心权限、审批、数据范围、状态机或业务对象关系。

## 1. 业务依据

- 目标：{case["goal"]}
- 场景：{case["scenario"]}
- 边界：只承接当前需求片段，不新增权限治理能力。

## 2. 核心业务规则影响

- 权限：不改变已有权限范围，只展示当前用户可见内容。
- 数据范围：不扩大查询、筛选或申请可见数据。
- 审批：不新增审批节点，不改变审批模式。
- 状态机：只补充可见反馈，不新增业务状态。
- 业务对象关系：不改变用户、角色、权限、组织或申请对象关系。

## 3. 体验可承接内容

- 角色：管理员或员工按当前入口完成操作。
- 流程：进入页面、触发局部筛选或查看说明、理解结果并继续原任务。
- 状态：正常、有结果、无结果、失败和恢复。
- 异常：加载失败或无权限沿用现有异常反馈。
- 文案：说明当前状态、原因和下一步。

## 4. 升级信号

- 如果后续发现需要新增审批、授权范围、数据范围或状态机，应升级到 standard 或 full。

## 5. 待确认问题

- 是否已有统一文案规范和空状态规范。
"""


def business_lite(case: dict[str, object], route: str) -> str:
    return f"""
# 轻量业务蓝图

## 0. 路线说明

- 执行路线：{route}。
- 采用轻量业务蓝图的原因：需求涉及既有能力扩展、业务规则或状态反馈，需要先明确业务边界，再进入体验承接。

## 1. 一句话结论

{case["goal"]}成立，但应限制在当前需求范围内，优先澄清权限、数据范围、审批、状态机和业务对象关系边界。

## 2. 关键业务规则

- 权限：操作者只能处理自己可授权、可查询或可配置的权限范围。
- 数据范围：查询、复制、筛选或申请结果必须受当前数据范围约束。
- 审批：未明确新增审批时沿用现有模式；涉及高风险时需要升级完整评估。
- 状态机：至少区分初始、处理中、成功、失败、部分成功、无结果和待确认。
- 业务对象关系：用户、角色、权限、组织、申请记录和审批记录需要明确归属。

## 3. 边界与风险

{chr(10).join(f"- {item}" for item in case["risks"])}
- 边界：不重构权限模型，不新增无来源业务对象。
- 风险：用户可能误解结果来源、授权范围或失败原因。

## 4. 体验承接要求

- 角色：管理员、员工、审批人按需求实际出现范围承接。
- 流程：展示入口、选择对象、校验规则、提交或查看结果、处理异常。
- 状态：需要显性展示成功、失败、无结果、部分成功和未保存状态。
- 异常：越权、数据为空、对象不可用、审批缺失和保存失败需要可恢复。
- 文案：解释原因、影响范围和下一步操作。

## 5. 升级信号

- 如出现新增核心申请能力、审批模式变化、权限模型重构或状态机重构，应升级 full。

## 6. 待确认问题

- 审计记录、导出限制和通知规则是否已由平台统一提供。
"""


def business_full(case: dict[str, object], route: str) -> str:
    return f"""
# 业务蓝图

## 0. 本次关键设计判断

- 执行路线：{route}。
- 当前需求涉及权限治理、审批、数据范围、状态机或新增核心能力，需要完整业务判断。

## 1. 一句话结论

{case["goal"]}成立，但必须以权限边界、审批治理、状态闭环和审计可追踪为前提。

## 2. 需求是否成立

- 成立依据：{case["scenario"]}
- 业务痛点：现有能力不足以让用户安全、清晰地完成该权限任务。
- 成立边界：只覆盖 {case["source"]} 需求族中明确出现的对象和流程。

## 3. 值不值得做

- 值得做，因为它能降低权限配置、查询或申请的人工成本。
- 前提是不能扩大无授权访问，不能绕过审批，不能造成审计缺口。

## 4. 应该做成什么能力形态

- 能力形态：权限治理型工作流能力。
- 角色：管理员、员工、审批人和系统记录者。
- 对象：用户、角色、权限、组织、表单、报表、申请单和审批记录。

## 5. 推荐业务方案

- 入口：在现有权限管理或员工自助入口承接。
- 配置：管理员定义可操作范围、审批模式和生效规则。
- 操作：用户选择对象、系统校验权限和数据范围、生成申请或查询结果。
- 审批：高风险操作进入审批，审批通过后才生效。
- 结果：展示成功、失败、部分成功、拒绝、撤回和在途状态。
- 审计：记录操作者、对象、范围、结果和时间。

## 6. 必须守住的规则和边界

- 权限：不能突破当前操作者可授权或可查询范围。
- 数据范围：敏感对象和导出结果必须受数据范围约束。
- 审批：高风险变更必须保留审批治理和可追踪记录。
- 状态机：申请、审批、授权和关闭必须有明确状态。
- 业务对象关系：用户、角色、权限、组织和申请记录之间要可追溯。

## 7. 主要风险与保护策略

{chr(10).join(f"- 风险：{item} 保护：通过校验、阻断、提示和审计记录降低影响。" for item in case["risks"])}
- 风险：在途任务与模式关闭冲突。保护：关闭前提示影响范围，并定义在途处理策略。

## 8. 方案承接要求

- 体验必须覆盖主流程、次流程、异常流程、状态反馈和用户可见文案。
- 体验必须解释权限不足、范围越界、审批中、部分成功和失败原因。
- 体验不得输出前端实现细节。

## 9. 待确认问题

- 审批人规则、通知方式、导出限制和审计字段是否已有统一平台能力。

## 附录：事实、知识与判断追踪

- 输入来源：{case["source"]}。
- 关键事实：{case["facts"][0]}
- 判断：按完整路线处理权限治理和状态闭环。
"""


def experience(case: dict[str, object], route: str) -> str:
    return f"""
# 体验蓝图

## 0. 本次关键设计判断

- 执行路线：{route}。
- 体验重点：承接权限、数据范围、审批、状态机、异常和文案，不进入前端实现。

## 1. 交互流程总览

- 用户进入相关权限页面或自助入口。
- 用户查看说明、选择筛选条件、选择对象、提交查询、复制或申请。
- 系统校验权限、数据范围、审批规则和对象状态。
- 系统展示成功、失败、无结果、部分成功、待审批或已关闭反馈。

## 2. 主交互流程

- 进入入口后先展示当前任务目标和可操作范围。
- 用户选择对象或条件后，系统即时提示是否超出权限边界。
- 用户确认操作后，系统给出结果明细和下一步操作。
- 对于需要审批的操作，提交后进入待审批状态并展示审批进度。

## 3. 次交互流程

- 用户可以清空筛选、返回上一层、查看失败明细或重新选择对象。
- 管理员可以查看复制、查询或申请结果的来源说明。
- 审批人可以查看申请原因、权限范围、数据范围和历史记录。

## 4. 异常与阻断流程

- 权限不足：阻断操作并说明当前账号不可处理该对象。
- 数据范围越界：隐藏不可见对象，并说明仅展示可见范围内结果。
- 审批缺失：提示需要配置审批人或切换处理方式。
- 状态冲突：提示在途、已关闭、已失效或部分成功原因。
- 保存失败：保留用户已选内容，提供重试和返回路径。

## 5. 页面 / 弹窗 / 抽屉设计

- 页面：承载列表、筛选条件、对象选择和结果区域。
- 弹窗：用于确认高风险操作、展示影响范围和二次确认。
- 抽屉：用于展示权限、角色、组织、申请或审批明细。
- 结果区：展示成功、失败、部分成功、无结果和下一步。
- 审计区：在需要时展示操作记录和结果来源。

## 6. 状态与反馈文案

- 状态：正常可操作。文案：当前展示的是你有权处理的范围。
- 状态：无结果。文案：当前条件下没有匹配结果，可以清空条件后重试。
- 状态：部分成功。文案：部分对象未完成，请查看失败原因。
- 状态：待审批。文案：申请已提交，审批通过后生效。
- 状态：权限不足。文案：你暂无权处理该对象，请联系管理员。
- 状态：已关闭。文案：当前模式已关闭，在途申请按平台规则继续处理。

## 7. 待确认问题

- 是否需要统一通知、导出、审计和审批进度组件。
"""


def write_sources() -> None:
    for case in CASES:
        base = ROOT / str(case["id"])
        write(base / "source" / "task_card.md", task_card(case))
        write(base / "source" / "requirement.md", source_requirement(case))
        write(base / "source" / "background.md", background(case))


def write_artifacts() -> None:
    for case in CASES:
        base = ROOT / str(case["id"])
        route = route_for(case)
        workspace = base / "workspace"
        write(base / "source" / "task_card.md", task_card(case, route))
        write(workspace / "facts.md", facts(case))
        write(workspace / "experience_blueprint.md", experience(case, route))
        if route == "fast":
            write(workspace / "business_note.md", business_note(case, route))
        elif route == "standard":
            write(workspace / "business_blueprint_lite.md", business_lite(case, route))
        else:
            write(workspace / "business_blueprint.md", business_full(case, route))
        write(workspace / "gap_list.md", "# Gap List\n\n## Blockers\n\n- 无。\n\n## Warnings\n\n- 无。\n\n## 待补信息\n\n- 无阻断缺口。")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["sources", "artifacts", "all"], default="all")
    args = parser.parse_args()
    if args.phase in {"sources", "all"}:
        write_sources()
    if args.phase in {"artifacts", "all"}:
        write_artifacts()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
