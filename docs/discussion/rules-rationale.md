# rules-rationale

> 作用：规则“解释层（why）+ 证据依赖（depends_on）”。  
> 维护边界：不重复写规则正文；规则真值只在 `rules-unified-source.md`。  
> 分发约定：S3 / S2.5A 读取 Rules + Rationale；S2.5B 读取 Rules + DependsOn；S4 只读 Rules。

## Shared Rationale

### 全阶段统一（S2.5 / S3 / S4）
- `DRU-001` rationale：先“用户目标/业务约束”，再落到阶段规则，避免为满足阶段模板而偏离真实任务目标。
- `DRU-004` rationale：无证据的结论会放大误判风险，必须在输出中显式区分“可判定”与“不可判定（疑似）”。
- `DRU-005` rationale：统一术语可降低跨阶段信息损耗，减少 S3 决策与 S4 落地的语义漂移。
- `DRU-006` rationale：规则正文单处维护可避免双处维护和版本分叉。
- `DRU-009` rationale：token-first 可减少样式漂移；像素值与语义标识成对出现有利于下游映射与自动校验。
- `DRU-010` rationale：把“决策规则”和“实现细节”分开维护，能降低阶段耦合和重复维护。
- `DRU-011` rationale：S3 前置做语义决策可减少 S4 推断误差；S4 兜底只应补空缺，不应重写设计意图。

### 多规则命中与冲突处理（跨阶段统一）
- `XRU-001`（MUST）：先按 `strength` 决策，`MUST > SHOULD`。
- `XRU-002`（MUST）：同强度冲突时按优先级链处理：`用户明确需求 > 业务约束 > 阶段规则 > 默认策略`。
- `XRU-003`（MUST）：若仍无法收敛，输出“需人工确认”，并给出冲突 `rule_id[]` 与 `missing_evidence[]`。
- `XRU-004`（SHOULD）：同一场景命中多条规则时，输出“主导规则 + 被抑制规则 + 抑制原因”，防止黑盒结论。

## S3 Rationale

### 容器与尺寸决策
- `S3R-003` rationale：`1200` 以上继续放大固定档位会造成可读性和操作距离下降；应转“动态尺寸”并说明触发条件。
- `S3R-004` rationale：优先 `size_tier` 可提升系统一致性，只有业务明确要求时才给 `width_px` 例外值。
- `S3R-006` rationale：`1280` 屏宽场景下将固定上限控制在 `1200`，可兼顾可读性和留白。

### 容器形态选择
- `S3R-101/102/103` rationale：页面/抽屉/弹窗本质是“任务连续性 vs 打断成本”的平衡，不是视觉偏好。
- `S3R-104` rationale：列表项较多仍塞入小弹窗会造成滚动和定位负担，通常应升级承载容器。
- `S3R-105` rationale：高风险动作需要强化确认链路，减少误触与不可逆后果。

### 按钮位置、顺序与分组
- `S3R-203` rationale：多个同级主按钮会提高决策成本，降低关键路径确定性。
- `S3R-204` rationale：主按钮左右顺序是行为引导，不同场景需要显式声明策略依据。
- `S3R-205` rationale：Header/Body/Footer 的操作语义不同，遵循区域习惯可降低搜索成本。
- `S3R-207` rationale：行内操作超过 `3` 时继续平铺会挤占表格信息区并干扰扫描。
- `S3R-208/209` rationale：权限态和条件态需要可预期反馈，避免“能看到但不知道为什么不能做”。

### 控件选型（Radio / Switch / Text List / Title）
- `S3R-401` rationale：Radio 的优势是互斥语义清晰，能显式对比候选项。
- `S3R-403` rationale：Switch 适合即时状态切换，不适合复杂参数选择。
- `S3R-404` rationale：高风险切换需确认/回滚，是对操作后果可控性的保障。
- `S3R-405` rationale：列表“可进入详情”需要稳定入口提示，避免“看起来可看却点不进去”。
- `S3R-407` rationale：整行可点击若无视觉提示，用户难以建立可点击心智。
- `S3R-501` rationale：标题层级稳定是信息架构可预测性的基础。

### 布局与容器语义（Surface / Wrapper）
- `S3R-651` rationale：先定容器语义再定视觉边界，可避免“为了布局误加视觉层”的冗余结构。
- `S3R-652/653` rationale：留白责任单层归属可以控制密度一致性，避免父子层双重 padding。
- `S3R-654` rationale：分隔强度应最小可用，过早上 Surface 会制造无谓视觉噪声。
- `S3R-655/656` rationale：Flex 优先有助于响应式与结构稳定；Row/Col 用在明确分栏更可控。
- `S3R-657` rationale：溢出优先滚动而非截断，保障信息完整与任务可完成性。

### 表单、壳层与流程模式
- `S3R-701/702/703` rationale：表单布局一致性能降低阅读与录入切换成本，例外需给出可读性依据。
- `S3R-705~708` rationale：壳层是页面骨架，必须前置决策；TopBar 单实例是避免重复导航与认知冲突的底线。
- `S3R-801~804` rationale：流程模式决定任务心智；`wizard/Steps` 只用于真实分步依赖，避免伪流程化。
- `S3R-805/806` rationale：筛选区和选择场景类型明确后，下游组件映射才稳定，不易误落成普通列表。

## S2.5A Rationale

### 策略评测口径
- `S25A-001` rationale：先看容器与任务复杂度是否匹配，再看细节视觉；容器错配通常是高优先级风险。
- `S25A-101` rationale：主次动作不清晰会直接影响完成率，应优先标红。
- `S25A-104` rationale：按钮放置违背区域习惯会增加用户搜索和定位成本。
- `S25A-204` rationale：控件选型错误会导致用户心智模型偏差，属于策略层风险而非样式小问题。
- `S25A-301` rationale：容器语义不清和留白责任冲突会引发全局密度与层级紊乱。
- `S25A-302` rationale：同表单混用布局会破坏扫描节奏并增加填写错误概率。
- `S25A-303` rationale：壳层决策缺失常导致实现阶段补猜，回归风险高。
- `S25A-304` rationale：无依赖却用分步流程会增加操作时长与认知负担。

### 输出口径（策略层）
- 若证据完整：给出明确风险等级与修复方向。
- 若证据不足：给“疑似风险 + 待补证据”，避免过度断言。
- 若命中多风险：按 `影响路径（主任务） > 影响范围（覆盖用户） > 修复成本` 排序输出。

## S2.5B DependsOn

### 判定协议（可判定 / 不可判定）
- `DP-001`（MUST）：`depends_on` 证据齐全且满足条件，输出“可判定：命中/不命中”。
- `DP-002`（MUST）：任一必要证据缺失，输出“不可判定”，并列出 `missing_evidence[]`。
- `DP-003`（SHOULD）：在不可判定场景可给“疑似结论”，但必须降级并标注置信度。
- `DP-004`（MUST）：S2.5B 每条结论输出统一结构：`rule_id / status / evidence[] / missing_evidence[] / reason`。

### 规则证据映射：容器与尺寸
- `S25B-001` depends_on：容器类型树（page/drawer/modal）与父子层级关系；缺层级树则不可判定。
- `S25B-002` depends_on：`overlay.width_px` 或可换算宽度证据；若无尺寸证据则不可判定。
- `S25B-003` depends_on：`overlay.position/center_evidence` + `overlay.height_px` + `viewport_height`；缺任一则不可判定。
- `S25B-004` depends_on：超宽事实（`width_px > 1200`）+ 动态尺寸说明证据；缺一则疑似。
- `S25B-005` depends_on：列表项数量估计（IR count）+ 容器类型；缺计数则疑似。

### 规则证据映射：按钮与交互
- `S25B-101` depends_on：同组按钮的 `variant/priority/order`；仅有文案无样式强度证据则不可判定。
- `S25B-102` depends_on：区域类型（header/body/footer/table-toolbar/row-action）+ 排序证据。
- `S25B-103` depends_on：同区域按钮数量统计 + 是否存在“更多/下拉”控件。
- `S25B-104` depends_on：行内操作数量统计 + 折叠入口证据。
- `S25B-105` depends_on：按钮 bbox + 所属区域 bbox，用于判断是否违背区域放置习惯。
- `S25B-106` depends_on：权限状态线索（role/权限管理/tag）+ 动作可点击状态 + 是否有原因提示。
- `S25B-107` depends_on：数据可用性/前置条件线索 + 动作状态（enabled/disabled）+ 提示文案证据。

### 规则证据映射：层级符号
- `S25B-201` depends_on：图标方向 + 交互后状态变化证据；仅静态图且无状态上下文时不可判定。
- `S25B-202` depends_on：同类节点集合 + 箭头方向一致性统计。
- `S25B-203` depends_on：层级深度线索（tree depth）+ 深入入口线索（`→` 或同义入口）。

### 规则证据映射：控件选型、标题、布局
- `S25B-301` depends_on：候选项关系（互斥）+ 控件类型识别（radio/switch/select）。
- `S25B-302` depends_on：Switch 与状态字段绑定证据（on/off state）+ 任务语义标签。
- `S25B-304` depends_on：列表项点击区或右侧入口（arrow/action）证据。
- `S25B-305` depends_on：列表项主次信息与入口的对齐证据（bbox/基线/列对齐）。
- `S25B-306` depends_on：整行可点击证据 + hover/focus 态证据（或等效可达提示）。
- `S25B-401` depends_on：同层区块对齐线/间距测量证据；缺 bbox 或间距证据则不可判定。
- `S25B-402` depends_on：控件宽度测量值 + 档位命中规则（`120/200/320/400`）。
- `S25B-403` depends_on：控件 bbox 与容器 bbox 的左右留白测量。
- `S25B-404` depends_on：同层标题样式 token（字号/字重/颜色）或视觉强度标签。
- `S25B-405` depends_on：标题与内容块包含关系（tree + bbox containment）与距离证据。

### 规则证据映射：表单、壳层与流程
- `S25B-501` depends_on：父子容器 padding/margin 证据 + 区块层级关系（tree）。
- `S25B-502` depends_on：分组强度证据（标题/Divider/Surface）与场景复杂度线索。
- `S25B-503` depends_on：同一表单作用域内 `form.layout` 或可推断布局模式集合。
- `S25B-504` depends_on：`page_shell_specs.topbar.single_instance` + topbar 节点计数证据。
- `S25B-505` depends_on：`page_shell_specs.sider.present` + 实际 sider 节点存在性证据。
- `S25B-506` depends_on：`flow_pattern` / `steps_spec.enabled` + `Steps` 节点存在性证据。
- `S25B-507` depends_on：筛选区节点识别 + `重置/查询` 动作组合证据（或替代说明证据）。
- `S25B-508` depends_on：选择场景特征证据（复选、列结构、搜索/分页）+ 模块类型落地证据。
