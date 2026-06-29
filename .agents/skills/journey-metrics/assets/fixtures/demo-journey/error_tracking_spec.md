# 报错/异常/中断埋点需求文档

## 1. 报错埋点范围说明

本文档覆盖旅程中的用户可见报错、异常和中断情况；推荐 Info4 需以线上/测试环境实际展示组件为准：

| 展示形式 | 说明 | 示例 |
|---|---|---|
| toast / snackbar | 页面顶部或中央的短暂提示，自动消失 | 提交失败提示 |
| inline 提示 | 表单字段下方的校验错误提示 | 驳回原因为空时的校验提示 |
| 空状态页 | 无数据时页面状态 | 审批列表无待审批项 |
| 阻断提示 | 页面级错误状态，不阻断其他区域操作 | 审批冲突提示 |
| 状态标签 | 行内状态标记 | 申请列表中"已驳回"标签 |
| 弹窗 | modalConfirm / modalWarning / modalError / modalInfo | 以线上实际组件为准 | 撤回申请确认 |

## 2. 报错/异常/中断场景

### 2.1 审批详情页 - 驳回操作

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_APPROVE_REJECT_REASON_EMPTY` |
| **触发条件** | 管理员点击确认驳回但未选择驳回原因 |
| **展示形式** | inline |
| **展示位置** | 驳回原因下拉框下方 |
| **可见文案** | "请选择驳回原因" |
| **用户下一步** | 选择驳回原因后重新提交 |
| **是否需要补救路径** | 是，选择后即可提交 |
| **来源** | confirmed |

---

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_APPROVE_REJECT_CONFLICT` |
| **触发条件** | 管理员提交驳回时，该申请已被其他管理员处理 |
| **展示形式** | toast |
| **展示位置** | 页面顶部 |
| **可见文案** | "该申请已被其他管理员处理，请刷新页面" |
| **用户下一步** | 刷新列表，不再处理此申请 |
| **是否需要补救路径** | 否 |
| **来源** | inferred |

### 2.2 申请详情页 - 驳回查看

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_APPLY_DETAIL_LOAD_FAIL` |
| **触发条件** | 申请详情页加载时接口返回失败（网络异常或权限不足） |
| **展示形式** | 空状态 |
| **展示位置** | 页面主内容区 |
| **可见文案** | "加载失败，请稍后重试" |
| **用户下一步** | 点击重试按钮，或返回列表页 |
| **是否需要补救路径** | 是，提供重试按钮和返回按钮 |
| **来源** | inferred |

---

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_APPLY_STATUS_EXPIRED` |
| **触发条件** | 员工查看的申请已被撤销或过期 |
| **展示形式** | 状态标签 |
| **展示位置** | 申请详情页顶部状态区 |
| **可见文案** | "该申请已过期" |
| **用户下一步** | 返回列表页，或发起新的申请 |
| **是否需要补救路径** | 否 |
| **来源** | inferred |

## 3. 报错埋点事件

### 3.1 审批详情页报错埋点

| 字段 | 值 |
|---|---|
| **事件ID** | `approve_error_reject_reason_empty` |
| **事件名称** | 驳回原因未选择校验提示 |
| **事件类型** | event_error |
| **触发时机** | 管理员点击确认驳回但驳回原因为空，inline 提示展示时 |
| **所属页面/模块** | 审批详情页 |
| **关联错误场景** | `ERR_APPROVE_REJECT_REASON_EMPTY` |
| **来源** | confirmed |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| error_code | string | FORM_VALIDATION | 前端定义 |
| error_message | string | 请选择驳回原因 | 前端定义 |
| error_type | string | inline | 前端定义 |
| trigger_page | string | /approve/detail | 前端路由 |
| current_status | string | approving | 前端状态 |
| user_role | string | admin | 登录态 |

**选传参数：** 无可选传参数

---

| 字段 | 值 |
|---|---|
| **事件ID** | `approve_error_reject_conflict` |
| **事件名称** | 审批驳回冲突提示 |
| **事件类型** | event_error |
| **触发时机** | 管理员提交驳回时接口返回冲突错误，toast 展示时 |
| **所属页面/模块** | 审批详情页 |
| **关联错误场景** | `ERR_APPROVE_REJECT_CONFLICT` |
| **来源** | inferred |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| error_code | string | APPROVE_CONFLICT | 接口返回 |
| error_message | string | 该申请已被其他管理员处理 | 接口返回 |
| error_type | string | toast | 前端定义 |
| trigger_page | string | /approve/detail | 前端路由 |
| current_status | string | approving | 前端状态 |
| user_role | string | admin | 登录态 |

**选传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| conflict_operator | string | 冲突处理人 | 接口返回 |

### 3.2 申请详情页报错埋点

| 字段 | 值 |
|---|---|
| **事件ID** | `apply_error_detail_load_fail` |
| **事件名称** | 申请详情加载失败 |
| **事件类型** | event_error |
| **触发时机** | 申请详情页接口返回失败，空状态页展示时 |
| **所属页面/模块** | 申请详情页 |
| **关联错误场景** | `ERR_APPLY_DETAIL_LOAD_FAIL` |
| **来源** | inferred |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| error_code | string | 接口返回的错误码 | 接口返回 |
| error_message | string | 加载失败，请稍后重试 | 前端定义 |
| error_type | string | empty | 前端定义 |
| trigger_page | string | /apply/detail | 前端路由 |
| current_status | string | loading | 前端状态 |
| user_role | string | employee | 登录态 |

**选传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| apply_id | string | 申请单ID | URL参数 |

## 4. 报错形式确认说明

| 报错场景 | 推荐 Info4 | 线上/测试环境实际形式 | 是否需调整 | 依据/说明 |
|---|---|---|---|---|
| 驳回原因未选择 | FormError | inline | 否 | 内联校验 |
| 审批冲突 | Toast | toast | 否 | 短暂提示 |
| 详情加载失败 | resultError | 空状态 | 否 | 页面内状态 |
| 申请已过期 | AlertWarning | 状态标签 | 需确认 | 如线上确为标签，需要确认团队 Info4 映射 |
| 撤回申请确认 | modalConfirm | 确认弹窗 | 否 | modal 枚举已纳入范围，最终以线上实际组件为准 |
