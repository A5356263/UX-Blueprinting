# HTML 预览执行细则

这份文件只说明体验蓝图阶段如何在 Skill 内稳定生成 HTML 预览，不引入 `packages/` 侧的新正式能力。

## 1. 原则

- HTML 预览属于 `experience-blueprint` Skill 的输出职责
- 固定复用 `preview_template.html` 的骨架，不让模型临时设计结构
- 业务蓝图和体验蓝图必须同时承接到同一个 HTML
- 缺少组件化映射时，优先完整保留章节内容，不允许漏章节

## 2. 固定输入

- `spark-output/uxb_output.md`
- `spark-output/experience_blueprint.md`
- `references/preview_template.html`

## 3. 固定输出

- `spark-output/preview/experience_blueprint_preview.html`

## 4. 执行顺序

1. 读取 `uxb_output.md`，提取业务蓝图章节
2. 读取 `experience_blueprint.md`，提取体验蓝图章节
3. 生成双面板导航项
4. 将两侧章节按固定容器映射进模板
5. 保留表格、ASCII 框图、附录和待确认问题
6. 在 Skill 内完成内容注入并输出最终 HTML

## 5. 不允许的做法

- 不允许重新设计布局
- 不允许把业务蓝图压成摘要再塞进页面
- 不允许跳过 `§0`、附录、状态表、ASCII 框图
- 不允许把生成能力外溢成当前分支的新 CLI / package 主链路
