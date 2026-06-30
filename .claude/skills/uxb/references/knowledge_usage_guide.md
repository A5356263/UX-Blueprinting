# 知识使用说明

> **知识消费入口**：本文档中的知识读取，统一指向 `knowledge-wiki` 这个知识 skill，而不是某个固定文件路径或目录别名。

这份说明只负责一件事：

**明确 UXB 在分析阶段怎么读知识。**

## 核心目标

不是读得越多越好，而是：

1. 先明确当前要回答什么判断问题
2. 再选择能提供证据的知识入口
3. 先读 `summary`
4. 再读该 `summary` 对应的 `raw`
5. 再进入具体分析

## 唯一现行协议

当前只保留这一条知识消费协议：

```text
先命中知识
→ 先读 summary
→ 再读该 summary 对应的 raw
→ 再进入具体分析
```

`summary` 是路由层，不是停留层。

## Summary 发现规则

当前 `knowledge-wiki` 的 `summary` 层不是通过文件名前缀发现，而是通过固定结构发现：

1. 业务知识的 `summary` 位于 `knowledge-wiki` skill 内的 `knowledge/wiki/summaries/...`
2. 设计知识的 `summary` 也位于 `knowledge-wiki` skill 内的 `knowledge/wiki/summaries/...`
3. `wiki/summaries/.../README.md` 属于 `summary` 层的域路由说明
4. `raw/.../README.md` 属于 `raw` 层的入口说明，不可替代 `summary`

编号对应规则固定为：

1. 先命中领域
2. 先读该领域的 `wiki/summaries/.../README.md`
3. 再读命中的编号 `summary`
4. 再读同编号 `raw`

例如：

```text
先命中 yewu/quanxian-guanli
→ 先读 wiki/summaries/yewu/quanxian-guanli/README.md
→ 再读 wiki/summaries/yewu/quanxian-guanli/10_nengli-ditu.md
→ 再读 raw/yewu/quanxian-guanli/10_nengli-ditu.md
```

禁止：

1. 不得用 `summary*.md` 这类猜测式 glob 判断 `summary` 是否存在
2. 不得因为没搜到 `summary*.md` 就认定 `knowledge-wiki` 没有 `summary`
3. 不得把 `raw/.../README.md` 直接当作 `summary` 层替代品

## 什么时候触发

只要进入下面任一场景，就按这条协议读知识：

1. 需求分析
2. 体验诊断
3. 生成需求定案文档前的证据收敛

## Step 1 与 Step 2 的知识职责

默认分工是：

```text
Step 1：业务知识主导
Step 2：业务知识提供边界，设计知识帮助诊断体验问题
```

Step 1 读业务知识的目的主要是：

1. 理解领域术语
2. 避免误解业务对象
3. 识别明显规则边界
4. 判断需求是不是重复已有能力
5. 发现明显错误前提

Step 2 默认复用 Step 1 已读过的业务知识，不从零重读。

## Step 1 到 Step 2 的结论分型

知识转成分析结论时，至少区分这四类：

1. 已确认事实
2. 知识支持的推断
3. 设计判断
4. 必须确认的缺口

默认规则：

1. 需求文档里的方案描述不自动升级成已确认事实
2. 领域基线不自动等于当前场景事实
3. 设计判断不得写入已确认事实
4. 同一事项不得同时写成已确认事实和必须确认缺口

## 读取顺序

默认顺序固定为：

1. 先使用 `knowledge-wiki` 命中当前最相关的知识领域
2. 先找到该领域在 `wiki/summaries/...` 下的路由 README 与最相关 `summary`
3. 读这个 `summary`
4. 继续读它对应的 `raw`
5. 再进入 `Step 1` 或后续分析

如果一个 `summary` 对应多个 `raw`，优先选择：

1. 最直接支撑当前判断点的
2. 最小必要集合

## Step 2 什么时候补读业务知识

只有以下三个条件同时成立时，`Step 2` 才补读业务知识：

1. 角色、业务对象、规则、状态或责任关系存在不确定性
2. 该不确定性会改变任务链路、体验问题判断或策略方向
3. 项目业务知识里存在可能提供事实依据的内容

如果需要补读，顺序仍然是：

```text
先明确当前要确认什么
→ 命中最相关 summary
→ 读取对应 raw
→ 将知识转成当前判断依据
```

进入 `Step 2` 并确定本次重点体验维度后，必须在输出 `Step 2` 前完成对应设计知识的定向读取。

执行顺序同样固定为：

```text
先读设计 summary
→ 再读对应设计 raw
→ 再进入 Step 2 收敛
```

## 文件角色

读取时先分清这些角色：

1. `knowledge-wiki` 的领域路由信息
2. `knowledge-wiki` 中命中的 `summary`
3. 对应领域的入口说明、领域概述、规则边界等 `raw`
4. 与当前判断直接相关的其他 `raw`
5. `knowledge-wiki` 中的模板内容：不参与 UXB 正式知识消费

## 在回答里怎么使用知识

理想状态是：

1. 用户能感受到你参考了业务知识
2. 但输出主体仍然是在判断这次需求
3. 不是在复述知识文件

优先这样写：

```text
按当前项目知识看，这里真正变化的不是入口多了一个按钮，而是权限来源和审批闭环发生了变化。
```

避免这样写：

1. 大段贴原文
2. 机械报路径
3. 把知识库当搜索结果列表扔给用户
