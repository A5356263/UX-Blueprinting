---
name: preview-renderer
description: >
  统一预览渲染 Skill。用于在正式产物已经生成后，把支持预览的 skill 产物按各自模板与渲染规则投影为 HTML 预览，并挂载到统一预览容器中。当前只在用户明确表示“生成 HTML 预览”“渲染成预览页”“把 md 做成可视化页面”“打开预览”“把产物做成 html”这类场景下触发；不要在正式产物生成时自动执行，除非上游 skill 已明确提示并得到用户确认。
---

# Preview Renderer

这个 skill 只负责一件事：

**把已经完成的正式产物渲染成统一风格的 HTML 预览。**

它不是业务分析 skill，不是体验设计 skill，也不是页面原型生成 skill。

## 核心定位

`preview-renderer` 是一个底层预览能力。

它负责：

- 识别当前有哪些 skill 产物支持预览
- 扫描 `spark-output/` 中已经存在的正式产物
- 使用统一预览容器承载多个 skill 的预览结果
- 保持整体视觉风格一致
- 把选中的 skill 内容挂载到统一 HTML 中

它不负责：

- 改写正式 Markdown 正文
- 补写缺失业务内容
- 修改任何业务 skill 的正式职责
- 依赖业务 skill 自带 preview 接入文件
- 让业务 skill 感知模板、脚本或渲染规则

## 统一预览容器

最终预览不是“一 skill 一页面”的松散模式，而是一个统一容器：

- 左侧顶部：预制所有支持预览的产物选择器
- 左侧：当前激活 skill 的章节锚点导航
- 右侧：当前激活 skill 的正文渲染结果

硬规则：

- 产物选择器属于公共层
- 左侧锚点只显示当前 skill 自己的章节
- 右侧正文只显示当前 skill 的渲染结果
- 产物选择项固定写在公共壳中，不由单个 skill 模板动态生成；某次未渲染的选项可以继续展示，但不得伪装成已生成内容
- 没有产物或未接入的 skill 可以静态展示，但不得伪装成“已可渲染”

## 触发时机

只在以下条件同时满足时执行：

1. 某个正式产物已经生成
2. 用户明确要求继续生成 HTML 预览，或上游 skill 在完成后提示并得到用户确认

不要：

- 在主链执行中自动强制渲染
- 把 HTML 预览当成正式主产物
- 因为某个 skill 支持预览，就默认每次都生成

## 上游交互方式

推荐由支持预览的 skill 在产物生成后追加一句固定提示：

```text
正式产物已生成。
如果需要，我可以继续把本次产物渲染成 HTML 预览。
```

当用户确认后，再进入 `preview-renderer`。

## 执行流程

执行时固定按以下顺序：

1. 扫描 `spark-output/` 下的正式 Markdown 产物
2. 排除 `spark-output/preview/`、`spark-output/context/`、进度预览、临时文件和非正式产物
3. 根据文件名、一级标题和关联 Context JSON 识别产物类型
4. 汇总“当前可渲染产物列表”
5. 如果存在多个可渲染目标，先让用户选择一个或多个
6. 根据 `preview-renderer` 内部集中规则选择模板、脚本或降级方式
7. 最后生成统一预览容器输出

如果只有一个可渲染目标，也不要静默执行，仍应先确认用户是否要生成预览。

## 产物识别规则

默认只扫描：

- `spark-output/*.md`

默认排除：

- `spark-output/context/`
- `spark-output/preview/`
- `spark-output/progress-preview.html`
- `spark-output/**/progress-preview.html`
- `*.tmp`
- `*.bak`
- `*.draft.md`
- 非正式主产物 Markdown

识别优先级：

1. 文件名精确匹配
2. Markdown 一级标题匹配
3. 关联 Context JSON 存在性校验
4. 用户手动选择

不得只凭正文关键词猜测产物类型。

当前支持产物：

| 产物类型 | Markdown | Context JSON | 渲染方式 | 输出 |
|---|---|---|---|---|
| 业务蓝图 | `spark-output/uxb_output.md` | `spark-output/context/uxb.json` | native-script | `spark-output/preview/uxb_preview.html` |
| 问题框定 | `spark-output/problem_framing.md` | `spark-output/context/problem-framing.json` | native-script | `spark-output/preview/problem_framing_preview.html` |
| 用户故事 | `spark-output/stories.md` | `spark-output/context/stories.json` | native-script | `spark-output/preview/stories_preview.html` |
| 角色旅程 | `spark-output/journey_analysis.md` | `spark-output/context/journey-analysis.json` | native-script | `spark-output/preview/journey_analysis_preview.html` |
| 体验蓝图 | `spark-output/experience_blueprint.md` | `spark-output/context/experience-blueprint.json` | native-script | `spark-output/preview/experience_blueprint_preview.html` |

集中资产：

| 产物类型 | 模板 / 脚本 | 规则参考 |
|---|---|---|
| 业务蓝图 | `.claude/skills/preview-renderer/assets/skills/uxb/preview_template.html` 与 `.claude/skills/preview-renderer/assets/skills/uxb/generate_preview.js` | `.claude/skills/preview-renderer/assets/skills/uxb/html_preview_execution_guide.md` |
| 问题框定 | `.claude/skills/preview-renderer/assets/skills/problem-framing/preview_template.html` 与 `.claude/skills/preview-renderer/assets/skills/problem-framing/generate_preview.js` | `.claude/skills/preview-renderer/assets/skills/problem-framing/html_preview_execution_guide.md` |
| 用户故事 | `.claude/skills/preview-renderer/assets/skills/stories/preview_template.html` 与 `.claude/skills/preview-renderer/assets/skills/stories/generate_preview.js` | `.claude/skills/preview-renderer/assets/skills/stories/html_preview_execution_guide.md` |
| 角色旅程 | `.claude/skills/preview-renderer/assets/skills/journey-analysis/journey_preview_template.html` 与 `.claude/skills/preview-renderer/assets/skills/journey-analysis/generate_preview.js` | `.claude/skills/preview-renderer/assets/skills/journey-analysis/html_preview_execution_guide.md` |
| 体验蓝图 | `.claude/skills/preview-renderer/assets/skills/experience-blueprint/preview_template.html` 与 `.claude/skills/preview-renderer/assets/skills/experience-blueprint/generate_preview.js` | `.claude/skills/preview-renderer/assets/skills/experience-blueprint/html_preview_execution_guide.md` |

统一公共壳：

- `.claude/skills/preview-renderer/assets/shell/preview_shell.html`

## 公共层与规则层

### 公共层

公共层由 `preview-renderer` 统一维护，只负责：

- 整体视觉 token
- 基础布局骨架
- 左侧产物选择器
- 左侧锚点导航容器
- 右侧正文容器
- 基础排版样式
- 通用预览运行脚本

### 规则层

规则层由 `preview-renderer` 统一维护，负责：

- 产物识别规则
- 产物到模板的匹配规则
- 产物到脚本的匹配规则
- 每类产物的降级方式
- 每类产物的输出路径

硬规则：

- 公共层负责“像同一套产品”
- 规则层负责“识别和渲染具体产物”
- 公共壳不得暴露项目名构建占位字段；项目名只允许进入最终 `<title>` 或具体内容区
- 公共壳固定维护当前支持预览的产物选项：`uxb`、`problem-framing`、`stories`、`journey-analysis`、`experience-blueprint`
- 业务 skill 不维护 `preview/manifest.json`、`render-rule.md`、模板或脚本
- 不允许为了预览要求业务 skill 反向补充接入配置
- 预览脚本只允许结构化展示既有 Markdown 与 Context JSON，不得新增业务结论、改写优先级、补写缺失验收标准或替代正式产物
- HTML 信息必须 100% 来源于正式 Markdown / Context JSON；允许改变展示结构和视觉样式，不允许改变业务语义、字段含义、优先级、状态或验收口径

## 视觉基线

统一预览容器的视觉气质默认参考：

- `preview-renderer/assets/skills/experience-blueprint/preview_template.html`
- 公共壳实际承载文件：`preview-renderer/assets/shell/preview_shell.html`

风格要求：

- 米白 / 浅暖灰背景
- 低饱和绿色主强调
- 文档阅读型布局
- 固定导航 + 右侧正文
- 轻边框、轻阴影、低噪音

这套气质属于公共层默认风格。

允许各类产物在 `preview-renderer` 的集中模板里保留局部结构差异，但不得明显偏离整体风格方向，除非用户明确要求特殊展示形态。

## 输出规则

统一输出目录：

- `spark-output/preview/`

统一容器入口：

- `spark-output/preview/index.html`

按 skill 生成的局部结果可以落到：

- `spark-output/preview/<skill-id>.html`
- 或中间注入片段

但最终用户打开的默认入口应优先指向：

- `spark-output/preview/index.html`

## 执行原则

1. 先判断能不能渲染，不要先假设自己能渲染
2. 先扫描正式产物，再让用户确认目标，再读模板或脚本
3. 先生成当前产物的章节导航数据，再挂进统一壳层
4. 先保证结构正确，再考虑局部美化
5. 如果某类产物的投影规则不完整，宁可降级为正文直出，也不要瞎补结构

## 降级规则

如果出现以下情况，允许降级：

- 模板存在，但局部结构无法完整投影
- 只有 Markdown，没有足够的 JSON 辅助
- 文件名无法稳定识别，但用户明确选择该产物

降级方式：

- 保留统一容器
- 保留当前 skill 产物选项
- 保留章节锚点
- 正文区降级为通用文档渲染

补充规则：

- `template-projection` 缺少 Context JSON 时，可降级为 Markdown 直出。
- `native-script` 缺少必要 JSON 时，不得绕过脚本临时拼装 HTML，应提示缺少必要输入。
- 模板缺失时，不现场设计新模板，只提示当前产物暂无法生成专属预览。
- 用户选择未支持的 Markdown 时，只能输出通用降级预览，并明确标注为通用预览。

禁止：

- 因为投影不完整就伪造章节
- 因为字段缺失就补造业务内容
- 因为模板缺口就现场重新设计整页结构

## 当前接入范围

当前支持专属预览的正式产物：

- `uxb`
- `problem-framing`
- `stories`
- `journey-analysis`
- `experience-blueprint`

接入原则：

- 已有正式 Markdown / Context JSON 的产物，才允许进入专属预览。
- `problem-framing`、`stories`、`journey-analysis` 走 `native-script`，由集中脚本完成结构化投影。
- `uxb`、`experience-blueprint` 走 `native-script`，由集中脚本读取正式 Markdown 并注入专属内容模板。
- `xft-design` 当前不属于正式产物投影预览范围，暂不接入。

## 边界

- 不并入 `shared-workflow`
- 不作为主链节点
- 不要求所有 skill 必须支持预览
- 不要求所有 skill 的模板结构完全统一
- 不把“统一样式”误做成“统一内容结构”
- 不在没有用户确认时自动生成 HTML

## 接入补充约束

- 业务 skill 不再提供 `preview/manifest.json` 或 `render-rule.md`。
- 模板、脚本和规则说明等正式预览资产统一收口到 `preview-renderer/assets/skills/`。
- `journey-analysis` 这类依赖脚本的产物，必须复用 `preview-renderer/assets/skills/` 中登记的正式脚本入口，不得绕过。
- 原 skill 内不得继续保留第二套 HTML 预览模板、脚本或执行细则副本。
