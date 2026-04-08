# 检查合同

## 目标

定义执行中枢如何对输出结果进行正式检查与状态判定。

## 检查范围

- 结构完整性
- 阶段边界越权
- 开放问题缺失
- 事实与蓝图的覆盖关系
- 机器可读状态产出

## 正式输出

- `projects/<project-id>/workspace/check_report.md`
- `projects/<project-id>/workspace/check_status.json`

## 状态层级

- `blocker`
- `warning`
- `info`

## 状态判定规则

- 存在 `blocker` 时，`check_status.json.status` 必须为 `failed`
- 不存在 `blocker` 但存在 `warning` 时，`status` 必须为 `warning`
- 不存在 `blocker` 与 `warning` 时，`status` 必须为 `passed`

## 双产物分工

- `check_status.json`：机器正式判断依据
- `check_report.md`：人类解释说明依据

## 失败条件

- `check_report.md` 缺失
- `check_status.json` 缺失
- Markdown 报告与 JSON 状态不一致
- 存在 blocker 但未显式写出失败状态
