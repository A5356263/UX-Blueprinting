# 设计工作台

DeepSeek Harness 0.2.2-rc.1 组合包。启用后从左侧打开「设计工作台」：选工作区、选会话（没有就首次发送自动建），在输入框里说要做的事；插件保留执行时间线、产物和下一步。

## 安装

- 发布或验收：在仓库根目录执行 `npm pack --pack-destination out`，用生成的 tgz 从「添加插件」安装；也可使用固定提交的 Git 地址。
- 开发调试：在支持目录链接的源码版 Web 或开发版 Desktop 中直接指向本目录。安装包已含客户端产物，不需要安装期构建；改动 Host 代码后需重启 Harness。

## 使用形态

- 没有“建任务”步骤；插件页是当前会话的控制台；
- 左侧：模拟会话窗口（流水线、时间线、输入框）；
- 右侧：技能（完成/可做/锁定）与下一步（默认）；
- 输入框：上传占位在左下（P2），技能在右，路径或 URL 直接写在文字里，发送在右；
- 发送后留在当前页；底部可继续发消息，运行中排队，可停止；
- 需要完整输入能力时点「进入会话」；回来时间线继续；
- 切换或重新打开工作台时，自动恢复上次的工作区、会话和进度；右上角「重置工作台」才会清空；
- 模型完成后调用 `submit_design_artifact`，插件按“规划窗口 + Skill”覆盖当前产物并刷新右侧；

## 范围

安装包包含 20 个可注册 Skill，全部只输出 Markdown：

- 设计：board、edge、journey-analysis、journey-metrics、knowledge-wiki、page-spec、prd-review、problem-framing、solution-swimlane、stories、uxb。
- 分析：objective-data-analysis、subjective-feedback-analysis、experience-heuristic-analysis、evidence-govern、root-cause-synthesis、business-impact、outcome-validation-recheck、evidence-archive、data-visualization。

## 运作中枢

- 阶段、依赖与下一步：`shared-workflow/skill-graph.json` + `runtime/orchestration.js`；
- 会话、运行记录与产物：`runtime/workbench.js` + `runtime/state.js`；
- 产物校验：`runtime/artifacts.js`；
- 预览：`runtime/preview.js`；
- 模型工具：`submit_design_artifact`、`design_next_steps`、`read_design_reference`。

## 产物位置

一个规划窗口（会话）一个文件夹，里面每个 Skill 一个 Markdown，覆盖更新、不做版本积压：

```
spark-output/design-workbench/<会话>/
  manifest.json
  prd-review.md
  page-spec.md
  edge.md
```

- 同一个 Skill 重跑，覆盖它自己的文件；
- 新开窗口，就是新文件夹；
- 上游覆盖后，依赖它的下游会在 `manifest.json` 中标记 `stale`，右侧显示「可能过期」，不自动重跑；
- 人工改动会被内容哈希校验拒绝。

## 已知边界

- 一个会话可承载多个任务，由 AI 识别；同一个规划窗口内按 Skill 覆盖，不区分任务版本；
- 时间线是整段会话，不按任务切分；
- 轻量代理只支持文字 + 技能标签；不支持 @ 文件、斜杠命令、模型选择；草稿不与原生输入同步；
- 文件上传 P2；P1 只支持工作区路径或 URL；
- 工作台直接使用 Node 文件 API 读写选定工作区，所有路径都经过工作区包含校验。
