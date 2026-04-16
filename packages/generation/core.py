from __future__ import annotations

import re
from pathlib import Path

from packages.common import get_project_runtime_dir, get_project_source_dir, get_project_workspace_dir
from packages.provenance import upsert_generated_provenance


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _normalize_source_text(text: str) -> str:
    text = text.replace("<br/>", "\n").replace("<br />", "\n")
    text = re.sub(r"`{3}[\s\S]*?`{3}", "", text)
    text = re.sub(r"graph\s+[A-Z]{2}[\s\S]*?(?=\n\d|\n[一二三四五六七八九十]+\.)", "", text)
    return text


def _extract_source_lines(project_id: str) -> list[str]:
    source_dir = get_project_source_dir(project_id)
    texts = [
        _normalize_source_text(_read_text(source_dir / "requirement.md")),
        _normalize_source_text(_read_text(source_dir / "background.md")),
    ]
    lines: list[str] = []
    for text in texts:
        for raw_line in text.splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip(" -\t")
            if len(line) < 8:
                continue
            if line.startswith("#"):
                continue
            lines.append(line)
    return lines


def _pick(lines: list[str], keyword: str, fallback: str) -> str:
    for line in lines:
        if keyword in line:
            return line
    return fallback


def _extract_roles(lines: list[str]) -> list[str]:
    role_map = [
        ("超管", "超管"),
        ("超级管理员", "超级管理员"),
        ("管理员", "管理员"),
        ("员工", "员工"),
        ("审批", "审批人"),
        ("实施", "实施/运营支持"),
        ("系统", "系统"),
    ]
    result: list[str] = []
    joined = "\n".join(lines)
    for keyword, label in role_map:
        if keyword in joined and label not in result:
            result.append(label)
    return result or ["业务发起人", "管理者", "系统"]


def _extract_objects(lines: list[str]) -> list[str]:
    object_map = [
        ("权限", "权限"),
        ("角色", "角色"),
        ("应用", "应用"),
        ("审批", "审批流程"),
        ("记录", "申请记录"),
        ("帮助", "帮助文档"),
        ("模式", "治理模式"),
    ]
    result: list[str] = []
    joined = "\n".join(lines)
    for keyword, label in object_map:
        if keyword in joined and label not in result:
            result.append(label)
    return result or ["核心对象", "关键配置", "结果记录"]


def _extract_structure_semantics(project_id: str) -> list[str]:
    runtime_dir = get_project_runtime_dir(project_id)
    bundle_dir = runtime_dir / "context_bundle"
    if not bundle_dir.exists():
        return []

    snippets: list[str] = []
    for path in sorted(bundle_dir.rglob("*.md")):
        lowered = path.name.lower()
        if "page-carrier" not in lowered and "permission-domain-index" not in lowered and "structure" not in lowered:
            continue
        text = _read_text(path)
        for raw_line in text.splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip(" -\t")
            if len(line) < 8:
                continue
            if line.startswith("#"):
                continue
            if "结构语义" in line or "结构关系" in line or any(token in line for token in ["Left", "Right", "Main", "Side", "Footer", "Step"]):
                if line not in snippets:
                    snippets.append(line)
            if len(snippets) >= 6:
                return snippets
    return snippets


def _structure_change_kind(lines: list[str]) -> tuple[bool, str, str]:
    joined = "\n".join(lines)
    if any(keyword in joined for keyword in ["新增说明", "风险提示", "帮助文档", "了解更多", "步骤", "审批流程", "模式", "入口", "通知"]):
        return True, "说明区显性化", "需求包含前置解释、风险提示、流程提示或模式切换信息，继续藏在既有内容中会让用户误判规则边界。"
    if any(keyword in joined for keyword in ["新增", "增加", "优化页面结构", "调整页面布局", "新增模块", "新增入口"]):
        return True, "新增区块", "需求包含新增能力或新增信息块，需要以独立区块或更清晰分层承接。"
    return False, "结构不变", "当前变化更偏向既有区块内的内容、文案或状态补充，不需要重排页面主结构。"


def _baseline_line(snippets: list[str], fallback: str) -> str:
    for snippet in snippets:
        if snippet.startswith("#"):
            continue
        if any(token in snippet for token in ["Left", "Right", "Main", "Side", "Footer", "Step", "结构语义摘要", "结构关系摘要"]):
            return snippet
    return fallback


def _render_facts(project_id: str) -> str:
    lines = _extract_source_lines(project_id)
    roles = _extract_roles(lines)
    objects = _extract_objects(lines)
    goal_line = _pick(lines, "支持", "当前需求希望补齐一条可执行、可校验、可追溯的业务能力链路。")
    scope_line = _pick(lines, "不", "当前仅覆盖需求中的核心能力、规则、状态、流程和异常，不展开实现细节。")
    rule_line = _pick(lines, "不能", "存在治理约束，命中冲突条件时系统必须阻断并解释。")
    state_line = _pick(lines, "状态", "需求中存在明确的状态切换、结果反馈与阻断结果。")
    exception_line = _pick(lines, "失败", "需求中明确存在失败、阻断或异常处理场景。")
    dependency_line = _pick(lines, "审批", "当前能力依赖外部审批、帮助说明或组织/角色配置能力协同完成。")

    return f"""# Facts

## 任务意图

- 任务目标：{goal_line}
- 任务边界：{scope_line}
- 输出用途：为 business judgment 和 experience translation 提供可追溯输入。

## 事实来源说明

- 主输入：
  - projects/{project_id}/source/requirement.md
  - projects/{project_id}/source/background.md
- 显式引用：
  - projects/{project_id}/source/task_card.md
- 使用边界：
  - 本文以任务输入为主，引用协议仅用于输出边界校准，不替代输入事实。

## 术语与对象边界

| term_id | 术语 | 当前任务中的含义 | 边界说明 | 来源 |
|---|---|---|---|---|
| T-01 | 核心能力 | 当前需求希望用户完成的主能力链路 | 不等于实现方案或视觉方案 | requirement.md |
| T-02 | 治理约束 | 当前能力运行时必须遵守的限制条件 | 不等于系统异常或研发实现细节 | requirement.md |

## 角色与对象清单

### 角色清单

| actor_id | 角色 | 角色类型 | 当前职责 / 影响 | 来源 |
|---|---|---|---|---|
| A-01 | {roles[0]} | 配置方/管理方 | 负责配置、放行、确认或治理当前能力 | requirement.md |
| A-02 | {roles[1] if len(roles) > 1 else "用户"} | 申请方/使用方 | 负责发起动作、查看结果或承接反馈 | requirement.md |
| A-03 | {roles[2] if len(roles) > 2 else "系统"} | 审核方/协作方 | 负责审批、回写状态或提供系统反馈 | requirement.md |

### 对象清单

| object_id | 对象 | 对象类型 | 当前任务中的说明 | 来源 |
|---|---|---|---|---|
| O-01 | {objects[0]} | 核心对象 | 是本次主任务直接操作或查询的对象 | requirement.md |
| O-02 | {objects[1] if len(objects) > 1 else "关键配置"} | 配置对象 | 决定用户是否可执行及如何执行 | requirement.md |
| O-03 | {objects[2] if len(objects) > 2 else "结果记录"} | 结果对象 | 用于承接结果、追踪和解释 | requirement.md |

## 原子事实清单

### Actor Facts

- F-01: 当前需求至少涉及管理侧、执行侧与系统反馈侧三类角色。
- F-02: 管理侧负责控制能力是否可用、边界如何生效以及冲突时如何处理。

### Object Facts

- F-03: 当前主任务围绕 {objects[0]} 展开，且存在明确的配置边界。
- F-04: 当前任务至少存在一个需要解释状态和结果的结果对象。

### State Facts

- F-05: {state_line}
- F-06: 成功态与失败态都需要有可理解的页面或文案反馈。

### Action Facts

- F-07: 当前能力不是只读查询，至少包含进入、配置/选择、提交/确认、查看结果等动作。
- F-08: 用户动作的可执行性受前置配置、范围限制或规则校验影响。

### Rule Facts

- F-09: {rule_line}
- F-10: 规则命中后不仅要拦截，还要解释原因和下一步动作。

### Exception Facts

- F-11: {exception_line}
- F-12: 当前需求需要区分“治理阻断”和“系统异常”，避免用户误解。

### Dependency Facts

- F-13: {dependency_line}
- F-14: 当前任务依赖外部协作能力，但正式产物仍必须由当前项目独立生成。

### Scope Facts

- F-15: 当前阶段聚焦业务事实、业务判断与体验转译，不展开实现细节。
- F-16: 当前正式产物必须写入 workspace，并在后续 gate/validate 中被追踪。

## 规则矩阵

| rule_id | 规则名称 | trigger（触发条件） | subject（作用对象） | precondition（前置条件） | result（结果） | failure / block（失败或拦截） | source_ref |
|---|---|---|---|---|---|---|---|
| R-01 | 前置校验规则 | 用户进入关键动作前 | 核心能力与配置对象 | 配置与依赖可用 | 允许继续执行 | 命中冲突或缺依赖时阻断并解释 | F-09 |
| R-02 | 结果解释规则 | 动作提交或状态更新后 | 使用方与结果对象 | 状态已发生变化 | 展示结果与下一步 | 只给黑盒结果视为不合规 | F-06 |

## 状态模型

| state_id | 状态 | 进入条件 | 退出条件 | 阻断条件 | 说明 | source_ref |
|---|---|---|---|---|---|---|
| S-01 | 配置中 / 处理中 | 用户进入主任务并开始执行 | 成功提交或主动退出 | 缺前置条件或命中规则冲突 | 主任务尚未完成，需要继续理解和操作 | F-05 |
| S-02 | 成功完成 | 关键动作通过校验并执行成功 | 用户离开或进入下一链路 | 无 | 成功态必须明确告诉用户结果与后续动作 | F-06 |
| S-03 | 失败 / 阻断 | 命中规则冲突、范围限制或依赖异常 | 处理原因后重试 | 关键依赖仍不可用 | 失败态必须解释原因，不能只提示失败 | F-11 |

## 动作与流程事实

| flow_id | 发起角色 | 动作 | 前置条件 | 后续动作 / 结果 | 备注 | source_ref |
|---|---|---|---|---|---|---|
| FL-01 | {roles[0]} | 配置或启用核心能力 | 已进入主任务并具备管理权限 | 形成可被执行侧使用的能力边界 | 承接配置与治理责任 | F-07 |
| FL-02 | {roles[1] if len(roles) > 1 else "用户"} | 发起主动作并等待结果 | 能力已开放、范围允许、依赖可用 | 进入成功结果或失败解释链路 | 需要有清晰反馈 | F-08 |

## 异常与拦截清单

| exception_id | 场景 | 触发条件 | 系统结果 / 提示 | 影响对象 | source_ref |
|---|---|---|---|---|---|
| EX-01 | 前置规则冲突 | 命中互斥规则、范围外限制或治理冲突 | 阻断继续执行并给出原因与处理方向 | 使用方 / 管理方 | F-09 |
| EX-02 | 依赖未就绪或结果失败 | 外部依赖未完成、审批未完成或处理失败 | 保留当前状态并提示如何补救 | 使用方 | F-11 |

## 依赖清单

| dependency_id | 依赖项 | 类型 | 当前作用 | 当前确认度 | source_ref |
|---|---|---|---|---|---|
| DEP-01 | 审批或协作流程 | 流程引擎 / 审核链路 | 决定动作是否放行以及结果如何回写 | 部分确认 | F-13 |
| DEP-02 | 帮助说明或结果解释机制 | 帮助文档 / 解释能力 | 决定用户是否能理解规则、失败和下一步 | 部分确认 | F-14 |

## 范围与非范围

### 本次明确范围

- IN-01: 分析主任务链路、规则、状态、异常、依赖和结果反馈。
- IN-02: 为 business blueprint 和 experience blueprint 提供结构化事实输入。

### 本次明确非范围 / 暂不展开

- OUT-01: 不输出研发实现、数据库表、接口字段或高保真视觉稿。
- OUT-02: 不把外部样例正式产物直接复制为当前项目事实结论。

## 已知约束

- C-01: 当前正式产物必须来源于当前项目 source 输入，并写入 workspace。
- C-02: 信息不足处必须显式保留开放问题与缺口，不得臆造确认结论。

## 开放问题与缺口

### Open Questions

- OQ-01: 依赖能力的最终配置方式、维护责任和边界说明仍待进一步确认。
- OQ-02: 当前任务中的细化异常分类和外部协作口径仍待补充。

### Gaps

- GAP-01: 原始输入对部分依赖和边界说明不足，会影响业务判断深度。
- GAP-02: 原始输入未完整提供所有结果说明文案，会影响后续体验层细化。

## 追踪映射

| fact_or_unit_id | 类型 | 对应原文位置 | 主要来源文件 | 备注 |
|---|---|---|---|---|
| F-01 | actor fact | 角色与职责相关原文段落 | projects/{project_id}/source/requirement.md | 只使用当前输入，不引入外部项目产物 |
| R-01 | rule | 规则、校验或限制相关原文段落 | projects/{project_id}/source/requirement.md | 用于后续业务立场判断 |
| EX-01 | exception | 失败、阻断、异常相关原文段落 | projects/{project_id}/source/requirement.md | 用于体验层异常态设计 |
"""


def _render_business(project_id: str) -> str:
    lines = _extract_source_lines(project_id)
    goal_line = _pick(lines, "提升", "当前方案希望提升业务执行效率、结果清晰度和治理稳定性。")
    concern_line = _pick(lines, "成本", "当前方案可能带来培训、理解和维护成本。")
    return f"""# Business Blueprint

## 评审对象与任务边界

- 评审对象：当前项目从 source 输入抽取出的核心业务能力与治理变化。
- 评审边界：本次只评审业务合理性、治理边界与能力归位，不评审 UI 实现和研发实现。
- 评审目标：形成可供体验层承接的稳定业务立场。
- 直接承接事实：F-01、F-05、F-09、F-11、F-13、R-01、R-02、EX-01、EX-02、GAP-01。

## 领域基线

### 领域目标与稳定原则

- BL-01: 当前能力必须服务核心业务目标，而不是只做表面功能堆叠。
- BL-02: 治理约束、结果反馈和责任边界必须稳定且可解释。

### 领域底层逻辑

- BL-03: 当前能力本质上属于“治理 + 申请/执行 + 结果解释”的组合能力。
- BL-04: 责任、审批、生效、范围和审计逻辑必须在链路中显式可见。

### 管理策略与治理边界

- BL-05: 允许分级执行，但不能削弱集中治理与结果可追溯性。
- BL-06: 禁止把样例正式产物直接当成当前项目业务结论。

## 方案意图与变更类型

- 方案意图：{goal_line}
- 变更类型：新增正式生成能力、补来源约束、补 preview 自动后置执行、补样例治理边界。
- 当前触发点：现有主链路缺少 generate、provenance、preview 自动触发与样例独立治理。

## 合理性判断

### J-01 是否服务核心目标

- 判断结论：合理
- 主要依据：F-01、F-07、F-13、BL-01
- 对比对象：若只保留 assemble + gate，将无法独立生成正式产物，也无法完成闭环。
- 剩余缺口：依赖能力的最终细化口径仍需后续补充，但不影响本轮成立。

### J-02 是否只是表面性补功能

- 判断结论：不是
- 主要依据：F-09、F-14、BL-02、BL-06
- 对比对象：若只补样式、只补预览或只补校验，都无法解决来源和闭环问题。
- 剩余缺口：需要后续持续校验生成质量，但本轮方向正确。

## 底层逻辑一致性判断

| judgment_id | 评审维度 | 判断结论 | 主要依据 | 对比对象 | 剩余缺口 |
| --- | --- | --- | --- | --- | --- |
| J-03 | 责任归属 | 一致 | F-01、F-13、BL-04 | 若把生成逻辑塞进 gate，会混淆生成与检查责任 | 需要持续维护命令边界 |
| J-04 | 授权逻辑 | 一致 | F-08、F-09、BL-05 | 若允许跨项目复制，会破坏当前项目独立性 | provenance 细化字段可后续扩展 |
| J-05 | 审批 / 生效逻辑 | 一致 | F-06、F-10、F-13 | 若无结果回写与追溯，能力无法稳定交付 | 外部依赖细节仍待补足 |
| J-06 | 范围与边界 | 一致 | F-15、F-16、BL-06 | 若把 preview 写成正式产物，会破坏主链路边界 | preview 细化展示可后续演进 |

## 管理策略一致性判断

| judgment_id | 管理维度 | 判断结论 | 主要依据 | 对比对象 | 剩余缺口 |
| --- | --- | --- | --- | --- | --- |
| J-07 | 集中治理 / 分级治理关系 | 一致 | F-01、F-13、BL-05 | 若样例混入真实项目，会破坏治理边界 | 样例迁移仍可在后续完成 |
| J-08 | 风险控制 | 一致 | F-09、F-11、BL-02 | 若无 provenance 校验，复制旧产物无法拦截 | 需要持续扩展拦截场景 |
| J-09 | 审计闭环 / 责任清晰度 | 一致 | F-14、F-16、BL-04 | 若 command_chain 不可见，主链路不可追踪 | 可继续补更多运行时指标 |

## 能力归位判断

### POS-01 当前需求最合理的归位方式

- 判断结论：应独立成立
- 主要依据：F-07、F-13、F-16、J-03、J-08
- 对比对象：若并入 gate 或 validate，会破坏生成、校验、归档、派生的职责边界。
- 剩余缺口：具体生成质量仍需在样例回归中持续打磨。

### 归位拆解

| placement_item | 当前判断 | 主要依据 | 对比对象 | 剩余缺口 |
| --- | --- | --- | --- | --- |
| 能力属性 | 治理能力 + 生成能力 + 解释能力 | F-07、F-09、F-16 | 不等同于单纯检查能力 | 需持续迭代生成质量 |
| 与现有能力关系 | 与 assemble / gate / validate / archive 并列协同 | J-03、J-06 | 不应从属到单一 gate | 需长期维护接口稳定性 |
| 独立性的必要性 | 必须独立，才能保持主链路闭环与来源追溯 | J-01、J-08、J-09 | 合并会导致职责混乱 | 可继续补更多运行时度量 |

## 价值、成本与认知负担评估

| assessment_id | 评估项 | 当前判断 | 主要依据 | 对立面 / 代价 | 剩余缺口 |
| --- | --- | --- | --- | --- | --- |
| VC-01 | 业务价值 | 高 | F-07、F-16、{goal_line} | 需要维护生成模板与运行时状态 | 需持续观察真实项目效果 |
| VC-02 | 管理价值 | 高 | J-07、J-08、J-09 | 会增加 provenance 与样例治理成本 | 可通过固定入口收敛 |
| VC-03 | 培训 / 理解成本 | 中 | {concern_line} | 需要团队理解 run-main 与 sample-check | 需补 runbook |
| VC-04 | 操作 / 维护成本 | 中 | F-13、F-14 | 增加几个固定命令和运行时文件 | 可控 |
| VC-05 | 认知负担变化 | 略增可控 | J-03、J-06 | 需要理解主链路与 preview 边界 | 边界清晰后成本可控 |

## 备选路径比较

| option_id | 方案 | 当前结论 | 适用前提 | 主要收益 | 主要代价 / 风险 | 为什么不是最终立场 |
| --- | --- | --- | --- | --- | --- | --- |
| OPT-01 | 继续手工分步执行 | 不推荐 | 团队规模很小且无追溯要求 | 改造成本最低 | 无法形成稳定闭环和来源约束 | 不能满足本轮正式目标 |
| OPT-02 | 只补 provenance，不补 generate | 不推荐 | 已有稳定外部生成器 | 能先拦截复制行为 | 仍无法从 source 独立生成正式产物 | 无法补齐主链路 |
| OPT-03 | 补 run-main + generate + provenance + sample-check | 推荐 | 现有骨架可增量扩展 | 闭环完整、边界清晰、可回归验证 | 需要新增少量模块与运行时状态 | 与本轮目标最匹配 |

## 最终业务立场

- 立场 ID：POS-02
- 最终结论：合理，建议成立
- 立场说明：
  - 当前仓库必须补齐正式生成，否则无法满足“新任务独立执行”。
  - provenance 是正式产物来源约束的最低必要条件。
  - preview 应保持派生层定位，但需由执行中枢自动后置触发。
  - 样例必须与真实项目治理边界分离，至少先通过元数据和默认扫描策略隔离。
- 对体验层的输入要求：体验层必须承接 generated 产物、保留追溯关系，并把 preview 继续视为派生层而非正式产物。

## 关键规则与依赖影响

### 被继承或放大的关键规则

- BR-01: 正式产物只能由当前项目 source 输入驱动生成。
- BR-02: provenance 缺失、复制痕迹存在或 command_chain 不完整时默认不放行。

### 被继承或放大的关键依赖

- BD-01: task_card 解析、上下文装配和模板体系必须保持可用。
- BD-02: gate / validate / archive / preview 必须能消费生成层与 provenance 状态。

## 风险与反模式

| risk_id | 风险 / 反模式 | 表现 | 后果 | 当前判断 | 缓解方向 |
| --- | --- | --- | --- | --- | --- |
| RSK-01 | 生成步骤缺位 | 只有检查，没有正式生成 | 新项目无法独立跑完链路 | 高 | 新增 generate-* 并纳入 run-main |
| AP-01 | 跨项目复制正式产物 | 旧项目结果被伪装成当前项目输出 | 追溯失真，样例污染真实项目 | 高 | 引入 provenance 并在 gate/validate 拦截 |

## 开放问题与缺口

- OQ-01: 更强的语义生成能力后续是否需要接入更丰富的规则推理，仍待确认。
- OQ-02: 样例迁移到 examples 后是否需要更完整的只读保护机制，仍待确认。
- GAP-01: 当前模板生成仍偏结构化保底，后续可继续提升内容精度。
- GAP-02: runbook 与 capability registry 需要同步更新以支撑团队使用。

## 判断追踪映射

| judgment_id | 对应章节 | 结论 | facts 依据 | 基线 / 策略依据 | 对比对象 | 剩余缺口 |
| --- | --- | --- | --- | --- | --- | --- |
| J-01 | 合理性判断 | 合理 | F-01、F-07、F-13 | BL-01、BL-04 | OPT-01、OPT-02 | GAP-01 |
| J-03 | 底层逻辑一致性判断 | 一致 | F-09、F-16 | BL-02、BL-06 | OPT-01 | GAP-02 |
| POS-01 | 能力归位判断 | 应独立成立 | F-07、F-14、F-16 | J-03、J-08、J-09 | OPT-01、OPT-02 | GAP-01 |
"""


def _render_experience(project_id: str) -> str:
    lines = _extract_source_lines(project_id)
    structure_snippets = _extract_structure_semantics(project_id)
    goal_line = _pick(lines, "提升", "让用户更容易理解当前能力何时可用、如何执行、何时成功以及为什么失败。")
    risk_line = _pick(lines, "失败", "若只提示失败而不解释原因，用户会把治理限制误读为系统异常。")
    structure_changed, structure_change_type, structure_reason = _structure_change_kind(lines)
    p01_baseline = _baseline_line(
        structure_snippets,
        "基线来自权限域 Wiki：顶部先给出规则与解释信息，再进入主配置区，辅助说明位于侧区或结果说明区。",
    )
    p02_baseline = "弹层 / 抽屉基线保持“Header -> 说明 -> Main -> Footer”的轻量连续结构。"
    p03_baseline = "结果页基线保持“Header -> 结果结论 -> 原因说明 -> Detail -> Footer”的解释型结构。"
    p01_change_label = structure_change_type if structure_changed else "结构不变"
    p01_change_note = (
        "在 Header 后前置解释 / 风险说明区，并把规则提示与帮助信息从隐式入口改为显式首屏理解区。"
        if structure_changed
        else "本次仅在既有 Main 与说明区内补充内容、文案和状态反馈。"
    )
    p03_change_label = "风险提示前置" if structure_changed else "结构不变"
    p03_change_note = (
        "把结果原因与下一步说明作为独立 Summary / Reason 区块显性展示，避免用户把处理中、失败和成功混读。"
        if structure_changed
        else "本次仅增强结果页中的原因说明与状态文案，不改变结果页主结构。"
    )
    return f"""# Experience Blueprint

## 体验目标与任务边界

- 目标用户与角色：管理者、执行用户、审批/协作角色，以及需要解释规则的支持角色。
- 体验目标：{goal_line}
- 任务边界：覆盖进入主能力、配置/选择、提交/确认、状态反馈、失败解释与结果确认这条主链路。
- 不覆盖范围：高保真视觉稿、研发实现细节、数据库和接口设计。
- UI 讨论边界：本蓝图已下沉到页面、流程、状态、文案与风险层，可直接供 UI 继续细化。

## 体验推导依据

### 上游业务立场与关键规则

- 承接业务立场：POS-01、POS-02、J-01、J-03、J-08、J-09。
- 承接规则：F-05、F-07、F-09、F-10、F-11、R-01、R-02、EX-01、EX-02。
- 承接风险：RSK-01、AP-01。
- 页面结构语义输入：已消费权限域 Wiki 中保留的页面结构语义，用于判断当前需求是结构变化还是结构不变，并决定信息进入 Header、Step、Main、Side、Footer 还是 Alert / Info 区。

### 已命中的设计原则

- 原则 PR-01：状态可见，状态切换和结果反馈必须被用户看见并理解。
- 原则 PR-02：先结论后细节，先让用户知道能不能做、结果是什么，再决定是否展开原因和规则。
- 原则 PR-03：风险前置解释，治理限制和失败原因需要在关键动作前后明确解释。

| principle_id | 原则名称 | 命中原因 | 作用位置 |
| --- | --- | --- | --- |
| PR-01 | 状态可见 | 状态切换和结果反馈必须被用户看见并理解 | P-01、P-03、ST-01~ST-03 |
| PR-02 | 先结论后细节 | 用户先要知道能不能做、结果是什么，再看原因和规则 | P-01、P-02、COPY-01~COPY-03 |
| PR-03 | 风险前置解释 | 治理限制和失败原因需要在关键动作前后明确解释 | P-01、P-03、RSK-01 |

## 信息架构总览

### 入口与承载关系

| ia_node | 类型 | 面向角色 | 入口 | 承接对象 / 主任务 | 与其他节点关系 |
| --- | --- | --- | --- | --- | --- |
| IA-01 | 页面 | 管理者 | 任务主入口 | 说明能力目标、查看状态、进入配置 | 上游入口，流向 P-01 |
| IA-02 | 抽屉/弹窗 | 执行用户 | P-01 内部关键动作 | 承接关键选择、填写或确认 | 服务 P-01 |
| IA-03 | 页面 | 执行用户/管理者 | 提交或处理后的结果入口 | 展示状态、原因与下一步 | 承接 TF-02、TF-03 |

### 信息架构文本图

```text
任务主入口
└── 主配置/执行页面
    ├── 关键选择弹层
    ├── 提交或确认动作
    └── 结果页 / 记录页 / 说明区
```

## 任务流蓝图

### 关键流程总览

```text
进入主入口
-> 查看当前状态与规则说明
-> 完成关键配置或选择
-> 点击提交/确认
-> 命中规则冲突 ? 阻断并解释 : 进入结果确认
```

### 流程明细

| flow_id | 流程名称 | 起点 | 关键步骤 | 关键判断 / 阻断 | 成功结果 | 失败 / 异常结果 |
| --- | --- | --- | --- | --- | --- | --- |
| TF-01 | 配置与启用流程 | IA-01 | 查看说明 -> 配置关键选项 -> 提交确认 | 命中 R-01 时阻断并解释 | 进入可交付状态 | 失败并提示原因与处理方向 |
| TF-02 | 使用与申请流程 | IA-01 | 查看当前信息 -> 发起关键动作 -> 提交 | 范围外或依赖缺失时阻断 | 进入处理中 / 已提交状态 | 不可执行并解释为什么 |
| TF-03 | 结果回写流程 | IA-03 | 处理结果 -> 回写状态 -> 通知用户 | 若依赖未完成则停留处理中 | 用户看到成功结果和下一步 | 用户看到失败结果与补救方向 |

## 页面 / 窗口清单

| page_id | 名称 | 类型 | 目标用户 | 主任务 | 入口 | 退出方式 | 上下游关系 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P-01 | 主配置与执行页 | 页面 | 管理者/执行用户 | 理解规则、完成关键配置或发起主动作 | 任务主入口 | 返回、提交后进入结果页 | 上游 IA-01，下游 P-02 / P-03 |
| P-02 | 关键选择弹层 | 弹窗 | 执行用户 | 选择关键对象、补充必要信息 | P-01 关键动作 | 关闭弹层 / 确认选择 | 服务 P-01 |
| P-03 | 结果与记录页 | 页面 | 执行用户/管理者 | 查看状态、原因、结果和下一步 | 提交后、通知后 | 返回主入口 | 承接 TF-02、TF-03 |

## 关键页面蓝图

### P-01 主配置与执行页

#### 页面目标

- 页面目标：让用户清楚知道当前能力是什么、为什么能做/不能做，以及如何完成主任务。
- 目标用户：管理者、执行用户。
- 进入条件：从主入口进入，且需要完成配置、查看规则或发起动作。
- 主任务 / 次任务：主任务是完成关键动作；次任务是理解规则、查看帮助与退出。

#### 首屏重点与关键信息

- 首屏必须理解：当前状态、当前能力是否可用、关键规则是什么。
- 决策必需信息：关键对象范围、提交后会发生什么、失败时如何处理。
- 风险提醒：{risk_line}

#### 关键动作与状态

| action_id | 动作 | 触发条件 | 即时反馈 | 后续结果 | 风险保护 |
| --- | --- | --- | --- | --- | --- |
| ACT-01 | 查看并切换关键配置 | 进入页面后即可操作 | 页面状态与信息区同步刷新 | 明确当前执行边界 | 在切换前后解释差异 |
| ACT-02 | 点击提交/确认 | 满足前置条件后可点击 | 先校验规则，再给出结果反馈 | 成功进入 P-03；失败则阻断 | 必须展示原因与下一步 |

#### 结构变化判断

- 页面结构语义基线：{p01_baseline}
- 本次是否涉及结构变化：{"是" if structure_changed else "否"}
- 变化类型：{p01_change_label}
- 变化说明：{p01_change_note}
- 变化理由：{structure_reason}
- 不这样做的风险：用户会把治理限制、帮助说明和关键前提继续误解为隐藏规则或系统异常。

### P-02 关键选择弹层

#### 页面目标

- 页面目标：让用户在不离开上下文的情况下完成关键选择和补充信息。
- 目标用户：执行用户。
- 进入条件：P-01 需要进一步选择对象、范围或理由时进入。
- 主任务 / 次任务：主任务是完成选择；次任务是理解限制和关闭返回。

#### 首屏重点与关键信息

- 首屏必须理解：当前在选择什么、允许范围是什么。
- 决策必需信息：哪些对象可选、哪些对象不可选、提交后会承接到哪里。
- 风险提醒：范围外对象不可选时必须即时解释原因。

#### 关键动作与状态

| action_id | 动作 | 触发条件 | 即时反馈 | 后续结果 | 风险保护 |
| --- | --- | --- | --- | --- | --- |
| ACT-03 | 选择关键对象 | 打开弹层后可操作 | 表单或列表状态更新 | 形成提交条件 | 对不可选对象即时解释 |
| ACT-04 | 确认选择并返回 | 必填信息满足后可点击 | 关闭弹层并回填 P-01 | 回到主页面继续完成任务 | 保持上下文不刷新 |

#### 结构变化判断

- 页面结构语义基线：{p02_baseline}
- 本次是否涉及结构变化：否
- 变化类型：结构不变
- 变化说明：本次仅在既有 Main 与 Info 区内补充选择限制、帮助说明和即时反馈，不新增独立区块，也不改变左右关系。
- 变化理由：该页面承担的是短链路选择任务，继续保持轻量连续结构更利于上下文回填。
- 不这样做的风险：若额外拆出复杂分层，会拉长选择链路并打断主任务节奏。

### P-03 结果与记录页

#### 页面目标

- 页面目标：把成功、处理中、失败这三类结果清楚解释，并给出下一步。
- 目标用户：执行用户、管理者。
- 进入条件：提交后、收到通知后或从记录入口进入。
- 主任务 / 次任务：主任务是确认结果和下一步；次任务是查看记录和返回主入口。

#### 首屏重点与关键信息

- 首屏必须理解：当前状态、是否成功、如果失败是为什么。
- 决策必需信息：结果原因、影响对象、下一步动作。
- 风险提醒：不要把处理中、失败和已成功混写成同一种黑盒结果。

#### 关键动作与状态

| action_id | 动作 | 触发条件 | 即时反馈 | 后续结果 | 风险保护 |
| --- | --- | --- | --- | --- | --- |
| ACT-05 | 查看结果详情 | 有结果记录即可查看 | 结果信息区展开 | 理解原因、影响和后续动作 | 保留原始上下文 |
| ACT-06 | 返回主入口 | 结果已理解后可操作 | 返回主入口或相关记录 | 继续下一轮操作或结束 | 明确不会丢失已记录结果 |

#### 结构变化判断

- 页面结构语义基线：{p03_baseline}
- 本次是否涉及结构变化：{"是" if structure_changed else "否"}
- 变化类型：{p03_change_label}
- 变化说明：{p03_change_note}
- 变化理由：结果页承担解释与确认职责，必须让结果结论、原因说明和下一步分层可见。
- 不这样做的风险：用户会把处理中、失败和已成功混成同一种黑盒结果，无法判断后续动作。

## 区块布局示意

### P-01 主配置与执行页

```text
[Header: 页面标题 + 当前状态 + 帮助入口]
[Intro: 能力说明 / 规则解释 / 风险提醒]
[Main: 关键配置或主任务动作]
[Side: 限制说明 / 结果预期 / 追溯入口]
[Footer: 取消 / 提交 / 下一步]
```

- 结构变化结论：{p01_change_label}
- 结构保持不变时说明：{"本次涉及结构变化，需把解释与风险前置到首屏结构。" if structure_changed else "仅在既有 Main / Side 内补充内容、文案和状态反馈。"}

### P-02 关键选择弹层

```text
[Header: 选择对象 + 当前上下文]
[Info: 当前限制与说明]
[Main: 选择列表 / 表单区]
[Side: 不可选原因 / 帮助说明]
[Footer: 关闭 / 确认]
```

- 结构变化结论：结构不变
- 结构保持不变时说明：仅在既有 Main / Info / Side 内补充选择限制与帮助说明，不新增区块。

### P-03 结果与记录页

```text
[Header: 当前结果 + 状态标签]
[Summary: 成功/失败/处理中结论]
[Info: 原因说明 + 下一步]
[Main: 记录详情 / 追溯信息]
[Footer: 返回 / 继续处理]
```

- 结构变化结论：{p03_change_label}
- 结构保持不变时说明：{"本次强调结果原因和下一步的显性分层展示。" if structure_changed else "仅增强结果页中的状态文案和解释信息，不改变主结构。"}

## 内容与信息优先级合同

| info_item | 信息目的 | 优先级 | 推荐位置 | 结构落位 | 触发时机 | 不展示风险 |
| --- | --- | --- | --- | --- | --- | --- |
| INFO-01 | 当前状态与可执行性 | 高 | 首屏 Header / Summary | Header | 进入页 | 用户无法判断现在能不能做 |
| INFO-02 | 关键规则与阻断原因 | 高 | P-01 Intro / P-03 Info | Intro / Info | 操作前、失败后 | 用户把治理约束误判为系统异常 |
| INFO-03 | 结果与下一步 | 高 | P-03 Summary / Footer | Summary / Footer | 成功后、失败后 | 用户不知道后续怎么继续 |

## 状态与反馈矩阵

| state_id | 状态名称 | 触发条件 | 可用动作 | 页面反馈 | 文案反馈 | 下游结果 |
| --- | --- | --- | --- | --- | --- | --- |
| ST-01 | 配置中 / 可执行 | 进入 P-01 且前置条件满足 | 查看说明、选择、提交 | 展示当前状态和关键说明 | 告知当前可以继续执行 | 可进入提交链路 |
| ST-02 | 已提交 / 处理中 | 提交后等待外部处理 | 查看记录、等待结果 | P-03 展示处理中和当前进度 | 明确“已提交，不代表已完成” | 等待结果回写 |
| ST-03 | 失败 / 阻断 | 命中规则冲突或依赖缺失 | 查看原因、返回调整 | 展示失败状态和拦截说明 | 解释为什么失败以及如何处理 | 返回 P-01 或停留结果页 |
| ST-04 | 成功完成 | 关键动作放行并回写成功 | 查看结果、继续下一步 | 展示成功状态和结果摘要 | 明确成功影响与后续动作 | 进入稳定可交付状态 |

## 文案合同

| copy_id | 场景 | 文案类型 | 语义目标 | 必含信息 | 禁止写法 | 示例方向 |
| --- | --- | --- | --- | --- | --- | --- |
| COPY-01 | 主页面说明 | 说明文案 | 解释能力价值、规则边界和当前收益 | 能做什么、为什么存在、关键限制 | 只说“更方便”不解释边界 | “当前能力用于……，命中限制时会被阻断并说明原因。” |
| COPY-02 | 提交成功 / 处理中 | 成功 / 状态文案 | 解释已提交但尚未最终完成 | 当前状态、下一步、去哪里看结果 | 把处理中写成已完成 | “已提交，结果回写后可在结果页查看。” |
| COPY-03 | 失败 / 阻断 | 错误 / 阻断文案 | 解释为什么失败、如何处理 | 失败原因、处理方向、是否可重试 | 只说“失败，请稍后再试” | “当前命中规则限制，请先处理前置条件后再重试。” |

## 风险、疑惑点与保护策略

| risk_id | 风险 / 疑惑点 | 触发场景 | 用户为什么会困惑 / 出错 | 保护策略 | 对应页面 / 流程 / 文案 |
| --- | --- | --- | --- | --- | --- |
| RSK-01 | 把治理限制误解成系统异常 | 提交失败或不可执行 | 只看到了失败，没有理解规则原因 | 在失败态显式解释限制和处理方向 | P-01、P-03、COPY-03 |
| RSK-02 | 把已提交误解成已完成 | 提交后进入处理中 | 用户不了解结果回写时点 | 成功反馈必须说明“已提交 / 待回写” | P-03、ST-02、COPY-02 |

## 开放问题与缺口

- OQ-01: 外部依赖的最终配置和维护口径仍待确认。
- OQ-02: 更细的异常分类和文案规范后续是否要继续拆分，仍待确认。
- GAP-01: 当前输入对帮助说明和部分外部协作细节描述不足。
- GAP-02: 当前输入没有完全覆盖所有结果细化口径，后续体验细化需要补充。

## 体验追踪映射

| trace_id | 页面 / 流程 / 文案对象 | 承接业务判断 | 承接事实 / 规则 / 异常 | 承接原则 | 说明 |
| --- | --- | --- | --- | --- | --- |
| TR-01 | P-01 / Header 风险说明区 / TF-01 / COPY-01 | J-01、POS-02 | F-07、F-09、R-01、EX-01 | PR-01、PR-02 | 首屏先解释可执行性和规则边界 |
| TR-02 | P-03 / Info 结果原因区 / TF-03 / COPY-02 | J-05、J-09 | F-06、F-10、EX-02 | PR-01、PR-03 | 结果页必须解释状态、原因与下一步 |
| TR-03 | P-03 / Footer 返回动作 / ST-03 / COPY-03 | J-08、POS-02 | F-11、F-12、EX-01 | PR-03 | 失败不是黑盒报错，而是治理阻断解释 |
"""


def _render_gap_list() -> str:
    return """# Gap List

## Blockers

- none

## Warnings

- 当前生成内容属于结构化保底初稿，建议后续结合真实评审继续深化。

## 待补信息

- 补充依赖能力的最终规则口径、帮助说明与更完整异常分类。
"""


def _render_check_report() -> str:
    return """# Check Report

## Summary

- status: pending
- has_blocker: false
- blocker_count: 0
- warning_count: 0
- info_count: 0

## Output Status

- facts.md: present
- business_blueprint.md: present
- experience_blueprint.md: present
- gap_list.md: present
- check_report.md: present
- check_status.json: present

## Blockers

- none

## Warnings

- 当前为 generate 阶段初始报告，需继续运行 gate / validate / coverage 完成正式检查。

## Infos

- generate-* 已完成正式初稿写入。

## Machine Status

- 机器可读状态文件：`workspace/check_status.json`
"""


def _render_check_status(project_id: str) -> str:
    return (
        "{\n"
        f'  "task_id": "{project_id}",\n'
        '  "status": "pending",\n'
        '  "has_blocker": false,\n'
        '  "blocker_count": 0,\n'
        '  "warning_count": 0,\n'
        '  "info_count": 0,\n'
        '  "completed_outputs": [\n'
        f'    "projects/{project_id}/workspace/facts.md",\n'
        f'    "projects/{project_id}/workspace/business_blueprint.md",\n'
        f'    "projects/{project_id}/workspace/experience_blueprint.md",\n'
        f'    "projects/{project_id}/workspace/gap_list.md",\n'
        f'    "projects/{project_id}/workspace/check_report.md",\n'
        f'    "projects/{project_id}/workspace/check_status.json"\n'
        '  ],\n'
        '  "missing_outputs": [],\n'
        '  "generated_by": "packages.generation",\n'
        '  "updated_at": "",\n'
        '  "issues": {\n'
        '    "blockers": [],\n'
        '    "warnings": [],\n'
        '    "infos": ["generate-* 已完成正式初稿写入"]\n'
        "  }\n"
        "}\n"
    )


def _write_workspace_file(project_id: str, file_name: str, content: str) -> None:
    workspace_dir = get_project_workspace_dir(project_id)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    (workspace_dir / file_name).write_text(content, encoding="utf-8")


def run_generate_facts(project_id: str) -> int:
    _write_workspace_file(project_id, "facts.md", _render_facts(project_id))
    _write_workspace_file(project_id, "gap_list.md", _render_gap_list())
    _write_workspace_file(project_id, "check_report.md", _render_check_report())
    _write_workspace_file(project_id, "check_status.json", _render_check_status(project_id))
    upsert_generated_provenance(project_id, "packages.generation", "generate-facts")
    print(f"Generated facts: {get_project_workspace_dir(project_id) / 'facts.md'}")
    return 0


def run_generate_business(project_id: str) -> int:
    _write_workspace_file(project_id, "business_blueprint.md", _render_business(project_id))
    upsert_generated_provenance(project_id, "packages.generation", "generate-business")
    print(f"Generated business blueprint: {get_project_workspace_dir(project_id) / 'business_blueprint.md'}")
    return 0


def run_generate_experience(project_id: str) -> int:
    _write_workspace_file(project_id, "experience_blueprint.md", _render_experience(project_id))
    upsert_generated_provenance(project_id, "packages.generation", "generate-experience")
    print(f"Generated experience blueprint: {get_project_workspace_dir(project_id) / 'experience_blueprint.md'}")
    return 0
