# 交接规则

本文件用于约束 `knowledge-wiki` 与其他 skill 的交接方式。

## 主链路边界

- `knowledge-wiki` 不进入 `uxb -> experience-blueprint` 主链路
- `knowledge-wiki` 是支撑型 skill，不主动推进业务流程

## UXB 到 knowledge-wiki

当 UXB 发现了可长期复用的知识变化时，只做最小交接，不直接写候选文件。

推荐交接文案：

```text
这条内容后续可能会复用，建议进入 knowledge-wiki 生成知识候选，不直接入库。
```

## knowledge-wiki 到 UXB

当问题超出知识问答范围，涉及需求判断、方案边界或体验诊断时，应转回 UXB。

推荐转接文案：

```text
这个问题已经超出知识库问答范围，需要做需求判断、方案边界或体验诊断。建议进入 UXB 处理。
```

## 交接原则

- 只交接必要上下文
- 不把内部脚本细节暴露给用户
- 不把 knowledge-wiki 改造成主流程路由器
