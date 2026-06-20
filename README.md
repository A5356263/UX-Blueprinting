# 体验蓝图构建思路

一个轻量的 prompt 驱动型体验设计工作站。

目标是用两个 Skill 完成从需求文档到体验蓝图的全链路：分析需求事实、构建业务判断、输出体验设计方案。不依赖 CLI 工程管道，由 AI 直接读取 Skill 定义并执行。

## 架构

```
input/                      ← 用户输入（需求文档、背景材料）
knowledge/                  ← 业务知识 + 设计准则（两个 Skill 共享）
.claude/skills/
  ├── uxb/                  ← 需求定案 Skill（分析 + 统一文档输出）
  └── experience-blueprint/ ← 体验蓝图 Skill（交互设计方案输出）
_shared/                    ← 跨 Skill 协调（流转关系、JSON 规范、交接模板）
spark-output/               ← 输出层
  ├── context/              ← 结构化 JSON（uxb.json、experience_blueprint.json）
  └── ...                   ← 文档产出（uxb_output.md、experience_blueprint.md）
```

## 两个 Skill

**UXB（需求定案）**：读取需求文档 + 业务知识，经过分析对话后输出统一的需求定案文档（`uxb_output.md`，10 章结构）和结构化数据（`uxb.json`）。负责事实提炼、价值论证、角色功能定义、规则状态梳理、体验风险预判和 GAP 管理。

**体验蓝图**：读取 UXB 产出，输出完整的体验设计方案（`experience_blueprint.md`），包含旅程图、交互流程（主/次/异常）、页面设计、状态文案和待确认问题。

Skill 之间通过 `_shared/` 定义的协议交接，不直接调用。

## 使用方式

1. 将需求文档放入 `input/` 目录
2. 触发 UXB Skill，完成分析对话，获得需求定案
3. 触发体验蓝图 Skill，读取 UXB 产出，生成体验蓝图
4. 如需 HTML 预览，可在体验蓝图 Skill 中直接生成

## 目录说明

| 目录 | 职责 |
|------|------|
| `input/` | 用户输入层，存放需求文档等原始材料 |
| `knowledge/` | 业务知识 + 设计准则，两个 Skill 共享读取 |
| `.claude/skills/` | Skill 定义文件（SKILL.md + references/） |
| `_shared/` | 跨 Skill 协调文件（skill-graph.json、context-schema.md、handoff.md） |
| `spark-output/` | 输出层，包含结构化 JSON 和文档产出 |

## 说明

- 本项目不再有 CLI 命令、工程管道或 gate/validate/coverage 硬规则
- 所有分析判断和质量自检由 Skill prompt 内置的自检清单驱动
- `knowledge/` 中的业务知识和设计准则是数据层，Skill 按需读取但不修改
