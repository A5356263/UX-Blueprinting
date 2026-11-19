# 页面设计 Skill 工作流

本项目以 Skill 完成需求闭环、页面方案推导与设计文档交付。各 Skill 由用户明确触发，并按自己的规则处理状态、上下文交接和知识检索。

## 当前主链

1. `prd-review`：审查用户明确提供的 PRD，关闭阻断问题后输出 `spark-output/requirements_baseline.md`。
2. `page-spec`：读取同一需求的正式基线或用户明确指定的材料，在内部完成知识消费和页面方案推导，输出 `spark-output/page_spec.md`。正式输出不包含体验蓝图式长叙事，也不生成 Page Spec Context JSON。

`uxb` 与 `journey-analysis` 是 Page Spec 前的可选增强，是否采用由本轮用户意图和各 Skill 的输入规则决定。各 Skill 根据自身任务判断何时查询知识及如何采用结果。

## 目录职责

- `.agents/skills/`：Skill 定义、执行规则与补充参考。
- `knowledge-import/`：本分支维护的权威知识正文，可整体导入内网知识库。
- `input/`：用户提供材料的存放位置；不会因文件存在而自动选择输入。
- `spark-output/`：正式产物及按需生成的预览。九个数据分析 Skill 各输出一份正式 Markdown。其他 Skill 遵循自身输出约定。
- `spec/`：讨论与执行文档。

旧体验蓝图分支保留历史链路供后续对照；本分支的正式页面交付入口为 `page-spec`。测试阶段须另行按执行文档启动。

## 内网部署

将 `knowledge-import/` 的 Markdown 正文整体导入内网知识库。将 `.agents/skills/` 下的业务 Skill 逐个整目录压缩并注册，保留目录结构。

日常交接使用用户或宿主明确传入的本轮 Markdown 文件。旅程渲染需要宿主能运行随包 Python 脚本。归档场景需要宿主提供获准的长期存储和按编号读回能力。

`knowledge-wiki` 留在源分支，负责维护正文和登记实际更新。需要增量更新时，可按时间、主题或记录提取，并在内网核对替换和删除结果。
