# 旅程埋点需求文档

> 本模板定义 `journey_tracking_spec.md` 的输出结构。
> 埋点方法优先遵循宿主已提供的本地埋点方法文档；若不存在，再通过 `knowledge-wiki` 命中相关埋点方法知识，并按 `summary -> raw` 顺序消费。
> 旅程节点使用 `x-track-taskname` 属性（Button）或 `tasknodeName` 手动埋点，taskName 建议格式 `{DOMAIN}_{MODULE}_{ACTION}`。
> 每个事件标注"来源"属性：confirmed / inferred / conflict。参数取值来源必须明确，不得使用 `待定`、`TBD` 等占位符。
> 基础信息（企业信息、页面信息、任务上下文）由系统自动携带，不在此文档中列出。

## 1. 埋点方法说明

本次旅程埋点遵循以下规范：

- **旅程管理**：`window.UX.startUserTask(taskName, taskId?)` 开启上下文，`window.UX.endUserTask()` 结束
- **子任务管理**：`window.UX.startUserSubTask(subTaskName)` 开启子任务上下文，`window.UX.endUserSubTask()` 结束
- **节点标记**（Button）：`<Button x-track-taskname="节点名称">`
- **节点标记**（非 Button / 手动埋点）：`Util.trackData({ tasknodeName: '节点名称' }, TrackType.custom)`，字段大小写必须是 `tasknodeName`
- **taskName 命名**：建议使用 `{DOMAIN}_{MODULE}_{ACTION}`，如 `TRIP_APPLY_SUBMIT`、`FINANCE_APPROVE_REJECT`；建议级，不强制
- **subTaskName 命名**：建议使用 `{DOMAIN}_{MODULE}_{ACTION}`，如 `TRIP_APPROVE_REVIEW`、`FINANCE_APPROVE_CHECK`；建议级，不强制
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
| **taskName** | `{DOMAIN}_{MODULE}_{ACTION}` |
| **任务描述** | <本次旅程覆盖的完整任务场景> |
| **涉及角色** | <角色 A>、<角色 B> |

**核心任务节点：**

| 节点类型 | taskNodeName | 节点描述 | 角色 | 对应旅程节点 |
|---|---|---|---|---|
| 开始节点 | <taskNodeName> | <该节点做什么> | <角色> | N1 <节点名称> |
| 关键节点 | <taskNodeName> | <该节点做什么> | <角色> | N2 <节点名称> |
| 关键节点 | <taskNodeName> | <该节点做什么> | <角色> | N3 <节点名称> |
| 结束节点 | <taskNodeName> | <该节点做什么> | <角色> | N5 <节点名称> |

### 3.2 子任务（如有）

<!-- 仅当旅程包含独立子流程时填写。每个子任务独立定义一个 block。 -->

| 字段 | 值 |
|---|---|
| **subTaskName** | `{DOMAIN}_{MODULE}_{ACTION}` |
| **父任务** | <关联的 taskName> |
| **子任务描述** | <子任务覆盖的子流程场景> |
| **涉及角色** | <角色 B> |

**子任务节点：**

| 节点类型 | taskNodeName | 节点描述 | 角色 | 对应旅程节点 |
|---|---|---|---|---|
| 开始节点 | <taskNodeName> | <该节点做什么> | <角色> | N10 <节点名称> |
| 关键节点 | <taskNodeName> | <该节点做什么> | <角色> | N11 <节点名称> |
| 结束节点 | <taskNodeName> | <该节点做什么> | <角色> | N12 <节点名称> |

## 4. 旅程埋点事件

<!-- 按任务层级组织，每个节点一个埋点事件 block。 -->

### 4.1 核心任务：{taskName}

#### 开始节点：<taskNodeName> `[confirmed]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | <节点名称，对应 x-track-taskname 属性值> |
| **节点描述** | <人类可读的节点描述> |
| **节点类型** | 开始节点 |
| **所属任务** | 核心任务（{taskName}） |
| **标记方式** | x-track-taskname / Util.trackData |
| **触发时机** | <在什么用户操作或系统条件下触发> |
| **所属页面/模块** | <页面名称或功能模块> |
| **对应旅程节点** | N1 <节点名称> |
| **来源** | `[confirmed]` / `[inferred]` / `[conflict]` |

<!-- 当来源为 conflict 时，追加冲突说明：-->
<!-- **冲突说明**：<冲突描述，引用 knowledge-wiki 中命中的相关知识> -->

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 自定义埋点名称，用于标识功能模块或业务场景 | 前端定义 |
| <param_name> | string | <参数含义> | <URL参数/接口返回/前端状态/用户输入> |

**选传参数：** 无可选传参数

---

#### 关键节点：<taskNodeName> `[inferred]`

| 字段 | 值 |
|---|---|
| **taskNodeName** | <节点名称> |
| **节点描述** | <节点描述> |
| **节点类型** | 关键节点 |
| **所属任务** | 核心任务（{taskName}） |
| **标记方式** | <x-track-taskname / Util.trackData> |
| **触发时机** | <触发时机> |
| **所属页面/模块** | <页面/模块> |
| **对应旅程节点** | N2 <节点名称> |
| **来源** | `[confirmed]` / `[inferred]` / `[conflict]` |

**必传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| cust_id | string | 自定义埋点名称，用于标识功能模块或业务场景 | 前端定义 |
| <param_name> | string | <参数含义> | <取值来源> |

**选传参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| <param_name> | string | <参数含义> | <取值来源> |

---

#### 结束节点：<taskNodeName> `[confirmed]`

<!-- 同结构，结束节点通常标记 x-track-taskname="旅程结束" -->

---

### 4.2 子任务：{subTaskName}（如有）

<!-- 同核心任务结构，每个子任务的开始/关键/结束节点各一个 block。 -->

#### 开始节点：<taskNodeName> `[confirmed]`

<!-- 同结构，所属任务字段填 "子任务（{subTaskName}）" -->

## 5. 事件-旅程节点映射

<!-- 交叉引用表，便于快速定位。区分任务层级和节点类型。 -->

| taskNodeName | 所属任务 | 节点类型 | 标记方式 | 角色 | 对应旅程节点 | 来源 |
|---|---|---|---|---|---|---|
| <节点名称> | 核心任务 | 开始节点 | x-track-taskname | <角色> | N1 | confirmed |
| <节点名称> | 核心任务 | 关键节点 | Util.trackData | <角色> | N2 | inferred |
| <节点名称> | 子任务({subTaskName}) | 开始节点 | x-track-taskname | <角色> | N10 | confirmed |

## 6. 旅程生命周期代码示例

<!-- 给出本次旅程的完整埋点代码骨架，包含核心任务和子任务 -->

```js
// ===== 核心任务 =====
const taskName = '{taskName}';
const taskId = `${taskName}_${batchNo || applyNo || Date.now()}`;

// 1. 开始旅程上下文。注意：startUserTask 只注册 taskName/taskId，不会自动打点。
window.UX.startUserTask(taskName, taskId);

// 2. 开始节点 — Button 节点用 x-track-taskname 标记。
<Button
  x-track-taskname="<开始节点名称>"
  onClick={() => {
    // 进入/开始当前旅程的业务动作
  }}
>
  开始
</Button>

// 3. 中间节点 — Button 节点用 x-track-taskname。
<Button x-track-taskname="<关键节点名称>" onClick={...}>操作</Button>

// 4. 中间节点 — 非按钮或页面加载类节点用 TrackType.custom 手动标记。
Util.trackData({
  cust_id: '<功能模块或业务场景埋点名称>',
  tasknodeName: '<中间节点名称>',
}, TrackType.custom);

// ===== 子任务（如有）=====
window.UX.startUserSubTask('{subTaskName}');

// 子任务开始节点
<Button x-track-taskname="<子任务开始节点>" onClick={...}>开始审批</Button>

// 子任务关键节点
Util.trackData({
  cust_id: '<功能模块或业务场景埋点名称>',
  tasknodeName: '<子任务关键节点>',
}, TrackType.custom);

// 子任务结束时，先上报子任务结束节点，再清理子任务上下文。
Util.trackData({
  cust_id: '<功能模块或业务场景埋点名称>',
  tasknodeName: '<子任务结束节点>',
}, TrackType.custom);
window.UX.endUserSubTask();

// ===== 旅程结束 =====
// 5. 任务成功结束节点。注意：先打结束节点，再 endUserTask。
Util.trackData({
  cust_id: '<功能模块或业务场景埋点名称>',
  tasknodeName: '<任务成功结束节点名称>',
}, TrackType.custom);
window.UX.endUserTask();
```

## 7. 知识冲突项

<!-- 仅当检测到需求与知识库冲突时填写，无冲突可删除此章节 -->

1. **<冲突标题>**
   - **知识库规则**：<规则内容>（来源：`knowledge-wiki` 命中的相关知识）
   - **需求文档主张**：<主张内容>
   - **影响节点**：<Nx, Ny>
   - **影响 taskNodeName**：<taskNodeName_1, taskNodeName_2>
   - **当前处理**：已按需求生成埋点，标记为 [conflict]
   - **建议**：回到业务判断阶段或等效治理流程，确认需求是否成立。
