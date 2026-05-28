# 知识使用说明

当知识问答、诊断咨询、任务成型需要用到仓库知识时，用这份说明。

## 目标

用尽量小的读取范围，找到当前问题真正需要的知识，不把 `knowledge/` 整棵树一股脑读进来。

## 核心规则

- 先判断当前到底要确认什么，再决定读什么
- 从导航、summary、README、index 开始，不要一上来直翻 raw
- 知识是为了支撑判断，不是为了把文件内容搬给用户
- 如果现有知识不足，直接说明不确定点

## 知识问答态怎么读

优先处理这些问题：

- 操作方式
- 规则解释
- 前置条件
- 流程关系
- 状态含义
- 模块依赖

默认步骤：

1. 从 `knowledge/wiki/index.md` 开始
2. 先找导航、route card、summary、索引、领域入口文档
3. 只有 summary 不够时，才继续往 raw 深挖
4. 如果仍不能确认，就明确告诉用户哪些点还不确定

## 读取入口

从这里开始：

```text
knowledge/wiki/index.md
```

然后按当前仓库结构逐层缩小范围，比如：

- navigation 页面
- route card
- index
- summary
- 业务 README

不要假设旧目录结构还有效，以当前仓库实际结构为准。

## Knowledge 文件边界补充

读取知识时，先区分这些文件角色：

- `knowledge/wiki/index.md`：全局知识入口，用于初步定位领域和 summary
- `knowledge/wiki/summaries/**`：AI 路由卡，用于判断某份 raw 是否值得进入后续消费
- `knowledge/raw/业务/<领域>/README.md`：领域内二级路由，用于命中领域后继续缩小范围
- `knowledge/raw/业务/<领域>/00_领域概述.md`：领域事实总览，用于理解领域定义、边界、对象关系和上下游依赖
- `knowledge/templates/**`：知识入库模板，只服务知识维护和新领域建档，不参与 UXB 主链路知识消费

使用原则：

1. 不把领域 README 当成正式业务事实来源。
2. 不把 `00_领域概述.md` 当成目录维护说明。
3. 不在正式任务知识选择中选择 `knowledge/templates/**`。
4. 只有在做知识入库、知识维护或新建领域时，才读取 templates。
5. 如果已通过 summary 明确命中具体 raw，应优先选择具体文件，不停留在入口型 README。

## 范围控制

不要为了省事默认读取整个 `knowledge/`。

缩小范围时优先看这些线索：

- 业务对象
- 用户角色
- 用户动作
- 状态变化
- 异常场景
- 模块名
- 页面名
- 流程名
- 权限、审批、配置、反馈、文案类问题

## Summary First, Raw Later

优先读：

- summary 文件
- route card
- 模块描述
- 概览入口

只有下面这些情况再读更细的 raw：

- summary 不够
- 需要证据
- 用户要求可追溯来源

## 知识消费深度

正式做知识选择前，先判断这次需要读到什么深度：

- `L1 领域定位 / 方向判断`：只读 `index + summary + 领域 README`，不直接选择 raw。
- `L2 UXB 路由判断 / 轻量蓝图判断`：summary 为主，领域 README 辅助；只有需要确认具体规则、对象关系、状态、流程、字段、路径、异常或边界时，才选择少量 raw。
- `L3 正式 facts / business / experience 生成`：可以消费 raw，但 raw 必须已经由 summary / README 路由命中，并写入 `uxb_route_decision.json`。

## 正式任务前的知识选择

当用户确认进入正式 UXB 主链路时，知识不再由代码自动选择，而是由 UXB 先写入：

- `projects/<project-id>/runtime/uxb_route_decision.json`

判断阶段只做资料选择，不做深度消费。

要求：

1. 先从 `knowledge/wiki/index.md`、summary、route card 或领域入口缩小范围
2. 先回答“这次到底要确认什么问题”，再选 ref
3. 优先选择后续正式产物会直接消费的最小文件集合
4. 每个 ref 都必须写入 `knowledge_selection.selection_reasons`
5. 如果说不清为什么需要这份资料、支撑哪个判断、影响哪个正式输出，就不要选
6. 不为了保险全量选择业务知识
7. 不为了证明“参考过指南”而选设计指南
8. raw 只在 summary 不足、需要证据或需要关键细节时选择
9. 不把 `knowledge/templates/**` 选进 `uxb_route_decision.json` 的 `business_refs` 或 `guideline_refs`

### Raw 选择必要性

`business_refs` / `guideline_refs` 默认优先选择 summary、领域 README 或入口型知识。

如果选择 `knowledge/raw/**`，`selection_reasons` 至少要说明：

1. 该 raw 由哪个 summary / README / index 线索命中。
2. 该 raw 主要支撑 facts / business / experience 中哪个阶段。
3. 该 raw 支撑什么具体判断点。

不要因为“保险”“可能有用”“了解背景”直接选择大量 raw。

### 什么时候优先选文件级 ref

下面这些情况，优先选文件级 ref，不要只停留在入口文档：

- 已经知道要确认的是哪条规则、哪类对象关系、哪段流程
- 已经能判断后续 facts / business / experience 会直接用到某个具体文件
- 已经不是在“找方向”，而是在“确认判断”

入口型 ref 更适合：

- 先定位领域
- 先确认有哪些候选知识
- 当前还不能确定具体会用哪一份资料

### 什么时候该选 guideline

不是看到“体验”就默认选 guideline。

更适合选 guideline 的情况：

- 后续体验产物需要解释复杂表单、列表、导航或信息结构
- 明显需要设计异常反馈、报错、阻断或状态说明
- 明显需要处理信息层级、可读性、可用性

如果只是先做业务边界判断，且体验承接还没有深入到这些问题，可以不选 guideline。

## 用户纠错时的处理

如果用户纠正了现有知识：

1. 先修正当前回答
2. 不直接覆盖 `knowledge/`
3. 如果这条纠正看起来是稳定规则，可以自然询问是否记入知识候选区
4. 用户确认后，再创建候选文件
5. 候选未确认前，不当成正式稳定知识

不要把聊天原文直接写进 knowledge，也不要一边纠错一边直接触发入库。

## 在回答里怎么使用知识

优先把知识转成用户能直接理解的判断，比如：

```text
按当前项目知识看，这更像是状态说明没有交代清楚，不只是按钮位置的问题。
```

避免：

- 大段贴文件内容
- 机械报文件路径
- 把知识库当搜索结果清单扔给用户

如果用户明确要来源，再补具体文件线索。
