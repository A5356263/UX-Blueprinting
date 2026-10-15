# 旅程埋点需求文档

## 1. 埋点方法说明

本次旅程埋点遵循以下规范：

- **旅程管理**：`window.UX.startUserTask(taskName, taskId?)` 开启上下文，`window.UX.endUserTask()` 结束
- **子任务管理**：`window.UX.startUserSubTask(subTaskName)` 开启子任务上下文，`window.UX.endUserSubTask()` 结束
- **节点标记**（Button）：`<Button x-track-taskname="节点名称">`
- **节点标记**（非 Button / 手动埋点）：`Util.trackData({ tasknodeName: '节点名称' }, TrackType.custom)`，字段大小写必须是 `tasknodeName`
- **taskName 命名**：建议使用 `{DOMAIN}_{MODULE}_{ACTION}`；建议级，不强制
- **subTaskName 命名**：建议使用 `{DOMAIN}_{MODULE}_{ACTION}`；建议级，不强制
- **taskId**：可不传；不传时系统基于 taskName 自动生成唯一 ID
- **来源标记**：`[confirmed]` / `[inferred]` / `[conflict]`
- **开始/结束 API 不自动打点**：`startUserTask` / `endUserTask` 只注册或清理上下文，不产生节点埋点
- **结束节点顺序**：非按钮结束节点必须先 `Util.trackData(..., TrackType.custom)` 上报结束节点，再调用 `window.UX.endUserTask()`

## 2. 系统自动携带参数

| 参数 | 说明 |
|---|---|
| 企业信息 | 用户所属企业标识 |
| 页面信息 | 当前页面路由、标题 |
| 任务上下文 | taskName, taskId, subTaskName（当旅程 API 已调用时） |

## 3. 旅程任务定义

### 3.1 核心任务

| 字段 | 值 |
|---|---|
| **taskName** | `TRIP_PERMISSION_APPLY` |
| **任务描述** | 企业内部权限申请审批流程：员工提交权限申请，管理员审批（通过/驳回），员工查看结果 |
| **涉及角色** | 员工、管理员 |

**核心任务节点：**

| 节点类型 | taskNodeName | 节点描述 | 角色 | 对应旅程节点 |
|---|---|---|---|---|
| 开始节点 | 进入申请页 | 员工进入权限申请页面 | 员工 | N1 进入申请页 |
| 关键节点 | 填写申请信息 | 员工填写权限类型和申请理由 | 员工 | N2 填写申请信息 |
| 关键节点 | 提交申请 | 员工点击提交按钮 | 员工 | N3 提交申请 |
| 关键节点 | 查看申请状态 | 员工在申请列表查看审批进度 | 员工 | N4 查看申请状态 |
| 关键节点 | 查看驳回原因 | 员工查看被驳回的具体原因和说明 | 员工 | N7 查看驳回原因及说明 |
| 关键节点 | 重新编辑申请 | 员工基于驳回原因编辑并重新进入申请 | 员工 | N8 重新编辑申请 |
| 结束节点 | 查看通过结果 | 员工确认申请已通过 | 员工 | N6 确认通过 |

### 3.2 子任务：审批

| 字段 | 值 |
|---|---|
| **subTaskName** | `TRIP_PERMISSION_APPROVE` |
| **父任务** | `TRIP_PERMISSION_APPLY` |
| **子任务描述** | 管理员对权限申请进行审批操作（通过或驳回），驳回时填写原因和补充说明 |
| **涉及角色** | 管理员 |

**子任务节点：**

| 节点类型 | taskNodeName | 节点描述 | 角色 | 对应旅程节点 |
|---|---|---|---|---|
| 开始节点 | 进入审批列表 | 管理员进入待审批列表页面 | 管理员 | N21 进入审批列表 |
| 关键节点 | 查看待审批详情 | 管理员查看待审批申请的具体信息 | 管理员 | N22 查看待审批申请 |
| 关键节点 | 选择驳回原因 | 管理员在驳回原因下拉中选择类型 | 管理员 | N25 选择驳回原因 |
| 关键节点 | 填写补充说明 | 管理员在文本域中输入补充说明 | 管理员 | N26 填写补充说明 |
| 结束节点 | 确认驳回 | 管理员点击确认驳回提交审批结果 | 管理员 | N27 确认驳回 |

## 4. 旅程埋点事件

### 4.1 核心任务：TRIP_PERMISSION_APPLY

#### 开始节点：进入申请页 `[inferred]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | 进入申请页 |
| **节点描述** | 员工进入权限申请页面 |
| **节点类型** | 开始节点 |
| **所属任务** | 核心任务（TRIP_PERMISSION_APPLY） |
| **标记方式** | x-track-taskname |
| **触发时机** | 员工点击导航中的"权限申请"入口，页面加载完成 |
| **所属页面/模块** | 权限申请页 |
| **对应旅程节点** | N1 进入申请页 |
| **来源** | inferred |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 员工标识 | 登录态 |
| entry_source | string | 入口来源（导航/列表/重新编辑） | URL参数 |

**选传参数：** 无可选传参数

---

#### 关键节点：查看驳回原因 `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | 查看驳回原因 |
| **节点描述** | 员工在申请详情页查看驳回原因类型和补充说明 |
| **节点类型** | 关键节点 |
| **所属任务** | 核心任务（TRIP_PERMISSION_APPLY） |
| **标记方式** | x-track-taskname |
| **触发时机** | 申请详情页加载完成，申请状态为"已驳回"，展示驳回原因区域 |
| **所属页面/模块** | 申请详情页 |
| **对应旅程节点** | N7 查看驳回原因及说明 |
| **来源** | confirmed |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 申请单ID | URL参数 |
| apply_status | string | 申请状态（rejected） | 接口返回 |
| reject_reason | string | 驳回原因类型 | 接口返回 |
| has_reject_note | boolean | 是否有补充说明 | 接口返回 |

**选传参数：** 无可选传参数

---

#### 关键节点：重新编辑申请 `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | 重新编辑申请 |
| **节点描述** | 员工查看驳回原因后点击重新编辑按钮 |
| **节点类型** | 关键节点 |
| **所属任务** | 核心任务（TRIP_PERMISSION_APPLY） |
| **标记方式** | x-track-taskname |
| **触发时机** | 员工在驳回详情页点击"重新编辑"按钮 |
| **所属页面/模块** | 申请详情页 |
| **对应旅程节点** | N8 重新编辑申请 |
| **来源** | confirmed |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 申请单ID | URL参数 |
| reject_reason | string | 触发重新编辑的驳回原因类型 | 接口返回 |

**选传参数：** 无可选传参数

---

#### 结束节点：查看通过结果 `[inferred]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | 查看通过结果 |
| **节点描述** | 员工确认申请已审批通过 |
| **节点类型** | 结束节点 |
| **所属任务** | 核心任务（TRIP_PERMISSION_APPLY） |
| **标记方式** | x-track-taskname |
| **触发时机** | 申请详情页加载，状态为"已通过" |
| **所属页面/模块** | 申请详情页 |
| **对应旅程节点** | N6 确认通过 |
| **来源** | inferred |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 申请单ID | URL参数 |
| apply_status | string | 申请状态（approved） | 接口返回 |

**选传参数：** 无可选传参数

### 4.2 子任务：TRIP_PERMISSION_APPROVE

#### 开始节点：进入审批列表 `[inferred]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | 进入审批列表 |
| **节点描述** | 管理员进入待审批列表页面 |
| **节点类型** | 开始节点 |
| **所属任务** | 子任务（TRIP_PERMISSION_APPROVE） |
| **标记方式** | x-track-taskname |
| **触发时机** | 管理员点击导航中的"审批管理"入口，页面加载完成 |
| **所属页面/模块** | 审批列表页 |
| **对应旅程节点** | N21 进入审批列表 |
| **来源** | inferred |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 管理员标识 | 登录态 |

**选传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| pending_count | number | 待审批数量 | 接口返回 |

---

#### 关键节点：选择驳回原因 `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | 选择驳回原因 |
| **节点描述** | 管理员在驳回原因下拉框中选择驳回原因类型 |
| **节点类型** | 关键节点 |
| **所属任务** | 子任务（TRIP_PERMISSION_APPROVE） |
| **标记方式** | x-track-taskname |
| **触发时机** | 管理员点击驳回按钮后，在下拉框中选择驳回原因 |
| **所属页面/模块** | 审批详情页 |
| **对应旅程节点** | N25 选择驳回原因 |
| **来源** | confirmed |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 申请单ID | URL参数 |
| reject_reason | string | 选择的驳回原因类型 | 用户输入 |

**选传参数：** 无可选传参数

---

#### 结束节点：确认驳回 `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | 确认驳回 |
| **节点描述** | 管理员选择驳回原因后点击确认驳回提交审批结果 |
| **节点类型** | 结束节点 |
| **所属任务** | 子任务（TRIP_PERMISSION_APPROVE） |
| **标记方式** | Util.trackData |
| **触发时机** | 管理员点击确认驳回按钮，接口返回成功 |
| **所属页面/模块** | 审批详情页 |
| **对应旅程节点** | N27 确认驳回 |
| **来源** | confirmed |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 申请单ID | URL参数 |
| reject_reason | string | 驳回原因类型 | 用户输入 |
| has_reject_note | boolean | 是否填写了补充说明 | 前端状态 |
| approve_result | string | 审批结果（rejected） | 前端状态 |

**选传参数：** 无可选传参数

## 5. 事件-旅程节点映射

| taskNodeName | 所属任务 | 节点类型 | 标记方式 | 角色 | 对应旅程节点 | 来源 |
|---|---|---|---|---|---|---|
| 进入申请页 | 核心任务 | 开始节点 | x-track-taskname | 员工 | N1 | inferred |
| 查看驳回原因 | 核心任务 | 关键节点 | x-track-taskname | 员工 | N7 | confirmed |
| 重新编辑申请 | 核心任务 | 关键节点 | x-track-taskname | 员工 | N8 | confirmed |
| 查看通过结果 | 核心任务 | 结束节点 | x-track-taskname | 员工 | N6 | inferred |
| 进入审批列表 | 子任务(TRIP_PERMISSION_APPROVE) | 开始节点 | x-track-taskname | 管理员 | N21 | inferred |
| 选择驳回原因 | 子任务(TRIP_PERMISSION_APPROVE) | 关键节点 | x-track-taskname | 管理员 | N25 | confirmed |
| 确认驳回 | 子任务(TRIP_PERMISSION_APPROVE) | 结束节点 | Util.trackData | 管理员 | N27 | confirmed |

## 6. 旅程生命周期代码示例

```js
// ===== 核心任务：权限申请 =====
window.UX.startUserTask('TRIP_PERMISSION_APPLY');

// 开始节点
<Button x-track-taskname="进入申请页" onClick={...}>权限申请</Button>

// 关键节点 — 手动埋点（非按钮场景）
Util.trackData({
  cust_id: applyId,
  tasknodeName: '提交申请',
}, TrackType.custom);

// 关键节点
<Button x-track-taskname="查看驳回原因" onClick={...}>查看详情</Button>

// 关键节点
<Button x-track-taskname="重新编辑申请" onClick={...}>重新编辑</Button>

// ===== 子任务：审批 =====
window.UX.startUserSubTask('TRIP_PERMISSION_APPROVE');

// 开始节点
<Button x-track-taskname="进入审批列表" onClick={...}>审批管理</Button>

// 关键节点
<Button x-track-taskname="选择驳回原因" onClick={...}>驳回</Button>

// 结束节点 — 手动埋点
Util.trackData({
  cust_id: applyId,
  tasknodeName: '确认驳回',
}, TrackType.custom);

window.UX.endUserSubTask();

// ===== 结束节点 =====
Util.trackData({
  cust_id: applyId,
  tasknodeName: '查看通过结果',
}, TrackType.custom);

window.UX.endUserTask();
```
