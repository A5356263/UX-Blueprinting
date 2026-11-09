# 设计工作台

DeepSeek Harness 0.2.2-rc.1 组合包。启用后从左侧打开「设计工作台」，选择已有工作区，再选择要运行的 Skill。插件负责流程状态、下一步、确认、产物登记与预览；Skill 只提供专业推理规则和 Markdown 产物结构。

## 安装

- 发布或验收：在仓库根目录执行 `npm pack --pack-destination out`，用生成的 `out/dsh-ux-blueprinting-0.1.0.tgz` 从「添加插件」安装；也可使用固定提交的 Git 地址。
- 开发调试：在支持目录链接的源码版 Web 或开发版 Desktop 中直接指向本目录。安装包已含客户端产物，不需要安装期构建；改动 Host 代码后需重启 Harness 才会加载新的模块。

## 范围

安装包包含 20 个可注册 Skill：

- 设计：board、edge、journey-analysis、journey-metrics、knowledge-wiki、page-spec、prd-review、problem-framing、solution-swimlane、stories、uxb。
- 分析：objective-data-analysis、subjective-feedback-analysis、experience-heuristic-analysis、evidence-govern、root-cause-synthesis、business-impact、outcome-validation-recheck、evidence-archive、data-visualization。

所有 Skill 只输出 Markdown，不产出 JSON、schema、脚本结果或字段清单。预览由插件统一渲染。

## 运作中枢

- 可执行 Skill 与下一步由 `shared-workflow/skill-graph.json` 和 `runtime/orchestration.js` 计算；模型可通过 `design_next_steps` 查询，Skill 正文不再保存 Handoff 或固定下一步。
- 任务状态、修订号、防重复提交、取消与重试在 `runtime/state.js`；产物登记、哈希校验和工作区隔离在 `runtime/workbench.js`。
- 阶段执行通过固定 preset 的子 Agent 完成；每个工作区只建立一条内部会话，空闲 2 秒后自动归档，下次执行前恢复。
- 预览由 `runtime/preview.js` 把登记产物渲染为独立 HTML，界面中的「预览」按钮直接打开。

## 产物位置

任务状态与正式产物位于所选工作区的 `spark-output/design-workbench/<任务>/`，产物文件名为 `<执行标识>-<skill>.md`。人工改动会被内容哈希校验拒绝。

## 已知边界

- 工作台直接使用 Node 文件 API 读写选定工作区：DSH 的 `ctx.fs` 契约不含创建目录和递归操作，无法承载“每个任务一个目录”的布局。所有路径都经过工作区包含校验，任务目录拒绝符号链接，写入使用临时文件加原子替换。
- 工作台 HTTP 路由注册在 DSH 已认证的 `/api` 连接通道上。处理函数只接受已登记的工作区标识，身份由通道认证，不取自请求体。
- 阶段执行器通过 `subagents` 在固定 preset 内运行；取消会中断正在运行的子 Agent，迟到回执不会登记产物。

## 验证

- 20 个 Skill 均可解析，正文不含 JSON、schema、脚本结果或固定下一步。
- 阶段引擎按 skill-graph 计算可执行项；状态机、产物登记与预览渲染通过语法检查和基础状态流转验证。
