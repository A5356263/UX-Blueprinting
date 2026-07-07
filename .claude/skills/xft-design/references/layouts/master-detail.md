# Master Detail Layout

## 1. 定位

用于企业 B 端左主右从、左树右表、左列表右详情、左对象右配置类页面的主内容区骨架。

该 layout 只定义主从区域关系，不定义树、表格、详情、表单的具体控件实现。

## 2. Use When

适用于：

- 页面存在一个主对象集合与一个从属内容区。
- 左侧用于选择组织、分类、对象、记录或范围。
- 右侧展示对应的详情、配置、列表或操作区。
- 用户任务依赖主从联动关系。

## 3. Must Not

禁止：

- 不用于普通单栏列表页。
- 不用于普通单栏表单页。
- 不把左侧导航与全局 sidebar 混淆。
- 不在 layout 中实现复杂联动 JS 行为。
- 不让左右两侧各自形成两个无关主任务。

## 4. Region Order

默认结构：

```text
header -> split content
split content = master pane + detail pane
```

detail pane 内部可继续使用：

```text
pane header -> filter/action/form/detail/table
```

可裁剪：

- 无 header 时，可直接进入 split content。
- master pane 内容较轻时，可收窄。
- detail pane 可承载 list-management、form-workflow 或 detail-reading 的局部结构。

## 5. Allowed Changes

允许改写：

- master pane 宽度档位。
- master pane 内容类型。
- detail pane 内部区域数量。
- 右侧承载列表、详情、表单或配置。
- 空状态文案。

默认不改：

- 主从关系。
- master pane 与 detail pane 的职责边界。
- 左侧对象选择不等于全局导航。
- 复杂联动行为不在 layout 层实现。

## 6. Block Mapping

推荐映射：

- header：`references/blocks/page-header.html`
- master pane：`references/blocks/tree-panel.html` 或 `references/blocks/list-panel.html`
- detail pane header：`references/blocks/page-header.html`
- detail pane content：按任务继承 `filter-bar.html`、`action-bar.html`、`table component`、`pagination component`、`form component`、`detail-section.html`

如果相关 pane block 不存在，应先补 block，而不是让 layout 承担完整实现。

## 7. HTML Skeleton

```html
<!-- EDITABLE: 区域组合 - 按需求裁剪区域是否出现、调整区域顺序 -->
<div class="xftv0-layout xftv0-layout-master-detail">
  <!-- Surface 1：页面标题（可选） -->
  <div class="xftv0-surface">
    <section data-region="header">
      <!-- EDITABLE: 此处使用 references/blocks/page-header.html -->
    </section>
  </div>

  <!-- Surface 2：主从联动区域 -->
  <div class="xftv0-surface">
    <div class="xftv0-split" style="display: flex; gap: var(--spacing-6);">
      <aside data-region="master-pane" style="flex: 0 0 260px; min-width: 0;">
        <!-- EDITABLE: 此处使用 references/blocks/tree-panel.html 或 list-panel -->
      </aside>

      <main data-region="detail-pane" style="flex: 1; min-width: 0;">
        <!-- EDITABLE: 此处按任务使用 filter-bar、action-bar、table、form、detail-section -->
      </main>
    </div>
  </div>
</div>
<!-- /EDITABLE -->
```

## 7.1 Composition

默认包裹策略：

- Surface 1 包裹 header（可选，无 header 时省略）。
- Surface 2 包裹 split-content（master-pane + detail-pane）：主从联动是一个功能单元。
- 左右面板之间用 `gap: var(--spacing-6)` 分隔。
- master-pane 默认宽度 260px（可按需求调整），使用 `flex: 0 0` 固定。
- detail-pane 使用 `flex: 1` 自适应。

裁剪规则：

- master-pane 内容较轻时可收窄至 200px。
- detail-pane 内部可继续使用 Surface/Wrapper 做二次组合（使用 `.xftv0-surface--nested`）。
- 无 header 时直接从 Surface 2 开始。

## 8. Checklist

生成后至少检查：

- 左侧是否承担对象选择或范围选择职责。
- 右侧是否展示被选对象相关内容。
- 左侧是否没有被误写成全局 sidebar。
- 右侧是否没有与左侧脱节形成独立无关页面。
