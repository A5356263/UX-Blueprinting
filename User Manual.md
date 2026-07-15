# Skill 套件使用手册

## 1. 这是什么

这是一套给产品设计师使用的 AI Skill。

它可以帮助你完成：

- 需求定案
- 问题框定
- 用户故事和用户旅程
- 体验蓝图
- 页面规格
- 异常态、视觉方向、设计走查和度量补强
- 项目知识维护

你不需要了解 AI、Agent 或代码。打开项目，用自然语言告诉 Agent 你要做什么即可。

## 2. 第一次使用

1. 用公司提供的 Agent 或 AI IDE 打开项目根目录。
2. 把 PRD、截图和业务材料放入 `input/`。
3. 在对话中说明任务和材料路径。

示例：

```text
请使用 uxb，分析 input/需求文档.md，并完成需求定案。
```

如果工具没有识别 `.claude/skills/`，不要自行修改 Skill 文件。请按公司 Agent 的安装方式配置 Skill 目录。

## 3. 查看路线和进度

### 查看全部 Skill 和路线

打开：

`shared-workflow/progress-preview.html`

这是静态路线总览。用于了解当前 Skill、保留能力和所处阶段。

在文件树中找到该文件，选择“在浏览器中打开”。如果工具不支持，用系统文件管理器双击打开。

### 查看当前任务进度

任务开始后，打开：

`spark-output/progress-preview.html`

这是当前任务的进度页。它会根据 `spark-output/context/` 中的正式产物显示完成状态。

每完成一个 Skill，刷新或重新打开该页面。

如果文件不存在或状态没有更新，告诉 Agent：

```text
请刷新进度预览。
```

不要把这两个页面混淆：

| 页面 | 用途 |
|---|---|
| `shared-workflow/progress-preview.html` | 查看全部 Skill 和静态路线 |
| `spark-output/progress-preview.html` | 查看当前任务的实际进度 |

## 4. 选择适合的路线

没有一条路线适合所有项目。先按手上的材料选择起点。

### 场景一：已有 PRD 或明确需求

```text
uxb → journey-analysis → experience-blueprint → page-spec
```

必须：

- `uxb`：完成正式需求定案
- `experience-blueprint`：生成正式体验方案

按交付目标决定：

- 需要页面生成规格时，执行 `page-spec`

增强：

- `stories`：把需求拆成可设计、可验证的任务
- `journey-analysis`：补齐阶段、触点、痛点和流失风险，当前为 UXB 后的优先推荐

### 场景二：没有 PRD，只有模糊想法

```text
problem-framing → stories → journey-analysis → experience-blueprint → page-spec
```

必须：

- `problem-framing`：先定清问题、角色、范围和方向
- `experience-blueprint`：需要正式体验方案时执行

增强：

- `stories`：把方向拆成任务单元，当前为问题框定后的优先推荐
- `journey-analysis`：检查完整任务旅程和体验风险

按交付目标决定：

- 需要页面生成规格时，执行 `page-spec`

### 场景三：已有页面，需要先诊断

```text
interface-audit → uxb / product-analysis / journey-analysis
```

必须：

- `interface-audit`：基于截图、DOM 或现有页面输出诊断证据

诊断后再决定：

- 需要正式定案：进入 `uxb`
- 方向不成立：进入 `product-analysis`
- 需要分析任务旅程：进入 `journey-analysis`

### 场景四：已有方向，但方向可能不成立

```text
product-analysis → uxb
```

必须：

- `product-analysis`：重构问题并给出可行方向
- `uxb`：对选定方向做正式定案

### 场景五：只做单项补强

不需要强行执行完整主链。直接选择对应 Skill：

| Skill | 核心定位 |
|---|---|
| `edge` | 补齐异常态、空状态、加载态和边界状态 |
| `board` | 收敛视觉风格方向和设计变量 |
| `check` | 检查正式设计产物的完整性与一致性 |
| `journey-metrics` | 定义旅程埋点、度量和异常追踪 |
| `design-strategy` | 独立输出设计判断和策略报告 |
| `knowledge-wiki` | 查询、写入和维护项目知识 |

增强 Skill 只补强一个维度，不替代需求定案或体验蓝图。

## 5. Skill 完成后怎么继续

主链 Skill 完成后通常会：

1. 输出 Markdown 正式文档。
2. 输出供后续 Skill 读取的 Context JSON。
3. 给出固定的下一步推荐。
4. 检查推荐项是否已经产出，并标记“已产出”。

独立增强 Skill 的输出形式可能不同，以完成提示为准。

Agent 只负责推荐，不会自动执行下一步。回复推荐项名称即可继续。

正式产物都在：

`spark-output/`

常见文件：

- `spark-output/uxb_output.md`
- `spark-output/stories.md`
- `spark-output/journey_analysis.md`
- `spark-output/experience_blueprint.md`
- `spark-output/page_spec.md`
- `spark-output/context/*.json`

设计师优先阅读 Markdown。Context JSON 主要供 Skill 交接，不建议手动修改。

## 6. 生成 HTML 预览

HTML 预览默认不会自动生成，也不会改变主链进度。

当前有专属预览的正式产物：

- 需求定案
- 问题框定
- 用户故事
- 用户旅程
- 体验蓝图

这些 Skill 完成后会询问是否生成 HTML。你也可以随时主动要求：

```text
请把本次产物生成 HTML 预览。
```

只生成指定产物：

```text
请生成用户旅程和体验蓝图的 HTML 预览。
```

查看当前可生成的预览：

```text
请列出当前可以生成的 HTML 预览，我再选择。
```

统一入口：

`spark-output/preview/index.html`

在文件树中选择“在浏览器中打开”，或用系统文件管理器双击打开。

其他产物没有专属模板时，只能生成通用预览。HTML 仅用于阅读，不替代 Markdown 正式产物。

## 7. 更换项目和知识库

不同设计师负责不同项目时，不要继续使用示例项目的业务知识和产物。

### 先清理项目数据

清空：

- `input/` 中的示例材料
- `spark-output/` 中的旧产物

保留目录本身，不要删除 Skill。

### 再重置业务知识

需要清理的是：

`.claude/skills/knowledge-wiki/knowledge/raw/业务/`

建议保留：

- `raw/设计准则/`
- `raw/交互模式/`
- `scripts/`
- `templates/`
- `knowledge-wiki` 的其他结构文件

不要手动修改 `wiki/` 中的 summary 和索引。旧业务 summary 应由 `knowledge-wiki` 清理，再由工具重新生成。

把新项目材料放入 `input/` 后，对 Agent 说：

```text
请使用 knowledge-wiki 重置当前业务知识。
删除 raw/业务/ 下的旧业务内容，保留设计准则、交互模式、脚本和模板。
同步清理旧业务 summary，然后读取 input/ 下的新项目材料，建立新的业务知识，并刷新 wiki、索引和校验报告。
执行删除前先列出范围并等待我确认。
```

这是破坏性操作。必须先确认删除范围，再执行。

完成后让 Agent 检查：

- 新材料是否进入 `raw/业务/`
- summary 是否重新生成
- `wiki/index.md` 是否更新
- 是否存在断链、孤立 summary 或未入库材料

## 8. 使用原则

- 不确定从哪里开始时，有 PRD 用 `uxb`，没有 PRD 用 `problem-framing`。
- 已有界面需要诊断时，用 `interface-audit`。
- 增强 Skill 按需使用，不需要全部执行。
- 每完成一个 Skill，先看正式产物和下一步推荐。
- 执行任务时，用 `spark-output/progress-preview.html` 查看进度。
- 新项目开始前，清空旧产物并重置业务知识。
