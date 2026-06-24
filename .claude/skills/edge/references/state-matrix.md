# Edge 状态矩阵

## 1. 空状态

- `empty-first-time`：首次进入、从未产生过数据
- `empty-collection`：列表或集合为空
- `empty-search`：搜索无结果
- `empty-filter`：筛选后为空

设计原则：

- 说明为什么为空
- 明确下一步 CTA
- 区分“从未有过”和“当前没结果”

## 2. 加载状态

- `loading-initial`：首次加载
- `loading-refresh`：刷新中
- `loading-fetch-more`：加载更多
- `loading-submit`：提交处理中

设计原则：

- 首次加载优先 skeleton
- 提交态要防重复点击
- 长任务要给出进度或等待预期

## 3. 错误状态

- `error-network`：网络错误
- `error-permission`：权限错误
- `error-not-found`：资源不存在
- `error-server`：服务端错误
- `error-validation`：校验错误
- `error-rate-limit`：频率限制

设计原则：

- 不直接暴露技术报错
- 必须告诉用户下一步能做什么
- 尽量保留已填写数据

## 4. 边界数据

- `boundary-zero`：数值为 0
- `boundary-overflow`：数据超大
- `boundary-long-text`：文本超长
- `boundary-null`：字段缺失或为空

设计原则：

- 不让极端数据破坏布局
- 缺失值要弱化展示，不显示 `null` / `undefined`
- 长文本要截断、换行或提供补充查看

## 5. 权限状态

- `permission-anonymous`：未登录
- `permission-not-authorized`：无权限
- `permission-read-only`：只读
- `permission-tier-limited`：版本或套餐受限

设计原则：

- 说明为什么受限
- 给出登录、申请、升级或返回路径
- 不要只做纯阻断提示

## 6. 离线状态

- `offline-no-network`：完全离线
- `offline-poor-connection`：弱网
- `offline-partial-sync`：部分同步

设计原则：

- 尽量保留用户输入
- 明确哪些内容还能看、哪些操作要延后
- 有同步能力时写清同步状态
