---
name: preview-renderer
description: >
  统一预览渲染 Skill。用于在正式产物已经生成后，把支持预览的 skill 产物按各自模板与渲染规则投影为单产物 HTML 预览，并生成统一卡片式预览目录页。当前只在用户明确表示“生成 HTML 预览”“渲染成预览页”“把 md 做成可视化页面”“打开预览”“把产物做成 html”这类场景下触发；不要在正式产物生成时自动执行，除非上游 skill 已明确提示并得到用户确认。
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
- 使用各产物自己的模板生成单产物 HTML 预览页
- 生成 `spark-output/preview/index.html` 卡片式目录页
- 保持整体视觉风格一致
- 告诉用户哪些预览已生成、哪些待生成、点击去哪里

它不负责：

- 改写正式 Markdown 正文
- 补写缺失业务内容
- 修改任何业务 skill 的正式职责
- 依赖业务 skill 自带 preview 接入文件
- 让业务 skill 感知模板、脚本或渲染规则

## 统一预览入口

最终预览入口是卡片式目录页：

- 目录页路径：`spark-output/preview/index.html`
- 单产物预览页路径：`spark-output/preview/<skill>_preview.html`
- 目录页只展示状态卡片和跳转入口
- 单产物预览页继续使用各自的阅读壳和章节导航

硬规则：

- `index.html` 只能由 `assets/shell/generate_index.js` 生成
- 不得复制某个单产物 HTML 覆盖 `index.html`
- 目录页不得读取、抽取或合并单产物 HTML 正文
- 目录页不得承担主链推荐、业务分析或产物重写职责
- 某个产物未生成 HTML 时，目录页只展示“待生成预览”，不得伪装成可点击内容

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

1. 扫描支持产物的正式 Markdown、专属脚本和 HTML preview 状态
2. 输出当前预览状态表，区分“已生成预览”“可生成但尚未生成”“缺少正式 Markdown”“缺少脚本”
3. 如果存在多个可生成但尚未生成的目标，先让用户选择一个或多个
4. 用户选择后，根据 `preview-renderer` 内部集中规则调用对应 `generate_preview.js`
5. 所有选中单产物 HTML 生成后，执行 `assets/shell/generate_index.js`
6. 输出统一目录入口和本次生成的单产物入口
7. 回显“预览不会改变主链状态”

如果只有一个可渲染目标，也不要静默执行，仍应先确认用户是否要生成预览。

执行前固定输出状态表：

```text
当前预览状态：
- 问题框定：Markdown 已存在 / HTML 已生成
- 用户故事：Markdown 已存在 / HTML 未生成
- 角色旅程：Markdown 已存在 / HTML 已生成
- 体验蓝图：Markdown 已存在 / HTML 已生成
- 业务蓝图：Markdown 未检测到 / HTML 未生成
```

如果存在 Markdown 已存在但 HTML 未生成的产物，必须提示用户可以选择编号补齐，不得直接说“所有产物预览均已生成”。

执行完成后固定说明：

```text
HTML 预览已生成。
统一入口：spark-output/preview/index.html
本次生成：{列表}

附加说明：
预览不会改变主链状态。
请继续使用上一个业务 skill 完成时给出的主链下一步。
```

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
3. 用户手动选择

不得只凭正文关键词猜测产物类型。

Context JSON 只允许作为目录页状态展示，不得作为是否能生成 HTML 预览的前置条件。

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
- `.claude/skills/preview-renderer/assets/shell/generate_index.js`

## 公共层与规则层

### 公共层

公共层由 `preview-renderer` 统一维护，只负责：

- 整体视觉 token
- 单产物阅读壳
- 卡片式目录页生成器
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
- 目录页固定维护当前支持预览的产物卡片：`uxb`、`problem-framing`、`stories`、`journey-analysis`、`experience-blueprint`
- 业务 skill 不维护 `preview/manifest.json`、`render-rule.md`、模板或脚本
- 不允许为了预览要求业务 skill 反向补充接入配置
- 预览脚本只允许结构化展示既有 Markdown，不得新增业务结论、改写优先级、补写缺失验收标准或替代正式产物
- HTML 信息必须 100% 来源于正式 Markdown；允许改变展示结构和视觉样式，不允许改变业务语义、字段含义、优先级、状态或验收口径

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

统一目录入口：

- `spark-output/preview/index.html`

按 skill 生成的单产物预览页落到：

- `spark-output/preview/<skill>_preview.html`

最终用户打开的默认入口应优先指向：

- `spark-output/preview/index.html`

## 执行原则

1. 先判断能不能渲染，不要先假设自己能渲染
2. 先扫描正式产物，再让用户确认目标，再读模板或脚本
3. 先生成选中的单产物 HTML，再刷新卡片式目录页
4. 先保证结构正确，再考虑局部美化
5. 如果某类产物的投影规则不完整，宁可降级为正文直出，也不要瞎补结构

## 降级规则

如果出现以下情况，允许降级：

- 模板存在，但局部结构无法完整投影
- 文件名无法稳定识别，但用户明确选择该产物

降级方式：

- 保留单产物预览页
- 保留当前 skill 的章节锚点
- 正文区降级为通用文档渲染
- 生成或刷新卡片式目录页

补充规则：

- 缺少 Context JSON 时，不得阻断 HTML 预览生成。
- 现有 `native-script` 不得把 Context JSON 作为预览生成的必要输入。
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

- 已有正式 Markdown 的产物，才允许进入专属预览。
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
