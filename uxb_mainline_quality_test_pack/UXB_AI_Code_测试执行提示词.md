# UXB 主链路测试执行指令

你现在只负责执行 UXB 主链路测试，并记录测试结果。

## 一、核心目标

本次任务只做测试，不做项目逻辑修改。

测试目标是验证：

1. AI 是否根据需求真实判断知识选择，而不是按固定习惯套知识。
2. AI 是否真正消费知识，并把知识用于 business / experience 推理。
3. business 是否有真实业务判断，而不是复述需求。
4. experience 是否承接 business 中的角色、规则、状态、异常和文案要求。
5. 各阶段链路耗时是否可接受。

## 二、严禁修改的内容

禁止修改以下目录和文件：

```text
packages/
specs/
templates/
knowledge/
gate / validate / coverage 相关逻辑
```

也禁止修改：

```text
正式主链路代码
正式契约
正式模板
正式知识库
正式校验规则
```

如果测试中发现问题，只能记录问题，不要修复代码。

## 三、允许生成的内容

允许创建测试项目和测试报告：

```text
projects/<test-project-id>/
evaluation/uxb_mainline_quality/results/
```

允许写入：

```text
runtime/uxb_route_decision.json
runtime/context_manifest.json
workspace/facts.md
workspace/business_blueprint.md
workspace/experience_blueprint.md
workspace/gap_list.md
workspace/check_report.md
evaluation_report.md
timing_log.md
summary_report.md
```

## 四、执行方式

请读取：

```text
uxb_mainline_quality_test_pack/
```

读取顺序：

```text
README.md
run_ai_code.md
cases/对应测试用例.md
inputs/对应需求文档.md
templates/report_template.md
templates/timing_log_template.md
```

每个测试用例都必须走正式主链路，不允许只做静态分析。

## 五、每个用例必须记录

每个用例完成后，输出：

```text
evaluation/uxb_mainline_quality/results/<case-id>/evaluation_report.md
evaluation/uxb_mainline_quality/results/<case-id>/timing_log.md
```

报告必须包含：

1. route_decision 是否合理。
2. 知识选择是否足够、精准、冗余。
3. 是否存在固定习惯输出。
4. 知识是否真正进入 business 推理。
5. experience 是否承接 business。
6. 是否存在脑补、漏项、弱承接。
7. 各阶段耗时。
8. 失败阶段和失败原因。
9. 是否建议后续继续观察或优化，但不要直接修改代码。

## 六、耗时记录要求

每个阶段都要记录：

```text
开始时间
结束时间
耗时
exit code
是否失败
失败摘要
```

阶段包括：

```text
route_decision
assemble
generate-facts
gate-facts
generate-business / generate-business-lite / generate-business-note
gate-business / gate-business-lite / gate-business-note
generate-experience
gate-experience
validate / validate-lite
coverage / coverage-lite
archive，如执行
旁路评估报告生成
```

## 七、测试结束后

全部用例完成后，输出：

```text
evaluation/uxb_mainline_quality/results/summary_report.md
```

汇总报告需要说明：

1. 哪些用例通过、部分通过、不通过。
2. 是否存在共性的知识选择问题。
3. 是否存在“看似消费知识但实际按习惯输出”的问题。
4. 是否存在 business 到 experience 承接断点。
5. 哪个阶段耗时最高。
6. 当前是否需要修改主链路。

## 八、重要约束

如果发现问题，只记录，不修改。

如果你认为必须修改以下内容才能继续：

```text
packages/
specs/
templates/
knowledge/
gate / validate / coverage
```

请立即停止，并在报告中写明：

```text
测试无法继续
阻断原因
建议后续由 Codex / 强模型单独分析
```

本次任务的最终目标是：

```text
生成真实测试结果 + 问题原因 + 耗时记录
```

不是修复项目。
