from __future__ import annotations

from .schemas import (
    BusinessModel,
    CopyEntry,
    ExperienceModel,
    ExperienceRiskEntry,
    ExperienceTraceEntry,
    FactsModel,
    IaEntry,
    InfoContractEntry,
    PageBlueprint,
    PageEntry,
    PrincipleEntry,
    StateFeedbackEntry,
    TaskFlowEntry,
)


def build_experience_model(project_id: str, facts_model: FactsModel, business_model: BusinessModel) -> ExperienceModel:
    key_page_1_layout = """[Header: 页面标题 + 状态标签 + 帮助入口]
[Intro: 模式说明 / 规则边界 / 风险提醒]
[Main: 关键输入、选择项、提交动作]
[Side: 规则解释 / 依赖说明 / 追踪入口]
[Footer: 取消 / 返回 / 确认]"""
    key_page_2_layout = """[Header: 结果标题 + 当前状态]
[Summary: 结果摘要 / 是否已生效]
[Main: 结果明细 / 下一步动作]
[Support: 失败解释 / 帮助文档 / 追踪信息]
[Footer: 返回 / 关闭 / 继续处理]"""
    return ExperienceModel(
        project_id=project_id,
        target_users="体验设计师、产品经理，以及需要共同评审该能力的业务与管理角色。",
        experience_goal="把已经通过业务审视的生成能力，翻译成可进入页面、流程、状态和文案讨论的体验蓝图。",
        task_boundary="本次覆盖 generation 的核心主流程、关键状态、阻断解释与结果反馈，不覆盖高保真视觉和前端实现。",
        excluded_scope="不产出品牌样式、像素级界面稿、前端技术方案和超出当前合同范围的扩展能力。",
        ui_boundary="蓝图已足以支持 IA、页面承载、状态反馈和文案职责讨论；具体视觉样式留给后续阶段。",
        business_basis=[
            f"承接最终业务立场：{business_model.final_position}",
            "承接能力归位判断：generation 内部应推理化，但对外合同结构保持稳定。",
        ],
        rule_basis=[
            "承接关键规则 R-01：关键动作前需要校验前置条件并解释阻断原因。",
            "承接关键规则 R-02：结果反馈必须解释状态与下一步，而不是只给黑盒结果。",
        ],
        risk_basis=[
            "承接业务层风险：不能让推理层再次退化为模板拼接。",
            "承接业务层风险：不能为了体验便利而越权重写业务立场。",
        ],
        principles=[
            PrincipleEntry("PR-01", "先解释边界，再允许动作", "当前能力受规则、依赖和状态影响，用户需要先理解边界。", "P-01 / TF-01 / COPY-01"),
            PrincipleEntry("PR-02", "结果必须可解释", "处理成功、处理中、失败都不能是黑盒结果。", "P-02 / TF-02 / COPY-02"),
            PrincipleEntry("PR-03", "风险要落到页面与文案上", "业务风险必须在页面结构、状态和文案里被承接。", "P-01 / P-02 / COPY-03"),
        ],
        ia_entries=[
            IaEntry("IA-01", "页面", "管理方 / 设计评审方", "主工作台或 generation 入口", "推理式生成主流程", "上游入口"),
            IaEntry("IA-02", "结果页 / 详情页", "管理方 / 协作方", "由主流程提交后进入", "生成结果、状态解释与后续动作", "下游结果页"),
            IaEntry("IA-03", "帮助 / 追踪模块", "所有角色", "主页面或结果页辅助入口", "规则说明、来源追踪、阻断解释", "并列支持模块"),
        ],
        ia_diagram="""generation 主入口
└── 推理式生成主页面（P-01）
    ├── 规则解释 / 依赖说明 / 追踪入口（辅助区）
    └── 结果反馈页（P-02）
        └── 帮助与追踪模块（支持区）""",
        flow_overview_diagram="""进入 generation 主页面
-> 理解目标与边界
-> 检查前置条件与选择生成动作
-> 提交生成
-> 进入处理中 / 成功 / 失败结果
-> 查看追踪、解释或继续下一步""",
        task_flows=[
            TaskFlowEntry("TF-01", "发起生成流", "进入 generation 主页面", "阅读边界 -> 检查依赖 -> 触发生成", "命中规则时在本页阻断并解释", "进入结果页或处理中状态", "留在当前页并展示阻断原因"),
            TaskFlowEntry("TF-02", "结果解释流", "生成提交后", "查看状态 -> 理解结果 -> 决定下一步", "结果未完成或失败时说明原因与补救方向", "用户理解结果并继续后续动作", "用户回到主页重试或补齐条件"),
        ],
        pages=[
            PageEntry("P-01", "推理式生成主页面", "页面", "管理方 / 设计评审方", "发起生成并理解边界", "generation 主入口", "提交后进入结果页或返回", "上游入口页"),
            PageEntry("P-02", "生成结果与状态页", "页面 / 详情页", "管理方 / 协作方", "理解结果、状态与下一步", "主页面提交后", "关闭或继续后续动作", "下游结果页"),
            PageEntry("P-03", "帮助与追踪模块", "内嵌模块 / 抽屉", "所有角色", "查看规则、来源与阻断解释", "主页和结果页辅助入口", "关闭后回到原页面", "并列支持模块"),
        ],
        key_pages=[
            PageBlueprint(
                page_id="P-01",
                name="推理式生成主页面",
                goal="在发起生成前，让用户先理解这次生成要解决什么、依据什么、何时会被阻断。",
                target_user="管理方 / 设计评审方",
                entry_condition="进入 generation 主入口并具备查看正式产物的上下文。",
                primary_task="选择或触发生成动作。",
                secondary_task="查看规则边界、依赖状态与追踪入口。",
                first_screen_focus="任务目标、边界、当前前置状态、可执行动作。",
                key_information="需要把目标、前置条件、阻断规则和依赖说明一起前置展示。",
                key_actions=["触发 generate-facts / generate-business / generate-experience", "打开帮助与追踪入口", "返回上游整理输入"],
                key_states=["可执行", "前置缺失", "处理中"],
                risks=["用户误以为这是无条件的一键生成", "用户不知道阻断来自治理规则还是系统异常"],
                relation="上游入口页，通向结果与状态页。",
                layout_diagram=key_page_1_layout,
            ),
            PageBlueprint(
                page_id="P-02",
                name="生成结果与状态页",
                goal="让用户理解生成是否完成、当前处于什么状态，以及后续该做什么。",
                target_user="管理方 / 协作方",
                entry_condition="主页面已经触发生成动作。",
                primary_task="查看结果和下一步。",
                secondary_task="查看失败原因、追踪来源或返回重试。",
                first_screen_focus="结果状态、结果摘要、下一步动作。",
                key_information="需要把结果状态、成功影响、失败解释和补救方向分开说明。",
                key_actions=["查看正式产物", "查看追踪映射", "返回补齐输入并重试"],
                key_states=["处理中", "成功完成", "失败 / 阻断"],
                risks=["把处理中误解成已经完成", "只看到失败不知道如何处理"],
                relation="承接主页面提交后的下游结果页。",
                layout_diagram=key_page_2_layout,
            ),
        ],
        info_contracts=[
            InfoContractEntry("INFO-01", "解释这次生成的目标与范围", "高", "P-01 首屏", "进入页面时", "若不展示，用户会误判动作边界。"),
            InfoContractEntry("INFO-02", "解释前置条件与阻断规则", "高", "P-01 主区域 / 辅助区", "操作前", "若不展示，会增加误操作和反复试错。"),
            InfoContractEntry("INFO-03", "解释结果状态与下一步", "高", "P-02 首屏", "提交后", "若不展示，会把处理中误判为完成。"),
            InfoContractEntry("INFO-04", "解释来源追踪与帮助信息", "中", "P-03 或折叠区", "用户需要深挖时", "若不展示，评审时难以回链到事实与业务判断。"),
        ],
        state_feedbacks=[
            StateFeedbackEntry("ST-01", "可执行", "进入 P-01 且前置条件满足", "查看说明、选择、提交", "展示当前状态和关键说明", "告知当前可以继续执行", "进入提交链路"),
            StateFeedbackEntry("ST-02", "已提交 / 处理中", "提交后等待处理完成", "查看记录、等待结果", "P-02 展示处理中和当前进度", "明确“已提交，不代表已完成”", "等待结果回写"),
            StateFeedbackEntry("ST-03", "失败 / 阻断", "命中规则冲突或依赖缺失", "查看原因、返回调整", "展示失败状态与阻断说明", "解释为什么失败以及如何处理", "返回 P-01 或停留结果页"),
            StateFeedbackEntry("ST-04", "成功完成", "关键动作放行并回写成功", "查看结果、继续下一步", "展示成功状态和结果摘要", "明确成功影响与后续动作", "进入稳定可交付状态"),
        ],
        copy_contracts=[
            CopyEntry("COPY-01", "主页面说明", "说明文案", "解释能力价值、规则边界和当前收益", "能做什么、为什么存在、关键限制", "只说“更方便”而不解释边界", "当前生成会先基于 source 推理，再输出正式文档。"),
            CopyEntry("COPY-02", "处理中 / 成功反馈", "状态文案", "解释已提交但未必已最终完成", "当前状态、下一步、去哪里看结果", "把处理中写成已完成", "已提交，结果回写后可在正式产物区查看。"),
            CopyEntry("COPY-03", "失败 / 阻断反馈", "错误 / 阻断文案", "解释为什么失败以及如何处理", "失败原因、处理方向、是否可重试", "只说“失败，请稍后再试”", "当前命中规则限制，请先补齐前置条件后再重试。"),
        ],
        risks=[
            ExperienceRiskEntry("RSK-01", "把治理限制误解成系统异常", "提交失败或不可执行", "用户只看到失败，没有理解规则原因", "在失败态显式解释限制和处理方向", "P-01 / P-02 / COPY-03"),
            ExperienceRiskEntry("RSK-02", "把已提交误解成已完成", "提交后进入处理中", "用户不了解结果回写时点", "成功反馈必须说明“已提交 / 待回写”", "P-02 / ST-02 / COPY-02"),
        ],
        open_questions=business_model.open_questions[:],
        gaps=business_model.gaps[:],
        trace_links=[
            ExperienceTraceEntry("TR-01", "P-01 / TF-01 / COPY-01", "J-01 / POS-01", "F-07 / F-09 / R-01 / EX-01", "PR-01 / PR-03", "首屏先解释可执行性和规则边界。"),
            ExperienceTraceEntry("TR-02", "P-02 / TF-02 / COPY-02", "J-05 / J-09", "F-06 / F-10 / EX-02", "PR-02", "结果页必须解释状态、原因与下一步。"),
            ExperienceTraceEntry("TR-03", "P-02 / ST-03 / COPY-03", "J-08 / POS-01", "F-11 / F-12 / EX-01", "PR-03", "失败不是黑盒报错，而是治理阻断解释。"),
        ],
    )
