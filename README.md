# 内网 Skill 与知识发布源

`only-x-cp` 用于维护和交付内网的业务 Skill 与知识正文。需求审查到页面规格以 Markdown 交接，内网运行时的知识检索由宿主提供。

## 准备交付

1. 将 [`knowledge-import/`](knowledge-import/) 下的 Markdown 正文整体导入内网知识库。
2. 从 [`.agents/skills/`](.agents/skills/) 选择需部署的业务 Skill，按各自目录打包并注册，保留包内结构。[`knowledge-wiki`](.agents/skills/knowledge-wiki/SKILL.md) 用于源分支的知识维护。
3. 使用同一需求的样例核对输入文件、知识检索与产物交接。旅程渲染需要宿主能运行随包 Python 脚本。归档需要宿主提供已授权的长期存储及按编号读回能力。

### 上传 Skill 时让内网 AI 写入知识库绑定的提示词

在内网平台上传 Skill 并选择知识库后，将以下提示词交给平台 AI。

```text
为指定 Skill 写入知识库绑定。绑定句使用以下格式：

使用 `mcp__xsearch-tools__xsearch` 工具指定 `kbNames=['<知识库名称>']`，在知识库「<知识库别名>」中检索。

将占位符替换为平台提供的实际值：
- <知识库名称>：知识库的唯一标识，按原值填写，例如 1800710491bea3dd。
- <知识库别名>：知识库的通俗名称，例如「薪福通设计知识库」。

填充示例：
使用 `mcp__xsearch-tools__xsearch` 工具指定 `kbNames=['1800710491bea3dd']`，在知识库「薪福通设计知识库」中检索。

写作要求：
1. 绑定句只包含工具名、参数、知识库唯一标识和别名。
2. 查询时机、查询内容、检索词、证据是否充分、知识优先级、适用条件、例外、冲突和缺口，均沿用 Skill 现有规则。
3. 保持 Skill 原有规则和结构。绑定句只新增一段，同一知识库只绑定一次。

写入位置：
在 `SKILL.md` 中找到现有的知识消费、知识依据或业务知识锚定段落，紧接第一段知识判断规则之后，将绑定句独立成段。若具体规则写在随包参考中，则放在 `SKILL.md` 引用该参考的段落之后。若该 Skill 的任务规则没有知识库消费需求，跳过写入。
```

## 使用方式

[PRD Review](.agents/skills/prd-review/SKILL.md) 在阻断关闭后生成正式需求基线 `requirements_baseline.md`。由用户或宿主把本轮基线传给 [Page Spec](.agents/skills/page-spec/SKILL.md)，生成 `page_spec.md`。也可明确传入原始需求或设计材料。UXB 和 Journey Analysis 按需使用。

## 项目结构

| 目录 | 用途 |
| --- | --- |
| `knowledge-import/` | 内网发布的权威知识正文 |
| `.agents/skills/` | 业务 Skill 和源分支维护规则 |
| `spec/` | 内网适配、讨论与实施记录 |

增量更新可按时间、主题或记录提取，导入后应核对正文的新增、替换和删除结果。源记录见 [知识更新记录](.agents/skills/knowledge-wiki/knowledge-changes.md)。
