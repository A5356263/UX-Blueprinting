# 旅程埋点需求文档

> 基于体验蓝图 `spark-output/experience_blueprint.md` 和 `journey_visual.md` 生成。
> 埋点方法参考 `journey-metrics` 合同规范。项目根目录无 `tracking_spec.md`，无 `knowledge/raw/业务/埋点统一方法.md`，按合同内建 API 规范生成。

## 1. 埋点方法说明

本次旅程埋点遵循以下规范：

- **旅程管理**：`window.UX.startUserTask(taskName, taskId?)` 开启上下文，`window.UX.endUserTask()` 结束
- **子任务管理**：`window.UX.startUserSubTask(subTaskName)` 开启子任务上下文，`window.UX.endUserSubTask()` 结束
- **节点标记**（Button）：`<Button x-track-taskname="节点名称">`
- **节点标记**（非 Button / 手动埋点）：`Util.trackData({ tasknodeName: '节点名称' }, TrackType.custom)`，字段大小写必须是 `tasknodeName`
- **taskName 命名**：建议使用 `{DOMAIN}_{MODULE}_{ACTION}`，本次使用 `PERMISSION_SUBADMIN_COPY`
- **taskId**：可不传；不传时系统基于 taskName 自动生成唯一 ID
- **来源标记**：每个事件标注 `[confirmed]` / `[inferred]` / `[conflict]`
- **开始/结束 API 不自动打点**：`startUserTask` / `endUserTask` 只注册或清理上下文，不产生节点埋点
- **结束节点顺序**：非按钮结束节点必须先 `Util.trackData(..., TrackType.custom)` 上报结束节点，再调用 `window.UX.endUserTask()`

## 2. 系统自动携带参数

以下参数由系统自动携带，**不在此文档中逐事件列出**：

| 参数 | 说明 |
|---|---|
| 企业信息 | 用户所属企业标识 |
| 页面信息 | 当前页面路由、标题 |
| 任务上下文 | taskName, taskId, subTaskName（当旅程 API 已调用时） |

## 3. 旅程任务定义

### 3.1 核心任务

| 字段 | 值 |
|---|---|
| **taskName** | `PERMISSION_SUBADMIN_COPY` |
| **任务描述** | 权限管理员在子管理员模式列表中，从已有子管理员复制可授权组织和可授权功能给其他用户 |
| **涉及角色** | 权限管理员 / 超级管理员 |

**核心任务节点：**

| 节点类型 | taskNodeName | 节点描述 | 角色 | 对应旅程节点 |
|---|---|---|---|---|
| 开始节点 | PERMISSION_SUBADMIN_LIST_VIEW | 进入子管理员模式列表页，页面加载完成 | 权限管理员 | N1 进入子管理员列表 |
| 关键节点 | PERMISSION_SUBADMIN_COPY_ENTRY | 点击来源子管理员操作列的复制按钮 | 权限管理员 | N2 点击复制入口 |
| 关键节点 | PERMISSION_SUBADMIN_COPY_INFO_CONFIRM | 在复制弹窗中确认或调整复制信息勾选 | 权限管理员 | N3 确认复制信息 |
| 关键节点 | PERMISSION_SUBADMIN_COPY_TARGET_SELECT | 通过员工选择器选择目标用户 | 权限管理员 | N4 选择复制对象 |
| 关键节点 | PERMISSION_SUBADMIN_COPY_VALIDATE | 点击确认触发逐项校验并提交 | 权限管理员 | N5 提交校验 |
| 关键节点 | PERMISSION_SUBADMIN_COPY_BLOCKED | 校验阻断，查看不符合用户列表 | 权限管理员 | N6 校验阻断-调整选择 |
| 关键节点 | PERMISSION_SUBADMIN_COPY_WRITE | 校验通过后系统写入权限配置 | 权限管理员 | N7 复制写入中 |
| 结束节点 | PERMISSION_SUBADMIN_COPY_RESULT | 查看复制结果弹窗，确认完成后关闭 | 权限管理员 | N8 查看复制结果 |

## 4. 旅程埋点事件

### 4.1 核心任务：PERMISSION_SUBADMIN_COPY

#### 开始节点：PERMISSION_SUBADMIN_LIST_VIEW `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | PERMISSION_SUBADMIN_LIST_VIEW |
| **节点描述** | 进入子管理员模式列表页，页面加载完成，操作列可见 |
| **节点类型** | 开始节点 |
| **所属任务** | 核心任务（PERMISSION_SUBADMIN_COPY） |
| **标记方式** | Util.trackData |
| **触发时机** | 子管理员模式列表页加载完成，数据渲染完毕 |
| **所属页面/模块** | 子管理员模式列表页 |
| **对应旅程节点** | N1 进入子管理员列表 |
| **来源** | `[confirmed]` |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_list` |

**选传参数：** 无可选传参数

---

#### 关键节点：PERMISSION_SUBADMIN_COPY_ENTRY `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | PERMISSION_SUBADMIN_COPY_ENTRY |
| **节点描述** | 在子管理员列表操作列点击复制按钮，打开复制弹窗 |
| **节点类型** | 关键节点 |
| **所属任务** | 核心任务（PERMISSION_SUBADMIN_COPY） |
| **标记方式** | x-track-taskname |
| **触发时机** | 点击来源子管理员行操作列的「复制」按钮 |
| **所属页面/模块** | 子管理员模式列表页 → 操作列 |
| **对应旅程节点** | N2 点击复制入口 |
| **来源** | `[confirmed]` |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_list` |

**选传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| source_admin_id | string | 复制来源子管理员的用户 ID | 列表行数据 |
| source_admin_name | string | 复制来源子管理员的姓名 | 列表行数据 |

---

#### 关键节点：PERMISSION_SUBADMIN_COPY_INFO_CONFIRM `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | PERMISSION_SUBADMIN_COPY_INFO_CONFIRM |
| **节点描述** | 在复制弹窗中确认复制信息勾选状态（默认全选，可取消某项） |
| **节点类型** | 关键节点 |
| **所属任务** | 核心任务（PERMISSION_SUBADMIN_COPY） |
| **标记方式** | Util.trackData |
| **触发时机** | 复制弹窗中"复制信息"区 checkbox 状态变更时（debounce 500ms） |
| **所属页面/模块** | 复制弹窗 → 复制信息区 |
| **对应旅程节点** | N3 确认复制信息 |
| **来源** | `[confirmed]` |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_dialog` |

**选传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| copy_org_checked | boolean | 可授权组织是否勾选 | checkbox 状态 |
| copy_func_checked | boolean | 可授权功能是否勾选 | checkbox 状态 |

---

#### 关键节点：PERMISSION_SUBADMIN_COPY_TARGET_SELECT `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | PERMISSION_SUBADMIN_COPY_TARGET_SELECT |
| **节点描述** | 通过员工选择器选择或移除目标用户，选择完成 |
| **节点类型** | 关键节点 |
| **所属任务** | 核心任务（PERMISSION_SUBADMIN_COPY） |
| **标记方式** | Util.trackData |
| **触发时机** | 选择员工弹窗关闭时（确定选择），或复制对象标签被移除时 |
| **所属页面/模块** | 复制弹窗 → 复制对象区 / 选择员工弹窗 |
| **对应旅程节点** | N4 选择复制对象 |
| **来源** | `[confirmed]` |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_dialog` |

**选传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| target_count | number | 当前已选目标用户数量 | 选择器计数器 |
| action | string | 操作类型：`add`（添加）/ `remove`（移除） | 前端状态 |

---

#### 关键节点：PERMISSION_SUBADMIN_COPY_VALIDATE `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | PERMISSION_SUBADMIN_COPY_VALIDATE |
| **节点描述** | 点击确认按钮，系统开始逐项校验 |
| **节点类型** | 关键节点 |
| **所属任务** | 核心任务（PERMISSION_SUBADMIN_COPY） |
| **标记方式** | x-track-taskname |
| **触发时机** | 点击复制弹窗「确认」按钮 |
| **所属页面/模块** | 复制弹窗 → 底部按钮区 |
| **对应旅程节点** | N5 提交校验 |
| **来源** | `[confirmed]` |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_dialog` |

**选传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| copy_org_checked | boolean | 可授权组织是否勾选 | checkbox 状态 |
| copy_func_checked | boolean | 可授权功能是否勾选 | checkbox 状态 |
| target_count | number | 复制对象数量 | 选择器计数器 |
| validate_result | string | 校验结果：`pass` / `fail_info` / `fail_target` / `fail_join_status` / `fail_auth_status` | 校验结果 |

---

#### 关键节点：PERMISSION_SUBADMIN_COPY_BLOCKED `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | PERMISSION_SUBADMIN_COPY_BLOCKED |
| **节点描述** | 校验阻断，弹窗展示阻断提示区，列出不符合用户 |
| **节点类型** | 关键节点 |
| **所属任务** | 核心任务（PERMISSION_SUBADMIN_COPY） |
| **标记方式** | Util.trackData |
| **触发时机** | 校验步骤 3（加入状态）或步骤 4（认证状态）不通过，阻断提示区展示时 |
| **所属页面/模块** | 复制弹窗 → 阻断提示区 |
| **对应旅程节点** | N6 校验阻断-调整选择 |
| **来源** | `[confirmed]` |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_dialog` |

**选传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| blocked_reason | string | 阻断原因：`join_status` / `auth_status` | 校验结果 |
| blocked_user_count | number | 被阻断的用户数量 | 阻断列表长度 |
| blocked_user_ids | string | 被阻断的用户 ID 列表（逗号分隔） | 阻断列表数据 |

---

#### 关键节点：PERMISSION_SUBADMIN_COPY_WRITE `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | PERMISSION_SUBADMIN_COPY_WRITE |
| **节点描述** | 校验通过，系统开始写入权限配置，弹窗进入 loading 态 |
| **节点类型** | 关键节点 |
| **所属任务** | 核心任务（PERMISSION_SUBADMIN_COPY） |
| **标记方式** | Util.trackData |
| **触发时机** | 校验通过后，发起写入请求时 |
| **所属页面/模块** | 复制弹窗 → 写入中 |
| **对应旅程节点** | N7 复制写入中 |
| **来源** | `[confirmed]` |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_dialog` |

**选传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| source_admin_id | string | 复制来源子管理员 ID | 列表行数据 |
| target_count | number | 目标用户总数 | 选择器计数器 |
| copy_org | boolean | 是否复制可授权组织 | checkbox 状态 |
| copy_func | boolean | 是否复制可授权功能 | checkbox 状态 |
| write_result | string | 写入结果：`success` / `partial` / `fail` | 接口返回 |

---

#### 结束节点：PERMISSION_SUBADMIN_COPY_RESULT `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | PERMISSION_SUBADMIN_COPY_RESULT |
| **节点描述** | 查看复制结果弹窗，确认新增/叠加/失败明细后关闭 |
| **节点类型** | 结束节点 |
| **所属任务** | 核心任务（PERMISSION_SUBADMIN_COPY） |
| **标记方式** | Util.trackData |
| **触发时机** | 点击结果弹窗「知道了」按钮关闭弹窗时 |
| **所属页面/模块** | 复制结果弹窗 |
| **对应旅程节点** | N8 查看复制结果 |
| **来源** | `[confirmed]` |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 自定义埋点名称 | 前端定义：`admin_subadmin_copy_result` |

**选传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| total_success | number | 成功复制的总人数 | 写入结果 |
| new_admin_count | number | 新增子管理员人数 | 写入结果 |
| overlay_count | number | 权限已叠加人数 | 写入结果 |
| fail_count | number | 复制失败人数 | 写入结果 |
| result_type | string | 结果类型：`all_success` / `partial_success` / `all_fail` | 写入结果 |

---

## 5. 事件-旅程节点映射

| taskNodeName | 所属任务 | 节点类型 | 标记方式 | 角色 | 对应旅程节点 | 来源 |
|---|---|---|---|---|---|---|
| PERMISSION_SUBADMIN_LIST_VIEW | 核心任务 | 开始节点 | Util.trackData | 权限管理员 | N1 | confirmed |
| PERMISSION_SUBADMIN_COPY_ENTRY | 核心任务 | 关键节点 | x-track-taskname | 权限管理员 | N2 | confirmed |
| PERMISSION_SUBADMIN_COPY_INFO_CONFIRM | 核心任务 | 关键节点 | Util.trackData | 权限管理员 | N3 | confirmed |
| PERMISSION_SUBADMIN_COPY_TARGET_SELECT | 核心任务 | 关键节点 | Util.trackData | 权限管理员 | N4 | confirmed |
| PERMISSION_SUBADMIN_COPY_VALIDATE | 核心任务 | 关键节点 | x-track-taskname | 权限管理员 | N5 | confirmed |
| PERMISSION_SUBADMIN_COPY_BLOCKED | 核心任务 | 关键节点 | Util.trackData | 权限管理员 | N6 | confirmed |
| PERMISSION_SUBADMIN_COPY_WRITE | 核心任务 | 关键节点 | Util.trackData | 权限管理员 | N7 | confirmed |
| PERMISSION_SUBADMIN_COPY_RESULT | 核心任务 | 结束节点 | Util.trackData | 权限管理员 | N8 | confirmed |

## 6. 旅程生命周期代码示例

```js
// ===== 核心任务：PERMISSION_SUBADMIN_COPY =====
import { Util, TrackType } from '@lw36.01/common';

const taskName = 'PERMISSION_SUBADMIN_COPY';
const taskId = `${taskName}_${sourceAdminId}_${Date.now()}`;

// 1. 开始旅程上下文。startUserTask 只注册 taskName/taskId，不会自动打点。
window.UX.startUserTask(taskName, taskId);

// 2. 开始节点 — 子管理员列表页加载完成
// 页面加载完成后手动标记
useEffect(() => {
  if (listLoaded) {
    Util.trackData({
      cust_id: 'admin_subadmin_list',
      tasknodeName: 'PERMISSION_SUBADMIN_LIST_VIEW',
    }, TrackType.custom);
  }
}, [listLoaded]);

// 3. 关键节点 — 点击复制按钮，打开弹窗
<Button
  x-track-taskname="PERMISSION_SUBADMIN_COPY_ENTRY"
  onClick={(record) => {
    setCopySource(record);
    setDialogVisible(true);
  }}
>
  复制
</Button>

// 4. 关键节点 — 复制信息 checkbox 变更（debounce 500ms）
const handleCopyInfoChange = useDebounce((checked) => {
  Util.trackData({
    cust_id: 'admin_subadmin_copy_dialog',
    tasknodeName: 'PERMISSION_SUBADMIN_COPY_INFO_CONFIRM',
    copy_org_checked: checked.org,
    copy_func_checked: checked.func,
  }, TrackType.custom);
}, 500);

// 5. 关键节点 — 选择员工弹窗关闭
const handleStaffSelectClose = (selectedUsers, action) => {
  Util.trackData({
    cust_id: 'admin_subadmin_copy_dialog',
    tasknodeName: 'PERMISSION_SUBADMIN_COPY_TARGET_SELECT',
    target_count: selectedUsers.length,
    action: action, // 'add' | 'remove'
  }, TrackType.custom);
};

// 6. 关键节点 — 点击确认校验
<Button
  x-track-taskname="PERMISSION_SUBADMIN_COPY_VALIDATE"
  onClick={async () => {
    const result = await validateAndSubmit();
    // validate_result 在 validateAndSubmit 内部通过额外的 custom event 上报
  }}
>
  确认
</Button>

// 7. 关键节点 — 校验阻断（在 validateAndSubmit 内部）
const handleBlocked = (reason, blockedUsers) => {
  Util.trackData({
    cust_id: 'admin_subadmin_copy_dialog',
    tasknodeName: 'PERMISSION_SUBADMIN_COPY_BLOCKED',
    blocked_reason: reason, // 'join_status' | 'auth_status'
    blocked_user_count: blockedUsers.length,
    blocked_user_ids: blockedUsers.map(u => u.id).join(','),
  }, TrackType.custom);
};

// 8. 关键节点 — 写入请求
const handleWrite = (params) => {
  Util.trackData({
    cust_id: 'admin_subadmin_copy_dialog',
    tasknodeName: 'PERMISSION_SUBADMIN_COPY_WRITE',
    source_admin_id: params.sourceAdminId,
    target_count: params.targetIds.length,
    copy_org: params.copyOrg,
    copy_func: params.copyFunc,
    write_result: params.result, // 'success' | 'partial' | 'fail'
  }, TrackType.custom);
};

// ===== 旅程结束 =====
// 9. 结束节点 — 结果弹窗关闭。先打结束节点，再 endUserTask。
const handleResultClose = (resultSummary) => {
  Util.trackData({
    cust_id: 'admin_subadmin_copy_result',
    tasknodeName: 'PERMISSION_SUBADMIN_COPY_RESULT',
    total_success: resultSummary.totalSuccess,
    new_admin_count: resultSummary.newAdminCount,
    overlay_count: resultSummary.overlayCount,
    fail_count: resultSummary.failCount,
    result_type: resultSummary.type, // 'all_success' | 'partial_success' | 'all_fail'
  }, TrackType.custom);
  window.UX.endUserTask();
};
```

## 7. 知识冲突项

1. **子管理员模式与双管理员模式互斥**
   - **知识库规则**：R-009 子管理员模式与双管理员模式不可同时开启（来源：`knowledge/raw/业务/权限管理/23_规则契约.md`）
   - **需求文档主张**：PRD §10 "若开启双管理员互审模式，复制完成时需要生成一条审批"
   - **影响节点**：N7, N8
   - **影响 taskNodeName**：PERMISSION_SUBADMIN_COPY_WRITE, PERMISSION_SUBADMIN_COPY_RESULT
   - **当前处理**：已按互斥成立（写入直接生效，无审批状态）生成埋点，标记为 `[conflict]`。如果互斥不成立，PERMISSION_SUBADMIN_COPY_WRITE 后需增加 `PERMISSION_SUBADMIN_COPY_APPROVAL_PENDING` 节点。
   - **建议**：UXB 已按互斥成立推进，GAP-02 等待产品最终确认。
