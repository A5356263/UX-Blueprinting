# 内网 Skill 与知识发布源

`only-x-cp` 用于维护和交付内网的业务 Skill 与知识正文。需求审查到页面规格以 Markdown 交接，内网运行时的知识检索由宿主提供。

## 准备交付

1. 将 [`knowledge-import/`](knowledge-import/) 下的 Markdown 正文整体导入内网知识库。
2. 从 [`.agents/skills/`](.agents/skills/) 选择需部署的业务 Skill，按各自目录打包并注册，保留包内结构。[`knowledge-wiki`](.agents/skills/knowledge-wiki/SKILL.md) 用于源分支的知识维护。
3. 使用同一需求的样例核对输入文件、知识检索与产物交接。旅程渲染需要宿主能运行随包 Python 脚本。归档需要宿主提供已授权的长期存储及按编号读回能力。

## 使用方式

[PRD Review](.agents/skills/prd-review/SKILL.md) 在阻断关闭后生成正式需求基线 `requirements_baseline.md`。由用户或宿主把本轮基线传给 [Page Spec](.agents/skills/page-spec/SKILL.md)，生成 `page_spec.md`。也可明确传入原始需求或设计材料。UXB 和 Journey Analysis 按需使用。

## 项目结构

| 目录 | 用途 |
| --- | --- |
| `knowledge-import/` | 内网发布的权威知识正文 |
| `.agents/skills/` | 业务 Skill 和源分支维护规则 |
| `spec/` | 内网适配、讨论与实施记录 |

增量更新可按时间、主题或记录提取，导入后应核对正文的新增、替换和删除结果。源记录见 [知识更新记录](.agents/skills/knowledge-wiki/knowledge-changes.md)。
