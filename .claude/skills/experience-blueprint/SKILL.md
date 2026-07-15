---
name: experience-blueprint
description: >
  体验蓝图 Skill。基于正式上游结论生成完整体验方案，包含旅程消费摘要、交互流程、页面设计和状态文案。
  触发关键词：体验蓝图、完整体验方案、交互设计方案、交互流程设计、蓝图设计、生成体验设计方案。
  仅在用户明确要求生成体验蓝图或完整交互方案时使用；不得仅因 UXB、问题框定、用户故事或旅程产物存在而自动触发。
  排除：需求定案（用 uxb）、设计策略（用 design-strategy）、页面规格（用 page-spec）、旅程分析（用 journey-analysis）。
---

# Experience Blueprint

这个 skill 负责读取第一阶梯正式上游结论，并把它展开为完整的交互设计方案。默认只输出 Markdown 与 Context JSON；如需预览，交给 `preview-renderer`。

本次能力支持多上游承接，但不改变 `§0-§9` 的正文分析骨架。

## Step 0 · 运行入口

### Step 0.1 · 本 Skill 产物状态

执行本 Skill 前，只检查本 Skill 对应正式产物是否存在。

正式产物：
- `spark-output/experience_blueprint.md`
- `spark-output/context/experience-blueprint.json`

只允许检查文件是否存在；禁止读取产物正文、禁止解析 JSON 内容、禁止根据已有产物改变当前任务类型。

若任一正式产物存在，先输出以下状态提示，然后继续执行本 Skill 的入口规则：

```text
检测到本 Skill 已有正式产物（已产出）。
```

该提示只表示状态，不代表采取任何处理动作。

禁止：
- 读取产物正文
- 解析 JSON 内容
- 根据已有产物改变当前任务类型
- 根据已有产物执行下游
- 根据已有产物询问处理方式
- 根据已有产物推断用户意图

### Step 0.2 · 上游读取

启动后固定按以下顺序读取：

1. 按当前 `SKILL.md` 的规则确认本 Skill 自身角色和输入边界
2. 读取 `spark-output/context/uxb.json`
3. 读取 `spark-output/uxb_output.md`
4. 读取 `spark-output/context/problem-framing.json`
5. 读取 `spark-output/problem_framing.md`
6. 读取 `spark-output/context/stories.json`（如存在），用于 `§2-§4` 的任务单元深化
7. 读取 `spark-output/stories.md`（如存在），用于任务叙述补充
8. 读取 `spark-output/context/journey-analysis.json`（如存在），用于 `§1` 旅程消费摘要的结构化数据
9. 读取 `spark-output/journey_analysis.md`（如存在），用于 `§1` 旅程消费摘要的叙述性分析
10. 优先读取第一阶梯来源中的待确认问题，判断上游稳定性
11. 执行知识补充消费（必须执行，不可跳过）

这是链路消费型 skill，默认承接 `spark-output/` 中的上游产物属于正式工作流，不视为历史残留。

双轨读取原因：

- JSON 负责结构化数据骨架
- MD 负责叙述性判断和策略
- 两者一起用，比只读长文档更稳

### Step 0.3 · 模式判断与降级

模式判断：

- `uxb-mode`：检测到 `uxb.json` 或 `uxb_output.md`，以 UXB 作为第一阶梯正式来源
- `framing-mode`：未检测到 UXB，但检测到 `problem-framing.json` 或 `problem_framing.md`，以问题框定作为第一阶梯正式来源
- `deepened-mode`：在 `uxb-mode` 或 `framing-mode` 基础上，同时检测到 `stories` 或 `journey-analysis`

硬规则：

- 当一级正式来源为 `uxb` 时，不追加本轮新增的 `3+1` 门槛判断，仍按现有主链规则直接展开。
- 当一级正式来源为 `problem-framing` 时，才执行本轮新增的 `3+1` 门槛判断。

降级规则：

- 如果 `uxb.json` 未找到，回退到只读 `uxb_output.md`
- 如果 `uxb.json` 存在但 `uxb_output.md` 未找到，仅基于 JSON 结构化数据继续执行，在 `§0` 中标注"叙述性分析缺失，仅基于结构化数据推导"
- 如果 UXB 不存在但 `problem-framing` 存在，进入 `framing-mode`，基于问题定义、推荐方向和承接要求继续执行
- 如果 UXB 和 `problem-framing` 均不存在，不进入正式蓝图生成，输出引导提示：
  "未找到第一阶梯正式上游结论。建议先完成 UXB 需求定案或问题框定，再进入体验蓝图。"
- 如果 `stories` 不存在，允许继续，但必须在 `§9` 标注"当前未经过用户故事深化，主任务链基于第一阶梯结论推导"
- 如果 `journey_analysis.md` 存在但 `journey-analysis.json` 不存在，仅基于 MD 继续
- 如果 `journey-analysis.json` 存在但 `journey_analysis.md` 不存在，仅基于 JSON 继续，在 `§1` 标注"叙述性分析缺失"
- 如果两者均未找到，`§1` 进入降级模式（从第一阶梯结论或 stories 推导简化旅程）
- 如果 `knowledge-wiki` 当前不可用，在 `§9` 附录注明”知识库不可用”，继续后续设计，但不得伪造知识消费结果

### Step 0.4 · framing-mode 来源可用性检查

当进入 `framing-mode` 时，先固定检查 `3+1`：

1. `角色与目标是否明确`
   - 谁在完成什么任务
   - 成功结果是什么
2. `业务边界与对象是否明确`
   - 当前处理的正式业务对象是什么
   - 本轮进入范围与不进入范围是什么
3. `关键状态与阻断是否明确`
   - 主流程经过哪些关键状态
   - 哪些异常、阻断或规则会改变流程推进
4. `是否存在会直接改写主流程结构的未决问题`
   - 会改写主流程
   - 会改写页面结构
   - 会改写关键交互

只有同时满足以下条件，才允许输出完整体验蓝图：

- 上述 3 个主项全部通过
- 不存在会直接改写主流程结构的未决问题

如果 `3+1` 未通过：

- 不回上游
- 不触发 loop
- 不伪装成完整蓝图
- 只允许对已确认部分做“局部展开 + 显式保留”

## 角色定义

体验蓝图负责：

- 组织交互流程与角色承接
- 写清用户动作、系统反馈、页面文案和下一步
- 展开异常与阻断
- 承接业务边界、风险与反馈要求
- 生成旅程消费摘要模块
- 在第一阶梯已定边界上输出尽量完整的体验方案

体验蓝图不负责：

- 高保真视觉设计
- 前端实现方案
- 接口设计
- 重新做业务判断

## 知识补充消费

体验蓝图阶段必须独立执行一轮知识补充消费。UXB 的知识消费服务于需求定案；体验蓝图的知识消费服务于交互设计展开。

固定协议只有一条：

```text
先命中知识
→ 先读 summary
→ 再读该 summary 对应的 raw
→ 再进入体验推导
```

知识消费发现顺序固定为：

1. 读取当前可用 knowledge-wiki 的知识索引 / overview / index
2. 从索引中定位目标领域的 summaries 入口
3. 读取命中的 summary
4. 根据 summary 中记录的 source_path / raw 指向读取对应 raw
5. raw 读取失败时，该知识不得进入“已消费知识”，只能进入知识缺口

`summary` 只负责路由，不能作为正式判断依据。
`raw` 以知识索引或 summary 中的指向为准。
不得用猜测目录名、README 替代 summary、直接广读 raw 的方式绕过索引路由。

强制步骤：

1. 按固定发现顺序命中知识
2. 结合第一阶梯正式来源，判断哪些知识与当前体验设计相关
3. 对判断为“相关”的条目，先读 summary，再继续读该 summary 对应的 raw
4. 将提取出的体验策略写入 `§9` 附录，并在正文中落到真实章节或节点
5. 完成孤儿判断反查，确认不存在“有知识来源、无设计落点”的条目

必须遵守：

- 不得跳过整个知识消费步骤
- 不得只抄第一阶梯已选结论而不做体验阶段独立判断
- 不得只读 summary 不读 raw
- 不得只留下“知识来源”而没有正文落点
- 不得把 summary 当作可以停留的深度信息层

## 体验推导责任

体验蓝图必须承接第一阶梯已经形成的正式结论，并将其转译为：

- 角色路径
- 任务流
- 页面结构
- 状态反馈
- 异常阻断
- 保护策略

不得：

- 重新裁决需求是否成立
- 绕过第一阶梯来源自行判断能力形态
- 只根据需求文档罗列页面功能，不基于第一阶梯边界展开
- 用“体验友好”“提示清晰”这类空泛表述替代具体页面结构、状态和文案
- 绕回原始输入重新解释业务规则、状态模型或能力形态
- 用 `stories` 或 `journey-analysis` 的派生信息反向覆盖第一阶梯正式结论
- 如果第一阶梯来源仍未定主方向、核心角色职责、关键状态闭环或核心异常策略，硬输出“完整方案”
- 在 `framing-mode` 下把 `working_assumptions` 当作完整蓝图事实基础
- 在 `framing-mode` 下把会改写主流程的未决问题静默抹平

## 输出结构

输出到：

- `spark-output/experience_blueprint.md`
- `spark-output/context/experience-blueprint.json`

输出规则补充：

- 如果宿主支持文件系统，先检查并创建 `spark-output/` 与 `spark-output/context/`，再写入产物

必须包含以下 9 个正文章节和 1 个附录部分：

- `§0` 本次关键设计判断
- `§1` 旅程消费摘要
- `§2` 交互流程总览
- `§3` 主交互流程
- `§4` 次交互流程
- `§5` 异常与阻断流程
- `§6` 页面 / 弹窗 / 抽屉设计
- `§7` 状态与反馈文案
- `§8` 待确认问题
- `§9` 附录：设计指南消费说明

当来源为 `problem-framing` 且 `3+1` 未通过时，不得在 `§0` 开头增加 `来源可用性检查` 或 `本轮展开限制`。

`3+1` 检查只作为 `framing-mode` 的内部承接门槛和尾部追踪信息：

- `§0` 仍只写体验蓝图自己的关键设计判断
- `§8` 汇总会影响流程、页面、状态或文案的待确认问题
- `§9` 用最小篇幅记录 `上游承接检查`，只写大白话，不写内部字段名
- Context JSON 可记录机器侧字段，但用户侧 Markdown 正文不得直接展示 `source_usability_check`、`expansion_mode`、`confirmed_facts`、`working_assumptions`、`full`、`limited`

## 正文承载规则

为避免 Markdown 文档整章表格化，正文默认按下列方式承载：

- `§0` 到 `§6` 默认使用“大标题 + 小标题 + 正文 / 短列表”
- `§7` 允许使用短表格承载状态 key、反馈口径、文案 key 等高密度枚举信息
- `§9` 允许使用最小记录表，但不得扩展成大篇幅审计表
- 未明确允许的章节，不用 Markdown 表格承载主体内容

特别要求：

- `§2` 到 `§6` 不得整章退化成流程表、状态表、字段表
- 即使存在多个节点、多个字段、多个分支，也优先用“小标题 + 正文 / 短列表”表达

## `§0` 本次关键设计判断

体验蓝图自己的核心设计判断，不复述第一阶梯来源的 `§0` 或关键判断。

每条判断必须包含具体的设计做法。"需要关注 XX"是复述，"XX 场景用 XX 方式处理"是判断。

五段式结构：

- 判断（体验层面的关键决策，不是业务层面的）
- 主要影响（这个决策影响哪些页面 / 流程）
- 建议方案（具体的设计做法）
- 不建议方案（以及为什么不适合当前场景）
- 关键待确认（影响本判断成立的前提）

当来源为 `problem-framing` 且 `3+1` 未通过时，`§0` 的判断不得写成“完整路线已确定”，只能围绕已确认部分做局部设计判断。

禁止表达：

- “当前按完整执行路线处理”
- “标准路线下优先写主流程”
- 任何内部执行术语
- 对第一阶梯关键判断的重新表述或增强措辞

## `§1` 旅程消费摘要

旅程图由 journey-analysis Skill 独立产出，体验蓝图不再生成旅程图。

本节从 journey-analysis 产出中提取三类信息，驱动后续章节的设计决策：

- 信心最低点 → 驱动 `§5` 异常流程的设计优先级（信心越低的阶段，异常处理越重要）
- 关键转折 → 驱动 `§3` / `§4` 交互流程的"前置说明"字段（用户在转折点需要更多上下文）
- 流失风险 → 驱动 `§6` 页面设计的引导策略（高风险阶段需要更强的操作引导）

每个提取项写明来源角色和阶段，以及在本蓝图中的具体落点。

降级：如果 journey-analysis 未执行（`spark-output/journey_analysis.md` 和 `spark-output/context/journey-analysis.json` 均不存在），从第一阶梯正式来源和 stories 推导简化版旅程，并标注"基于上游结论推导，未经深度旅程分析"。

## `§2` 交互流程总览

`§2` 是点击动作级交互流程图，不是旅程摘要。只写页面 / 弹窗 / 抽屉 / 用户动作 / 系统反馈 / 状态变化 / Toast / InlineError / EmptyState / LoadingState。

要求：

- 列出本次设计包含的交互路径（几条主路径、几条分支路径）
- 每条路径必须具体到点击、输入、选择、提交等动作级别
- 每条路径说明经过哪些页面 / 弹窗 / 抽屉，关键分支点在哪
- `§3` 的详细节点必须能在这里找到承接
- 不展开页面结构细节，页面结构仍归 `§6`
- 不使用 ASCII 框图、终端布局图或字符边框图

禁止把以下内容作为流程节点：

- 等待审批
- 获知结果
- 验证生效
- 感知
- 确认现状
- 信心
- 痛点
- 流失风险

正向案例：

```markdown
### 主路径：{角色}提交{业务对象}申请

{承载页面} Page
→ 点击 [发起{核心任务}]
→ 打开 {业务对象}申请 Drawer
→ 选择{业务对象}
→ 输入申请原因
→ 点击 [提交申请]
→ 校验通过
→ Drawer 关闭
→ Toast：提交成功
→ {结果列表}新增一条“处理中”记录

分支：
- 未选择{业务对象} → [提交申请] 置灰，不进入提交
- 申请原因不足 → Drawer 不关闭，原因输入区下方显示 InlineError
- {处理角色}不存在 → Drawer 不关闭，Toast 提示处理配置异常
```

反向约束：

- 不把整条主路径写成三列表或多列表大表格
- 不把分支条件折叠成“条件 / 结果 / 下一步”总表

## `§3` 主交互流程

每个节点必须包含：

- 用户动作
- 系统反馈
- 需要前置解释的信息
- 建议文案
- 下一步

`§1` 是旅程消费摘要，`§3` 是操作层，不要混写。

承载要求：

- 每个主流程节点用小标题分块展开
- 节点内用正文或短列表写清字段
- 不把整个主流程写成一张总表

## `§4` 次交互流程

展开非主路径任务，如编辑配置、查看详情、撤销申请、重新提交等。

要求：

- 每个次流程至少包含：触发条件、用户动作、系统反馈、下一步
- 如果流程涉及权限、审批、范围、关闭、撤销、授权失败等易误解概念，补充“需要前置解释的信息”
- 如果流程涉及弹窗、toast、按钮或错误反馈，补充“建议文案”
- 不需要为了凑格式把每个次流程都写满所有字段
- 不退化成一整段自然语言概述或纯数字步骤列表

承载要求：

- 每个次流程独立成块
- 不把多个次流程并排塞进一张对照表

## `§5` 异常与阻断流程

每个异常必须包含：

- 发生时机
- 触发条件
- 判断依据
- 反馈形式
- 系统反馈
- 用户下一步
- 恢复路径（用户回到正常流程需要几步、中间是否丢失已填信息）

恢复路径用大白话写清楚，不用编号体系。如果某个异常的恢复是原路返回且无信息丢失，直接写"原路恢复，无信息丢失"。

异常与阻断流程是正式体验内容，不是附录。

承载要求：

- 每个异常独立展开
- 不把多个异常压成统一总表

## `§6` 页面 / 弹窗 / 抽屉设计

页面类界面至少包含：

- 页面目标
- 进入条件
- 页面结构
- 按钮
- 成功反馈
- 失败反馈

如果存在加载态、空状态、审批中、已关闭、异常态，应补“状态反馈区”。
如果存在按钮置灰、入口隐藏、阻断弹窗、字段校验，应补“异常状态下的结构变化”。
如果存在关键提示、表单字段、弹窗或 toast，应补“具体文案”。
如果当前场景没有合理内容，不要为了凑结构保留空字段或空小节。

弹窗类界面优先包含：

- 弹窗目标
- 触发条件
- 弹窗结构
- 具体文案
- 按钮
- 成功反馈
- 失败反馈

抽屉类界面优先包含：

- 抽屉目标
- 进入条件
- 抽屉结构
- 具体文案
- 按钮
- 成功反馈
- 失败反馈

如果抽屉包含表单，应补充字段校验、提交前校验和提交失败反馈。

每个页面 / 弹窗 / 抽屉必须包含“结构草图”。
结构草图必须使用 fenced code block + ASCII，不得退化为自然语言列表。
生成结构草图前，必须优先读取 knowledge-wiki 中与当前页面相关的页面载体语义 / 页面结构 `raw`。
如果知识库存在对应结构，按其结构模式输出 ASCII 草图。
如果知识库没有对应结构，再基于当前页面目标输出低保真 ASCII 草图，并在图中标注待确认区域。

ASCII 结构草图只允许出现在这一章的“页面结构”部分。

结构草图中的示例业务数据必须变量化。

使用：

- `{业务对象总数}`
- `{分类数}`
- `{分类名}`
- `{业务对象名称}`
- `{业务范围}`
- `{处理人姓名}`
- `{处理时间}`

不得把具体人名、具体数量、具体业务应用名当作默认页面数据。

承载要求：

- 页面、弹窗、抽屉逐个成节展开
- 结构草图保留在 code block 中
- 草图之外的说明使用正文或短列表
- 不用大表格承载整页结构、整页按钮规则或整页状态变化

## `§7` 状态与反馈文案

以统一状态口径表为主，至少包含：

- 状态
- 含义
- 适用对象
- 用户可操作
- 统一反馈口径

这里允许短表格，但只用于状态口径、文案 key、短字段枚举这类高密度对照信息。

## `§8` 待确认问题

每条至少包含：

- 问题标题
- 影响
- 建议确认方

如果第一阶梯来源中的关键待确认问题仍未闭合，必须在这里标注“基于推荐方案推进”。
当来源为 `problem-framing` 且 `3+1` 未通过时，必须同步保留“本轮未完整展开”的说明。

## `§9` 附录：设计指南消费说明

仅在实际装配并使用了设计准则或业务知识时填写。

包含三类记录：

- 设计准则消费
- 业务知识消费
- 知识缺口
- 上游承接追踪

`上游承接追踪` 固定表格：

| 上游判断 | 对体验意味着什么 | 体验设计决策 | 落点章节 |
|---|---|---|---|
| [来自 UXB §7 / uxb.json.experience_handoff_requirements / problem-framing.handoff_contract] | [体验影响] | [本次体验蓝图的具体设计决策] | [§3 / §5 / §6 / §7 等] |

## 自检清单

生成 `experience_blueprint.md` 前，回看第一阶梯正式来源，逐项检查：

```text
□ 1. 第一阶梯来源中的每个角色是否都有对应的路径、页面或职责落点？
□ 2. 第一阶梯来源中的每条承接要求是否都有对应展开？
□ 3. 第一阶梯来源中的每个异常或风险是否都有交互流程展开？
□ 4. 第一阶梯来源中的每种状态是否都有展示位置和反馈文案？
□ 5. 配置态 / 关闭态 / 回退态等非主线场景是否被省略？
□ 6. 第一阶梯来源中的关键待确认问题是否在文档中标注为“基于推荐方案推进”？
□ 7. 第一阶梯来源的关键判断、规则边界和已消费知识条目，是否都在体验蓝图中有对应的设计落点？
□ 8. `§9` 的承接追踪是否非空，且每行都能落到真实章节？
□ 9. `§0` 每条判断是否都包含具体设计做法，而非第一阶梯结论的复述或增强？
□ 10. `§1` 旅程消费摘要是否非空，且三类信息（信心最低点 / 关键转折 / 流失风险）都有提取？
□ 11. 是否输出了预览交接提示？
```

关键原则：

- 只检查自己的输出，不检查上游来源的输出质量
- 如果某项目前无法明确承接，应显式写入 `§8`
- 如果某项属于第一阶梯本应定清的主方案前提，应优先指出上游未闭合
- 自检第 7 项是反向检查：不是检查“体验蓝图写了什么”，而是检查“第一阶梯来源的判断和已消费知识是否被遗漏了”
- 当来源为 `uxb` 时，不执行 `3+1` 的完整性拦截
- 当来源为 `problem-framing` 时，如 `3+1` 未通过，不得输出假完整方案

## Context JSON 写入

文档生成并自检通过后，按固定结构写入 `spark-output/context/experience-blueprint.json`。

固定结构：

```json
{
  "skill": "experience-blueprint",
  "version": "1.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/experience_blueprint.md",
  "source_refs": [],
  "read_sections": [],
  "source_mode": "unknown",
  "source_usability_check": {
    "usable": "unknown",
    "reason": "unknown",
    "missing_inputs": []
  },
  "expansion_mode": "unknown",
  "critical_design_judgments": [
    {
      "judgment": "unknown",
      "major_impact": "unknown",
      "recommended_solution": "unknown",
      "not_recommended_solution": "unknown",
      "key_open_question": "unknown"
    }
  ],
  "uxb_mapping": [
    {
      "upstream_judgment": "unknown",
      "experience_meaning": "unknown",
      "blueprint_decision": "unknown",
      "target_section": "unknown"
    }
  ],
  "problem_framing_mapping": [
    {
      "upstream_judgment": "unknown",
      "experience_meaning": "unknown",
      "blueprint_decision": "unknown",
      "target_section": "unknown"
    }
  ],
  "stories_consumption": {
    "used_stories": [],
    "excluded_stories": [],
    "story_to_flow_mapping": []
  },
  "journey_consumption": {
    "confidence_lows": [
      {
        "role": "unknown",
        "stage": "unknown",
        "reason": "unknown",
        "blueprint_impact": "unknown"
      }
    ],
    "key_transitions": [
      {
        "from_stage": "unknown",
        "to_stage": "unknown",
        "trigger": "unknown",
        "blueprint_impact": "unknown"
      }
    ],
    "dropout_risks": [
      {
        "role": "unknown",
        "stage": "unknown",
        "risk": "unknown",
        "blueprint_impact": "unknown"
      }
    ]
  },
  "interaction_overview": {
    "pages": [],
    "modals": [],
    "drawers": [],
    "user_actions": [],
    "system_feedback": [],
    "state_changes": [],
    "toast": [],
    "inline_error": [],
    "empty_state": [],
    "loading_state": []
  },
  "main_flow": [
    {
      "node_id": "unknown",
      "node_name": "unknown",
      "user_action": "unknown",
      "system_feedback": "unknown",
      "pre_explanation": "unknown",
      "copy_suggestion": "unknown",
      "state_change": "unknown",
      "next_step": "unknown"
    }
  ],
  "sub_flows": [
    {
      "flow_id": "unknown",
      "flow_name": "unknown",
      "trigger_condition": "unknown",
      "user_action": "unknown",
      "system_feedback": "unknown",
      "pre_explanation": "unknown",
      "copy_suggestion": "unknown",
      "next_step": "unknown"
    }
  ],
  "exceptions": [
    {
      "exception_id": "unknown",
      "name": "unknown",
      "timing": "unknown",
      "trigger_condition": "unknown",
      "basis": "unknown",
      "feedback_form": "unknown",
      "system_feedback": "unknown",
      "user_next_step": "unknown",
      "recovery_path": "unknown"
    }
  ],
  "pages": [
    {
      "page_id": "unknown",
      "page_name": "unknown",
      "page_goal": "unknown",
      "entry_condition": "unknown",
      "structure_ascii": "unknown",
      "regions": [],
      "buttons": [],
      "success_feedback": "unknown",
      "failure_feedback": "unknown"
    }
  ],
  "modals": [
    {
      "modal_id": "unknown",
      "modal_name": "unknown",
      "goal": "unknown",
      "trigger_condition": "unknown",
      "structure_ascii": "unknown",
      "copy": [],
      "buttons": [],
      "success_feedback": "unknown",
      "failure_feedback": "unknown"
    }
  ],
  "drawers": [
    {
      "drawer_id": "unknown",
      "drawer_name": "unknown",
      "goal": "unknown",
      "entry_condition": "unknown",
      "structure_ascii": "unknown",
      "copy": [],
      "buttons": [],
      "success_feedback": "unknown",
      "failure_feedback": "unknown"
    }
  ],
  "states": [
    {
      "state": "unknown",
      "meaning": "unknown",
      "applies_to": "unknown",
      "user_action_available": "unknown",
      "feedback_standard": "unknown"
    }
  ],
  "open_questions": [
    {
      "question": "unknown",
      "impact": "unknown",
      "suggested_owner": "unknown"
    }
  ],
  "knowledge_consumption": {
    "design_guidelines_used": [],
    "business_knowledge_used": [],
    "knowledge_gaps": [],
    "upstream_trace": []
  }
}
```

硬规则：

- 字段固定，不得新增、删除或改名。
- 只填入本 Skill 正式 Markdown 已产出的信息；缺失信息写 `unknown`、空数组，或进入 `open_questions[]`。
- 不得为了填满 JSON 编造信息。
- `expansion_mode` 只能是 `full`、`limited` 或 `unknown`。
- `interaction_overview` 必须保留 `toast`、`inline_error`、`empty_state`、`loading_state`。
- `pages[]`、`modals[]`、`drawers[]` 不得合并成无类型数组。
- `structure_ascii` 必须来自 Markdown 中的结构草图；未输出则写 `unknown`。
- `source_usability_check`、`expansion_mode`、`full`、`limited` 属于机器侧承接记录，不得作为用户侧 Markdown 正文字段名直接展示。
- JSON 不复制 Markdown 全文。
- 写入失败不阻断完成，但应在输出中提示。

## 预览交接

- `experience-blueprint` 自身不再生成 HTML 预览。
- 正式产物完成后，如用户明确确认需要预览，再交给 `preview-renderer`；不得为了预览修改当前 skill 的正式 Markdown、Context JSON 或知识消费逻辑。
- 预览是附加动作，不改变主链流转，也不进入 `next_hint`。
- 固定提示口径：

```text
附加操作：
如果需要，我可以继续把本次正式产物渲染成 HTML 预览。
这不会改变主链流转。
```

## Handoff · 固定下一步

本 Skill 完成后，只输出固定下一步推荐。

输出推荐前，只按以下映射检查推荐项正式产物是否存在；若存在，只在推荐项名称后追加“（已产出）”。

推荐项产物映射：
- 页面规格：`spark-output/page_spec.md` 或 `spark-output/context/page-spec.json`
- 异常态：`spark-output/edge_output.md` 或 `spark-output/context/edge.json`
- 视觉情绪板：`spark-output/board_output.md` 或 `spark-output/context/board.json`
- 旅程埋点与度量需求：`spark-output/journey_metrics/journey_visual.md`、`spark-output/journey_metrics/journey_visual.html`、`spark-output/journey_metrics/journey_tracking_spec.md` 或 `spark-output/journey_metrics/error_tracking_spec.md`

禁止：
- 读取推荐项产物正文
- 根据产物存在改变推荐顺序
- 动态计算候选项
- 读取 shared-workflow/next-skill.md 生成候选项
- 读取 shared-workflow/skill-graph.json 生成候选项
- 直接执行下一步

固定输出：

```text
体验蓝图已完成。你可以继续：
1. 页面规格
2. 异常态
3. 视觉情绪板
4. 旅程埋点与度量需求

你回复对应名称即可。
```

“（已产出）”只代表状态，不代表该项被选中或质量通过。

如需刷新进度预览，可使用项目已有预览入口；刷新失败不影响当前 Skill 完成。

## 设计参考使用规则

- 优先承接第一阶梯来源已明确选中的设计准则和业务知识
- 可以补充第一阶梯来源未选中但与当前体验设计强相关的知识条目
- 不根据关键词自动命中设计指南
- 命中 guideline 后，必须先读 summary，再读对应 raw
- 不自动补充与当前体验设计无关的 guideline
- guideline 只吸收原则，不在正文暴露内部路径或编号

具体判断方法、记录格式、反查清单和示例，统一参考：

- `references/knowledge_consumption_guide.md`
