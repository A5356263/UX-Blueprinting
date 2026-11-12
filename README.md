# 页面设计 Skill 工作流

本项目以 Skill 完成需求闭环、页面方案推导与设计文档交付。各 Skill 由用户明确触发，并按自己的规则处理状态、上下文交接和知识检索。

## 当前主链

1. `prd-review`：审查用户明确提供的 PRD，关闭阻断问题后输出 `spark-output/requirements_baseline.md`。
2. `page-spec`：读取同一需求的正式基线或用户明确指定的材料，在内部完成知识消费和页面方案推导，输出 `spark-output/page_spec.md`。正式输出不包含体验蓝图式长叙事，也不生成 Page Spec Context JSON。

`uxb` 与 `journey-analysis` 是 Page Spec 前的可选增强；是否采用由本轮用户意图和各 Skill 的输入规则决定。内网运行通过萃知获取正式知识；仓库中的 `knowledge-wiki` 用于审定原文和维护发布。其他 Skill 按自身 `SKILL.md` 的触发和输入门禁独立使用。

## 目录职责

- `.agents/skills/`：Skill 定义、执行规则与补充参考。
- `input/`：用户提供材料的存放位置；不会因文件存在而自动选择输入。
- `spark-output/`：正式产物及按需生成的预览。九个数据分析 Skill 各输出一份正式 Markdown。其他 Skill 遵循自身输出约定。
- `spec/`：讨论与执行文档。

旧体验蓝图分支保留历史链路供后续对照；本分支的正式页面交付入口为 `page-spec`。测试阶段须另行按执行文档启动。

## 内网部署

按需压缩各 Skill 目录并在内网注册。将审定的业务和设计知识原文发布到萃知，由内网 Agent 绑定正式知识空间。
