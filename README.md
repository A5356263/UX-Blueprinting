# 设计工作台

DeepSeek Harness 0.2.2-rc.1 组合包。个人设计工作台：用 Skill 卡片发起任务，在右栏看动态、对话和下一步，在「沉淀」里回看任务产物。

## 安装

- 发布或验收：`npm pack --pack-destination out`，用生成的 tgz 从「添加插件」安装；
- 开发调试：支持目录链接的源码版 Web 或开发版 Desktop 可直接指向本目录；
- 安装包已含客户端产物，不需要安装期构建；改动 Host 代码后需重启 Harness。

## 使用形态

- 顶部：任务 / 沉淀、工作区、重置；
- 任务页：三组 Skill 卡片，点卡片或「使用 Skill」只回填底部输入，点「执行任务」才创建任务；
- 右栏：任务头（ID/状态/新建/暂停/结束/恢复/重命名）、动态/对话、下一步；
- 沉淀：全部任务按时间倒序，支持状态、Skill、关键词筛选；
- 个人使用，不做多人协作。

## 任务与产物

- 一个任务一个目录：
  ```
  spark-output/design-workbench/<taskId>/
    manifest.json
    prd-review.md
    page-spec.md
  ```
- 同一任务同一 Skill 重跑覆盖，不做版本堆积；
- 正式产物只写入任务目录；不要直接写 `spark-output/` 根目录；
- 上游变更后下游标记「可能过期」，不自动重跑。

## 范围

安装包包含 20 个可注册 Skill，全部只输出 Markdown：

- 设计：board、edge、journey-analysis、journey-metrics、knowledge-wiki、page-spec、prd-review、problem-framing、solution-swimlane、stories、uxs。
- 分析：objective-data-analysis、subjective-feedback-analysis、experience-heuristic-analysis、evidence-govern、root-cause-synthesis、business-impact、outcome-validation-recheck、evidence-archive、data-visualization。

## 工具

- `submit_design_artifact`：必须带 `taskId`；只接受 active 任务；
- `design_next_steps`：查询下一步；
- `read_design_reference`：读取插件内参考资料。

## 已知边界

- 会话复用：任务可复用当前会话，动态/对话按任务事件段过滤；
- 任务完成后需恢复才能继续执行；
- 轻量代理只支持文字 + 技能标签 + 附件；不支持 @ 文件、斜杠命令、模型选择；
- 文件上传走 DSH 已有上传通道；
- 固定使用 DSH 主题 token，浅色暖白、深色自适应。
