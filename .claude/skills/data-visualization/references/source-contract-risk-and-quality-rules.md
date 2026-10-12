# 来源契约、风险与质量规则

## 1. 权威来源

机器可执行来源矩阵位于 `../schemas/source-contracts.json`。本文件解释消费规则，不重复维护版本号和路径。

`registered_upstream` 必须同时满足：

1. `artifact_type`、`artifact_version` 和 `producer_skill` 命中矩阵；
2. Artifact Instance Ref 的 run、项目、版本、producer 与内容摘要全部匹配；
3. `consumed_paths` 是矩阵允许路径的子集；
4. 来源引用是明确文件或 Context 引用，不是目录扫描结果；
5. 上游限制、置信与敏感性信息被继承。
6. `artifact_bundle.source_run_ids` 与本次显式上游实例完全相等，报告配置为 `objective_journey`、`business_problem` 或 `full_diagnostic`。

正式发布还必须校验：

1. 候选包中的 producer、artifact type/version 和 source run 与本次请求的 Artifact Instance 完全一致；
2. `consumed_paths` 除 Handoff 授权元数据外，均包含在本次 `requested_paths`；
3. Objective 完整报告已获准消费 `#/analysis_results`、`#/findings` 和 `#/limitations`；
4. 正式 `output_files[]` 与 `delivery.files[]` 指向同一组不可变 JSON/HTML。
5. 请求携带的 Handoff 与来源 Artifact 内登记的 Data Visualization Handoff 完全一致；不得由消费者临时伪造放行。

## 2. 阻断正式输出

- 单位、分母或时间窗口缺失并会改变含义；
- 来源运行或字段无法追溯；
- 关系方向、节点含义或权重单位存在实质歧义；
- Schema 或来源契约不合规；
- 请求把相关、候选机制、估算或预测表达为确定事实；
- 输出路径越界、覆盖保护失败；
- 敏感内容缺少展示授权且无法安全降级。

阻断项进入 `manual_review_requests[]`，`render_status=blocked`，不得生成正式数值图。

## 3. 允许降级

- 数据完整但样本量不足；
- 置信度较低或有明确 caveat；
- 可选维度缺失；
- 只有 brief，足以形成规格但不足以渲染正式数值结果。

降级项必须出现在图表、文字摘要和 `quality` 中，不能静默隐藏。

## 4. Epistemic status

允许状态：

- `observed`
- `reported`
- `heuristic`
- `candidate`
- `estimated`
- `forecast`
- `validated`
- `unknown`

Data Visualization 原样继承状态。只有生产者正式输出 `validated` 时才可展示为已验证。

## 5. 来源与敏感性

`source_contracts[]` 记录：

- 来源技能、类型、版本、运行与相对路径；
- 允许路径和实际消费路径；
- 敏感性状态；
- 来源门禁结果。

不得把绝对路径、访问令牌或未脱敏定位信息写入 Context 或 HTML。缺少敏感性说明时不自行删改事实，转人工复核。

## 6. 写入安全

- 所有交付文件必须位于显式 `output_root`。
- Context 使用 Registry 的 `immutable_result_with_purpose_pointer` 策略。
- HTML 同名冲突默认版本化，不覆盖。
- 先完成契约与语义校验，再执行原子写入。
- `output_files[]` 记录相对路径、格式、用途、来源运行和写入状态。
- `write_safety` 记录路径检查、覆盖策略、原子写入和敏感信息检查结果。
- 候选构建阶段不写旧 Context 或预生成正式 HTML；必需 HTML 渲染失败时，JSON 和 Current Pointer 都不得发布。
