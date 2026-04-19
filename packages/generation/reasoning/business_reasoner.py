from __future__ import annotations

from .schemas import (
    BaselineEntry,
    BusinessModel,
    BusinessTraceEntry,
    FactsModel,
    JudgmentEntry,
    PlacementOption,
    RiskEntry,
)


def build_business_model(project_id: str, facts_model: FactsModel) -> BusinessModel:
    logic_checks = [
        JudgmentEntry("J-03", "责任归属", "一致", "F-01、F-13、BL-04", "若把生成逻辑塞进 gate，会混淆生成与检查职责。", "命令边界仍需持续维护。"),
        JudgmentEntry("J-04", "授权逻辑", "一致", "F-08、F-09、BL-05", "若允许跨项目复制，会破坏当前项目独立性。", "provenance 细化字段可后续扩展。"),
        JudgmentEntry("J-05", "审批 / 生效逻辑", "一致", "F-06、F-10、F-13", "若无结果回写与追踪，能力无法稳定交付。", "外部依赖细节仍待补足。"),
        JudgmentEntry("J-06", "范围与边界", "一致", "F-15、F-16、BL-06", "若把 preview 写成正式产物，会破坏主链路边界。", "preview 展示细节可后续演进。"),
    ]
    strategy_checks = [
        JudgmentEntry("J-07", "集中治理 / 分级治理关系", "一致", "F-09、F-13、BL-05", "若放宽治理口径，后续会放大规则冲突。", "治理口径仍需结合真实项目继续校准。"),
        JudgmentEntry("J-08", "风险控制", "一致", "F-10、F-11、BL-02", "若只保留模板壳，不引入推理链，则难以识别风险。", "风险等级仍需结合真实需求再调优。"),
        JudgmentEntry("J-09", "审计闭环 / 责任清晰度", "一致", "F-06、F-14、BL-06", "若沿用样例产物或硬编码段落，后续追踪会失真。", "追踪字段还可继续细化。"),
    ]
    value_cost_assessment = [
        JudgmentEntry("VC-01", "业务价值", "高", "F-15、J-01", "不改造将继续把结构化生成和模板填充混在一起。", "需要更多真实案例验证收益曲线。"),
        JudgmentEntry("VC-02", "管理价值", "高", "F-16、J-03", "推理层和渲染层分离后，合同回归更容易做。", "维护者需要理解新的模块边界。"),
        JudgmentEntry("VC-03", "培训 / 理解成本", "中", "J-02、BL-03", "相比单文件模板器，新增子模块会带来学习成本。", "需要文档继续跟进。"),
        JudgmentEntry("VC-04", "操作 / 维护成本", "中", "J-05、J-08", "多一层模型定义，但换来更清晰的调试和扩展面。", "reasoner 规则需要持续维护。"),
        JudgmentEntry("VC-05", "认知负担变化", "略增可控", "J-03、J-09", "内部复杂度提升，但对外输出更加稳定。", "需要保持 renderer 不要重新变成硬模板。"),
    ]
    placement_options = [
        PlacementOption("OPT-01", "维持旧模板填空式生成", "不推荐", "仅在追求最低改造成本时成立", "改动小", "继续把推理和文稿耦在一起", "无法满足文档要求的推理链显式化"),
        PlacementOption("OPT-02", "引入推理模型 + renderer", "推荐", "需要保持外部命令与合同不变", "内部可推理、外部可兼容", "需要新增模块与维护模型", "这是当前最终立场"),
        PlacementOption("OPT-03", "把推理逻辑塞进 validate 或 gate", "不推荐", "仅在忽略职责边界时成立", "表面上减少模块数", "生成与检查职责混乱", "违背主线边界"),
    ]
    risks = [
        RiskEntry("RSK-01", "推理层再次退化成模板拼接", "reasoner 只换文件位置，不做模型推理", "内部结构仍不可扩展", "中", "保持 facts/business/experience model 为独立中间层"),
        RiskEntry("RSK-02", "输出结构偏离合同", "renderer 只追求自由表达，丢掉必需标题", "gate 与 validate 回归失败", "中", "保留合同要求的章节和编号"),
        RiskEntry("AP-01", "把体验便利建立在业务失真之上", "experience 直接越权改写业务结论", "体验方案和业务判断脱节", "高", "experience 只消费 business stance，不重写业务立场"),
    ]
    final_position = "合理，建议成立，并采用“推理模型 + 渲染器”替代原有模板填空式内部实现。"
    final_position_reason = [
        "reasoning 与 rendering 解耦后，facts、business、experience 三层的职责边界更清晰。",
        "对外仍保留现有文件名、章节结构与 provenance 机制，不打断主链路。",
        "业务判断能够显式回链到事实和基线，而不是被埋进固定模板措辞。",
        "体验层将基于任务流、页面、状态与文案职责继续展开，而不是照搬页面骨架。",
    ]
    adopted_rules = ["BR-01: 继续继承关键规则 R-01，体验层必须解释可执行性与阻断原因。", "BR-02: 继续继承结果解释规则 R-02，不能只输出黑盒结果。"]
    adopted_dependencies = ["BD-01: 外部审批 / 协作链路仍是能力成立前提。", "BD-02: 帮助说明与结果解释机制仍是体验层必需依赖。"]
    trace_links = [
        BusinessTraceEntry("J-01", "合理性判断", "合理", "F-01 / F-07 / F-13", "BL-01 / BL-02", "OPT-01", "GAP-01"),
        BusinessTraceEntry("J-03", "底层逻辑一致性判断", "一致", "F-08 / F-09 / F-16", "BL-04 / BL-06", "OPT-03", "GAP-02"),
        BusinessTraceEntry("POS-01", "能力归位判断", "应以 generation 内部推理化改造成立", "F-15 / F-16", "BL-03 / BL-06", "OPT-01 / OPT-03", "GAP-01"),
    ]
    return BusinessModel(
        project_id=project_id,
        review_target="当前项目 generation 阶段的正式生成机制，从模板填空式改为推理式内部实现。",
        review_boundary="本次只评审生成内部结构、业务合理性和能力归位，不评审 UI 实现与研发技术方案。",
        review_goal="形成可供体验层承接的稳定业务立场，并确认该改造是否应成立。",
        fact_links=["F-01", "F-05", "F-09", "F-11", "F-13", "R-01", "R-02", "EX-01", "EX-02", "GAP-01"],
        change_intent=facts_model.task_goal,
        change_type="正式生成能力内部重构，保持外部命令、合同结构与落盘路径不变。",
        trigger="现有 generation 把提取、判断、文稿输出混在一个大模板渲染器中，无法满足推理式生成要求。",
        baselines=[
            BaselineEntry("BL-01", "生成层必须服务核心业务目标，而不是只做表面模板填充。"),
            BaselineEntry("BL-02", "治理约束、结果反馈和责任边界必须稳定且可解释。"),
            BaselineEntry("BL-03", "当前能力本质上属于‘结构化提取 + 业务判断 + 体验翻译’的组合能力。"),
            BaselineEntry("BL-04", "事实、判断、体验翻译三层应分工明确，不能相互替代。"),
            BaselineEntry("BL-05", "允许分层执行，但不能削弱集中治理与结果可追踪性。"),
            BaselineEntry("BL-06", "禁止用样例正式产物、固定话术或临时模板替代当前项目真实推理结果。"),
        ],
        judgments=[
            JudgmentEntry("J-01", "是否服务核心目标", "合理", "F-01、F-07、F-13、BL-01", "若只保留 assemble + gate，将无法独立生成正式产物。", "依赖能力的最终细化口径仍待补充。"),
            JudgmentEntry("J-02", "是否只是表面性补功能", "不是", "F-09、F-14、BL-02、BL-06", "若只补样式、只补 preview 或只补校验，无法解决来源与闭环问题。", "后续仍需持续校验生成质量。"),
        ],
        logic_checks=logic_checks,
        strategy_checks=strategy_checks,
        placement_options=placement_options,
        final_position=final_position,
        final_position_reason=final_position_reason,
        experience_constraints=[
            "体验层必须承接最终业务立场，不得越权重写业务结论。",
            "页面、流程与文案需要显式解释规则命中、状态变化和阻断原因。",
            "体验蓝图应围绕任务流、页面、状态和阅读顺序展开，而不是复用固定页面骨架。",
        ],
        adopted_rules=adopted_rules,
        adopted_dependencies=adopted_dependencies,
        value_cost_assessment=value_cost_assessment,
        risks=risks,
        open_questions=facts_model.open_questions[:],
        gaps=facts_model.gaps[:],
        trace_links=trace_links,
    )
