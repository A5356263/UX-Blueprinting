from __future__ import annotations

import re
from pathlib import Path

from packages.common import get_project_runtime_dir, get_project_source_dir, get_project_workspace_dir, get_repo_root
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
        ("管理员", "管理者"),
        ("员工", "员工"),
        ("审批", "处理人"),
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
        ("角色", "角色"),
        ("应用", "应用"),
        ("配置", "关键配置"),
        ("范围", "范围对象"),
        ("详情", "明细对象"),
        ("结果", "结果状态"),
        ("审批", "处理流程"),
        ("记录", "申请记录"),
        ("帮助", "帮助说明"),
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
        if "page" not in lowered and "structure" not in lowered and "carrier" not in lowered and "index" not in lowered:
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
    if any(keyword in joined for keyword in ["新增说明", "风险提示", "帮助文档", "了解更多", "步骤", "处理流程", "模式", "入口", "通知"]):
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
    dependency_line = _pick(lines, "协作", "当前能力依赖外部处理流程、帮助说明或关键对象配置能力协同完成。")

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
| A-02 | {roles[1] if len(roles) > 1 else "用户"} | 发起方/使用方 | 负责发起动作、查看结果或承接反馈 | requirement.md |
| A-03 | {roles[2] if len(roles) > 2 else "系统"} | 处理方/协作方 | 负责处理、回写状态或提供系统反馈 | requirement.md |

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
| FL-01 | {roles[0]} | 配置或启用核心能力 | 已进入主任务并具备管理条件 | 形成可被执行侧使用的能力边界 | 承接配置与治理责任 | F-07 |
| FL-02 | {roles[1] if len(roles) > 1 else "用户"} | 发起主动作并等待结果 | 能力已开放、范围允许、依赖可用 | 进入成功结果或失败解释链路 | 需要有清晰反馈 | F-08 |

## 异常与拦截清单

| exception_id | 场景 | 触发条件 | 系统结果 / 提示 | 影响对象 | source_ref |
|---|---|---|---|---|---|
| EX-01 | 前置规则冲突 | 命中互斥规则、范围外限制或治理冲突 | 阻断继续执行并给出原因与处理方向 | 使用方 / 管理方 | F-09 |
| EX-02 | 依赖未就绪或结果失败 | 外部依赖未完成、协作处理未完成或处理失败 | 保留当前状态并提示如何补救 | 使用方 | F-11 |

## 依赖清单

| dependency_id | 依赖项 | 类型 | 当前作用 | 当前确认度 | source_ref |
|---|---|---|---|---|---|
| DEP-01 | 处理或协作流程 | 流程引擎 / 协作链路 | 决定动作是否放行以及结果如何回写 | 部分确认 | F-13 |
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

- BL-03: 当前能力本质上属于“治理 + 执行 + 结果解释”的组合能力。
- BL-04: 责任、处理、生效、范围和审计逻辑必须在链路中显式可见。

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
| J-05 | 处理 / 生效逻辑 | 一致 | F-06、F-10、F-13 | 若无结果回写与追溯，能力无法稳定交付 | 外部依赖细节仍待补足 |
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
    bundle_dir = runtime_dir / "context_bundle" / "knowledge" / "wiki"
    catalog: dict[str, dict[str, object]] = {}
    if not bundle_dir.exists():
        return []

    for path in sorted(bundle_dir.rglob("*.md")):
        text = _read_text(path)
        if not text:
            continue
        metadata = _parse_metadata(text)
        blocks = _split_heading_blocks(text, HEADING_L3_RE)
        canonical_name = metadata.get("canonical_name") or metadata.get("对象名称") or metadata.get("专题名称") or path.stem
        aliases = _parse_inline_list(metadata.get("aliases", ""))

        baseline_parts: list[str] = []
        layout_lines: list[str] = []
        for heading, body in blocks.items():
            if "结构语义摘要" in heading or "骨架结构" in heading:
                bullet_lines = _parse_bullet_lines(body)
                for bullet in bullet_lines:
                    if "：" in bullet:
                        name, baseline = bullet.split("：", 1)
                        _merge_catalog_entry(catalog, name.strip(), baseline=baseline.strip(), aliases=[canonical_name] + aliases)
                    else:
                        baseline_parts.append(bullet)
            if "原始区块关系图保留" in heading:
                layout_lines.extend([line.strip() for line in _extract_code_block(body).splitlines() if line.strip()])

        if baseline_parts or layout_lines:
            _merge_catalog_entry(catalog, canonical_name, baseline=" ".join(baseline_parts), layout_lines=layout_lines, aliases=aliases)

    return list(catalog.values())


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
            "Step": "关键步骤 / 范围 / 处理流程",
            "Alert": "模式互斥规则 / 前置限制 / 风险提醒",
            "Main": "配置表单 + 范围设置 + 启用动作",
            "Side": "规则解释 / 帮助说明 / 协作配置说明",
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
            "Intro": "主动作目标说明 / 能做什么 / 提交后预期",
            "Alert": "范围限制 / 前置条件 / 风险提醒",
            "Main": "关键对象选择 + 必要信息填写 + 提交动作",
            "Side": "规则解释 / 帮助文档 / 追溯入口",
            "Footer": "取消 / 提交主动作 / 查看当前结果",
        }
    if archetype == "detail_page":
        return {
            "Header": "当前对象 + 身份标签 + 返回入口",
            "Info": "解释说明 / 当前上下文 / 来源说明",
            "Tab": "身份 / 终端 / 分类维度切换",
            "Menu": "模块导航 / 目录切换",
            "Main": "明细构成 / 查询结果 / 解释内容",
            "Footer": "关闭 / 返回",
        }
    return {
        "Header": "当前结果 + 状态标签",
        "Summary": "处理结论 / 生效结果 / 处理中状态",
        "Info": "原因说明 + 下一步 + 通知解释",
        "Main": "处理记录 / 协作轨迹 / 结果变化详情",
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
        note = f"{page_name} 需要把关键配置与处理流程分成可理解的阶段，因此要补出 Step 级结构，而不是把所有设置压在单一主区。"
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


def _info_rows_for_page(page: dict[str, object]) -> list[dict[str, str]]:
    page_id = str(page["page_id"])
    page_name = str(page["name"])
    archetype = str(page["archetype"])
    if archetype == "config_workbench":
        return [
            {
                "purpose": "当前配置状态与可执行性",
                "priority": "高",
                "position": f"{page_id} Header / Alert",
                "slot": "Header / Alert",
                "trigger": "进入页、点击确认前",
                "risk": "用户无法判断当前配置是否可继续，容易把前置限制误判为系统异常。",
            },
            {
                "purpose": "关键步骤、范围与协作配置",
                "priority": "高",
                "position": f"{page_id} Step / Main",
                "slot": "Step / Main",
                "trigger": "配置过程中",
                "risk": "用户难以理解配置顺序，后续执行边界会不清楚。",
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
                "purpose": f"{page_name} 的可执行范围与规则解释",
                "priority": "高",
                "position": f"{page_id} Intro / Alert",
                "slot": "Intro / Alert",
                "trigger": "进入页、提交前",
                "risk": "用户不知道当前能执行什么、为什么被限制，容易误解主链路。",
            },
            {
                "purpose": "关键对象、必要信息与提交动作",
                "priority": "高",
                "position": f"{page_id} Main / Footer",
                "slot": "Main / Footer",
                "trigger": "填写并提交时",
                "risk": "主任务入口不清晰，用户无法完成当前动作。",
            },
        ]
    if archetype == "detail_page":
        return [
            {
                "purpose": f"{page_name} 的明细解释与来源说明",
                "priority": "高",
                "position": f"{page_id} Info / Tab / Main",
                "slot": "Info / Tab / Main",
                "trigger": "进入页、切换视角时",
                "risk": "用户只能看到聚合结果，无法完成结果核对和来源理解。",
            }
        ]
    return [
        {
            "purpose": f"{page_name} 的结果结论与下一步",
            "priority": "高",
            "position": f"{page_id} Summary / Info / Footer",
            "slot": "Summary / Info / Footer",
            "trigger": "提交后、收到通知后",
            "risk": "用户不知道当前是否完成、为何失败以及接下来该做什么。",
        }
    ]


def _parse_metadata(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, value = stripped[2:].split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def _parse_inline_list(value: str) -> list[str]:
    value = value.strip()
    if not value.startswith("[") or not value.endswith("]"):
        return []
    return [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]


def _normalize_lines_from_text(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip(" -\t")
        if len(line) < 2:
            continue
        lines.append(line)
    return lines


def _extract_backticked_terms(text: str) -> list[str]:
    terms: list[str] = []
    for term in re.findall(r"`([^`]+)`", text):
        cleaned = term.strip()
        if not cleaned or "/" in cleaned or ".md" in cleaned:
            continue
        terms.append(cleaned)
    return _dedupe_strings(terms)


def _infer_view_type_from_text(name: str, text: str) -> str:
    lowered = f"{name} {text}".lower()
    if "抽屉" in lowered or "drawer" in lowered:
        return "抽屉"
    if "弹窗" in lowered or "弹层" in lowered or "modal" in lowered or "dialog" in lowered:
        return "弹窗"
    if "子页面" in lowered or "subpage" in lowered:
        return "子页面"
    return "页面"


def _merge_page_candidate(
    catalog: dict[str, dict[str, object]],
    name: str,
    *,
    aliases: list[str] | None = None,
    page_type: str = "",
    summary: str = "",
    baseline: str = "",
    layout_lines: list[str] | None = None,
    roles: list[str] | None = None,
    objects: list[str] | None = None,
    relations: list[str] | None = None,
    source_ref: str = "",
) -> None:
    key = _normalize_name(name)
    existing = catalog.get(
        key,
        {
            "canonical_name": name,
            "aliases": [],
            "page_type": page_type or "页面",
            "summary": "",
            "baseline": "",
            "layout_lines": [],
            "zones": [],
            "roles": [],
            "objects": [],
            "relations": [],
            "source_refs": [],
        },
    )
    baseline_text = baseline.strip() or str(existing.get("baseline", "")).strip()
    merged_layout_lines = list(existing.get("layout_lines", [])) + list(layout_lines or [])
    zones = _extract_zone_tokens(([baseline_text] if baseline_text else []) + merged_layout_lines)
    existing["canonical_name"] = name
    existing["aliases"] = _dedupe_strings([name] + list(existing.get("aliases", [])) + list(aliases or []))
    existing["page_type"] = page_type or str(existing.get("page_type", "") or "页面")
    existing["summary"] = summary.strip() or str(existing.get("summary", "")).strip()
    existing["baseline"] = baseline_text
    existing["layout_lines"] = _dedupe_strings([str(item) for item in merged_layout_lines])
    existing["zones"] = zones
    existing["roles"] = _dedupe_strings([str(item) for item in list(existing.get("roles", [])) + list(roles or [])])
    existing["objects"] = _dedupe_strings([str(item) for item in list(existing.get("objects", [])) + list(objects or [])])
    existing["relations"] = _dedupe_strings([str(item) for item in list(existing.get("relations", [])) + list(relations or [])])
    if source_ref:
        existing["source_refs"] = _dedupe_strings([str(item) for item in list(existing.get("source_refs", [])) + [source_ref]])
    catalog[key] = existing


def _build_page_candidates(project_id: str) -> list[dict[str, object]]:
    runtime_dir = get_project_runtime_dir(project_id)
    bundle_dir = runtime_dir / "context_bundle" / "knowledge" / "wiki"
    catalog: dict[str, dict[str, object]] = {}

    for item in _build_structure_catalog(project_id):
        _merge_page_candidate(
            catalog,
            str(item.get("canonical_name", "")),
            aliases=[str(alias) for alias in item.get("aliases", [])],
            baseline=str(item.get("baseline", "")),
            layout_lines=[str(line) for line in item.get("layout_lines", [])],
            page_type=_infer_view_type_from_text(str(item.get("canonical_name", "")), str(item.get("baseline", ""))),
            source_ref="context_bundle/knowledge/wiki/topics/page-structure-catalog",
        )

    if not bundle_dir.exists():
        return list(catalog.values())

    for path in sorted(bundle_dir.rglob("*.md")):
        repo_rel = str(path.relative_to(get_repo_root())).replace("\\", "/")
        if any(skip in repo_rel for skip in ["/log.md", "/overview.md", "/templates/", "/archive/"]):
            continue
        text = _read_text(path)
        if not text:
            continue
        metadata = _parse_metadata(text)
        page_type_meta = metadata.get("page_type", "")
        if any(skip in page_type_meta.lower() for skip in ["template", "archive"]):
            continue

        blocks = _split_heading_blocks(text, HEADING_L3_RE)
        heading_text = " ".join(blocks.keys())
        canonical_name = (
            metadata.get("canonical_name")
            or metadata.get("对象名称")
            or metadata.get("专题名称")
            or _extract_backticked_terms(text)[:1][0] if _extract_backticked_terms(text) else path.stem
        )
        aliases = _parse_inline_list(metadata.get("aliases", ""))
        roles = _extract_roles(_normalize_lines_from_text(text))
        relations = _extract_backticked_terms(text)
        summary_candidates = []
        for heading, body in blocks.items():
            if any(marker in heading for marker in ["对象职责", "页面职责骨架", "专题目标", "结构分解", "当前结论", "结论"]):
                summary_candidates.extend(_parse_bullet_lines(body))
        summary = " ".join(summary_candidates[:2]) if summary_candidates else ""

        baseline_parts: list[str] = []
        layout_lines: list[str] = []
        for heading, body in blocks.items():
            if "结构语义摘要" in heading:
                baseline_parts.extend(_parse_bullet_lines(body))
            if "原始区块关系图保留" in heading:
                layout_lines.extend([line.strip() for line in _extract_code_block(body).splitlines() if line.strip()])
            if "骨架结构" in heading and not baseline_parts:
                baseline_parts.extend(_parse_bullet_lines(body))

        objects = []
        for term in [canonical_name] + relations:
            if len(term) >= 2:
                objects.append(term)

        if metadata.get("page_type", "").lower() == "entity":
            _merge_page_candidate(
                catalog,
                canonical_name,
                aliases=aliases,
                page_type=_infer_view_type_from_text(canonical_name, text),
                summary=summary,
                baseline=" ".join(baseline_parts),
                layout_lines=layout_lines,
                roles=roles,
                objects=objects,
                relations=relations,
                source_ref=repo_rel,
            )

        for term in relations:
            _merge_page_candidate(
                catalog,
                term,
                page_type=_infer_view_type_from_text(term, text),
                summary=summary,
                roles=roles,
                relations=[canonical_name],
                source_ref=repo_rel,
            )

    return list(catalog.values())


def _detect_interaction_signals(lines: list[str], facts_text: str, business_text: str) -> dict[str, object]:
    joined = "\n".join(lines + [facts_text, business_text])
    return {
        "joined": joined,
        "needs_configuration": any(keyword in joined for keyword in ["设置", "配置", "启用", "编辑", "关闭", "修改", "模式"]),
        "needs_selection_overlay": any(keyword in joined for keyword in ["弹窗", "弹层", "抽屉", "选择", "搜索", "分页", "部分"]),
        "needs_submission": any(keyword in joined for keyword in ["申请", "发起", "提交", "填写", "原因", "确认"]),
        "needs_detail": any(keyword in joined for keyword in ["详情", "明细", "查询", "清单", "核对", "查看"]),
        "needs_result": any(keyword in joined for keyword in ["结果", "通知", "成功", "失败", "处理中", "状态", "生效", "回写"]),
        "has_help_doc": any(keyword in joined for keyword in ["帮助", "了解更多", "说明", "提示", "文档"]),
        "has_risk_rules": any(keyword in joined for keyword in ["不能", "限制", "失败", "冲突", "阻断", "校验", "不可"]),
        "has_steps": any(keyword in joined for keyword in ["第一步", "第二步", "第三步", "步骤", "流程"]),
    }


def _score_candidate(
    candidate: dict[str, object],
    source_text: str,
    source_roles: list[str],
    signals: dict[str, object],
) -> tuple[int, list[str]]:
    aliases = [str(candidate.get("canonical_name", ""))] + [str(item) for item in candidate.get("aliases", [])]
    objects = [str(item) for item in candidate.get("objects", [])]
    relations = [str(item) for item in candidate.get("relations", [])]
    summary = str(candidate.get("summary", ""))
    zones = [str(item) for item in candidate.get("zones", [])]
    candidate_roles = [str(item) for item in candidate.get("roles", [])]

    score = 0
    evidence: list[str] = []

    alias_hits = [alias for alias in aliases if len(alias) >= 2 and alias in source_text]
    if alias_hits:
        score += len(alias_hits) * 4
        evidence.append(f"别名命中:{'、'.join(alias_hits[:3])}")

    object_hits = [item for item in objects if len(item) >= 2 and item in source_text]
    if object_hits:
        score += len(object_hits) * 3
        evidence.append(f"承载对象命中:{'、'.join(object_hits[:3])}")

    summary_tokens = [token.strip() for token in re.split(r"[、，,；;。:：/（）()\s]+", summary) if 2 <= len(token.strip()) <= 12]
    summary_hits = [token for token in summary_tokens if token in source_text]
    if summary_hits:
        score += min(len(summary_hits), 3) * 2
        evidence.append(f"主任务命中:{'、'.join(summary_hits[:3])}")

    role_hits = [role for role in candidate_roles if role in source_roles]
    if role_hits:
        score += len(role_hits) * 2
        evidence.append(f"角色命中:{'、'.join(role_hits)}")

    relation_hits = [item for item in relations if len(item) >= 2 and item in source_text]
    if relation_hits:
        score += len(relation_hits)
        evidence.append(f"上下游命中:{'、'.join(relation_hits[:3])}")

    if signals.get("needs_selection_overlay") and str(candidate.get("page_type")) in {"弹窗", "抽屉"}:
        score += 2
        evidence.append("页面类型命中:选择层")
    if signals.get("needs_configuration") and any(zone in zones for zone in ["Step", "Filter", "Action"]):
        score += 2
        evidence.append("结构语义命中:配置链路")
    if signals.get("needs_result") and any(zone in zones for zone in ["Summary", "Info", "Footer"]):
        score += 2
        evidence.append("结构语义命中:结果解释")
    if signals.get("needs_detail") and any(zone in zones for zone in ["Tab", "Menu", "Main"]):
        score += 1
        evidence.append("结构语义命中:详情/明细")
    if signals.get("has_risk_rules") and any(zone in zones for zone in ["Alert", "Info"]):
        score += 1
        evidence.append("事实规则命中:限制解释")

    return score, evidence


def _infer_archetype_for_candidate(candidate: dict[str, object], signals: dict[str, object]) -> str:
    page_type = str(candidate.get("page_type", "页面"))
    name = str(candidate.get("canonical_name", ""))
    summary = str(candidate.get("summary", ""))
    zones = [str(item) for item in candidate.get("zones", [])]
    combined = f"{name} {summary}"
    if page_type in {"弹窗", "抽屉"}:
        return "selection_dialog"
    if "Summary" in zones or ("结果" in combined and signals.get("needs_result")):
        return "result_page"
    if any(token in combined for token in ["详情", "明细", "查询", "核对"]) or ("Tab" in zones and "Menu" in zones):
        return "detail_page"
    if any(zone in zones for zone in ["Step", "Filter", "Action"]):
        return "config_workbench"
    if signals.get("needs_submission"):
        return "apply_page"
    return "detail_page" if signals.get("needs_detail") else "apply_page"


def _is_usable_page_name(name: str) -> bool:
    cleaned = name.strip()
    if not cleaned or len(cleaned) < 2 or len(cleaned) > 24:
        return False
    allowed_markers = ["页", "层", "弹窗", "抽屉", "详情", "结果", "查询", "设置", "配置", "入口", "清单", "明细", "状态", "方式"]
    forbidden_markers = [
        ".md",
        "README",
        "overview",
        "domain",
        "管理后台-",
        "http",
        "LOG-",
        "SRC-",
        "topic",
        "index",
        "专题",
        "索引",
        "尝试给",
        "不会推",
        "提升空间",
        "如其他",
        "客户使用",
        "企业场景",
        "当前有",
    ]
    if any(marker.lower() in cleaned.lower() for marker in forbidden_markers):
        return False
    if not any(marker in cleaned for marker in allowed_markers) and len(cleaned) > 8:
        return False
    if cleaned.count("，") >= 1 or cleaned.count(",") >= 1:
        return False
    return True


def _derive_page_name(lines: list[str], keywords: list[str], fallback: str) -> str:
    for line in lines:
        if not any(keyword in line for keyword in keywords):
            continue
        cleaned = line.strip()
        if "：" in cleaned:
            tail = cleaned.split("：")[-1].strip()
            if 2 <= len(tail) <= 20:
                cleaned = tail
        cleaned = re.sub(r"^[A-Za-z0-9一二三四五六七八九十.、（）()：: ]+", "", cleaned).strip()
        cleaned = cleaned.replace("点击", "").replace("需要", "").replace("支持", "").replace("用户可", "").strip()
        cleaned = re.split(r"[，,。；;]", cleaned)[0].strip()
        if _is_usable_page_name(cleaned):
            return cleaned
    return fallback


def _build_generic_page_from_candidate(
    archetype: str,
    candidate: dict[str, object] | None,
    lines: list[str],
    source_roles: list[str],
    signals: dict[str, object],
) -> dict[str, object]:
    candidate = candidate or {}
    candidate_name = str(candidate.get("canonical_name", "")).strip()
    usable_candidate_name = candidate_name if _is_usable_page_name(candidate_name) else ""
    baseline = str(candidate.get("baseline", "")).strip()
    relations = [str(item) for item in candidate.get("relations", [])]
    roles = [str(item) for item in candidate.get("roles", [])] or source_roles[:3] or ["使用方", "管理方", "协作方"]
    page_type = str(candidate.get("page_type", "") or ("弹窗" if archetype == "selection_dialog" else "页面"))

    name_map = {
        "config_workbench": _derive_page_name(lines, ["设置", "配置", "启用", "编辑", "关闭"], usable_candidate_name or "主配置与治理页"),
        "selection_dialog": _derive_page_name(lines, ["弹窗", "弹层", "抽屉", "选择", "搜索"], usable_candidate_name or "关键对象选择层"),
        "apply_page": _derive_page_name(lines, ["申请", "提交", "发起", "填写"], usable_candidate_name or "主提交与发起页"),
        "detail_page": _derive_page_name(lines, ["详情", "明细", "查询", "核对", "清单"], usable_candidate_name or "详情与核对页"),
        "result_page": _derive_page_name(lines, ["结果", "通知", "失败", "成功", "处理中", "状态"], usable_candidate_name or "结果与状态页"),
    }
    task_map = {
        "config_workbench": "完成关键配置、确认生效条件并决定是否提交治理动作。",
        "selection_dialog": "在不离开当前上下文的情况下完成关键对象或范围选择。",
        "apply_page": "完成主对象选择、填写必要信息并发起核心动作。",
        "detail_page": "查看当前结果、来源、明细和解释信息，完成核对。",
        "result_page": "确认当前状态、失败原因或后续动作，完成结果理解。",
    }
    focus_map = {
        "config_workbench": [
            "当前配置是否可继续、需要满足哪些前置条件",
            "关键步骤、范围边界和确认动作会如何影响后续结果",
            "命中失败或冲突时系统会如何解释",
        ],
        "selection_dialog": [
            "当前在选择什么、允许范围是什么",
            "哪些对象不可选、为什么不可选",
            "确认后会回填到哪里以及是否保留上下文",
        ],
        "apply_page": [
            "当前能做什么、需要补什么信息",
            "提交后会发生什么、谁来继续处理",
            "命中限制时系统会如何阻断并解释",
        ],
        "detail_page": [
            "当前对象是什么、明细或结果来源是什么",
            "哪些视角可以切换、应该先看哪部分内容",
            "若需要进一步追溯，应从哪里继续查看",
        ],
        "result_page": [
            "当前状态是什么、是否已经完成",
            "为什么成功、失败或仍在处理中",
            "接下来该返回哪里或继续做什么",
        ],
    }
    actions_map = {
        "config_workbench": [
            {
                "name": "查看并调整关键配置",
                "trigger": "进入页面后即可操作",
                "feedback": "步骤区与主配置区同步刷新当前选择结果",
                "outcome": "形成可被后续执行或提交的配置方案",
                "protection": "命中前置限制时即时解释原因",
            },
            {
                "name": "提交配置或确认变更",
                "trigger": "满足前置条件后可点击",
                "feedback": "先校验规则，再给出成功或失败反馈",
                "outcome": "进入已生效、已保存或后续处理状态",
                "protection": "失败时必须解释原因和下一步",
            },
        ],
        "selection_dialog": [
            {
                "name": "选择并确认对象",
                "trigger": "打开选择层后即可操作",
                "feedback": "搜索结果、选择状态和已选信息即时变化",
                "outcome": "形成回填到上层页面的结果",
                "protection": "对不可选对象即时解释原因",
            }
        ],
        "apply_page": [
            {
                "name": "填写必要信息并发起动作",
                "trigger": "进入页面后即可操作",
                "feedback": "主区和提示区同步刷新当前可执行状态",
                "outcome": "形成可提交的动作对象",
                "protection": "提交前必须明确限制和预期结果",
            }
        ],
        "detail_page": [
            {
                "name": "切换视角并查看明细",
                "trigger": "进入页面后即可操作",
                "feedback": "导航、标签和主体内容同步切换",
                "outcome": "完成明细查看与来源解释",
                "protection": "保持当前对象与上下文可见",
            }
        ],
        "result_page": [
            {
                "name": "查看状态与后续动作",
                "trigger": "产生结果后即可进入",
                "feedback": "状态、原因和下一步同步展示",
                "outcome": "用户理解当前结果并继续处理",
                "protection": "失败与处理中必须明确区分",
            }
        ],
    }
    entry_map = {
        "config_workbench": "从主入口或治理入口进入。",
        "selection_dialog": "从上层页面的关键选择动作进入。",
        "apply_page": "从主入口、任务入口或当前流程入口进入。",
        "detail_page": "从结果页、查询页或当前对象入口进入。",
        "result_page": "在提交、处理或状态回写后进入。",
    }
    exit_map = {
        "config_workbench": "返回上一页或提交后停留当前链路。",
        "selection_dialog": "确认后回填上层页面，或关闭返回。",
        "apply_page": "提交后进入结果链路，或取消返回上一入口。",
        "detail_page": "关闭或返回上一层，不承担新的提交动作。",
        "result_page": "返回上一页、返回入口或结束当前链路。",
    }

    relation_text = "；".join(relations[:3]) if relations else "由任务上下文命中，可与相邻页面形成前后链路。"
    return _build_page_plan(
        archetype,
        name_map[archetype],
        page_type,
        roles,
        task_map[archetype],
        entry_map[archetype],
        exit_map[archetype],
        relation_text,
        focus_map[archetype],
        "若关键解释、限制条件或结果状态没有在合适区块显性表达，用户会误解主任务边界或下一步。",
        actions_map[archetype],
        candidate,
        signals,
    )


def _identify_impacted_pages_generalized(project_id: str, lines: list[str], facts_text: str, business_text: str) -> list[dict[str, object]]:
    candidates = _build_page_candidates(project_id)
    signals = _detect_interaction_signals(lines, facts_text, business_text)
    source_text = str(signals["joined"])
    source_roles = _extract_roles(_normalize_lines_from_text(source_text))

    scored: list[dict[str, object]] = []
    for candidate in candidates:
        score, evidence = _score_candidate(candidate, source_text, source_roles, signals)
        if score <= 0:
            continue
        item = dict(candidate)
        item["score"] = score
        item["evidence"] = evidence
        item["archetype"] = _infer_archetype_for_candidate(candidate, signals)
        scored.append(item)

    scored.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    selected: list[dict[str, object]] = []
    used_archetypes: set[str] = set()
    for item in scored:
        archetype = str(item.get("archetype", ""))
        if archetype in used_archetypes:
            continue
        if int(item.get("score", 0)) < 3:
            continue
        selected.append(_build_generic_page_from_candidate(archetype, item, lines, source_roles, signals))
        used_archetypes.add(archetype)

    required_archetypes: list[str] = []
    if signals.get("needs_configuration"):
        required_archetypes.append("config_workbench")
    if signals.get("needs_selection_overlay"):
        required_archetypes.append("selection_dialog")
    if signals.get("needs_submission"):
        required_archetypes.append("apply_page")
    if signals.get("needs_detail"):
        required_archetypes.append("detail_page")
    if signals.get("needs_result"):
        required_archetypes.append("result_page")
    if not required_archetypes:
        required_archetypes = ["apply_page", "result_page"]

    for archetype in required_archetypes:
        if archetype in used_archetypes:
            continue
        best_candidate = next((item for item in scored if str(item.get("archetype")) == archetype), None)
        selected.append(_build_generic_page_from_candidate(archetype, best_candidate, lines, source_roles, signals))
        used_archetypes.add(archetype)

    return selected


def _render_experience(project_id: str) -> str:
    lines = _extract_source_lines(project_id)
    facts_text = _read_workspace_text(project_id, "facts.md")
    business_text = _read_workspace_text(project_id, "business_blueprint.md")
    goal_line = _pick(lines, "提升", "让用户更容易理解当前能力何时可用、如何执行、何时成功以及为什么失败。")
    pages = _identify_impacted_pages_generalized(project_id, lines, facts_text, business_text)
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
        flow_rows.append(
            "| TF-01 | 配置与治理流程 | IA-01 | 查看当前状态 -> 调整关键配置 -> 提交或确认变更 | 命中前置规则或冲突条件时阻断并解释 | 配置成功生效或进入后续处理 | 配置失败并提示原因与处理方向 |"
        )
    if "apply_page" in page_lookup:
        start_ia = next((f"IA-{index + 1:02d}" for index, page in enumerate(pages) if page["archetype"] == "apply_page"), "IA-01")
        flow_rows.append(
            f"| TF-02 | 主动作发起流程 | {start_ia} | 查看当前范围 -> 选择对象并填写必要信息 -> 提交主动作 | 命中范围限制或前置规则时阻断并解释 | 进入已提交 / 待处理状态 | 提交失败并说明原因与下一步 |"
        )
    if "result_page" in page_lookup:
        result_ia = next((f"IA-{index + 1:02d}" for index, page in enumerate(pages) if page["archetype"] == "result_page"), "IA-01")
        flow_rows.append(
            f"| TF-03 | 结果回写与进度确认流程 | {result_ia} | 查看当前状态 -> 理解结果原因 -> 决定返回上一层或继续下一步 | 处理未完成则停留处理中并解释当前进度 | 用户理解结果并继续下一步 | 把失败 / 处理中误解成黑盒结果 |"
        )
    if "detail_page" in page_lookup:
        detail_ia = next((f"IA-{index + 1:02d}" for index, page in enumerate(pages) if page["archetype"] == "detail_page"), "IA-01")
        flow_rows.append(
            f"| TF-04 | 详情查看与结果核对流程 | {detail_ia} | 进入详情入口 -> 切换视角 -> 查看明细与来源解释 | 找不到来源说明时需要继续下钻解释 | 完成明细查看和结果核对 | 用户只能看到聚合结果，无法确认来源 |"
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
        "| ST-01 | 配置中 / 可执行 | 用户进入主页面且前置条件满足 | 查看说明、选择、提交 | 展示当前状态与关键说明 | 明确当前可以继续执行 | 可进入提交或确认链路 |",
        "| ST-02 | 已提交 / 处理中 | 提交主动作后等待处理或结果回写 | 查看进度、返回上一页、查看详情 | 结果页展示处理中状态和当前进度 | 明确“已提交，不代表已完成” | 等待处理完成或结果回写 |",
        "| ST-03 | 失败 / 阻断 | 命中前置规则、范围限制或冲突校验 | 查看原因、返回调整、联系协作方 | 展示失败状态和拦截说明 | 解释为什么失败以及如何处理 | 返回上一页继续处理 |",
        "| ST-04 | 成功完成 / 已生效 | 关键动作放行并回写成功 | 查看结果、查看详情、继续下一步 | 展示成功状态和结果摘要 | 明确成功影响与后续动作 | 进入稳定可交付状态 |",
    ]

    copy_rows = [
        '| COPY-01 | 配置与入口说明 | 说明文案 | 解释当前能力价值、边界和前置限制 | 能做什么、为什么存在、什么时候不能继续 | 只说“更方便”不解释边界 | “当前能力用于……，命中限制时会被阻断并说明原因。” |',
        '| COPY-02 | 主动作说明 / 提交前提示 | 说明 / 提示文案 | 解释可执行范围、处理预期和限制条件 | 当前能做什么、处理链路是什么、被限制时如何处理 | 只给入口不解释规则 | “当前仅在满足范围和前置条件时可继续执行，失败会说明原因。” |',
        '| COPY-03 | 结果 / 处理中反馈 | 状态文案 | 解释已提交、处理中、已完成、失败这几种状态差异 | 当前状态、原因、下一步、去哪里看结果 | 把处理中写成已完成 | “已提交，处理完成后可在结果页查看最终状态。” |',
    ]

    risk_rows = [
        f"| RSK-01 | 把治理限制误解成系统异常 | 配置启用失败或主动作提交被阻断 | 只看到了失败，没有理解规则原因 | 在 {pages[0]['page_id'] if pages else 'P-01'} 的前置说明和结果页中显式解释限制与处理方向 | {'、'.join([page['page_id'] for page in pages[:2]]) if pages else 'P-01'}、COPY-01、COPY-03 |",
        f"| RSK-02 | 把已提交误解成已生效 | 提交主动作后进入处理中 | 用户不了解处理与回写时点 | 在结果页显式说明“已提交 / 待处理 / 已生效”的差异 | {next((page['page_id'] for page in pages if page['archetype'] == 'result_page'), 'P-01')}、ST-02、COPY-03 |",
    ]

    trace_rows: list[str] = []
    for index, page in enumerate(pages, start=1):
        trace_rows.append(
            f"| TR-{index:02d} | {page['page_id']} / {page['name']} / {page['layout_blocks'][0][0]} | J-01、POS-02 | F-07、F-09、F-10、EX-01、EX-02 | PR-01、PR-02、PR-03 | 该页由任务命中页面与 Wiki 页面结构语义共同推导生成 |"
        )

    return f"""# Experience Blueprint

## 体验目标与任务边界

- 目标用户与角色：管理者、执行用户、处理/协作角色，以及需要解释规则的支持角色。
- 体验目标：{goal_line}
- 任务边界：覆盖进入主能力、配置/选择、提交/确认、状态反馈、失败解释与结果确认这条主链路。
- 不覆盖范围：高保真视觉稿、研发实现细节、数据库和接口设计。
- UI 讨论边界：本蓝图已下沉到页面、流程、状态、文案与风险层，可直接供 UI 继续细化。

## 体验推导依据

### 上游业务立场与关键规则

- 承接业务立场：POS-01、POS-02、J-01、J-02、J-03、J-04、J-05、J-06、J-07、J-08、J-09。
- 承接规则：F-05、F-06、F-07、F-08、F-09、F-10、F-11、F-12、R-01、R-02、EX-01、EX-02。
- 承接风险：RSK-01、AP-01。
- 页面结构语义输入：已消费任务上下文中的 Wiki 页面知识与结构语义摘要，用于判断当前需求是结构变化还是结构不变，并决定信息进入 Header、Step、Main、Side、Footer 还是 Alert / Info 区。

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
├── 主动作与自查页面
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
