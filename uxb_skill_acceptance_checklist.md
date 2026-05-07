# UXB Skill Acceptance Checklist

这份文档用于验收项目级 `.codex/skills/uxb` 是否符合 `docs/discussion/UXB_研发版Skill_V2正式文档.md` 的目标。

它分成两部分：

- Skill 行为验收
- mac 分发前跨平台检查

这是一份临时测试文档，后续不需要时可以直接删除。

## 1. Skill 行为验收

### 1.1 纯咨询场景

目标：验证它会先咨询，不会直接执行。

测试输入示例：

- `这个功能不好用，你帮我看看问题在哪。`
- `这个页面总感觉怪怪的，应该怎么改？`
- `这个流程是不是有问题？`

预期结果：

- 先从业务、流程、状态、反馈、文案、页面承载等角度判断问题。
- 必要时才去查 `knowledge/wiki/index.md` 和相关 summary。
- 不直接创建任务。
- 不直接运行 `python -m packages`。
- 说话是中文、大白话，不端流程术语。

### 1.2 需求评估场景

目标：验证它会先评估材料质量，不自动开工。

测试输入示例：

- `我这里有一份需求文档，你先帮我看看有没有问题。`
- `这份方案你先评估一下，别急着执行。`

预期结果：

- 先读懂材料。
- 输出业务/体验层面的初步判断。
- 指出风险、缺口、关键问题。
- 告诉用户现在是否适合整理成正式任务。
- 仍然不直接执行。

### 1.3 知识使用场景

目标：验证它会优先走知识导航，而不是整包读 `knowledge/`。

测试输入示例：

- `审批配置这里用户为什么会搞不懂？`
- `成员离职流程里最容易出体验问题的是哪一段？`

预期结果：

- 先根据关键词定位领域。
- 优先从 `knowledge/wiki/index.md`、summary、README、导航入口开始。
- 不默认扫描整个 `knowledge/`。
- 如果一个词可能对应多个业务域，会先说明歧义，必要时确认。
- 回答时用知识辅助判断，不机械引用路径。

### 1.4 任务整理场景

目标：验证它会先整理任务摘要，并等待确认。

测试输入示例：

- `这件事已经比较清楚了，你帮我整理成一个 UXB 任务。`
- `你先给我出一版任务摘要，我确认后再执行。`

预期结果：

- 输出一版任务摘要。
- 摘要应覆盖：
  - 这次要解决什么
  - 用户真正关心什么
  - 当前已知信息
  - 不确定但不阻塞的点
  - 建议做到哪一层
  - 建议任务名
  - 建议 `project-id`
- 不在用户确认前创建项目。
- 不在用户确认前写正式产物。

### 1.5 确认执行场景

目标：验证它只在明确确认后执行。

测试输入示例：

- `可以，就按这个创建任务。`
- `确认，开始执行。`
- `按这个跑一遍。`

预期结果：

- 先用自然语言说明将要做的三件事：
  - 创建任务
  - 写正式输入
  - 按主链路生成并检查产物
- 然后才调用 `python -m packages`
- 正式产物进入 `projects/<project-id>/`

### 1.6 执行失败修复场景

目标：验证它不会口头糊弄通过。

测试方式：

- 任选一个故意制造检查失败的任务

预期结果：

- 不会只在聊天里说这里有问题就算完。
- 会回到正式文件里修。
- 会重新走检查。
- 不伪造通过状态。

## 2. Skill 自检清单

每次改完 skill，都可以按下面逐项确认：

- `SKILL.md` 明确写了先咨询、后整理、确认后执行。
- 明确写了只负责使用 UXB，不负责维护 UXB。
- 没有写仓库开发规范、Code Agent 规范、完整 CLI 手册。
- 没有复制 `packages/`、`knowledge/`、`specs/`、`templates/`、`projects/`。
- 明确知识入口优先是 `knowledge/wiki/index.md`。
- 明确执行入口是 `python -m packages`。
- 明确正式产物进入 `projects/<project-id>/`。
- 有 `references/`、薄 `scripts/`、少量 `assets/`。
- `uxb.sh` 仍然只是转发，不承载业务逻辑。
- `quick_validate.py` 已通过。

## 3. mac 分发前必须验证的跨平台检查表

这部分和 skill 文案不是一回事，它主要验证仓库主链路是否能在 mac 上跑。

### 3.1 Python 入口

在 mac 上检查：

```bash
python --version
python3 --version
python -m packages --help
python3 -m packages --help
```

确认：

- 默认可用的是 `python` 还是 `python3`
- `packages` 主入口到底哪种能跑

### 3.2 最小主链路

至少验证这些命令：

```bash
python3 -m packages capabilities-list
python3 -m packages bootstrap demo-task --task-name "demo"
python3 -m packages validate demo-task
```

如果项目最终约定使用 `python`，就换成 `python` 版本再跑一次。

### 3.3 语法兼容

重点看：

- Python 版本差异
- Windows 下能跑、mac 下不能跑的语法或依赖
- shell 脚本是否假设了 Windows 环境

### 3.4 路径与文件系统

检查：

- 是否硬编码了反斜杠路径
- 是否假设了 Windows 盘符
- 是否有大小写敏感问题
- 是否依赖 PowerShell 专属行为

### 3.5 编码与文档

检查：

- UTF-8 是否统一
- Markdown 和模板文件在 mac 上读取是否正常
- shell 文件是否有可执行权限要求

### 3.6 脚本入口

对 `uxb.sh` 检查：

```bash
bash .codex/skills/uxb/scripts/uxb.sh --help
```

确认：

- mac 上是否能直接执行
- 它调用的 Python 命令是否和 mac 实际入口一致

## 4. 建议的验收顺序

1. 先做 skill 行为验收。
2. 再做本机执行验收。
3. 最后做 mac 跨平台验收。

这样可以把“skill 写得对不对”和“仓库能不能跨平台跑”分开判断。
