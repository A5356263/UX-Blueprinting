# Page Type 路由

## 决策流程

```
用户需求 → 提取关键词 → 匹配 page_type → 查 page-type-router.csv 确定 recipe → 路由完成
```

路由不是单纯的关键词匹配，需要结合 Intent Model 中的 `page_goal` 和 `interaction_needs` 综合判断。例如"查看详情+审批"应路由到 ApprovalDetailPage 而非普通 DetailPage。

## Page Type 一览

| page_type | 场景特征 | 典型交互 |
|-----------|---------|---------|
| TablePage | 查询列表、批量操作、分页 | 筛选→浏览→行操作/批量操作 |
| CreatePage | 新建、提交、申请 | 填写→校验→提交→结果反馈 |
| DetailPage | 查看详情、单据详情 | 浏览→理解→决策→操作 |
| EditPage | 编辑、修改、回填 | 回填→修改→保存 |
| ApprovalDetailPage | 审批详情（含审批流+审批操作） | 浏览→审批决策→提交 |
| SettingsPage | 配置、设置 | 选择→配置→生效 |
| HomePage | 工作台、概览 | 扫读→导航→快速入口 |
| ReportPage | 报表、统计 | 筛选→查看汇总→导出 |
| ResultPage | 结果反馈（提交成功/失败） | 获知结果→下一步操作 |
| ErrorPage | 异常页（403/404/500） | 获知原因→恢复路径 |
| LoginPage | 登录 | 认证→进入系统 |

## 路由规则

精确路由规则见 **`data/content-assets/page-type-router.csv`**（22 条规则）。每条规则定义了 `match_keywords`、`negative_keywords`、目标 `recipe_id` 和优先级。

### 优先级原则

1. **显式场景优先于默认场景**：`router.workflow.detail`（审批详情）优先级 95，高于 `router.detail.basic`（默认详情）优先级 100
2. **否定关键词命中即排除**：`negative_keywords` 匹配时该路由不可选
3. **多命中时取高优先级**：priority 数值越低越优先（sort order）

### 兜底策略

当关键词无法明确匹配时：
- 有数据列表 → 默认 TablePage
- 有表单填写 → 默认 CreatePage
- 有详情展示 → 默认 DetailPage
- 都不确定 → 询问用户确认 page_type，不得猜测
