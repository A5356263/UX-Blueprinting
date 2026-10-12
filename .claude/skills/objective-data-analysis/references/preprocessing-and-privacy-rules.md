# 预处理与隐私规则

## 读取与血缘

- 只读取请求中明确列出的数据源和工作表。
- 为每个文件记录可移植路径引用、格式、行数、字段、大小和内容指纹；工作区内使用相对路径，工作区外使用请求中已有的 source_id，不写本机绝对路径。
- 默认不写出原始或标准化行级副本。
- XLSX 使用只读模式；非关键 XLSX 缺少 openpyxl 时记录来源失败并继续其他格式，唯一或关键来源失败时阻断整次运行。

## 字段与任务实例

每个来源优先使用自己的 `field_mapping` 与 `field_fallbacks`；缺失时仅按该来源表头的高置信字段别名候选匹配。关键映射包括 user_id、task_instance_id、event_time、event_name、journey_step、error_message、error_code 和 error_presentation。不得把一个来源的列名套到另一个来源。

数据粒度优先读取来源声明。只有存在完成标记、一次完成标记、任务报错汇总或旅程路径等任务汇总字段时，才可推断为一行一任务；仅有耗时字段不能把事件明细识别为任务汇总。

来源能力按字段组合识别为 `aggregate_metric_summary`、`task_summary`、`journey_node_detail`、`error_context_detail`、`business_blueprint` 或 `general_event_log`。文件名只用于来源引用，不参与语义判断。报错上下文即使含最近节点，也不具备完整旅程分析资格。

缺少 task_instance_id 时：

1. 以 session_id 为首选边界，user_id 为后备；
2. 按 event_time 排序；事件时间只接受 ISO-8601、10 位 epoch 秒或 13 位 epoch 毫秒，其他数值不猜测单位；
3. 上一终态后的新事件、明确重启事件或超过已确认超时阈值时开启新任务；活跃任务中的重复进入事件不拆单；
4. success/exit/draft 结束当前任务；
5. 写入稳定派生 ID 和 derivation 标记。

无法可靠形成任务边界时，不计算任务级比例。能够形成任务边界但没有完成标记、已确认成功事件或正式允许终态时，不计算完成数和完成率；明确完成规则存在且所有任务均未完成时才允许输出 0%。

## 排除、去重与事件分类

- 先应用明确排除规则，再去重。
- 默认只在同一来源内按用户、任务、会话、时间、事件、步骤、错误码和错误文本去重；跨源去重必须明确声明来源关系和稳定事件键。
- 明确 event_class 优先；其次使用来源级 `event_classification_rules` 或已确认的 event_mapping。存在错误文本/错误码本身不能把一行识别为 error_event。
- 未命中但具有事件或步骤的记录归为 step_event；空噪声归为 noise_event。

当前薪福通前端日志口径中，只有 `xft_type=messageInfo` 进入报错分析；`xft_info` 是报错信息，`xft_info3` 是可选错误码，`xft_info4` 是展示形式。错误签名由安全化报错信息、错误码和展示形式共同形成，不使用 `xft_eventID`，因此不同操作触发的同一错误模式可以聚合。

## 报错脱敏

在形成错误签名和标签前脱敏：

- 密码、Secret、Token、Authorization、Cookie、API Key；
- 邮箱、手机号、证件号、支付卡号；
- IP、UUID、个人用户/任务/会话/追踪/订单/员工/账户 ID；
- 带查询参数 URL、Unix/Windows 文件路径和长数字。

企业编号和企业名称可在授权范围内用于关联与分群，不按个人敏感字段自动删除。正式结果只输出 canonical_safe_label 和稳定签名。脱敏状态为 safe 时可保留剩余可读报错语义；uncertain/blocked 只输出通用安全标签。任何状态都不得输出原始个人或凭证敏感参数。

## 质量门禁

data_quality 至少包含输入/分析行数、来源失败、排除、去重、派生任务、任务边界可靠性、无效时间戳、缺失/歧义映射、事件类别数量、最终字段映射和 row_level_persisted=false。
