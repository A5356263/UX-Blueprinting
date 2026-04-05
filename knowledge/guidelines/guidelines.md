# 设计指南总检索

> 本文件现在作为兼容入口与总检索表使用，不再作为原则正文唯一真源。
> 原则正文请优先阅读 `principles/*/principles.md`。

## 1. 使用方法

1. 先到 `trigger_index.md` 依据场景查原则 ID
2. 再到下表定位对应正文文件
3. 只提取当前任务真正命中的原则，不整包注入

## 2. 原则总检索

| 分类 | 原则 ID 范围 | 正文文件 |
| --- | --- | --- |
| 无障碍与包容性 | `A11Y-*` | `principles/accessibility/principles.md` |
| 认知与决策 | `C-*` | `principles/cognition/principles.md` |
| 流程模式 | `BFM-*` | `principles/flow_mode/principles.md` |
| 治理与信任 | `G-*` | `principles/governance/principles.md` |
| 信息架构 | `IA-*` | `principles/information_architecture/principles.md` |
| 质量评估 | `Q-*` | `principles/quality/principles.md` |
| 可读性 | `R-*` | `principles/readability/principles.md` |
| 可用性 / ISO / 交互效率 | `U-*`、`ISO-*`、`I-*` | `principles/usability/principles.md` |
| 视觉层级 | `V-*` | `principles/visual/principles.md` |

## 3. 原则卡片统一字段

每张原则卡片建议保持以下字段：

- 原则 ID
- 来源
- 定义
- 触发
- 推导输出
- 文档落点
- 自检问句
- 反模式
- 取舍提示

## 4. 维护说明

- 若需要新增原则，请直接补到对应类别的 `principles.md`
- 若新增场景映射，请同步更新 `trigger_index.md`
- 若分类归属发生变化，请同步更新 `index.md` 与本文件
