# Dashboard Overview Layout

## 1. 定位

用于企业 B 端工作台、运营概览、指标总览类页面的主内容区骨架。

该 layout 是可选能力，不应优先用于常规列表、表单、详情任务。

## 2. Use When

适用于：

- 页面主任务是快速了解整体状态。
- 页面包含指标卡、趋势、待办、快捷入口、异常提醒等多个概览模块。
- 用户需要先扫全局，再进入具体任务。

## 3. Must Not

禁止：

- 不用于主任务明确的列表管理页。
- 不用于主任务明确的表单提交流程。
- 不让装饰性数据卡压过真实业务任务。
- 不把多个无关模块堆成信息墙。
- 不把 dashboard 当成默认首页模板。

## 4. Region Order

默认顺序：

```text
header -> key metrics -> primary work area -> secondary panels
```

可裁剪：

- 无指标时，可移除 key metrics。
- 若有明确待办主任务，primary work area 优先于次级图表。
- secondary panels 应保持弱层级，不压过主任务区。

## 5. Allowed Changes

允许改写：

- 指标卡数量。
- 主工作区类型。
- 次级面板数量。
- 提醒文案。
- 快捷入口文案。

默认不改：

- 概览优先服务任务入口，而不是装饰展示。
- primary work area 的视觉优先级。
- 组件尺寸与状态基线。
- 图表真实渲染能力不在 layout 层伪造。

## 6. Asset Mapping

推荐映射：

- header：`references/blocks/page-header.html`
- key metrics：`references/blocks/metric-cards.html`
- primary work area：按任务继承 `references/blocks/action-bar.html`、`references/components/ant/table/component.html`、`references/components/ant/pagination/component.html`、`references/blocks/detail-section.html`
- secondary panels：`references/blocks/info-panel.html` 或后续稳定资产

如果 block 不存在，不要在 layout 中补完整实现；应先创建稳定 block。

## 7. HTML Skeleton

```html
<!-- EDITABLE: 区域组合 - 按需求裁剪区域是否出现、调整区域顺序 -->
<div class="xftv0-layout xftv0-layout-dashboard-overview">
  <!-- Surface 1：页面标题 -->
  <div class="xftv0-surface">
    <section data-region="header">
      <!-- EDITABLE: 此处使用 references/blocks/page-header.html -->
    </section>
  </div>

  <!-- Surface 2：关键指标 -->
  <div class="xftv0-surface">
    <section data-region="key-metrics">
      <!-- EDITABLE: 此处使用 references/blocks/metric-cards.html -->
    </section>
  </div>

  <!-- Surface 3：主工作区 -->
  <div class="xftv0-surface">
    <section data-region="primary-work-area">
      <!-- EDITABLE: 此处按任务使用 table、action-bar、detail-section -->
    </section>
  </div>

  <!-- Surface 4（可选）：次级面板 -->
  <div class="xftv0-surface">
    <section data-region="secondary-panels">
      <!-- EDITABLE: 此处使用 references/blocks/info-panel.html -->
    </section>
  </div>
</div>
<!-- /EDITABLE -->
```

## 7.1 Composition

默认包裹策略：

- Dashboard 的每个模块通常独立成 Surface（指标卡、工作区、次级面板各自独立）。
- Surface 之间由 Shell 的 content-inner gap（spacing-6）自动间距。
- key-metrics 内部的指标卡排列由 metric-cards block 自身控制。

裁剪规则：

- 无 header 时省略 Surface 1。
- 无次级面板时省略 Surface 4。
- 指标卡与主工作区可合并为一个 Surface（指标卡作为工作区顶部摘要）。

## 8. Checklist

生成后至少检查：

- 页面是否服务整体状态理解和任务进入。
- 主工作区是否比次级信息更清晰。
- 指标卡是否没有变成装饰堆砌。
- 是否没有把 dashboard 用作所有页面的默认模板。
