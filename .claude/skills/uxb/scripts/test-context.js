"use strict";

const { validate } = require("./validate-context");

function minimalFixture() {
  return {
    skill: "uxb",
    version: "9.0",
    generated_at: "2026-08-04T10:00:00+08:00",
    project_name: "通用任务体验定案",
    artifact_md: "spark-output/uxb_output.md",
    decisions: [{
      id: "ED-001",
      task: "用户继续受阻任务",
      roles: ["用户"],
      decision: "用户受阻时，先理解阻断原因和可继续方向，再进入正式输入已经支持的恢复任务。",
    }],
    cross_cutting_constraints: [],
    upstream_trace: [{
      id: "UT-001",
      source_type: "正式输入",
      source_name: "正式解决方案",
      used_for: ["ED-001"],
    }],
  };
}

function fullFixture() {
  const data = clone(minimalFixture());

  data.decisions[0].business_objects = ["当前任务对象"];
  data.decisions[0].states = ["受阻"];
  data.decisions[0].conditions = ["正式输入已经支持恢复任务"];
  data.decisions[0].additional_constraints = ["只有存在真实承接对象时才保留上下文"];
  data.decisions[0].source_refs = ["UT-001", "UT-002"];

  data.cross_cutting_constraints = [{
    id: "CC-001",
    constraint: "相关任务使用一致的对象和状态含义。",
    applies_to: ["用户继续受阻任务", "处理人接手任务"],
  }];

  data.upstream_trace.push({
    id: "UT-002",
    source_type: "设计准则",
    source_name: "任务恢复准则",
    source_path: ".claude/skills/knowledge-wiki/knowledge/design/task-recovery.md",
    used_for: ["ED-001", "CC-001"],
  });

  return data;
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function assertValid(data, name) {
  const errors = validate(data);
  if (errors.length > 0) {
    throw new Error(name + " 应通过：" + errors.join("；"));
  }
}

function assertInvalid(data, name) {
  if (validate(data).length === 0) {
    throw new Error(name + " 应失败");
  }
}

assertValid(minimalFixture(), "最小合法结构");
assertValid(fullFixture(), "完整可选字段结构");

const noDecisions = minimalFixture();
noDecisions.decisions = [];
noDecisions.upstream_trace[0].used_for = ["本轮正式输入"];
assertValid(noDecisions, "无体验决定结构");

const semanticBoundary = minimalFixture();
semanticBoundary.decisions[0].decision = "页面顶部使用三个固定组件。";
assertValid(semanticBoundary, "脚本不执行语义越界判断");

const wrongVersion = minimalFixture();
wrongVersion.version = "8.0";
assertInvalid(wrongVersion, "错误版本");

const missingRoot = minimalFixture();
delete missingRoot.decisions;
assertInvalid(missingRoot, "缺少根字段");

const extraRoot = minimalFixture();
extraRoot.open_questions = [];
assertInvalid(extraRoot, "未知根字段");

const wrongId = minimalFixture();
wrongId.decisions[0].id = "TE-001";
assertInvalid(wrongId, "错误决定编号");

const duplicateDecisionId = fullFixture();
duplicateDecisionId.decisions.push(clone(duplicateDecisionId.decisions[0]));
assertInvalid(duplicateDecisionId, "重复决定编号");

const emptyRoles = minimalFixture();
emptyRoles.decisions[0].roles = [];
assertInvalid(emptyRoles, "角色数组为空");

const emptyDecision = minimalFixture();
emptyDecision.decisions[0].decision = "";
assertInvalid(emptyDecision, "决定正文为空");

const emptyOptionalArray = fullFixture();
emptyOptionalArray.decisions[0].conditions = [];
assertInvalid(emptyOptionalArray, "可选数组为空");

const duplicateConstraintId = fullFixture();
duplicateConstraintId.cross_cutting_constraints.push(
  clone(duplicateConstraintId.cross_cutting_constraints[0])
);
assertInvalid(duplicateConstraintId, "重复跨任务约束编号");

const missingSourceField = minimalFixture();
delete missingSourceField.upstream_trace[0].source_name;
assertInvalid(missingSourceField, "来源字段缺失");

const wrongGeneratedAt = minimalFixture();
wrongGeneratedAt.generated_at = "2026/08/04";
assertInvalid(wrongGeneratedAt, "错误时间格式");

console.log("UXB Context 9.0 结构测试通过：4 个正向用例，11 个反向用例。");
