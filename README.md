# 页面设计 Skill 工作流

`only-uxb` 是本地页面设计工作流分支。从明确提供的需求材料出发，通过 PRD 审查和页面方案推导，产出可交付的 Markdown 页面规格。

## 快速开始

1. 在能使用本仓库 Skill 的 AI 工作区中打开本分支，提供需求文件、附件或正文。
2. 需要梳理需求闭环时，启动 [PRD Review](.agents/skills/prd-review/SKILL.md)。存在阻断问题时先确认，全部关闭后生成 `spark-output/requirements_baseline.md`。
3. 使用 [Page Spec](.agents/skills/page-spec/SKILL.md) 承接同一需求的正式基线，或使用明确指定的需求与设计材料，生成 `spark-output/page_spec.md`。

[UXB](.agents/skills/uxb/SKILL.md) 和 [Journey Analysis](.agents/skills/journey-analysis/SKILL.md) 可按需用于体验策略和旅程分析。主链的页面交付是 Page Spec Markdown。

## 项目结构

| 目录 | 用途 |
| --- | --- |
| `.agents/skills/` | Skill 定义、规则和参考资料 |
| `.agents/skills/knowledge-wiki/knowledge/` | 本地业务与设计知识 |
| `shared-workflow/` | 工作流关系、交接说明和进度预览 |
| `input/` | 存放供用户指定的输入材料 |
| `spark-output/` | 正式产物和按需生成的预览 |
| [`spec/`](spec/README.md) | 讨论结论和实施文档的归档规范 |

## 进度与预览

如需手动刷新进度页，在仓库根目录运行 `node shared-workflow/generate-progress-preview.js`，再打开 `shared-workflow/progress-preview.html`。进度页展示产物完成情况。需要将正式产物渲染成 HTML 时，使用 [Preview Renderer](.agents/skills/preview-renderer/SKILL.md)。
