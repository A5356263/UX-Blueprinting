# Detail Reading Layout

## 1. 定位

用于企业 B 端单条记录、状态、结果或配置对象的详情阅读页主内容区骨架。

该 layout 只定义阅读主线，不定义具体详情字段实现。

## 2. Use When

适用于：

- 主任务是查看单条记录。
- 页面核心内容是摘要、详情分组、元数据、过程信息或状态结果。
- 用户主要行为是阅读、理解、少量局部操作。

## 3. Must Not

禁止：

- 不承载批量列表主线。
- 不承载长表单录入主线。
- 不把筛选区放入详情阅读主线。
- 不让次级统计信息压过主对象摘要。

## 4. Region Order

默认顺序：

```text
header -> summary -> detail sections -> footer or secondary actions
```

可裁剪：

- 摘要信息极少时，可并入第一个 detail section。
- 无底部动作时，可省略 footer actions。
- 若存在锚点导航，可作为辅助阅读结构，不改变详情主线。

## 5. Allowed Changes

允许改写：

- summary 是否出现。
- detail section 数量。
- 字段名称与展示内容。
- 状态说明。
- 过程信息。
- 次级操作文案。

默认不改：

- 单对象阅读主线。
- summary 优先于 detail sections 的层级。
- 主内容阅读顺序。
- 控件实现基线。

## 6. Block Mapping

推荐映射：

- header：`references/blocks/page-header.html`
- summary：`references/blocks/summary-section.html`
- detail sections：`references/blocks/detail-section.html`
- secondary actions：`references/blocks/action-bar.html` 或 `references/blocks/footer-actions.html`

如果对应 block 不存在，应优先补 block，而不是在 layout 中写完整实现。

## 7. HTML Skeleton

```html
<div class="xftv0-layout xftv0-layout-detail-reading">
  <section data-region="header">
    <!-- PAGE_HEADER_BLOCK -->
  </section>

  <section data-region="summary">
    <!-- SUMMARY_SECTION_BLOCK -->
  </section>

  <section data-region="detail-sections">
    <!-- DETAIL_SECTION_BLOCK -->
  </section>

  <section data-region="secondary-actions">
    <!-- SECONDARY_ACTIONS_BLOCK -->
  </section>
</div>
```

## 8. Checklist

生成后至少检查：

- 页面是否围绕单一对象展开。
- summary 是否没有被次级信息挤占。
- detail sections 是否服务阅读理解，而不是主录入。
- 操作是否没有打断主阅读路径。
