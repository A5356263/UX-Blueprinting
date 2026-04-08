# 检查说明

本文件用于解释项目为什么采用“Markdown 报告 + JSON 状态”的双产物检查方式。  
正式检查规则请见 [06_check_contract.md](E:/AI设计/体验蓝图构建思路/specs/06_check_contract.md)。

## 为什么不是只看 Markdown

如果只依赖 `check_report.md`，执行中枢和其他 AI 工具仍然需要阅读正文再猜状态。  
因此当前结构采用：

- `check_report.md`：给人看
- `check_status.json`：给机器判断

## 理解重点

- 状态判断以 JSON 为准
- 原因解释以 Markdown 为准
- 两者必须保持一致
