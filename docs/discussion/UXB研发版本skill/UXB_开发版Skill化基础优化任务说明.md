# UXB 开发版 Skill 化基础优化任务说明

> 本文档用于交给 AI Code / Codex 执行项目优化。  
> 目标是：**先优化开发版 UXB 的可维护性，同时为未来分发版 Skill 铺基础**。  
> 当前不要求完成完整 `.claude/skills/uxb/` Skill，也不要求把项目打包成分发版。
>
> 如果执行过程中发现本文档与现有项目实现存在冲突，请优先遵守现有主链路可运行原则，并基于实际代码做最小、安全、可回退的调整。不要为满足本文档而破坏当前项目运行。

---

## 1. 优化目标

当前项目已经是一个文档驱动型执行项目，核心结构包括：

```text
packages/    执行中枢
knowledge/   业务知识
specs/       规则真源
templates/   固定模板
projects/    项目产物
memory/      长期经验沉淀
```

本次优化目标：

1. 让路径入口可配置，但保留当前默认目录结构。
2. 让 `packages/` 内部统一通过路径 helper 获取目录。
3. 保持 CLI 命令稳定，为后续 Skill 调用做准备。
4. 把“知识与执行逻辑分离”等开发规则写入 `AGENTS.MD`。
5. 新增未来分发版 Skill 的打包入口占位，但不实现完整打包。

---

## 2. 本次不做

本次不要做以下事情：

```text
不创建完整分发版 Skill
不把 packages/ 移入 .claude/skills/uxb/
不把 knowledge/ 整包复制进 Skill
不大改 task_card 协议
不重构主链路阶段
不改变现有 CLI 使用方式
不破坏 python -m packages 的执行入口
```

---

## 3. 优化项一：路径入口集中配置化

### 3.1 修改范围

优先修改：

```text
packages/common.py
```

### 3.2 目标

让项目在没有任何环境变量时，继续使用当前默认目录：

```text
projects/
knowledge/
specs/
templates/
memory/
examples/
```

但允许后续通过环境变量覆盖路径。

### 3.3 建议新增环境变量

```text
UXB_ROOT
UXB_PROJECTS_DIR
UXB_KNOWLEDGE_DIR
UXB_SPECS_DIR
UXB_TEMPLATES_DIR
UXB_MEMORY_DIR
UXB_EXAMPLES_DIR
```

### 3.4 建议新增 helper

在 `packages/common.py` 中新增或补齐：

```python
get_repo_root()
get_projects_root_dir()
get_project_dir(project_id)
get_project_source_dir(project_id)
get_project_workspace_dir(project_id)
get_project_runtime_dir(project_id)
get_project_preview_dir(project_id)
get_project_exports_dir(project_id)
get_project_gates_dir(project_id)
get_project_remediation_dir(project_id)
get_project_memory_dir(project_id)

get_knowledge_root_dir()
get_specs_root_dir()
get_templates_root_dir()
get_memory_root_dir()
get_examples_root_dir()
```

### 3.5 实现原则

- 如果环境变量不存在，必须回退到当前默认路径。
- 不要改变现有项目目录结构。
- 不要改变现有产物输出位置。
- 路径返回统一使用 `Path`。
- 允许相对路径，但内部最好解析为稳定路径。
- 不要让配置化影响当前开发版运行。

---

## 4. 优化项二：packages 统一走路径 helper

### 4.1 目标

`packages/` 内部不要再直接拼接顶层目录名。

### 4.2 禁止模式

后续新增或修改代码时，避免直接写：

```python
get_repo_root() / "knowledge"
get_repo_root() / "specs"
get_repo_root() / "templates"
get_repo_root() / "projects"
get_repo_root() / "memory"
get_repo_root() / "examples"
```

也避免直接写：

```python
Path("specs/xxx.md")
Path("templates/xxx.md")
Path("knowledge/xxx.md")
```

### 4.3 推荐模式

统一使用：

```python
get_knowledge_root_dir()
get_specs_root_dir()
get_templates_root_dir()
get_projects_root_dir()
get_memory_root_dir()
get_examples_root_dir()
```

### 4.4 处理方式

本次可以做轻量替换：

- 优先替换明显的顶层目录拼接。
- 对 task_card 中已经存在的 repo-relative 路径，暂时保留兼容。
- 不要为了完全替换而大改协议解析逻辑。
- 若某些地方必须保留字符串路径，请加注释说明原因。

---

## 5. 优化项三：保持 CLI 命令稳定

### 5.1 原则

当前 CLI 入口继续保持：

```bash
python -m packages <command> <project-id>
```

不要改成调用内部文件。

### 5.2 必须保持可用的命令

至少保持以下命令不变：

```bash
python -m packages bootstrap <project-id>
python -m packages assemble <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
python -m packages archive <project-id>
python -m packages preview <project-id>
python -m packages run-main <project-id>
```

### 5.3 后续 Skill 调用原则

未来 `.claude/skills/uxb/` 只应该调用稳定 CLI，例如：

```bash
python -m packages run-main <project-id>
```

不要在 Skill 中直接调用：

```bash
python packages/context_assemble/core.py
python packages/generation/core.py
```

---

## 6. 优化项四：补充 AGENTS.MD 开发规则

### 6.1 目标

在项目根目录的 `AGENTS.MD` 中补充长期开发规则。

如果已有 `AGENTS.MD`，请在合适位置追加。  
如果没有，请创建。

### 6.2 建议追加内容

```md
## 路径与目录规则

1. 所有顶层路径必须通过 `packages/common.py` 中的统一 helper 获取。
2. 禁止在业务模块中直接硬编码 `projects/`、`knowledge/`、`specs/`、`templates/`、`memory/`、`examples/` 等顶层目录。
3. 新增目录类型时，必须先在 `packages/common.py` 增加统一 helper，再由业务模块调用。
4. 路径配置化必须保留当前默认目录结构，不得破坏开发版本地运行。

## 能力模块边界规则

1. `packages/` 只负责执行逻辑、流程编排、校验、归档、预览等工程能力。
2. `knowledge/` 负责业务知识、设计知识、原则知识，不应被写死进执行逻辑。
3. `specs/` 是正式规则真源，`templates/` 是产物模板，两者应可被替换、裁剪或打包。
4. 允许默认业务领域配置，但必须可替换，不得把某个业务域逻辑硬编码为唯一逻辑。
5. 新增能力时优先保持模块独立，不要把多个阶段逻辑混写在同一模块中。
```

### 6.3 注意

这部分是开发纪律，不是运行逻辑。  
它不会直接改变项目行为，但能约束后续 AI Code 的代码生成方式。

---

## 7. 优化项五：新增未来打包入口占位

### 7.1 新增文件

建议新增：

```text
tools/build_skill_package.py
```

如果没有 `tools/` 目录，请创建。

### 7.2 当前文件职责

本次只做占位，不要求实现完整打包。

文件内容可以包含：

```python
"""
Build UXB distributable Skill package.

This is a reserved entry for future packaging.

Current project remains development-mode:
- packages/ stays at repository root
- knowledge/ stays at repository root
- .claude/skills/uxb/ may be added later as a thin Skill entry

Future distribution-mode may package selected specs, templates,
knowledge packs, scripts, and runtime adapters into dist/uxb-skill/.
"""

from __future__ import annotations


def main() -> int:
    print("build_skill_package is reserved for future distribution packaging.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 7.3 注意

- 不要让它参与当前主链路。
- 不要让它影响 `python -m packages`。
- 不要自动复制或移动现有目录。
- 它只是未来分发版 Skill 的入口占位。

---

## 8. 验收标准

完成后需要满足：

### 8.1 当前开发版不受影响

以下命令仍可运行：

```bash
python -m packages capabilities-list
python -m packages sample-check
```

如项目内已有 demo task，也可继续运行：

```bash
python -m packages validate <已有 project-id>
python -m packages run-main <已有 project-id> --skip-preview
```

### 8.2 默认路径不变

不设置任何环境变量时，仍然使用：

```text
projects/
knowledge/
specs/
templates/
memory/
examples/
```

### 8.3 可被环境变量覆盖

至少验证一种路径覆盖方式，例如：

```bash
UXB_PROJECTS_DIR=/tmp/uxb-projects python -m packages bootstrap test-task
```

如果当前环境不方便验证绝对路径，也至少保证代码结构支持覆盖。

### 8.4 不破坏现有协议

不得强制要求修改：

```text
projects/<project-id>/source/task_card.md
projects/<project-id>/workspace/
projects/<project-id>/runtime/
```

### 8.5 不引入重 Skill 结构

本次不要求新增：

```text
.claude/skills/uxb/SKILL.md
.claude/skills/uxb/scripts/run.sh
```

如果确实新增，也只能作为薄入口，不得把 `packages/` 整体移动进去。

---

## 9. 推荐执行顺序

```text
1. 修改 packages/common.py，补齐路径配置 helper
2. 替换 packages 中明显的顶层目录硬编码
3. 确认 python -m packages 入口不变
4. 补充或创建 AGENT.MD
5. 新增 tools/build_skill_package.py 占位
6. 运行基础验证命令
```

---

## 10. 最终目标判断

完成本次优化后，项目应保持：

```text
开发版继续正常维护
packages 仍是独立执行引擎
knowledge 仍是独立知识资产
未来可以新增 .claude/skills/uxb/ 作为薄 Skill 入口
未来可以通过 tools/build_skill_package.py 生成分发版 Skill
```

核心原则：

> 当前不做重分发版，只让开发版具备未来可打包能力。
