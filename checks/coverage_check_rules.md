# Coverage Check Rules

## 目标

检查 `facts.md` 与蓝图之间是否存在显性承接关系。

## 最小规则

- `facts.md` 中的事实 ID 应在业务蓝图或体验蓝图中被引用
- 若未被引用，应在检查报告中输出 warning
- 若蓝图文件缺失，应输出 blocker
