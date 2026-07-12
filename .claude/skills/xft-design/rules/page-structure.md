# 页面结构总规则

## 页面壳选择

### 默认规则

- 产品内业务页面默认使用 `admin-side-shell`
- 明确为消息、待办、轻任务等无持续侧边导航页面时，使用 `admin-top-shell`

### 不允许

- 不因需求未提及侧边导航，就主动去掉 side shell
- 不把业务主内容直接塞进 shell 自身结构

## 区域落位规则

### Header

负责：

- 页面标题
- 页面身份信息
- 页面级上下文说明
- 明确影响整个页面的顶层操作

不负责：

- 表格主体
- 长表单内容
- 行级操作

### Filter

负责：

- 查询条件
- 轻量收窄条件
- 查询 / 重置 / 展开收起

不负责：

- 批量操作
- 结果统计主体
- 单记录说明内容

### Action

负责：

- 与当前结果集直接相关的页面级动作
- 视图切换、辅助工具、导出、列设置等

不负责：

- 查询字段主体
- 最终表单提交
- 单对象详情内容

### Primary Content

负责：

- 页面主信息载体
- 表格、列表、主体表单、详情主区

不负责：

- 纯装饰性填充内容

### Footer Actions

负责：

- 保存、提交、取消、关闭、确认

不负责：

- 机械重复顶部全部动作

## 列表管理页

### 适用条件

- 主任务是浏览、筛选、比对、批量处理或审核多条记录
- 主内容是表格、列表、卡片结果集

### 正式主线

```txt
header
-> filter
-> action
-> primary content
-> supporting actions / pagination
```

### 资产优先级

- shell：`admin-side-shell`
- header：`page-header`
- filter：`filter-bar`
- action：`action-bar`
- primary content：`data-table`

### 不允许

- 把单条记录详情混入主列表流程
- 把筛选区当成操作区
- 把最终表单提交动作写进 action 区

## 表单页

### 适用条件

- 主任务是创建、编辑、提交、配置或补录信息

### 正式主线

```txt
header
-> form sections
-> footer actions
```

### 资产优先级

- shell：`admin-side-shell`
- header：`page-header`
- 字段：以 `primitive` 组合

### 不允许

- 把结果浏览主线强行套成表单页
- 把页面主动作提前到未完成的表单主体前

## 详情页

### 适用条件

- 主任务是查看单条记录、单个配置对象或单次结果详情

### 正式主线

```txt
header
-> summary
-> detail sections
-> secondary / footer actions
```

### 资产优先级

- shell：`admin-side-shell`
- header：`page-header`
- detail：`detail-section`

### 不允许

- 把批量浏览结果区误写成详情主线
- 让无关说明信息挤占单对象阅读主线

## 弹层任务页

### 适用条件

- 当前任务在覆盖层中完成确认、补录、选择或查看

### 正式主线

```txt
modal header
-> modal body
-> footer actions
```

### 资产优先级

- 容器：`modal-task`
- 主体内容：优先复用既有 composition / primitive

### 不允许

- 把需要完整页面主流程的任务硬塞进弹层
- 让一个弹层承担多个无关主任务

## 冲突优先级

当页面组织存在冲突时，优先级如下：

1. 保住任务清晰度
2. 保住区域职责边界
3. 保住可读层级
4. 保住对齐一致性
5. 最后才保紧凑度

## 回退原则

- 如果一个区域职责不明确，优先不生成该区域
- 如果当前需求跨越多个页型主线，先拆主任务，再决定主线
- 如果局部需求无法命中现有 composition，允许下探 primitive 组合，但不跳过页型规则
