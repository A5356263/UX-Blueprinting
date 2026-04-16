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


HEADING_L3_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
ZONE_ORDER = ["Header", "Intro", "Step", "Alert", "Filter", "Tab", "Menu", "Summary", "Main", "Side", "Info", "Footer"]


def _read_workspace_text(project_id: str, file_name: str) -> str:
    return _read_text(get_project_workspace_dir(project_id) / file_name)


def _split_heading_blocks(text: str, pattern: re.Pattern[str]) -> dict[str, str]:
    matches = list(pattern.finditer(text))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[match.group(1).strip()] = text[start:end].strip()
    return blocks


def _parse_bullet_lines(section_text: str) -> list[str]:
    items: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def _extract_code_block(section_text: str) -> str:
    match = re.search(r"```(?:text)?\n([\s\S]*?)```", section_text)
    return match.group(1).strip() if match else ""


def _parse_markdown_table_rows(section_text: str) -> list[dict[str, str]]:
    rows = [line.strip() for line in section_text.splitlines() if line.strip().startswith("|")]
    if len(rows) < 2:
        return []
    headers = [cell.strip() for cell in rows[0].strip("|").split("|")]
    result: list[dict[str, str]] = []
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        result.append({headers[index]: cells[index] for index in range(len(headers))})
    return result


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = re.sub(r"\s+", " ", value).strip()
        if not cleaned:
            continue
        marker = cleaned.lower()
        if marker in seen:
            continue
        seen.add(marker)
        result.append(cleaned)
    return result


def _normalize_name(value: str) -> str:
    compact = re.sub(r"\s+", "", value).lower()
    for token in ["页面", "页", "弹窗", "弹层", "抽屉", "子页面", "窗口", "结果", "记录", "与", "及", "（", "）", "(", ")", "/"]:
        compact = compact.replace(token, "")
    return compact


def _extract_zone_tokens(parts: list[str]) -> list[str]:
    joined = "\n".join(parts)
    token_map = [
        ("Header", "Header"),
        ("Intro", "Intro"),
        ("Filter", "Filter"),
        ("Search", "Filter"),
        ("Action", "Action"),
        ("Menu", "Menu"),
        ("Tab", "Tab"),
        ("Sub-Tab", "Tab"),
        ("Step", "Step"),
        ("Summary", "Summary"),
        ("Main", "Main"),
        ("Side", "Side"),
        ("Footer", "Footer"),
        ("Alert", "Alert"),
        ("Info", "Info"),
        ("Left", "Left"),
        ("Right", "Right"),
    ]
    zones: list[str] = []
    lowered = joined.lower()
    for token, zone in token_map:
        if token.lower() in lowered and zone not in zones:
            zones.append(zone)
    if "Right" in zones and "Side" not in zones:
        zones.append("Side")
    if "Left" in zones and "Menu" not in zones and ("角色索引" in joined or "导航" in joined or "Menu" in joined):
        zones.append("Menu")
    return zones


def _merge_catalog_entry(
    catalog: dict[str, dict[str, object]],
    name: str,
    baseline: str = "",
    layout_lines: list[str] | None = None,
    aliases: list[str] | None = None,
) -> None:
    key = _normalize_name(name)
    existing = catalog.get(key, {"canonical_name": name, "aliases": [], "baseline": "", "layout_lines": [], "zones": []})
    alias_values = [name] + list(existing.get("aliases", [])) + list(aliases or [])
    layout_values = list(existing.get("layout_lines", [])) + list(layout_lines or [])
    baseline_text = baseline.strip() or str(existing.get("baseline", "")).strip()
    zones = _extract_zone_tokens(([baseline_text] if baseline_text else []) + layout_values)
    existing["canonical_name"] = name
    existing["aliases"] = _dedupe_strings(alias_values)
    existing["baseline"] = baseline_text
    existing["layout_lines"] = _dedupe_strings(layout_values)
    existing["zones"] = zones
    catalog[key] = existing


def _parse_named_layout_entries(code_block: str) -> dict[str, list[str]]:
    entries: dict[str, list[str]] = {}
    current_name = ""
    for raw_line in code_block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith("：") and not line.startswith("->"):
            current_name = line[:-1].strip()
            entries.setdefault(current_name, [])
            continue
        if current_name:
            entries[current_name].append(line)
    return entries


def _build_structure_catalog(project_id: str) -> list[dict[str, object]]:
    runtime_dir = get_project_runtime_dir(project_id)
    bundle_dir = runtime_dir / "context_bundle"
    catalog: dict[str, dict[str, object]] = {}
    topic_path = bundle_dir / "knowledge" / "wiki" / "topics" / "page-carrier-semantics-map.md"
    topic_text = _read_text(topic_path)
    if topic_text:
        topic_blocks = _split_heading_blocks(topic_text, HEADING_L3_RE)
        for bullet in _parse_bullet_lines(topic_blocks.get("3.5 结构语义摘要", "")):
            if "：" not in bullet:
                continue
            name, baseline = bullet.split("：", 1)
            _merge_catalog_entry(catalog, name.strip(), baseline=baseline.strip())
        named_layouts = _parse_named_layout_entries(_extract_code_block(topic_blocks.get("3.6 原始区块关系图保留", "")))
        for name, layout_lines in named_layouts.items():
            _merge_catalog_entry(catalog, name.strip(), layout_lines=layout_lines)

    detail_path = bundle_dir / "knowledge" / "wiki" / "entities" / "permission-detail-view.md"
    detail_text = _read_text(detail_path)
    if detail_text:
        detail_blocks = _split_heading_blocks(detail_text, HEADING_L3_RE)
        detail_baseline = " ".join(_parse_bullet_lines(detail_blocks.get("3.4 结构语义摘要", "")))
        detail_layout = [line.strip() for line in _extract_code_block(detail_blocks.get("3.5 原始区块关系图保留", "")).splitlines() if line.strip()]
        _merge_catalog_entry(catalog, "权限明细视图", baseline=detail_baseline, layout_lines=detail_layout, aliases=["权限明细", "权限详情"])

    return list(catalog.values())


def _find_catalog_entry(catalog: list[dict[str, object]], *candidate_names: str) -> dict[str, object] | None:
    normalized_candidates = [_normalize_name(name) for name in candidate_names if name.strip()]
    for candidate in normalized_candidates:
        for item in catalog:
            names = [str(item.get("canonical_name", ""))] + [str(alias) for alias in item.get("aliases", [])]
            if any(_normalize_name(name) == candidate for name in names if name.strip()):
                return item
    for candidate in normalized_candidates:
        for item in catalog:
            names = [str(item.get("canonical_name", ""))] + [str(alias) for alias in item.get("aliases", [])]
            if any(candidate and candidate in _normalize_name(name) for name in names if name.strip()):
                return item
    return None


def _detect_task_signals(lines: list[str], facts_text: str, business_text: str) -> dict[str, object]:
    joined = "\n".join(lines + [facts_text, business_text])
    return {
        "joined": joined,
        "has_mode_setup": any(keyword in joined for keyword in ["模式", "设置页面", "立即启用", "确认编辑", "关闭模式", "启用成功"]),
        "has_selection_dialog": any(keyword in joined for keyword in ["弹窗", "弹层", "搜索角色", "搜索应用", "部分角色", "部分应用", "分页展示"]),
        "has_apply_page": any(keyword in joined for keyword in ["申请权限", "自助申请", "发起申请", "提交申请"]),
        "has_my_permissions": any(keyword in joined for keyword in ["我的权限", "查看权限清单", "个人中心"]),
        "has_result_page": any(keyword in joined for keyword in ["审批通过", "收到通知", "权限生效", "关闭失败", "结果", "处理中", "审批人"]),
        "has_help_doc": any(keyword in joined for keyword in ["帮助文档", "了解更多", "说明文案", "提示文案"]),
        "has_risk_rules": any(keyword in joined for keyword in ["不能", "限制", "失败", "提示", "敏感", "校验", "不可选"]),
        "has_steps": any(keyword in joined for keyword in ["第一步", "第二步", "第三步", "审批流程", "步骤"]),
    }


def _ordered_slots(slots: list[str]) -> list[str]:
    return [slot for slot in ZONE_ORDER if slot in slots]


def _required_slots_for_page(archetype: str, signals: dict[str, object]) -> list[str]:
    if archetype == "config_workbench":
        slots = ["Header", "Step", "Alert", "Main", "Side", "Footer"]
        if not signals.get("has_steps"):
            slots.remove("Step")
        if not signals.get("has_risk_rules"):
            slots.remove("Alert")
        return slots
    if archetype == "selection_dialog":
        slots = ["Header", "Info", "Main", "Side", "Footer"]
        if not signals.get("has_help_doc"):
            slots.remove("Side")
        return slots
    if archetype == "apply_page":
        slots = ["Header", "Intro", "Alert", "Main", "Side", "Footer"]
        if not signals.get("has_risk_rules"):
            slots.remove("Alert")
        return slots
    if archetype == "detail_page":
        return ["Header", "Info", "Tab", "Menu", "Main", "Footer"]
    if archetype == "result_page":
        return ["Header", "Summary", "Info", "Main", "Footer"]
    return ["Header", "Main", "Footer"]


def _slot_summary_map(archetype: str) -> dict[str, str]:
    if archetype == "config_workbench":
        return {
            "Header": "模式名称 + 当前状态 + 帮助入口",
            "Step": "申请方式 / 范围 / 审批流程步骤",
            "Alert": "模式互斥规则 / 前置限制 / 风险提醒",
            "Main": "配置表单 + 范围设置 + 启用动作",
            "Side": "规则解释 / 帮助说明 / 审批配置说明",
            "Footer": "取消 / 启用 / 确认编辑",
        }
    if archetype == "selection_dialog":
        return {
            "Header": "选择对象 + 当前上下文",
            "Info": "可选范围 / 限制说明 / 已选提示",
            "Main": "搜索 + 列表 + 勾选结果",
            "Side": "不可选原因 / 帮助说明",
            "Footer": "取消 / 确认",
        }
    if archetype == "apply_page":
        return {
            "Header": "页面标题 + 当前身份 + 入口说明",
            "Intro": "申请目标说明 / 能做什么 / 申请后预期",
            "Alert": "敏感角色限制 / 审批前提 / 风险提醒",
            "Main": "权限选择 + 原因填写 + 提交动作",
            "Side": "规则解释 / 帮助文档 / 追溯入口",
            "Footer": "取消 / 提交申请 / 查看我的权限",
        }
    if archetype == "detail_page":
        return {
            "Header": "当前对象 + 身份标签 + 返回入口",
            "Info": "解释说明 / 当前上下文 / 来源说明",
            "Tab": "身份 / 终端 / 权限视角切换",
            "Menu": "模块导航 / 目录切换",
            "Main": "权限明细构成 / 查询结果 / 解释内容",
            "Footer": "关闭 / 返回",
        }
    return {
        "Header": "当前结果 + 状态标签",
        "Summary": "审批结论 / 生效结果 / 处理中状态",
        "Info": "原因说明 + 下一步 + 通知解释",
        "Main": "申请记录 / 审批轨迹 / 权限变化详情",
        "Footer": "返回 / 继续处理",
    }


def _build_layout_blocks(archetype: str, slots: list[str]) -> list[tuple[str, str]]:
    summary_map = _slot_summary_map(archetype)
    return [(slot, summary_map.get(slot, "")) for slot in _ordered_slots(slots)]


def _judge_structure_change(
    archetype: str,
    page_name: str,
    baseline_zones: list[str],
    required_slots: list[str],
    signals: dict[str, object],
) -> dict[str, str]:
    baseline_set = set(baseline_zones)
    missing_slots = [slot for slot in required_slots if slot not in baseline_set and not (slot == "Summary" and "Info" in baseline_set)]

    if archetype == "selection_dialog":
        return {
            "changed": "否",
            "type": "结构不变",
            "note": "该页面继续保持短链路选择结构，只在既有 Header / Info / Main / Footer 内补充范围限制和解释信息。",
            "reason": "选择弹窗的目标是快速完成对象选择与回填，不适合再拆出更重的多层结构。",
            "risk": "若把短链路选择页做成重工作台，会打断主任务节奏并增加理解成本。",
            "keep_note": "仅在既有区块内补充选择限制、帮助说明与即时反馈。",
        }

    if "Step" in missing_slots:
        change_type = "新增区块"
        note = f"{page_name} 需要把模式设置与审批配置分成可理解的阶段，因此要补出 Step 级结构，而不是把所有设置压在单一主区。"
    elif any(slot in missing_slots for slot in ["Alert", "Intro"]) and signals.get("has_risk_rules"):
        change_type = "风险提示前置"
        note = f"{page_name} 需要把限制条件、互斥规则和失败原因前置到主动作前，不再藏在操作后的被动解释里。"
    elif any(slot in missing_slots for slot in ["Info", "Side", "Summary"]):
        change_type = "说明区显性化"
        note = f"{page_name} 需要把帮助说明、结果解释或下一步提示显性分层，避免继续挤在 Main 内容中。"
    elif missing_slots:
        change_type = "主次调整"
        note = f"{page_name} 需要把新增信息重新放到更合适的结构位置，让主任务与解释信息的主次关系更清楚。"
    else:
        return {
            "changed": "否",
            "type": "结构不变",
            "note": f"{page_name} 可以在既有结构基线内完成本次增强，不需要新增独立区块，只需补充内容、文案和状态反馈。",
            "reason": "当前新增内容与页面原有承载语义一致，结构基线已经足以承接本次变化。",
            "risk": "若误做额外结构拆分，会让信息层级变重，用户反而更难理解主任务。",
            "keep_note": "仅在既有区块内补充内容、文案和状态反馈。",
        }

    return {
        "changed": "是",
        "type": change_type,
        "note": note,
        "reason": "本次判断综合了任务新增信息类型、业务限制和页面原有结构基线，而不是只根据“新增”做粗糙判断。",
        "risk": "若不显式调整结构，用户会把规则、结果或帮助信息继续误读为隐藏规则、系统异常或次要信息。",
        "keep_note": "本次涉及结构变化，需要在区块布局里显式表达新增或前置的结构层。",
    }


def _default_baseline(page_type: str) -> str:
    if page_type == "弹窗":
        return "弹层 / 抽屉基线保持“Header -> Info -> Main -> Footer”的短链路连续结构。"
    return "页面基线保持“Header -> Main -> Footer”的主任务结构，并在需要时用 Info / Side 承接解释信息。"


def _build_page_plan(
    archetype: str,
    page_name: str,
    page_type: str,
    roles: list[str],
    main_task: str,
    entry: str,
    exit_text: str,
    relation: str,
    focus_points: list[str],
    risk_text: str,
    actions: list[dict[str, str]],
    catalog_entry: dict[str, object] | None,
    signals: dict[str, object],
) -> dict[str, object]:
    baseline = str((catalog_entry or {}).get("baseline", "")).strip() or _default_baseline(page_type)
    baseline_zones = list((catalog_entry or {}).get("zones", []))
    required_slots = _required_slots_for_page(archetype, signals)
    structure = _judge_structure_change(archetype, page_name, baseline_zones, required_slots, signals)
    return {
        "archetype": archetype,
        "name": page_name,
        "page_type": page_type,
        "roles": roles,
        "main_task": main_task,
        "entry": entry,
        "exit": exit_text,
        "relation": relation,
        "baseline": baseline,
        "focus_points": focus_points,
        "risk_text": risk_text,
        "actions": actions,
        "layout_blocks": _build_layout_blocks(archetype, required_slots),
        "structure": structure,
    }


def _identify_impacted_pages(project_id: str, lines: list[str], facts_text: str, business_text: str) -> list[dict[str, object]]:
    catalog = _build_structure_catalog(project_id)
    signals = _detect_task_signals(lines, facts_text, business_text)
    pages: list[dict[str, object]] = []

    if signals.get("has_mode_setup"):
        pages.append(
            _build_page_plan(
                "config_workbench",
                "自助申请权限模式设置页",
                "页面",
                ["超管", "超级管理员"],
                "配置自助申请权限模式、申请范围和审批流程，并决定是否启用或编辑该模式。",
                "从权限管理模式页点击“立即启用”或“编辑”进入。",
                "取消返回上一页；启用或确认编辑后停留当前页并刷新状态。",
                "作为治理入口页，可流向范围选择弹窗、表单编辑子页和结果反馈页。",
                [
                    "当前模式是否可启用、为什么可启用或不可启用",
                    "申请方式、角色范围 / 应用范围、审批流程如何影响后续员工端",
                    "当前动作成功后会刷新什么、失败时如何处理",
                ],
                "若把互斥模式限制和在途流程校验藏在操作后，用户会把治理冲突误判为系统异常。",
                [
                    {
                        "name": "配置申请方式与范围",
                        "trigger": "进入页面后即可操作",
                        "feedback": "步骤区和主配置区同步刷新当前选择结果",
                        "outcome": "形成可启用的模式配置",
                        "protection": "对角色 / 应用范围的限制即时解释",
                    },
                    {
                        "name": "启用、关闭或确认编辑",
                        "trigger": "完成配置并满足前置条件后可点击",
                        "feedback": "先校验互斥模式和在途流程，再给出成功或失败反馈",
                        "outcome": "刷新为已开启、已关闭或已编辑状态",
                        "protection": "命中互斥模式或在途流程时必须阻断并解释原因",
                    },
                ],
                _find_catalog_entry(catalog, "功能授权", "角色管理"),
                signals,
            )
        )

    if signals.get("has_selection_dialog"):
        pages.append(
            _build_page_plan(
                "selection_dialog",
                "角色 / 应用范围选择弹窗",
                "弹窗",
                ["超管", "超级管理员"],
                "在不离开当前配置上下文的情况下选择允许申请的角色或应用范围。",
                "在设置页中选择“部分角色”或“部分应用”时打开。",
                "确认后回填配置页并保留当前上下文，取消则直接关闭。",
                "服务于模式设置页，选择完成后回流主配置页。",
                [
                    "当前在选择什么、可选范围是什么",
                    "哪些对象不可选、为什么不可选",
                    "确认选择后会回填到哪个设置项",
                ],
                "如果范围限制和不可选原因不在弹层内即时解释，用户会反复试错并怀疑系统数据有误。",
                [
                    {
                        "name": "搜索并勾选角色 / 应用",
                        "trigger": "弹窗打开后即可操作",
                        "feedback": "搜索结果、勾选状态和已选计数即时变化",
                        "outcome": "形成回填到设置页的范围结果",
                        "protection": "对不可选对象即时解释原因",
                    },
                    {
                        "name": "确认范围选择",
                        "trigger": "完成选择后可点击",
                        "feedback": "关闭弹窗并回填主配置页",
                        "outcome": "主配置页形成完整的范围设置",
                        "protection": "保持当前上下文不丢失",
                    },
                ],
                None,
                signals,
            )
        )

    if signals.get("has_apply_page"):
        pages.append(
            _build_page_plan(
                "apply_page",
                "员工申请权限页",
                "页面",
                ["员工", "业务管理员"],
                "查看可申请权限范围、填写申请原因并发起申请。",
                "从个人中心或权限入口进入“申请权限”。",
                "提交后进入结果 / 进度页，取消则返回上一入口。",
                "承接员工自助申请主任务，并流向结果与进度页。",
                [
                    "当前能申请什么、为什么能申请或不能申请",
                    "申请通过后会如何生效、需要经过哪些审批",
                    "如果命中敏感角色 / 组织限制，系统会如何提示",
                ],
                "若申请页只给入口不解释范围限制和审批预期，用户会把被拦截理解成系统异常或流程没生效。",
                [
                    {
                        "name": "选择权限并填写申请原因",
                        "trigger": "进入申请页后即可操作",
                        "feedback": "申请对象、原因和限制提示即时刷新",
                        "outcome": "形成可提交的申请单",
                        "protection": "命中敏感对象或范围外时立即阻断并解释",
                    },
                    {
                        "name": "提交申请",
                        "trigger": "满足前置校验后可点击",
                        "feedback": "进入待审批 / 已提交状态反馈",
                        "outcome": "流向审批与结果反馈链路",
                        "protection": "提交前必须明确审批预期和失败处理方向",
                    },
                ],
                _find_catalog_entry(catalog, "用户授权", "功能授权"),
                signals,
            )
        )

    if signals.get("has_my_permissions"):
        pages.append(
            _build_page_plan(
                "detail_page",
                "我的权限页",
                "页面",
                ["员工"],
                "查看当前已拥有的权限、来源和细粒度构成，支撑员工自查与核对。",
                "从个人中心新增的“我的权限”入口进入。",
                "关闭或返回个人中心，不承担新的治理提交动作。",
                "作为只读核对页，可继续下钻到权限明细解释层。",
                [
                    "当前有哪些权限、来源是什么、属于哪个身份或终端",
                    "如果申请已生效，哪些结果已经落到当前权限上",
                    "从哪里进入更细的权限明细解释",
                ],
                "如果“我的权限”只有聚合结果没有明细解释，用户无法完成自助核对，也无法判断权限为何生效。",
                [
                    {
                        "name": "切换权限视角并查看明细",
                        "trigger": "进入我的权限页后即可操作",
                        "feedback": "Tab、导航与明细内容同步切换",
                        "outcome": "完成权限核对和来源解释",
                        "protection": "保持当前对象和身份上下文可见",
                    }
                ],
                _find_catalog_entry(catalog, "权限详情", "权限明细视图"),
                signals,
            )
        )

    if signals.get("has_result_page"):
        pages.append(
            _build_page_plan(
                "result_page",
                "申请结果与审批进度页",
                "页面",
                ["员工", "审批人", "超管"],
                "查看申请当前处于待审批、已生效还是失败阻断，并给出下一步。",
                "提交申请后、收到通知后或从申请记录入口进入。",
                "返回申请页、返回我的权限页或结束当前链路。",
                "承接申请后的解释链路，并与我的权限页形成结果核对闭环。",
                [
                    "当前状态是什么、是否已经生效、为什么会失败或还在处理中",
                    "当前需要谁继续处理、用户下一步该做什么",
                    "如何回到申请页或我的权限页继续查看",
                ],
                "若结果页只告诉用户“成功/失败”，不解释审批进度、原因和下一步，用户无法判断是否还需要等待、重试或联系审批人。",
                [
                    {
                        "name": "查看当前结果与审批进度",
                        "trigger": "有申请记录后即可进入",
                        "feedback": "状态、原因和下一步同步展示",
                        "outcome": "用户理解当前结果并决定后续动作",
                        "protection": "失败与处理中必须明确区分，不能混成黑盒结果",
                    },
                    {
                        "name": "返回申请页或查看我的权限",
                        "trigger": "理解结果后可点击",
                        "feedback": "带着当前申请上下文跳回对应页面",
                        "outcome": "继续处理或完成核对",
                        "protection": "保持记录可追溯、状态不丢失",
                    },
                ],
                _find_catalog_entry(catalog, "权限详情", "权限明细视图"),
                signals,
            )
        )

    return pages


def _info_rows_for_page(page: dict[str, object]) -> list[dict[str, str]]:
    page_id = str(page["page_id"])
    page_name = str(page["name"])
    archetype = str(page["archetype"])
    if archetype == "config_workbench":
        return [
            {
                "purpose": "当前模式状态与可启用性",
                "priority": "高",
                "position": f"{page_id} Header / Alert",
                "slot": "Header / Alert",
                "trigger": "进入页、点击启用前",
                "risk": "用户无法判断当前模式是否能启用，容易把互斥限制误判为系统异常。",
            },
            {
                "purpose": "申请方式、范围与审批配置",
                "priority": "高",
                "position": f"{page_id} Step / Main",
                "slot": "Step / Main",
                "trigger": "配置过程中",
                "risk": "用户难以理解配置顺序，后续员工端能力边界会不清楚。",
            },
        ]
    if archetype == "selection_dialog":
        return [
            {
                "purpose": "可选范围与不可选原因",
                "priority": "高",
                "position": f"{page_id} Info / Main",
                "slot": "Info / Main",
                "trigger": "打开弹窗后",
                "risk": "用户会反复试错，无法理解为什么某些对象不可选。",
            }
        ]
    if archetype == "apply_page":
        return [
            {
                "purpose": f"{page_name} 的申请范围与规则解释",
                "priority": "高",
                "position": f"{page_id} Intro / Alert",
                "slot": "Intro / Alert",
                "trigger": "进入页、提交前",
                "risk": "用户不知道能申请什么、为什么被限制，容易误解申请链路。",
            },
            {
                "purpose": "申请对象、申请原因与提交动作",
                "priority": "高",
                "position": f"{page_id} Main / Footer",
                "slot": "Main / Footer",
                "trigger": "填写并提交时",
                "risk": "主任务入口不清晰，用户无法完成申请。",
            },
        ]
    if archetype == "detail_page":
        return [
            {
                "purpose": f"{page_name} 的权限解释与来源说明",
                "priority": "高",
                "position": f"{page_id} Info / Tab / Main",
                "slot": "Info / Tab / Main",
                "trigger": "进入页、切换视角时",
                "risk": "用户只能看到聚合结果，无法完成权限核对和来源理解。",
            }
        ]
    return [
        {
            "purpose": f"{page_name} 的结果结论与下一步",
            "priority": "高",
            "position": f"{page_id} Summary / Info / Footer",
            "slot": "Summary / Info / Footer",
            "trigger": "提交后、收到通知后",
            "risk": "用户不知道当前是否生效、为何失败以及接下来该做什么。",
        }
    ]


def _render_experience(project_id: str) -> str:
    lines = _extract_source_lines(project_id)
    facts_text = _read_workspace_text(project_id, "facts.md")
    business_text = _read_workspace_text(project_id, "business_blueprint.md")
    goal_line = _pick(lines, "提升", "让用户更容易理解当前能力何时可用、如何执行、何时成功以及为什么失败。")
    risk_line = _pick(lines, "失败", "若只提示失败而不解释原因，用户会把治理限制误读为系统异常。")
    pages = _identify_impacted_pages(project_id, lines, facts_text, business_text)
    for index, page in enumerate(pages, start=1):
        page["page_id"] = f"P-{index:02d}"

    page_lookup = {str(page["archetype"]): page for page in pages}
    ia_rows: list[str] = []
    for index, page in enumerate(pages, start=1):
        ia_rows.append(
            f"| IA-{index:02d} | {page['page_type']} | {'/'.join(page['roles'])} | {page['entry']} | {page['main_task']} | {page['relation']} |"
        )

    flow_rows: list[str] = []
    if "config_workbench" in page_lookup:
        config_page = page_lookup["config_workbench"]
        flow_rows.append(
            f"| TF-01 | 模式配置与启用流程 | IA-01 | 查看当前状态 -> 配置申请方式与范围 -> 配置审批流程 -> 点击启用/编辑确认 | 命中互斥模式或在途流程时阻断并解释 | 模式成功启用或编辑完成 | 启用失败并提示原因与处理方向 |"
        )
    if "apply_page" in page_lookup:
        apply_page = page_lookup["apply_page"]
        start_ia = next((f"IA-{index + 1:02d}" for index, page in enumerate(pages) if page["archetype"] == "apply_page"), "IA-01")
        flow_rows.append(
            f"| TF-02 | 员工自助申请流程 | {start_ia} | 查看可申请范围 -> 选择权限并填写原因 -> 提交申请 | 命中敏感对象或范围限制时阻断并解释 | 进入待审批 / 已提交状态 | 提交失败并说明原因与下一步 |"
        )
    if "result_page" in page_lookup:
        result_ia = next((f"IA-{index + 1:02d}" for index, page in enumerate(pages) if page["archetype"] == "result_page"), "IA-01")
        flow_rows.append(
            f"| TF-03 | 结果回写与进度确认流程 | {result_ia} | 查看审批状态 -> 理解结果原因 -> 决定返回申请页或查看我的权限 | 审批未完成则停留处理中并解释当前进度 | 用户理解结果并继续下一步 | 把失败 / 处理中误解成黑盒结果 |"
        )
    if "detail_page" in page_lookup:
        detail_ia = next((f"IA-{index + 1:02d}" for index, page in enumerate(pages) if page["archetype"] == "detail_page"), "IA-01")
        flow_rows.append(
            f"| TF-04 | 权限自查与核对流程 | {detail_ia} | 进入我的权限 -> 切换视角 -> 查看权限明细 | 找不到来源说明时需要继续下钻解释 | 完成权限自查和结果核对 | 用户只能看到聚合结果，无法确认权限来源 |"
        )

    page_rows: list[str] = []
    for page in pages:
        page_rows.append(
            f"| {page['page_id']} | {page['name']} | {page['page_type']} | {'/'.join(page['roles'])} | {page['main_task']} | {page['entry']} | {page['exit']} | {page['relation']} |"
        )

    blueprint_blocks: list[str] = []
    for page in pages:
        action_rows = "\n".join(
            [
                f"| ACT-{page['page_id'].split('-')[-1]}-{index + 1:02d} | {item['name']} | {item['trigger']} | {item['feedback']} | {item['outcome']} | {item['protection']} |"
                for index, item in enumerate(page["actions"])
            ]
        )
        structure = page["structure"]
        focus_lines = page["focus_points"]
        blueprint_blocks.append(
            f"""### {page['page_id']} {page['name']}

#### 页面目标

- 页面目标：{page['main_task']}
- 目标用户：{'、'.join(page['roles'])}
- 进入条件：{page['entry']}
- 主任务 / 次任务：主任务是{page['main_task']}；次任务是理解规则、查看解释或返回上一层。

#### 首屏重点与关键信息

- 首屏必须理解：{focus_lines[0]}
- 决策必需信息：{focus_lines[1] if len(focus_lines) > 1 else focus_lines[0]}
- 风险提醒：{page['risk_text']}

#### 关键动作与状态

| action_id | 动作 | 触发条件 | 即时反馈 | 后续结果 | 风险保护 |
| --- | --- | --- | --- | --- | --- |
{action_rows}

#### 结构变化判断

- 页面结构语义基线：{page['baseline']}
- 本次是否涉及结构变化：{structure['changed']}
- 变化类型：{structure['type']}
- 变化说明：{structure['note']}
- 变化理由：{structure['reason']}
- 不这样做的风险：{structure['risk']}
"""
        )

    layout_blocks: list[str] = []
    for page in pages:
        layout_text = "\n".join([f"[{label}: {summary}]" for label, summary in page["layout_blocks"]])
        structure = page["structure"]
        layout_blocks.append(
            f"""### {page['page_id']} {page['name']}

```text
{layout_text}
```

- 结构变化结论：{structure['type']}
- 结构保持不变时说明：{structure['keep_note']}
"""
        )

    info_rows: list[str] = []
    info_index = 1
    for page in pages:
        for row in _info_rows_for_page(page):
            info_rows.append(
                f"| INFO-{info_index:02d} | {row['purpose']} | {row['priority']} | {row['position']} | {row['slot']} | {row['trigger']} | {row['risk']} |"
            )
            info_index += 1

    state_rows = [
        "| ST-01 | 配置中 / 可申请 | 用户进入配置页或申请页且前置条件满足 | 查看说明、选择、提交 | 展示当前状态与关键说明 | 明确当前可以继续执行 | 可进入提交或启用链路 |",
        "| ST-02 | 待审批 / 处理中 | 提交申请后等待审批或结果回写 | 查看进度、返回上一页、查看我的权限 | 结果页展示处理中状态和当前进度 | 明确“已提交，不代表已完成” | 等待审批或结果回写 |",
        "| ST-03 | 失败 / 阻断 | 命中互斥模式、范围限制或在途流程校验 | 查看原因、返回调整、联系审批人 | 展示失败状态和拦截说明 | 解释为什么失败以及如何处理 | 返回配置页或申请页继续处理 |",
        "| ST-04 | 成功完成 / 已生效 | 关键动作放行并回写成功 | 查看结果、查看我的权限、继续下一步 | 展示成功状态和结果摘要 | 明确成功影响与后续动作 | 进入稳定可交付状态 |",
    ]

    copy_rows = [
        '| COPY-01 | 配置与启用说明 | 说明文案 | 解释模式价值、边界和互斥限制 | 能做什么、为什么存在、什么时候不能启用 | 只说“更方便”不解释治理边界 | “当前模式允许员工自助申请权限，命中互斥模式时将被阻断并说明原因。” |',
        '| COPY-02 | 申请页说明 / 提交前提示 | 说明 / 提示文案 | 解释可申请范围、审批预期和敏感对象限制 | 可申请什么、谁来审批、被限制时如何处理 | 只给入口不解释规则 | “当前仅可申请允许开放的角色或功能权限，敏感对象不可申请。” |',
        '| COPY-03 | 结果 / 处理中反馈 | 状态文案 | 解释已提交、处理中、已生效、失败这几种状态差异 | 当前状态、原因、下一步、去哪里看结果 | 把处理中写成已完成 | “已提交，审批通过后系统将自动分配权限。” |',
    ]

    risk_rows = [
        f"| RSK-01 | 把治理限制误解成系统异常 | 配置启用失败或申请提交被阻断 | 只看到了失败，没有理解规则原因 | 在 {pages[0]['page_id'] if pages else 'P-01'} 的前置说明和结果页中显式解释限制与处理方向 | {'、'.join([page['page_id'] for page in pages[:2]]) if pages else 'P-01'}、COPY-01、COPY-03 |",
        f"| RSK-02 | 把已提交误解成已生效 | 提交申请后进入处理中 | 用户不了解审批与回写时点 | 在结果页显式说明“已提交 / 待审批 / 已生效”的差异 | {next((page['page_id'] for page in pages if page['archetype'] == 'result_page'), 'P-01')}、ST-02、COPY-03 |",
    ]

    trace_rows: list[str] = []
    for index, page in enumerate(pages, start=1):
        trace_rows.append(
            f"| TR-{index:02d} | {page['page_id']} / {page['name']} / {page['layout_blocks'][0][0]} | J-01、POS-02 | F-07、F-09、F-10、EX-01、EX-02 | PR-01、PR-02、PR-03 | 该页由任务命中页面与 Wiki 页面结构语义共同推导生成 |"
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

- 承接业务立场：POS-01、POS-02、J-01、J-02、J-03、J-04、J-05、J-06、J-07、J-08、J-09。
- 承接规则：F-05、F-06、F-07、F-08、F-09、F-10、F-11、F-12、R-01、R-02、EX-01、EX-02。
- 承接风险：RSK-01、AP-01。
- 页面结构语义输入：已消费权限域 Wiki 中保留的页面结构语义，用于判断当前需求是结构变化还是结构不变，并决定信息进入 Header、Step、Main、Side、Footer 还是 Alert / Info 区。

### 已命中的设计原则

- 原则 PR-01：状态可见，状态切换和结果反馈必须被用户看见并理解。
- 原则 PR-02：先结论后细节，先让用户知道能不能做、结果是什么，再决定是否展开原因和规则。
- 原则 PR-03：风险前置解释，治理限制和失败原因需要在关键动作前后明确解释。
- 命中的页面集合：{"、".join([f"{page['page_id']} {page['name']}" for page in pages])}

| principle_id | 原则名称 | 命中原因 | 作用位置 |
| --- | --- | --- | --- |
| PR-01 | 状态可见 | 状态切换和结果反馈必须被用户看见并理解 | {pages[0]['page_id'] if pages else 'P-01'}、ST-01~ST-04 |
| PR-02 | 先结论后细节 | 用户先要知道能不能做、结果是什么，再看原因和规则 | {pages[0]['page_id'] if pages else 'P-01'}、COPY-01~COPY-03 |
| PR-03 | 风险前置解释 | 治理限制和失败原因需要在关键动作前后明确解释 | {next((page['page_id'] for page in pages if page['archetype'] == 'result_page'), pages[0]['page_id'] if pages else 'P-01')}、RSK-01 |

## 信息架构总览

### 入口与承载关系

| ia_node | 类型 | 面向角色 | 入口 | 承接对象 / 主任务 | 与其他节点关系 |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(ia_rows)}

### 信息架构文本图

```text
任务主入口
├── 配置与治理页面
├── 员工申请与自查页面
├── 关键范围选择弹窗
└── 结果 / 进度 / 明细解释页面
```

## 任务流蓝图

### 关键流程总览

```text
进入主入口
-> 识别当前是配置治理还是员工申请
-> 在命中页面内完成主任务与规则判断
-> 提交 / 启用 / 查看结果
-> 命中规则冲突 ? 阻断并解释 : 进入结果或明细确认
```

### 流程明细

| flow_id | 流程名称 | 起点 | 关键步骤 | 关键判断 / 阻断 | 成功结果 | 失败 / 异常结果 |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(flow_rows)}

## 页面 / 窗口清单

| page_id | 名称 | 类型 | 目标用户 | 主任务 | 入口 | 退出方式 | 上下游关系 |
| --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(page_rows)}

## 关键页面蓝图

{chr(10).join(blueprint_blocks)}

## 区块布局示意

{chr(10).join(layout_blocks)}

## 内容与信息优先级合同

| info_item | 信息目的 | 优先级 | 推荐位置 | 结构落位 | 触发时机 | 不展示风险 |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(info_rows)}

## 状态与反馈矩阵

| state_id | 状态名称 | 触发条件 | 可用动作 | 页面反馈 | 文案反馈 | 下游结果 |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(state_rows)}

## 文案合同

| copy_id | 场景 | 文案类型 | 语义目标 | 必含信息 | 禁止写法 | 示例方向 |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(copy_rows)}

## 风险、疑惑点与保护策略

| risk_id | 风险 / 疑惑点 | 触发场景 | 用户为什么会困惑 / 出错 | 保护策略 | 对应页面 / 流程 / 文案 |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(risk_rows)}

## 开放问题与缺口

- OQ-01: 外部依赖的最终配置和维护口径仍待确认。
- OQ-02: 更细的异常分类和文案规范后续是否要继续拆分，仍待确认。
- GAP-01: 当前输入对帮助说明和部分外部协作细节描述不足。
- GAP-02: 当前输入没有完全覆盖所有结果细化口径，后续体验细化需要补充。

## 体验追踪映射

| trace_id | 页面 / 流程 / 文案对象 | 承接业务判断 | 承接事实 / 规则 / 异常 | 承接原则 | 说明 |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(trace_rows)}
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
