# Knowledge Wiki 子系统说明

## 1. 这是什么

本目录是当前项目里的独立 Wiki 子系统。

它不再承担“重型正式知识页编译系统”的职责，而是承担一套更轻的知识入口机制：

- 维护 `knowledge/raw/**` 作为唯一高频真源
- 为每份 raw 生成一份一对一 summary
- 维护 `index.md`、`overview.md`、`questions.md`、`log.md`
- 让主项目与 LLM 默认走 `summary-first`，必要时再回查 raw

主项目默认先消费：

- `knowledge/wiki/index.md`
- `knowledge/wiki/summaries/**`
- `knowledge/wiki/overview.md`
- `knowledge/wiki/questions.md`

主项目不默认直接消费：

- `knowledge/raw/`
- `knowledge/outputs/`
- `knowledge/scripts/`

---

## 2. 子系统和主项目的关系

### 主项目负责

- 接收需求
- 装配任务上下文
- 消费 Wiki 入口页与 summary
- 在需要证据或细节时回查 raw
- 生成主项目产物

### Wiki 子系统负责

- 管理原始来源
- 生成 mirrored summaries
- 维护入口、状态页、问题池
- 做结构性检查
- 做自动更新

一句话：

**主项目先读 summary，Wiki 子系统负责把 raw 变成稳定入口。**

---

## 3. 目录结构

```text
knowledge/
  raw/
    业务/
    设计准则/
    inbox/

  wiki/
    index.md
    overview.md
    questions.md
    log.md
    summaries/
      业务/
      设计准则/

  outputs/
    answers/
    reports/
    diagrams/
    lint/

  scripts/
    scan_raw.py
    build_summaries.py
    reindex_wiki.py
    refresh_overview.py
    refresh_questions.py
    lint_wiki.py
    update_wiki.py
    auto_update_wiki.py
    run_auto_update_wiki.ps1
    install_wiki_autoupdate_task.ps1
    uninstall_wiki_autoupdate_task.ps1

  README.md
  LLM.md
```

---

## 4. 每一层是干什么的

### raw/

原始来源层，只保存事实来源和原始规则文本。

这里放：

- 业务知识真源
- 设计指南真源
- 新进但还没整理完的文件

### wiki/

轻量 Wiki 层，也是主项目默认消费入口。

这里放：

- `summaries/`：raw 的一对一摘要页
- `index.md`：总入口
- `overview.md`：机械状态页
- `questions.md`：显式问题池
- `log.md`：维护留痕

### outputs/

结果层。

这里放：

- 查询回答
- 报告
- 图表
- lint 报告

注意：

**outputs 不是正式 Wiki 入口。**

### scripts/

工具层。

这里放：

- 扫描 raw
- 生成 summaries
- 刷新 index / overview / questions
- lint 与自动更新

注意：

**脚本只做机械任务，不做语义裁决。**

---

## 5. 基本原则

### Raw 原文不可改

AI 可以读 raw，但不能把总结覆盖回 raw 正文。

### Summary 是 AI 路由卡，不是机械摘要

summary 不是 raw 的压缩版。
summary 是 AI 的第一路由节点。
summary 用于判断：该不该读取某份 raw、为什么读取、什么时候必须回查 raw。
summary 不替代 raw，不冒充证据，不做最终业务裁决。

summary 正文结构（7 段路由）：

1. 知识定位 — 这份 raw 解决什么判断问题
2. 任务触发线索 — 哪些任务问题会触发它
3. 覆盖内容 — 覆盖的对象、能力、页面、规则、状态、风险
4. 可直接使用的稳定结论
5. 必须回查 raw 的情况
6. 缺口 / 冲突 / 不确定项
7. 邻近阅读

### 默认消费顺序

1. 从 `knowledge/wiki/index.md` 进入
2. 先读对应 summary（路由卡），判断是否命中当前任务
3. 需要细节、证据、正式判断时再回查 raw

### 一对一镜像

summary 与 raw 保持：

- 同名
- 镜像路径
- 一对一对应

### 显式保留 gaps / conflicts / questions

当 raw 或 summary 中存在：

- `[GAP]`
- `[CONFLICT]`
- `[QUESTION]`

必须显式保留，不得自动抹平。

### 重要操作必须留痕

新来源入库、批量更新、lint、人工覆盖等动作，都要写入 `wiki/log.md`。

---

## 6. 如何触发 Wiki 维护

常见命令：

- 一次性编排更新：`python knowledge/scripts/update_wiki.py --apply`
- 预览本次将更新什么：`python knowledge/scripts/update_wiki.py --dry-run`
- 只更新单个 raw 对应 summary：`python knowledge/scripts/update_wiki.py --apply --only knowledge/raw/业务/权限管理/15_页面载体语义.md`
- 持续监听 raw 并自动触发：`python knowledge/scripts/auto_update_wiki.py --run-on-start`

自动更新不会再使用 registry、block sync 或 compiled wiki page 写回机制。

---

## 7. 系统页说明

### wiki/index.md

总入口和导航页，默认只索引 `summaries/`。

### wiki/overview.md

机械状态页，只做计数、覆盖率、最近变更和显式标记统计。

### wiki/questions.md

显式未决项聚合页，只汇总 raw / summary 中已出现的 `[GAP]`、`[CONFLICT]`、`[QUESTION]`。

### wiki/log.md

维护日志。

---

## 8. 推荐维护顺序

### 新来源进入时

1. 放入 `raw/业务/`、`raw/设计准则/` 或 `raw/inbox/`
2. 生成对应 summary
3. 刷新 `index.md`
4. 刷新 `overview.md`
5. 刷新 `questions.md`
6. 写入 `log.md`

### 做健康检查时

1. 扫描 raw 与 summaries
2. 运行 lint
3. 输出 lint 报告
4. 刷新 `overview.md`
5. 写入 `log.md`

---

## 9. 本子系统不做什么

- 不再维护 `concepts / entities / topics / relations / synthesis` 默认页型
- 不再维护 registry 驱动的 heavy-sync
- 不再做 block 级 AUTO-SYNC 回写
- 不给旧机制提供兼容层
- 不让主项目默认直接消费 raw

---

## 10. 一句话结论

**Knowledge 目录是一个以 raw 为事实真源、以 summary 为 AI 路由卡的轻量知识入口系统。**

低频 AI 语义填充任务请先阅读 `knowledge/LLM.md`。
