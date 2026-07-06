# List Management Layout

## 1. 定位

用于企业 B 端列表管理页的主内容区骨架。

该 layout 只定义区域顺序与组合关系，不定义单个控件实现。

## 2. Use When

适用于：

- 主任务是浏览、筛选、搜索、比较、批量处理或审核多条记录。
- 主内容是 table、list、card list 或 result set。
- 页面需要 filter、action area、primary data area、pagination 中的多个区域协同。

## 3. Must Not

禁止：

- 不承载单条记录详情主线。
- 不承载长表单提交流程。
- 不把筛选字段写进 action area。
- 不把批量操作写进 filter。
- 不把行级操作提升成页面级主操作。

## 4. Region Order

默认顺序：

```text
header -> filter -> action area -> primary data area -> pagination
```

可裁剪：

- 无筛选条件时，可移除 filter。
- 无页面级操作时，可移除 action area。
- 无分页时，可移除 pagination。
- 若筛选很轻，可在视觉上靠近 action area，但职责仍需区分。

## 5. Allowed Changes

允许改写：

- 区域是否出现。
- 筛选字段数量。
- 表格列数量。
- 操作文案。
- 空状态文案。
- 分页是否展示。
- 批量操作是否展示。

默认不改：

- filter 与 action area 的职责边界。
- primary data area 作为结果主体的位置。
- table 与 pagination 的主从关系。
- 控件尺寸、颜色、状态样式。
- runtime data-* 契约。

## 6. Asset Mapping

推荐映射：

- header：`references/blocks/page-header.html`
- filter：`references/blocks/filter-bar.html`
- action area：`references/blocks/action-bar.html`
- primary data area：`references/components/ant/table/component.html`
- pagination：`references/components/ant/pagination/component.html`

如果某个稳定资产不存在，不要在 layout 中补完整实现；应先创建或修复对应资产。

## 7. HTML Skeleton

```html
<div class="xftv0-layout xftv0-layout-list-management">
  <section data-region="header">
    <!-- PAGE_HEADER_BLOCK -->
  </section>

  <section data-region="filter">
    <!-- FILTER_BAR_BLOCK -->
  </section>

  <section data-region="action-area">
    <!-- ACTION_BAR_BLOCK -->
  </section>

  <section data-region="primary-data-area">
    <!-- table component -->
    <!-- pagination component (optional) -->
  </section>
</div>
```

## 8. Checklist

生成后至少检查：

- 页面是否只有一条清晰主线。
- filter 是否只承担筛选职责。
- action area 是否只承担结果集相关页面操作。
- primary data area 是否为结果主体。
- 有分页时是否紧随 table 组件。
- 同一窗口是否只有一个主视觉主按钮。
