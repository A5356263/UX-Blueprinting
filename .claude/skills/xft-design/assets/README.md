# Static Assets

本目录只存放原始静态资源。

## 负责

- 图标
- 图片
- Logo
- 插画
- 其他只需要引用、不参与结构推理与改写的静态文件

## 当前目录

- `icons/`：图标资源

后续可按真实需求扩展：

- `images/`
- `logos/`
- `illustrations/`

不要为了预留结构提前创建空目录。

## 不负责

本目录不存放：

- 页面 shell
- 内容区 layout
- 框架级 chrome
- 业务 block
- overlay
- component HTML 实现

以上需要 AI 读取、理解、组合和改写的稳定结构资产统一进入 `references/`。

## 判断标准

新增资源前先判断：

- 需要 AI 理解、组合、改写：进入 `references/`
- 只需要引用和使用：进入 `assets/`
