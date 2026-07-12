# Props Contract

本文件定义第一批正式资产允许暴露给 AI 的 `props` 白名单。

总原则：

- 只暴露页面生成高频必需能力
- 只暴露样式语义、内容组织、基础交互
- 不暴露底层技术控制面
- 不暴露复杂业务能力面
- 不透传底层组件库全量 API

---

## 1. Primitive

### Button

允许：

- `variant`: `primary | default | text`
- `disabled`
- `loading`
- `block`
- `children`
- `onClick`

不允许：

- 透传底层完整 button props
- 暴露复杂 icon render 控制
- 暴露危险技术实现细节

### SelectField

允许：

- `options`
- `placeholder`
- `value`
- `defaultValue`
- `width`
- `disabled`
- `onValueChange`

不允许：

- 远程搜索
- 自定义下拉容器
- 复杂筛选函数
- 多模式组合能力

### DateField

允许：

- `value`
- `defaultValue`
- `width`
- `disabled`
- `min`
- `max`
- `onChange`

不允许：

- 复杂日期面板控制
- 时间粒度系统
- 范围快捷策略
- 底层弹层控制

### StatusTag

允许：

- `tone`: `default | success | warning | error | info`
- `children`

不允许：

- 任意自定义颜色
- 任意样式覆盖

### DataTable

允许：

- `columns`
- `rows`
- `emptyText`

其中 `columns` 只允许：

- `key`
- `title`
- `dataIndex`
- `render`

不允许：

- `scroll`
- `expandable`
- `rowSelection`
- `sorter`
- `filters`
- `virtual`
- 服务端表格控制面

### Panel

允许：

- `title`
- `extra`
- `children`

不允许：

- 任意视觉变体扩散
- 多层 surface 技术开关

### Modal

允许：

- `open`
- `title`
- `footer`
- `children`
- `onClose`

不允许：

- 挂载容器控制
- 动画生命周期控制
- 任意尺寸系统

### AdminSideShell

允许：

- `title`
- `menuItems`
- `selectedKey`
- `topExtra`
- `children`

不允许：

- 页面层直接控制底层布局实现细节
- 任意侧边栏行为扩展

---

## 2. Composition

### PageHeader

允许：

- `title`
- `description`
- `actions`

不允许：

- 混入筛选字段
- 混入结果表格控制能力

### FilterBar

允许：

- `fields`
- `actions`

不允许：

- 结果集批量操作
- 详情阅读内容
- 页头级动作堆叠

### ActionBar

允许：

- `primary`
- `secondary`
- `tools`

不允许：

- 查询字段
- 详情信息
- 最终提交流控能力

### DetailSection

允许：

- `title`
- `description`
- `items`
- `sections`

其中 `items` 建议保持：

- `label`
- `value`

不允许：

- 大量录入控件
- 列表主内容能力

### SummaryStrip

允许：

- `items`

其中单项建议保持：

- `label`
- `value`
- `tone`

不允许：

- 图表级复杂能力
- 复杂统计卡系统

---

## 3. Shell

Shell 只暴露宿主结构语义，不暴露布局引擎细节。

第一阶段只允许：

- `AdminSideShell`

后续如果补 `AdminTopShell`，也应遵循同样原则：

- 只暴露标题、导航项、顶部附加区域、页面内容
- 不暴露底层布局系统技术控制面

---

## 4. AI 使用规则

- 先选 composition，再补 primitive。
- 如果当前需求需要的能力不在白名单内，优先裁剪需求表达，不要直接打开底层全量 API。
- 如果白名单明显不足，应扩正式资产，而不是临时透传底层库能力。
