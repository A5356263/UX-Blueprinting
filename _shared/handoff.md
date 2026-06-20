# 交接话术模板

> 每个 Skill 完成后，按以下三层结构输出交接话术。
> 数据来源：`_shared/skill-graph.json` 中当前 Skill 的 `next_hint`。

## 模板

```
✅ {Skill中文名} 已完成，{关键产物简述，≤30字}。

{emoji} **推荐下一步：`/{preferred[0]}`**（{reason}）
{如有 alternatives，逐条列出：想 {alt.reason} 走 `/{alt.id}`}

说"进入 {next_id}" 开始下一步。
```

## 规则

1. **第 1 行**：完成摘要，限 30 字以内，只提关键产物数量和类型
2. **第 2 行**：推荐下一步，来自 `skill-graph.json` 的 `next_hint.preferred`
3. **第 3 行**：备选项，来自 `next_hint.alternatives`，无可不写
4. **第 4 行**：触发语，方便用户直接复制

## 终端节点

如 `next_hint.preferred` 为空数组（如体验蓝图），输出：

```
✅ {Skill中文名} 已完成，{关键产物简述}。

当前链路已完成，无后续 Skill。
```

## 示例

### UXB 完成后

```
✅ 需求定案已完成，10 章定案文档 + 结构化 JSON。

🎯 **推荐下一步：`/experience-blueprint`**（需求定案已完成，进入体验蓝图设计阶段。）

说"进入体验蓝图" 开始下一步。
```

### 体验蓝图完成后

```
✅ 体验蓝图已完成，9 章设计文档 + 交互流程 + 页面设计。

当前链路已完成，无后续 Skill。
```
