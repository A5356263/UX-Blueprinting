# 报错/异常/中断埋点需求文档

> 基于体验蓝图 `spark-output/experience_blueprint.md` §5 异常与阻断流程生成。
> 优先按旅程识别所有用户可见的报错、异常和中断情况，再按 messageInfo 规范给出推荐 info4。最终 info4 以线上/测试环境实际组件为准。

## 1. 报错埋点范围说明

报错统一使用 `Util.trackData(params, TrackType.messageInfo)` 上报。`messageInfo` 必填字段为 `cust_id`、非空 `info`、`info4`。本文档覆盖旅程中的报错、异常和中断情况，并给出以下推荐 info4 枚举值：

| 展示形式 | info4 枚举 | 说明 | 示例 |
|---|---|---|---|
| FormError | `FormError` | 表单字段下方校验错误提示 | 必填字段为空、格式不合法 |
| message | `message` | 页面顶部或中央消息提示 | 操作失败提示 |
| Toast | `Toast` | 短暂 toast 提示 | 轻量提示，自动消失 |
| resultError | `resultError` | 空状态页或结果页错误状态 | 写入失败结果展示 |
| AlertError | `AlertError` | 页面级错误或警告横幅 | 弹窗内阻断提示区 |
| modalConfirm | `modalConfirm` | 确认式弹窗 | 二次确认 |
| modalError | `modalError` | 错误式弹窗 | 阻断错误弹窗 |

如线上实际为弹窗、确认框或输入式弹窗，应如实记录实际形态并使用对应 `modal*` 枚举；不要因为体验上"不推荐弹窗"而改写事实。若无法取得用户可见错误文案，跳过 `TrackType.messageInfo`，不要上报空 `info`。

> 报错上报基础信息（企业信息、页面信息、任务上下文）由系统自动携带。

## 2. 报错/异常/中断场景

### 2.1 复制弹窗 — 提交校验

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_INFO_NOT_SELECTED` |
| **触发条件** | 点击确认按钮时，两项复制信息均未勾选 |
| **展示形式** | inline 红字提示 |
| **展示位置** | 复制弹窗 C 区（复制信息区）下方 |
| **可见文案** | "请选择复制信息" |
| **用户下一步** | 勾选至少一项复制信息后重新点击确认 |
| **是否需要补救路径** | 否（就地修正） |
| **来源** | `[confirmed]` |

---

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_TARGET_NOT_SELECTED` |
| **触发条件** | 点击确认按钮时，复制对象选择器中未选择任何用户 |
| **展示形式** | inline 红字提示 |
| **展示位置** | 复制弹窗 D 区（复制对象区）下方 |
| **可见文案** | "请选择至少一名复制对象" |
| **用户下一步** | 选择至少一名用户后重新点击确认 |
| **是否需要补救路径** | 否（就地修正） |
| **来源** | `[confirmed]` |

---

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_JOIN_STATUS_FAIL` |
| **触发条件** | 已选目标用户中存在加入状态不是"已加入"的用户 |
| **展示形式** | 弹窗内阻断提示区（AlertError） |
| **展示位置** | 复制弹窗 E 区（阻断提示区） |
| **可见文案** | "以下用户的加入状态不符合要求，不能成为子管理员：{用户名} / {手机号}（当前状态：{实际状态}）请移除以上用户后重试。" |
| **用户下一步** | 在复制对象选择器中移除不符合的用户，重新点击确认 |
| **是否需要补救路径** | 否（就地修正，移除不符合用户） |
| **来源** | `[confirmed]` |

---

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_AUTH_STATUS_FAIL` |
| **触发条件** | 已选目标用户中存在未完成实名认证的用户 |
| **展示形式** | 弹窗内阻断提示区（AlertError） |
| **展示位置** | 复制弹窗 E 区（阻断提示区） |
| **可见文案** | "以下用户未完成实名认证，不能成为子管理员：{用户名} / {手机号}请移除以上用户后重试。" |
| **用户下一步** | 在复制对象选择器中移除不符合的用户，重新点击确认 |
| **是否需要补救路径** | 否（就地修正，移除不符合用户） |
| **来源** | `[confirmed]` |

---

### 2.2 复制弹窗 — 选择复制对象

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_TARGET_MAX_EXCEEDED` |
| **触发条件** | 已选用户数量达到 200 名后继续尝试添加 |
| **展示形式** | Toast |
| **展示位置** | 选择器或页面顶部 |
| **可见文案** | "最多可选择 200 名复制对象" |
| **用户下一步** | 确认当前已选名单，或移除部分用户后添加其他人 |
| **是否需要补救路径** | 否（即时限制） |
| **来源** | `[confirmed]` |

---

### 2.3 复制弹窗 — 写入阶段

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_WRITE_SYSTEM_ERROR` |
| **触发条件** | 后端服务异常、超时、数据库写入失败 |
| **展示形式** | 结果弹窗内失败分组（resultError） |
| **展示位置** | 复制结果弹窗 E 区（复制失败分组） |
| **可见文案** | "系统异常，请稍后重试" |
| **用户下一步** | 关闭结果弹窗，重新发起复制或联系技术支持 |
| **是否需要补救路径** | 是（重新发起复制） |
| **来源** | `[confirmed]` |

---

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_TARGET_DISABLED` |
| **触发条件** | 目标用户在写入时企业状态已变更为禁用或已移除 |
| **展示形式** | 结果弹窗内失败分组（resultError） |
| **展示位置** | 复制结果弹窗 E 区（复制失败分组），标注失败原因 |
| **可见文案** | "该用户在企业中已被禁用" |
| **用户下一步** | 查看结果汇总，确认其余用户复制结果。对失败用户后续单独处理 |
| **是否需要补救路径** | 是（对失败用户单独处理） |
| **来源** | `[confirmed]` |

---

### 2.4 复制弹窗 — 来源变更

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_SOURCE_CHANGED` |
| **触发条件** | 弹窗打开期间，来源子管理员的权限被其他管理员修改或子管理员身份被删除 |
| **展示形式** | 弹窗内阻断提示（AlertError） |
| **展示位置** | 复制弹窗内阻断区 |
| **可见文案** | "复制来源"{子管理员姓名}"的权限配置已被修改，请关闭弹窗后重新打开获取最新配置。" |
| **用户下一步** | 关闭弹窗，重新打开复制弹窗获取最新快照 |
| **是否需要补救路径** | 是（重新打开弹窗获取最新快照） |
| **来源** | `[confirmed]`（策略为"打开锁定快照，提交检测变更"，GAP-04 待确认） |

---

## 3. 报错埋点事件（messageInfo 格式）

### 3.1 复制弹窗 — 提交校验 报错埋点

#### ERR_COPY_INFO_NOT_SELECTED

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_INFO_NOT_SELECTED` |
| **触发时机** | 点击确认按钮，校验步骤 1 失败时 |
| **所属页面/模块** | 复制弹窗 |
| **关联错误场景** | `ERR_COPY_INFO_NOT_SELECTED` |
| **来源** | `[confirmed]` |

**messageInfo 参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| trackType | `'messageInfo'` | 固定类型 | 前端定义 |
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_dialog` |
| info | string | 用户可见错误信息："请选择复制信息" | 前端定义 |
| info2 | string | 校验步骤标识 | 前端定义：`validate_step_1` |
| info3 | string | 错误分类：`VALIDATION_INFO_EMPTY` | 前端定义 |
| info4 | string | 展示形式：`FormError` | 前端定义 |
| info5 | string | 触发动作：`confirm_click` | 前端定义 |

---

#### ERR_COPY_TARGET_NOT_SELECTED

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_TARGET_NOT_SELECTED` |
| **触发时机** | 点击确认按钮，校验步骤 2 失败时 |
| **所属页面/模块** | 复制弹窗 |
| **关联错误场景** | `ERR_COPY_TARGET_NOT_SELECTED` |
| **来源** | `[confirmed]` |

**messageInfo 参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| trackType | `'messageInfo'` | 固定类型 | 前端定义 |
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_dialog` |
| info | string | 用户可见错误信息："请选择至少一名复制对象" | 前端定义 |
| info2 | string | 校验步骤标识 | 前端定义：`validate_step_2` |
| info3 | string | 错误分类：`VALIDATION_TARGET_EMPTY` | 前端定义 |
| info4 | string | 展示形式：`FormError` | 前端定义 |
| info5 | string | 触发动作：`confirm_click` | 前端定义 |

---

#### ERR_COPY_JOIN_STATUS_FAIL

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_JOIN_STATUS_FAIL` |
| **触发时机** | 点击确认按钮，校验步骤 3 失败，阻断提示区展示时 |
| **所属页面/模块** | 复制弹窗 |
| **关联错误场景** | `ERR_COPY_JOIN_STATUS_FAIL` |
| **来源** | `[confirmed]` |

**messageInfo 参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| trackType | `'messageInfo'` | 固定类型 | 前端定义 |
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_dialog` |
| info | string | 用户可见错误信息（摘要）："以下用户的加入状态不符合要求，不能成为子管理员" | 前端定义 |
| info2 | string | 不符合用户 ID 列表（逗号分隔） | 校验结果 |
| info3 | string | 错误分类：`VALIDATION_JOIN_STATUS` | 前端定义 |
| info4 | string | 展示形式：`AlertError` | 前端定义 |
| info5 | string | 触发动作：`validate_fail_join_status` | 前端定义 |

---

#### ERR_COPY_AUTH_STATUS_FAIL

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_AUTH_STATUS_FAIL` |
| **触发时机** | 点击确认按钮，校验步骤 4 失败，阻断提示区展示时 |
| **所属页面/模块** | 复制弹窗 |
| **关联错误场景** | `ERR_COPY_AUTH_STATUS_FAIL` |
| **来源** | `[confirmed]` |

**messageInfo 参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| trackType | `'messageInfo'` | 固定类型 | 前端定义 |
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_dialog` |
| info | string | 用户可见错误信息（摘要）："以下用户未完成实名认证，不能成为子管理员" | 前端定义 |
| info2 | string | 不符合用户 ID 列表（逗号分隔） | 校验结果 |
| info3 | string | 错误分类：`VALIDATION_AUTH_STATUS` | 前端定义 |
| info4 | string | 展示形式：`AlertError` | 前端定义 |
| info5 | string | 触发动作：`validate_fail_auth_status` | 前端定义 |

---

### 3.2 复制弹窗 — 选择复制对象 报错埋点

#### ERR_COPY_TARGET_MAX_EXCEEDED

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_TARGET_MAX_EXCEEDED` |
| **触发时机** | 已选用户数达到 200 上限后继续尝试添加时 |
| **所属页面/模块** | 复制弹窗 / 选择员工弹窗 |
| **关联错误场景** | `ERR_COPY_TARGET_MAX_EXCEEDED` |
| **来源** | `[confirmed]` |

**messageInfo 参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| trackType | `'messageInfo'` | 固定类型 | 前端定义 |
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_dialog` |
| info | string | 用户可见错误信息："最多可选择 200 名复制对象" | 前端定义 |
| info2 | string | 当前已选数量 | 选择器计数器 |
| info3 | string | 错误分类：`VALIDATION_MAX_LIMIT` | 前端定义 |
| info4 | string | 展示形式：`Toast` | 前端定义 |
| info5 | string | 触发动作：`select_exceed_limit` | 前端定义 |

---

### 3.3 复制弹窗 — 写入阶段 报错埋点

#### ERR_COPY_WRITE_SYSTEM_ERROR

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_WRITE_SYSTEM_ERROR` |
| **触发时机** | 写入请求返回系统异常时，结果弹窗展示失败分组时 |
| **所属页面/模块** | 复制结果弹窗 |
| **关联错误场景** | `ERR_COPY_WRITE_SYSTEM_ERROR` |
| **来源** | `[confirmed]` |

**messageInfo 参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| trackType | `'messageInfo'` | 固定类型 | 前端定义 |
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_result` |
| info | string | 用户可见错误信息："系统异常，请稍后重试" | 前端定义 / 接口返回 |
| info2 | string | 失败人数 | 写入结果 |
| info3 | string | 错误码 errorCode | 接口返回 |
| info4 | string | 展示形式：`resultError` | 前端定义 |
| info5 | string | 触发动作：`request` | 前端定义 |
| traceid | string | 接口 traceid（可选） | 接口返回 |

---

#### ERR_COPY_TARGET_DISABLED

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_TARGET_DISABLED` |
| **触发时机** | 写入时检测到目标用户已被禁用或移除，结果弹窗展示时 |
| **所属页面/模块** | 复制结果弹窗 |
| **关联错误场景** | `ERR_COPY_TARGET_DISABLED` |
| **来源** | `[confirmed]` |

**messageInfo 参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| trackType | `'messageInfo'` | 固定类型 | 前端定义 |
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_result` |
| info | string | 用户可见错误信息："该用户在企业中已被禁用" | 前端定义 |
| info2 | string | 失败用户 ID | 接口返回 |
| info3 | string | 错误分类：`TARGET_USER_DISABLED` | 前端定义 |
| info4 | string | 展示形式：`resultError` | 前端定义 |
| info5 | string | 触发动作：`request` | 前端定义 |
| traceid | string | 接口 traceid（可选） | 接口返回 |

---

### 3.4 复制弹窗 — 来源变更 报错埋点

#### ERR_COPY_SOURCE_CHANGED

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_COPY_SOURCE_CHANGED` |
| **触发时机** | 提交时检测到来源权限已变更，弹窗内阻断 |
| **所属页面/模块** | 复制弹窗 |
| **关联错误场景** | `ERR_COPY_SOURCE_CHANGED` |
| **来源** | `[confirmed]`（策略待 GAP-04 确认） |

**messageInfo 参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| trackType | `'messageInfo'` | 固定类型 | 前端定义 |
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_dialog` |
| info | string | 用户可见错误信息："复制来源"{子管理员姓名}"的权限配置已被修改，请关闭弹窗后重新打开获取最新配置。" | 前端定义 |
| info2 | string | 来源子管理员 ID | 列表行数据 |
| info3 | string | 错误分类：`SOURCE_CHANGED` | 前端定义 |
| info4 | string | 展示形式：`AlertError` | 前端定义 |
| info5 | string | 触发动作：`request` | 前端定义 |

---

## 4. 报错形式确认说明

| 报错场景 | 推荐 info4 | 线上/测试环境实际形式 | 是否需调整 | 依据/说明 |
|---|---|---|---|---|
| 复制信息未选择 | `FormError` | 待实测 | 否 | 字段级校验，inline 红字最合适 |
| 复制对象未选择 | `FormError` | 待实测 | 否 | 字段级校验，inline 红字最合适 |
| 目标用户加入状态不符 | `AlertError` | 待实测 | 否 | 弹窗内阻断区，列出多个用户名，弹窗式阻断最合适 |
| 目标用户认证状态不符 | `AlertError` | 待实测 | 否 | 同上 |
| 复制对象超过上限 | `Toast` | 待实测 | 否 | 即时轻量提示，toast 自动消失最合适 |
| 写入阶段系统异常 | `resultError` | 待实测 | 否 | 在结果弹窗内展示，resultError 与结果页语境一致 |
| 目标用户被禁用或移除 | `resultError` | 待实测 | 否 | 同上，在结果弹窗失败分组中展示 |
| 来源被修改或删除 | `AlertError` | 待实测 | 否 | 弹窗内阻断提示，需明确操作指引 |

### 4.1 报错埋点代码示例

```ts
import { Util, TrackType } from '@lw36.01/common';

// ===== FormError 示例：复制信息未选择 =====
const visibleErrorMessage = '请选择复制信息';
if (visibleErrorMessage && visibleErrorMessage.trim()) {
  Util.trackData({
    cust_id: 'admin_subadmin_copy_dialog',
    info: visibleErrorMessage.trim(),
    info2: 'validate_step_1',
    info3: 'VALIDATION_INFO_EMPTY',
    info4: 'FormError',
    info5: 'confirm_click',
  }, TrackType.messageInfo);
}

// ===== AlertError 示例：加入状态不符 =====
const blockedUsers = getBlockedUsersByJoinStatus();
if (blockedUsers.length > 0) {
  const errorMsg = '以下用户的加入状态不符合要求，不能成为子管理员';
  if (errorMsg && errorMsg.trim()) {
    Util.trackData({
      cust_id: 'admin_subadmin_copy_dialog',
      info: errorMsg.trim(),
      info2: blockedUsers.map(u => u.id).join(','),
      info3: 'VALIDATION_JOIN_STATUS',
      info4: 'AlertError',
      info5: 'validate_fail_join_status',
    }, TrackType.messageInfo);
  }
}

// ===== Toast 示例：超过上限 =====
if (selectedCount >= 200) {
  const errorMsg = '最多可选择 200 名复制对象';
  if (errorMsg && errorMsg.trim()) {
    Util.trackData({
      cust_id: 'admin_subadmin_copy_dialog',
      info: errorMsg.trim(),
      info2: String(selectedCount),
      info3: 'VALIDATION_MAX_LIMIT',
      info4: 'Toast',
      info5: 'select_exceed_limit',
    }, TrackType.messageInfo);
  }
}

// ===== resultError 示例：写入系统异常 =====
const writeError = getWriteError();
const errorMsg = '系统异常，请稍后重试';
if (writeError && errorMsg && errorMsg.trim()) {
  Util.trackData({
    cust_id: 'admin_subadmin_copy_result',
    info: errorMsg.trim(),
    info2: String(failCount),
    info3: writeError.errorCode || 'WRITE_SYSTEM_ERROR',
    info4: 'resultError',
    info5: 'request',
    traceid: writeError.traceid,
  }, TrackType.messageInfo);
}
```

## 5. 报错-旅程节点关联

| 错误场景标识 | 关联旅程节点 | 上一个旅程节点 | 下一个旅程节点 | 来源 |
|---|---|---|---|---|
| ERR_COPY_INFO_NOT_SELECTED | N5 提交校验 | N3 确认复制信息 | N3 确认复制信息（修正后重试） | confirmed |
| ERR_COPY_TARGET_NOT_SELECTED | N5 提交校验 | N4 选择复制对象 | N4 选择复制对象（修正后重试） | confirmed |
| ERR_COPY_JOIN_STATUS_FAIL | N5 提交校验 / N6 校验阻断 | N4 选择复制对象 | N4 选择复制对象（移除后重选） | confirmed |
| ERR_COPY_AUTH_STATUS_FAIL | N5 提交校验 / N6 校验阻断 | N4 选择复制对象 | N4 选择复制对象（移除后重选） | confirmed |
| ERR_COPY_TARGET_MAX_EXCEEDED | N4 选择复制对象 | N4 选择复制对象 | N4 选择复制对象（确认当前或调整） | confirmed |
| ERR_COPY_WRITE_SYSTEM_ERROR | N7 复制写入中 | N7 复制写入中 | N8 查看复制结果（失败分组） | confirmed |
| ERR_COPY_TARGET_DISABLED | N7 复制写入中 | N7 复制写入中 | N8 查看复制结果（失败分组） | confirmed |
| ERR_COPY_SOURCE_CHANGED | N5 提交校验 | N2 点击复制入口 | N2 点击复制入口（重新打开弹窗） | confirmed |
