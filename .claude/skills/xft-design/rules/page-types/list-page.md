# 列表页

## 页面类型标识

- `Page Type ID`：`PAGE_TYPE.LIST`

## 触发条件

- 主任务是浏览、筛选、比对、批量处理或审核多条记录
- 页面主内容是表格、列表、卡片列表或结果集

## 主线结构

- 默认主线为 `header -> filter -> action area -> primary data area -> supporting actions or pagination`

## 区分边界

- 若主任务是新建、编辑、提交或配置，不归入列表页
- 若主任务是查看单条记录细节，不归入列表页
- 若主任务发生在覆盖层内，优先判断是否属于弹窗页

## 失败回退

- 无法确认是否属于列表页时，不强行套用列表页主线
