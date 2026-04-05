# wiki

本目录用于存放经整理、可持续维护、可跨任务复用的知识页。

它是当前仓库在 `knowledge/business/` 与 `knowledge/guidelines/` 之外新增的知识编译层。

## 目录职责

- `entities/`：实体页
- `concepts/`：概念页
- `topics/`：专题页
- `relations/`：关系页
- `indices/`：索引页

## 与其他目录的关系

- `knowledge/business/`：保留领域知识包真源与稳定专题材料
- `knowledge/guidelines/`：保留设计原则与通用指南
- `knowledge/wiki/`：承接跨资料归纳、长期维护、关系链接、冲突标注

## 维护原则

- 以页为单位持续迭代
- 保留来源
- 保留边界
- 显式保留 `[GAP]` 与 `[CONFLICT]`
- 不把 Wiki 页写成任务交付件

## 参考文档

- `docs/architecture/llm_wiki_adoption.md`
- `docs/sdd/06_wiki_page_spec.md`
- `docs/runbook/wiki_compilation_flow.md`
