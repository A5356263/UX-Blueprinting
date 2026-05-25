# UXB 主链路推理质量自动测试说明

## 1. 测试目标

本测试不是验证命令是否能跑通，也不是新增正式校验规则。

本测试用于验证 UXB 主链路真实运行时，AI 是否能做到：

1. 根据需求真实判断知识选择，而不是按固定习惯选择知识。
2. 判断所选知识是否足够、精准，是否存在明显漏选或冗余。
3. 真正消费知识，并把知识转化为业务判断、体验承接和待确认问题。
4. 避免“看似消费知识，但产物仍主要依赖常规经验或模板套路”。
5. 在 business 中区分需求事实、知识依据、AI 推导。
6. 在 experience 中承接 business 的角色、规则、状态、异常、风险和文案要求。
7. 记录不同需求类型下的全链路耗时，用于后续评估效率。

## 2. 测试边界

### 2.1 允许做的事

- 为每个测试用例创建临时 `projects/<test-project-id>/`。
- 走正式 UXB 主链路。
- 生成 `source/`、`runtime/`、`workspace/`、`exports/` 等正式链路产物。
- 在 `evaluation/uxb_mainline_quality/results/` 下输出旁路评估报告。
- 记录耗时、失败原因、返工次数、问题原因。

### 2.2 不允许做的事

- 不修改 `packages/` 主链路代码。
- 不修改 `specs/` 正式契约。
- 不修改 `templates/` 模板。
- 不修改 `knowledge/` 正式知识库。
- 不新增或修改正式 gate / validate / coverage 规则。
- 不为了让测试通过而反向修改需求文档。
- 不把旁路评估结论写入正式知识库。

## 3. 测试方式

每个用例分两条链路执行。

### 3.1 正式生成链路

必须真实运行主链路：

```text
准备测试 project
→ 生成或补齐 runtime/uxb_route_decision.json
→ route-decision
→ assemble
→ facts
→ gate-facts
→ business / business-lite / business-note
→ gate-business / gate-business-lite / gate-business-note
→ experience
→ gate-experience
→ validate / validate-lite
→ coverage / coverage-lite
→ 可选 archive
```

### 3.2 旁路评估链路

正式产物生成后，再由 AI 作为评测者读取产物并输出评估报告：

```text
读取 route_decision
→ 读取 context_manifest
→ 读取 facts
→ 读取 business
→ 读取 experience
→ 读取 gap_list / check_report / gates
→ 判断知识选择质量
→ 判断真实推理质量
→ 判断 business 到 experience 的承接质量
→ 判断是否存在固定习惯输出
→ 记录耗时与问题原因
```

旁路评估报告只用于质量观察，不参与正式主链路阻断。

## 4. 测试样本

| 用例 ID | 需求文档 | 样本定位 | 核心测试点 |
|---|---|---|---|
| uxb-qc-001-employee-self-service-permission | 低完整度需求文档_员工自助申请权限.md | 复杂业务能力 / 低完整度 | 知识选择、真实业务推理、不确定项处理、审批与权限关系 |
| uxb-qc-002-permission-query | 低完善读权限查询.md | 策略类 / 低完整度 | 是否做查询视角推导，是否避免直接套 UI |
| uxb-qc-003-permission-search-in-page | 功能权限设置支持筛选已勾选权限_需求文档.md | 局部体验优化 | 是否不过度消费权限业务知识，是否识别“查找不是筛选” |
| uxb-qc-004-sub-admin-copy | 子管理员支持复制_需求文档.md | 中高完整度规则需求 | 规则承接、校验顺序、叠加不覆盖、互审和审计处理 |

## 5. 总体评估维度

### 5.1 需求理解是否准确

- 是否识别需求类型。
- 是否识别业务改动深度。
- 是否识别体验压力。
- 是否把低完整度需求误判为完整需求。
- 是否把局部体验优化误判为复杂业务重构。

### 5.2 知识选择是否真实

- 是否按当前需求选择知识，而不是按“权限类需求”固定选择一批知识。
- 是否选中了必须的 raw 或设计准则。
- 是否缺少明显应该读取的知识。
- 是否选择了明显无关或过宽的知识。
- `selection_reasons` 是否说明“为什么读、支撑什么判断、影响什么输出”。

### 5.3 知识是否进入推理

有效推理应体现：

```text
需求事实 + 知识依据 → 新的业务判断 / 体验承接要求
```

有效示例：

```text
由于自助申请会成为权限来源的一种，因此不能只设计员工申请入口，
还需要定义它与现有来源模型、审批状态、生效记录之间的关系。
```

低价值示例：

```text
需要注意权限安全，避免风险。
```

后者属于常规话术，不能证明知识被真实消费。

### 5.4 是否存在固定习惯输出

- 是否所有权限需求都走同一种知识选择。
- 是否所有 business 都写成固定结构但没有真实判断。
- 是否所有 experience 都输出“列表 + 筛选 + 弹窗 + 表单”的套路。
- 是否没有根据需求复杂度调整输出深度。
- 是否把“页面内查找”误写成“筛选权限项”。

### 5.5 business 到 experience 是否承接

- business 中的角色、对象、规则、状态、风险是否进入 experience。
- experience 是否写清主流程、次流程、异常流程。
- experience 是否给出用户可见反馈和文案。
- gap_list 中的待确认问题是否没有被 experience 偷偷脑补。
- 高风险操作是否有二次确认、阻断或反馈。

### 5.6 耗时是否可接受

每个用例必须记录：

- route_decision 耗时
- 输入准备耗时
- assemble 耗时
- facts 生成耗时
- facts gate 耗时
- business 生成耗时
- business gate 耗时
- experience 生成耗时
- experience gate 耗时
- validate 耗时
- coverage 耗时
- archive 耗时，如执行
- 总耗时
- 返工次数
- 失败重跑次数

## 6. 输出要求

每个用例输出：

```text
evaluation/uxb_mainline_quality/results/<case-id>/evaluation_report.md
evaluation/uxb_mainline_quality/results/<case-id>/timing_log.md
```

全部用例完成后输出：

```text
evaluation/uxb_mainline_quality/results/summary_report.md
```

## 7. 结论使用方式

测试完成后，不直接修改主链路。

只有当多个用例稳定出现同类问题时，再判断是否需要：

1. 调整 UXB 判断单写法。
2. 调整测试提示。
3. 优化知识 summary 或 raw。
4. 最后才考虑进入 gate / validate / coverage。
