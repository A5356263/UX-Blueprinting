"use strict";

const { validate } = require("./validate-context");

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function completeFixture() {
  return {
    skill: "uxb",
    version: "10.0",
    generated_at: "2026-08-16T10:00:00+08:00",
    project_name: "通用体验策略",
    artifact_md: "spark-output/uxb_output.md",
    result_status: "strategy_ready",
    strategy_basis: {
      source_ref: "ST-001",
      problem_or_goal: "降低新任务理解成本",
      target_users: ["用户"],
      key_tasks: ["完成核心任务"],
      solution_direction: "提供已确认的新能力",
      scope: ["核心任务链"],
      out_of_scope: [],
    },
    key_insights: [{
      id: "KI-001",
      insight: "用户需要在首次使用和后续使用之间获得不同程度的说明。",
      applies_to: ["用户", "首次完成", "后续使用"],
      evidence_refs: ["ST-001", "ST-002"],
    }],
    experience_strategies: [{
      id: "ES-001",
      title: "渐进理解",
      thesis: "建立首次理解到熟练使用的渐进关系。",
      tension: "用户需要理解新方式，长期使用不应持续承受说明负担。",
      applies_to: ["用户", "核心任务"],
      expected_outcome: "用户能理解当前任务并逐步降低学习负担。",
      handoff_outcome: "后续方案支持首次必要解释和后续直接完成。",
      evidence_refs: ["ST-001", "ST-002"],
      confidence: "medium",
    }],
    design_criteria: [{
      id: "DC-001",
      criterion: "首次使用者获得必要解释，熟练用户可以直接继续任务。",
      strategy_refs: ["ES-001"],
      source_refs: ["ST-001", "ST-002"],
    }],
    strategy_boundaries: [{
      id: "SB-001",
      boundary: "页面容器、控件和具体文案由后续交互方案决定。",
      strategy_refs: ["ES-001"],
    }],
    source_trace: [{
      id: "ST-001",
      source_type: "formal_input",
      source_name: "正式解决方案",
      source_path: "spark-output/requirements_baseline.md",
      used_for: ["strategy_basis", "KI-001", "ES-001", "DC-001"],
    }, {
      id: "ST-002",
      source_type: "design_principle",
      source_name: "渐进披露",
      source_path: ".claude/skills/knowledge-wiki/knowledge/design/progressive-disclosure.md",
      used_for: ["KI-001", "ES-001", "DC-001"],
    }],
  };
}

function noStrategyFixture() {
  const data = completeFixture();
  data.result_status = "no_independent_strategy";
  data.key_insights = [];
  data.experience_strategies = [];
  data.design_criteria = [];
  data.strategy_boundaries = [];
  data.source_trace = [data.source_trace[0]];
  data.source_trace[0].used_for = ["strategy_basis"];
  return data;
}

function assertValid(data, name) {
  const errors = validate(data);
  if (errors.length > 0) throw new Error(name + " 应通过：" + errors.join("；"));
}

function assertInvalid(data, name) {
  if (validate(data).length === 0) throw new Error(name + " 应失败");
}

assertValid(completeFixture(), "完整策略结构");
assertValid(completeFixture(), "最小单策略结构");
assertValid(noStrategyFixture(), "无需独立体验策略结构");

const multiSource = completeFixture();
multiSource.source_trace.push({
  id: "ST-003",
  source_type: "stories",
  source_name: "用户故事",
  source_path: "spark-output/stories.md",
  used_for: ["ES-001"],
});
multiSource.source_trace.push({
  id: "ST-004",
  source_type: "journey",
  source_name: "用户旅程",
  source_path: "spark-output/journey_analysis.md",
  used_for: ["ES-001"],
});
multiSource.experience_strategies[0].evidence_refs.push("ST-003", "ST-004");
assertValid(multiSource, "包含 Stories 与 Journey 的结构");

const semanticBoundary = completeFixture();
semanticBoundary.experience_strategies[0].handoff_outcome = "在右侧抽屉使用蓝色主按钮。";
assertValid(semanticBoundary, "脚本不执行语义越界判断");

const wrongVersion = completeFixture();
wrongVersion.version = "9.0";
assertInvalid(wrongVersion, "错误版本");

const missingRoot = completeFixture();
delete missingRoot.strategy_basis;
assertInvalid(missingRoot, "缺少根字段");

const extraRoot = completeFixture();
extraRoot.open_questions = [];
assertInvalid(extraRoot, "未知根字段");

const wrongId = completeFixture();
wrongId.experience_strategies[0].id = "ED-001";
assertInvalid(wrongId, "错误编号");

const duplicateId = completeFixture();
duplicateId.key_insights.push(clone(duplicateId.key_insights[0]));
assertInvalid(duplicateId, "重复编号");

const emptyThesis = completeFixture();
emptyThesis.experience_strategies[0].thesis = "";
assertInvalid(emptyThesis, "策略主张为空");

const wrongAppliesTo = completeFixture();
wrongAppliesTo.experience_strategies[0].applies_to = "用户";
assertInvalid(wrongAppliesTo, "适用范围类型错误");

const wrongConfidence = completeFixture();
wrongConfidence.experience_strategies[0].confidence = "certain";
assertInvalid(wrongConfidence, "置信度非法");

const wrongSourceType = completeFixture();
wrongSourceType.source_trace[0].source_type = "unknown";
assertInvalid(wrongSourceType, "来源类型非法");

const missingSource = completeFixture();
missingSource.experience_strategies[0].evidence_refs = ["ST-999"];
assertInvalid(missingSource, "来源编号不存在");

const wrongTime = completeFixture();
wrongTime.generated_at = "2026/08/16";
assertInvalid(wrongTime, "时间格式错误");

const statusConflict = completeFixture();
statusConflict.result_status = "no_independent_strategy";
assertInvalid(statusConflict, "结果状态与策略数组不一致");

const missingStrategy = completeFixture();
missingStrategy.design_criteria[0].strategy_refs = ["ES-999"];
assertInvalid(missingStrategy, "策略引用不存在");

const invalidUsedFor = completeFixture();
invalidUsedFor.source_trace[0].used_for = ["ES-999"];
assertInvalid(invalidUsedFor, "来源用途引用不存在");

console.log("UXB Context 10.0 结构测试通过：5 个正向用例，14 个反向用例。");
