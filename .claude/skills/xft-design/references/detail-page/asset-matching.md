# Detail Page Asset Matching & Variant Decision（详情页资产匹配）

根据 Blueprint 从内容资产库中匹配 Region → Module → Variant。

## 1. 详情页 Region 族谱

详情页由以下 Region 族构成（按页面从上到下顺序）：

```
page-header          → 页面头部（标题 + 返回 + 操作）
detail-summary       → 摘要区（状态 + 关键字段 3-4 个）
detail-info-section  → 信息区（核心字段描述列表）
  ├── basic (描述列表)  ← Split/Stacked Basic 模式
  └── table-like grid   ← Split/Stacked Table-like 模式
approval-flow        → 审批流（仅审批场景，非必须）
operation-log        → 操作记录（页面靠后，非必须）
attachment-list      → 附件区（非必须）
related-table        → 关联表（非必须）
```

## 2. 从 CSV 匹配资产

### Step 1：查 Recipe → 可用资产族

查阅 **`data/content-assets/recipe-asset-map.csv`**（127 行），根据 `recipe_id` 获取对应的 `asset_id` 列表和可用变体。

常用详情页 Recipe：
- `recipe.detail.basic.vertical` — 上下基础详情（Stacked Basic）
- `recipe.detail.basic.horizontal` — 左右基础详情（Split Basic）
- `recipe.detail.table.vertical` — 上下表格详情（Stacked Table-like）
- `recipe.detail.table.horizontal` — 左右表格详情（Split Table-like）
- `recipe.detail.tabs` — 多标签详情页
- `recipe.detail.table-tabs` — 标签表格详情页
- `recipe.workflow.detail` — 审批详情页

### Step 2：查 Recipe Rules → 约束

查阅 **`data/content-assets/recipe-rules.csv`**，每个 recipe 定义了：
- `required_regions`：不可省略的区域
- `optional_modules`：可选的模块
- `forbidden_patterns`：禁止的模式
- `default_region_order`：推荐排列顺序

### Step 3：查 Asset Registry → 具体 HTML/CSS

查阅 **`data/content-assets/content-assets.csv`**（84 行），根据 `asset_id` 获取：
- `html_path`：HTML 模板路径
- `css_path`：CSS 文件路径
- `slots`：可用的插槽
- `validation`：校验规则
- `conditions`：适用条件

## 3. Variant 决策

### detail-summary 变体
- `basic`：3-4 个摘要项，状态可扫读，默认选择
- 无 rich 变体，复杂头部场景使用 `detail-header-rich` 模块

### detail-info-section 变体
- **描述列表**（Description List）：label-value 对，轻量间距。适用：基础档案、客户详情、合同详情
- **表格化网格**（Table-like Grid）：label 灰底 + value 白底 + 分割线。适用：报账单、对账单、付款单

选择逻辑：
```
字段值短且需要强边界区分？ → 表格化网格
字段值长或需要轻松阅读？   → 描述列表
```

### approval-flow 变体
- `basic`：简单审批节点列表
- `rich`：审批模式选择卡片 + 审批节点（审批详情页优先使用 rich）

### layout 选择
- 含审批流/操作记录右侧固定 → `layout.detail-side.basic`（左右 `1fr 375px`）
- 无右侧辅助信息 → 不使用 layout 资产（默认上下布局）

## 4. 模块组合约束

模块级组合规则见 **`data/content-assets/asset-rules.csv`**，核心约束：

| 模块 | 放置规则 | 条件 |
|------|---------|------|
| 描述列表 | `after:detail-summary` | 只读字段信息 |
| 审批流 | `after:basic-info or side-panel` | 审批详情必须展示 |
| 关联表 | `after:approval-flow or after:basic-info` | 关联对象 > 3 条 |
| 操作记录 | `last-section` | 放页面靠后，不打断主信息 |

## 5. 常见错误

1. ❌ 所有详情页机械使用 description list → 报账单应该用 table-like grid
2. ❌ 右侧栏为空却使用左右布局 → 无辅助信息就用上下布局
3. ❌ 审批流宽度随意调整 → 必须 375px
4. ❌ 操作记录放在信息区前面 → 必须放页面靠后
5. ❌ 详情页缺少摘要区 → 状态和关键字段必须优先暴露
