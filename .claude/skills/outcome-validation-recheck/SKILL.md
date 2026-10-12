---
name: outcome-validation-recheck
description: 结果验证与回检技能。基于 Root Cause 正式 Handoff、已批准的 Intervention Contract 和 Evidence Govern 放行的验证证据，按上线前/演示、试点/上线后、长期/回归三个模式判断准备度、效果、归因、护栏、分群、副作用与持续性；形成精准回流、Evidence 变更请求、Root Cause 反馈信号和监测要求。不得自行设计方案、重算上游统计、直接修改 Evidence/Root Cause、创建定时任务、自动回滚或自动重跑完整分析链。
---

# 结果验证与回检

判断“方案是否已经具备验证条件、是否产生预期效果、效果能否归因于本次干预、是否持续且无关键伤害”。本技能不发明方案，也不把一次指标变化直接写成因果结论。

## Step 0 · 运行入口

### 0.1 检查正式输入

启动时读取：

1. `shared-workflow/skill-graph.json`
2. `shared-workflow/data-analysis/artifact-registry.json`
3. `shared-workflow/data-analysis/references/context-handoff-protocol.md`
4. 用户本轮明确指定的正式输入或 Handoff

只接受 `.claude/skills/outcome-validation-recheck/schemas/input.schema.json` 定义的输入。必须有 Root Cause 面向本技能的 Handoff 和正式 Intervention Contract；效果或持续性验证还必须有 Evidence Govern 面向本技能的验证证据 Handoff。

不得扫描 `spark-output/context/`、Archive Store 或历史目录猜测“最新”输入。

### 0.2 已有产物状态

正式 latest：

```text
spark-output/results/outcome/ 与 spark-output/context/current/outcome.json
```

已有产物只表示曾经运行，不得自动沿用、改变本轮模式或跳过门禁。

### 0.3 独立调用沟通

输入齐全时直接执行。只有问题结论但没有确认方案时，用业务语言说明：

> 我可以帮你判断优化是否有效，但需要先确认验证的是哪一版方案、覆盖了哪些用户，以及这些用户是否真正体验到了完整改动。

不要询问 Schema、字段映射、payload 或内部 gate。一次只确认一个会改变范围、规则解释或验证阶段的问题。

## 角色与边界

负责：

- 上线前/演示阶段的验证准备度；
- 试点/上线后的干预效果与归因；
- 核心指标、护栏、关键分群、副作用和问题迁移；
- 长期持续性与已提供回归监测结果的评估；
- 精准 reroute、Evidence Patch 请求和 Root Cause 反馈信号；
- 面向未来 Automation Controller 的监测要求。

不负责：

- 自行设计或补全体验方案；
- 重做 Objective 的统计计算或重新解释原始数据；
- 绕过 Evidence Govern 使用新客观、主观或启发式证据；
- 自行设定业务阈值、告警频率、通知人；
- 持续拉数、创建定时任务、配置线上监控、自动回滚或自动重跑；
- 直接修改 Evidence、Root Cause、Knowledge Wiki 或归档状态。

## 总原则

1. “结果变好”和“由本次方案导致”是两道独立门。
2. `pre_launch` 和 `demo` 不能输出效果结论。
3. 暴露或实施不到位时不能判定方案无效。
4. 关键护栏或关键分群受损时不能输出单纯有效。
5. Root Cause 反馈必须先经 Evidence Govern 吸收。
6. JSON 是唯一结构化事实源；报告不增加新结论。

用户报告使用 `shared-workflow/data-analysis/presentation-vocabulary.json` 的中文状态、解释和下一步；内部 ID 与状态码只保留在 JSON 和追溯明细。
7. 人工审核只阻断受影响范围。

## 运行模式

一次运行只使用一种模式：

| 模式 | 阶段 | 核心问题 |
| --- | --- | --- |
| `readiness_validation` | `pre_launch`、`demo` | 是否已具备进入下一验证阶段的条件 |
| `effectiveness_validation` | `pilot`、`post_launch` | 结果是否改善、能否归因、是否有伤害 |
| `durability_monitoring` | `long_term`、`regression_monitoring` | 效果是否持续、是否衰减或回归 |

不得组合多个模式执行。

## 输入门禁

Root Cause Handoff 必须：

```text
source_skill = root-cause-synthesis
root_artifact_instance_ref = 完整且摘要匹配的 Root Cause 已发布实例
target_skill = outcome-validation-recheck
handoff_status = ready | ready_with_caveats
payload_refs[] are absolute JSON Pointers and all resolve
```

Intervention Contract 必须明确版本、来源、候选根因、预期机制、范围、人群、阶段、暴露、实施到位、指标、护栏和批准状态。

Pilot 以后还必须有：

```text
source_skill = evidence-govern
govern_artifact_instance_ref = 完整且摘要匹配的 Govern 已发布实例
target_skill = outcome-validation-recheck
handoff_status = ready | ready_with_caveats
```

任一 Handoff 含 `required_review_request_ids[]` 时，只接受与该 Artifact、run、Handoff 和全部 payload 精确绑定的已批准 `review_decisions[]`；审核缺失、拒绝或绑定不一致时 fail closed。

门禁状态：

- `blocked`：不形成效果结论；
- `needs_user_input`：只请求关键确认；
- `partial`：输出已完成范围和被阻断范围；
- `ready_with_caveats`：继承全部 caveat；
- `ready`：允许评估，不预设有效。

## Reference 路由

- 每次先读 `references/intervention-contract-and-readiness-rules.md`
- Pilot 以后读 `references/effectiveness-and-attribution-rules.md`
- 护栏、长期、回归或 reroute 时读 `references/guardrail-regression-and-reroute-rules.md`
- 每次输出前读 `references/handoff-reporting-and-risk-rules.md`

业务阈值、频率和通知策略只能沿精确引用最小读取，不扫描 Knowledge Wiki。

## 执行步骤

### Step 1 · 校验输入合同

```bash
python3 .claude/skills/outcome-validation-recheck/scripts/validate_and_write.py validate \
  --input <input.json> \
  --candidate <candidate-output.json>
```

先确认模式、阶段、方案版本、批准状态、Root Cause Handoff 以及验证证据 Handoff。

### Step 2 · 评估验证准备度

分别检查 baseline、观察窗口、暴露、实施到位和测量。缺少任何关键条件时明确 `not_ready` 或 `unknown`，不要用总分掩盖。

### Step 3 · 形成统一验证评估

所有阶段只输出一个 `validation_assessment`。Pre-launch/demo 只判断准备度；Pilot/post-launch 判断效果、归因、护栏和分群；长期/回归还判断持续性。

Outcome 只消费 Objective 的正式统计结论，不重算指标。新主观或启发式证据也必须经 Govern 放行。

### Step 4 · 检查伤害、混杂和问题迁移

关键分群或护栏恶化时结论至少降为 `mixed`；高混杂风险不能输出强因果；实施不到位不能判 `ineffective`。记录副作用和问题是否转移到其他环节。

### Step 5 · 生成反馈与精准回流

- Evidence 强弱变化 → `outcome_evidence_patch_requests[]`，目标只允许 Evidence Govern；
- 根因反馈 → `root_cause_feedback_signals[]`，必须标记先由 Govern 吸收；
- 跨案例观察 → `pattern_observation_signals[]`，不能自行形成模式；
- 输入缺口 → 只 reroute 对应技能，不自动重跑完整链。

### Step 6 · 形成监测要求

长期或回归场景可以生成 `monitoring_requirements[]`。没有正式阈值、频率或通知政策时只写 proposal/blocked；即使政策齐备也只交给未来 Automation Controller，当前 `can_schedule=false`。

### Step 7 · 生成交接

白名单：

```text
evidence-govern
objective-data-analysis
subjective-feedback-analysis
experience-heuristic-analysis
business-impact
data-visualization
evidence-archive
```

不得直接交 Root Cause。人工审核进入 `manual_review_requests[]`。Archive 需要显式授权；Business Impact 只接收 Pilot 以后可评估的效果。

### Step 8 · 校验并写入

生成临时候选 JSON 后执行：

```bash
python3 .claude/skills/outcome-validation-recheck/scripts/validate_and_write.py write \
  --input <input.json> \
  --candidate <candidate-output.json>
```

Input Schema、Output Schema 和语义门禁全部通过后，原子写入按分析目的维护的 Current Pointer；失败不覆盖旧产物。

## 输出

正式 JSON 顶层：

```text
run
analysis_contract
data_quality
limitations
handoff
analysis_summary
analysis_results
manual_review_requests
downstream_handoffs
quality
write_safety
```

只接受 Registry 登记的 `4.0.0` 契约；其他版本没有真实适配器时必须重跑。

`analysis_results.effect_measurements[]` 保存方案前后可复核的效果事实。每项必须绑定指标、粒度、维度、基线窗口和比较窗口；NPS 使用 `survey_response` 粒度，企业状态变化使用 `enterprise` 或 `enterprise_x_business_board` 粒度。不同粒度不得直接合并为一个效果值，预测值不得冒充实测效果。

独立调用可生成：

```text
spark-output/outcome-validation-recheck/[project-slug].md
```

链式调用默认不重复生成 Markdown。需要可视化时交 Data Visualization，不生成 HTML。

## 标准交接

完成后读取 `shared-workflow/next-skill.md`，依据本次 Handoff 给出下一步。写入成功后运行：

```bash
node shared-workflow/generate-progress-preview.js
```

刷新失败只告警，不改变分析结果。

## 内部自检

- 模式和阶段匹配；
- 方案版本、范围、暴露和实施到位可识别；
- Pilot 以后只使用 Govern 放行证据；
- 没有重算 Objective 统计；
- 效果与归因分离；
- 关键分群/护栏伤害没有被总体改善掩盖；
- 根因反馈先回 Govern；
- 没有定时任务、自动回滚、自动全链重跑或自动状态写入；
- Handoff 和人工审核引用可解析；
- JSON 与报告无明细身份信息和敏感参数；
- Schema、语义门禁和原子写入成功。

能修复的问题直接修复；不能修复时降级、局部阻断或提出精确补证。
