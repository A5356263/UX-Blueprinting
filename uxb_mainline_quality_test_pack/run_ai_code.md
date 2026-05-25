# AI Code 自动测试执行手册

## 1. 执行角色

你是 UXB 主链路质量测试执行者。

你的任务不是写一个理想答案，而是让每个测试样本真实走 UXB 正式主链路，然后评估主链路产物质量。

## 2. 执行总原则

1. 必须走正式主链路，不允许只做静态分析。
2. 不修改 `packages/`、`specs/`、`templates/`、`knowledge/`。
3. 不修改正式 gate / validate / coverage 规则。
4. 不把测试评估报告写入正式产物目录替代正式产物。
5. 正式产物与旁路评估报告分开。
6. 如果正式链路失败，记录失败阶段、报错、可能原因，不要私自改主链路代码修复。
7. 如果必须修改主链路才能继续，停止测试并在报告中说明。

## 3. 推荐目录

测试说明和报告可放在：

```text
evaluation/uxb_mainline_quality/
  cases/
  results/
```

正式链路产物仍放在：

```text
projects/<test-project-id>/
```

推荐 project id：

```text
uxb-qc-001-employee-self-service-permission
uxb-qc-002-permission-query
uxb-qc-003-permission-search-in-page
uxb-qc-004-sub-admin-copy
```

## 4. 每个用例的执行步骤

### Step 1：准备输入

1. 创建或确认 `projects/<project-id>/`。
2. 将对应需求文档写入 `projects/<project-id>/source/requirement.md`。
3. 如没有额外背景，创建 `projects/<project-id>/source/background.md`，写入：

```text
本测试仅使用 requirement.md 中的信息，不额外补充背景。
```

4. 创建或检查 `projects/<project-id>/source/task_card.md`。

### Step 2：生成 UXB 判断单

正式执行前必须生成：

```text
projects/<project-id>/runtime/uxb_route_decision.json
```

判断单必须包含：

- `judgment.demand_type`
- `judgment.business_depth`
- `judgment.experience_output`
- `judgment.reason`
- `complexity_judgment.business_change`
- `complexity_judgment.experience_pressure`
- `complexity_judgment.uncertainties`
- `knowledge_selection.business_refs`
- `knowledge_selection.guideline_refs`
- `knowledge_selection.complexity_refs`
- `knowledge_selection.selection_reasons`
- `execution.required_outputs`

重点要求：

1. 不要因为出现“权限”就固定选择同一批权限知识。
2. 先判断需求到底改变了什么，再选知识。
3. `selection_reasons` 必须说明为什么读、支撑哪个判断、影响哪个正式输出。
4. 对低完整度需求，必须区分阻断型不确定项和非阻断型不确定项。

### Step 3：记录 route decision 耗时

Windows PowerShell 示例：

```powershell
$start = Get-Date
python -m packages route-decision <project-id>
$end = Get-Date
$elapsed = $end - $start
```

将耗时写入：

```text
evaluation/uxb_mainline_quality/results/<case-id>/timing_log.md
```

### Step 4：执行正式链路

优先逐步执行，方便记录各阶段耗时：

```bash
python -m packages route-decision <project-id>
python -m packages assemble <project-id>
python -m packages generate-facts <project-id>
python -m packages gate-facts <project-id>
python -m packages generate-business <project-id>
python -m packages gate-business <project-id>
python -m packages generate-experience <project-id>
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
```

如果 `uxb_route_decision.json` 中选择 lite / note 输出，则使用对应命令：

```bash
python -m packages generate-business-lite <project-id>
python -m packages gate-business-lite <project-id>
python -m packages validate-lite <project-id>
python -m packages coverage-lite <project-id>
```

或：

```bash
python -m packages generate-business-note <project-id>
python -m packages gate-business-note <project-id>
```

每个命令都必须记录：

- 开始时间
- 结束时间
- 耗时
- exit code
- 是否失败
- 失败摘要

### Step 5：读取正式产物

正式链路完成后，读取：

```text
projects/<project-id>/runtime/uxb_route_decision.json
projects/<project-id>/runtime/context_manifest.json
projects/<project-id>/workspace/facts.md
projects/<project-id>/workspace/business_blueprint.md
projects/<project-id>/workspace/business_blueprint_lite.md，如存在
projects/<project-id>/workspace/business_note.md，如存在
projects/<project-id>/workspace/experience_blueprint.md
projects/<project-id>/workspace/gap_list.md
projects/<project-id>/workspace/check_report.md
projects/<project-id>/runtime/gates/*.md，如存在
```

### Step 6：输出旁路评估报告

按 `templates/report_template.md` 输出：

```text
evaluation/uxb_mainline_quality/results/<case-id>/evaluation_report.md
```

评估报告必须回答：

1. 知识选择是否合理。
2. 是否存在固定习惯选择知识。
3. 知识是否真正进入 business 推理。
4. business 是否形成明确判断，而不是复述需求。
5. experience 是否承接 business。
6. 是否出现脑补、漏项或弱承接。
7. 当前问题更像需求信息不足、知识选择不准、知识消费不足、AI 推理不足、business 承接不清、experience 转译不足、上下文过重还是主链路机制问题。
8. 是否建议继续观察，还是建议后续优化机制。

### Step 7：输出汇总报告

全部用例完成后，按 `templates/summary_template.md` 输出：

```text
evaluation/uxb_mainline_quality/results/summary_report.md
```

## 5. 质量判断标准

### 5.1 通过

- route_decision 与需求类型匹配。
- 知识选择精准，无明显关键漏选。
- business 中出现基于知识的推导。
- experience 承接了 business 的关键规则、状态、异常和文案。
- 没有明显套固定模板。
- GAP 没有被偷偷脑补。
- 耗时可解释。

### 5.2 部分通过

- 知识选择大体正确，但有轻微漏选或冗余。
- business 有推理，但部分判断偏常规。
- experience 承接主流程，但异常或状态不足。
- 耗时偏长但原因可解释。
- 有轻微模板化表达，但不影响主体判断。

### 5.3 不通过

- route_decision 需求类型明显误判。
- 知识选择明显套固定习惯。
- 关键知识没有进入推理。
- business 基本是需求复述。
- experience 与 business 脱节。
- 重要 GAP 被脑补成确定方案。
- 因上下文过重或产物结构混乱导致质量明显下降。
