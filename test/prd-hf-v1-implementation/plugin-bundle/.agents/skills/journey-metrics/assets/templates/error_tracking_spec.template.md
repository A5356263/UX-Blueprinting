# 报错/异常/中断埋点需求文档

> 本模板定义 `error_tracking_spec.md` 的输出结构。
> 核心原则：先按旅程识别所有用户可见的报错、异常和中断情况，不预先排除弹窗或非弹窗；再按照 messageInfo 规范给出推荐 info4。最终 info4 必须以线上/测试环境实际展示组件为准。
> 生成时请基于需求文档中的异常描述、宿主已提供的本地埋点方法文档（若存在）和 `journey-metrics` 合同中的报错分类规范填写。

## 1. 报错埋点范围说明

报错统一使用 `Util.trackData(params, TrackType.messageInfo)` 上报。`messageInfo` 必填字段为 `cust_id`、非空 `info`、`info4`。本文档覆盖旅程中的报错、异常和中断情况，并给出以下推荐 info4 枚举值：

| 展示形式 | info4 枚举 | 说明 | 示例 |
|---|---|---|---|
| FormError | `FormError` | 表单字段下方校验错误提示 | 必填字段为空、格式不合法 |
| Popover | `Popover` | 气泡提示 | 悬浮提示中的错误信息 |
| message | `message` | 页面顶部或中央消息提示 | 操作失败提示 |
| Toast | `Toast` | 短暂 toast 提示 | 轻量提示，自动消失 |
| messageError / messageWarning | `messageError`, `messageWarning` | 带语义状态的消息提示 | 错误消息、警告消息 |
| result / resultError / resultWarning | `result`, `resultError`, `resultWarning` | 空状态页或结果页状态 | 搜索无结果、付款失败、权限不足 |
| AlertError / AlertWarning | `AlertError`, `AlertWarning` | 页面级错误或警告横幅 | 顶部错误横幅、阻断提示 |
| modalConfirm | `modalConfirm` | 确认式弹窗 | 删除确认、二次确认 |
| modalWarning / modalWarn | `modalWarning`, `modalWarn` | 警告式弹窗 | 风险确认、超时警告 |
| modalError | `modalError` | 错误式弹窗 | 阻断错误弹窗 |
| modalInfo | `modalInfo` | 信息/选择/输入式弹窗 | 选择审批渠道、填写意见 |

如线上实际为弹窗、确认框或输入式弹窗，应如实记录实际形态并使用对应 `modal*` 枚举；不要因为体验上“不推荐弹窗”而改写事实。若无法取得用户可见错误文案，跳过 `TrackType.messageInfo`，不要上报空 `info`。

> 报错上报基础信息（企业信息、页面信息、任务上下文）由系统自动携带。

## 2. 报错/异常/中断场景

<!-- 按旅程和页面/模块组织，覆盖需求文档中所有用户可见的报错、异常和中断场景 -->

### 2.1 <页面/模块 A>

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_<MODULE>_<CONDITION>` |
| **触发条件** | <什么情况下触发此错误> |
| **展示形式** | toast / inline / 空状态 / 阻断提示 / 状态标签 |
| **展示位置** | <错误信息出现在页面的哪个区域> |
| **可见文案** | <用户看到的错误提示文字> |
| **用户下一步** | <用户看到错误后应该做什么> |
| **是否需要补救路径** | 是 / 否（如是，说明补救方式） |
| **来源** | `[confirmed]` / `[inferred]` / `[conflict]` |

<!-- 重复以上结构，为每个报错场景生成记录 -->

### 2.2 <页面/模块 B>

<!-- 同上结构 -->

## 3. 报错埋点事件（messageInfo 格式）

<!-- 每个报错场景对应一个 Util.trackData(params, TrackType.messageInfo) 调用 -->

### 3.1 <页面/模块 A> 报错埋点

| 字段 | 值 |
|---|---|
| **错误场景标识** | `ERR_<MODULE>_<CONDITION>` |
| **触发时机** | <错误展示时触发> |
| **所属页面/模块** | <页面/模块名称> |
| **关联错误场景** | `ERR_<MODULE>_<CONDITION>` |
| **来源** | `[confirmed]` / `[inferred]` / `[conflict]` |

**messageInfo 参数：**

| 参数名 | 类型 | 说明 | 取值来源 |
|---|---|---|---|
| trackType | `'messageInfo'` | 固定类型 | 前端定义 |
| cust_id | string | 自定义埋点名称，用于标识功能模块或业务场景 | 前端定义 |
| info | string | 用户可见的错误信息（对应 info4 位置的可见文案） | 前端定义 / 接口返回 |
| info2 | string | 开发分析用额外信息（如单据号） | 接口返回 / 前端状态 |
| info3 | string | 错误码 errorCode 或分类标识 | 接口返回 / 前端定义 |
| info4 | string | 组件呈现形式：FormError / Popover / message / result / AlertError / Toast / message* / result* / Alert* / modal* | 前端定义 |
| info5 | string | 触发来源：`request` 或稳定的前端触发动作，避免泛化 `click` | 前端定义 |
| traceid | string | 接口 traceid（可选） | 接口返回 |

**代码示例：**

```ts
import { Util, TrackType } from '@lw36.01/common';

const visibleErrorMessage = getVisibleErrorMessage(error);

if (visibleErrorMessage && visibleErrorMessage.trim()) {
  Util.trackData({
    cust_id: '<功能模块或业务场景埋点名称>',
    info: visibleErrorMessage.trim(),
    info2: '<单据号/批次号/字段名等额外上下文>',
    info3: '<errorCode 或稳定分类>',
    info4: '<FormError/message/modalConfirm/...>',
    info5: '<request 或稳定触发动作>',
    traceid,
  }, TrackType.messageInfo);
}
```

<!-- 重复以上结构，为每个报错场景生成埋点事件 -->

## 4. 报错形式确认说明

<!-- 列出需求文档中出现的所有报错/提示场景，区分推荐形式与线上/测试环境实际形式 -->

| 报错场景 | 推荐 info4 | 线上/测试环境实际形式 | 是否需调整 | 依据/说明 |
|---|---|---|---|---|
| <场景描述> | <FormError/message/modalConfirm/...> | <待实测 / 实际组件> | 是 / 否 | <说明推荐原因或实际证据> |
