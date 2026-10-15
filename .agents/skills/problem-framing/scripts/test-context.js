"use strict";

const { validate } = require("./validate-context");

function fixture(mode = "problem-definition") {
  return {
    skill: "problem-framing",
    version: "3.0",
    generated_at: "2026-08-16",
    project_name: "测试项目",
    artifact_md: "spark-output/problem_framing.md",
    source_refs: ["input/problem-summary.md"],
    mode,
    decision_summary: "应先建立统一的业务处理机制",
    problem_statement: "目标角色无法在当前业务过程中完成处理",
    primary_roles: ["目标角色"],
    solution_goal: "让目标角色能够完成处理并获得明确结果",
    success_signals: ["目标角色可以完成处理"],
    recommended_solution: "建立责任明确的统一处理机制",
    recommendation_basis: ["现有过程存在责任断点"],
    business_solution_points: ["新增统一处理能力"],
    handoff_requirements: ["后续按主推荐方案展开角色任务"],
    hard_constraints: ["沿用已确认的业务对象边界"],
    out_of_scope: ["本轮不重构相邻业务域"],
    confirmed_facts: ["当前处理责任不清"],
    working_assumptions: ["现有角色关系可以继续复用"],
    open_questions: ["跨组织范围是否纳入本期"],
  };
}

const negativeCases = [
  ["缺根字段", (data) => delete data.problem_statement],
  ["多余字段", (data) => { data.extra = true; }],
  ["错误类型", (data) => { data.primary_roles = "bad"; }],
  ["错误版本", (data) => { data.version = "2.0"; }],
  ["错误产物路径", (data) => { data.artifact_md = "wrong.md"; }],
  ["错误模式", (data) => { data.mode = "unsupported"; }],
  ["缺成效字段", (data) => delete data.success_signals],
  ["成效字段错误类型", (data) => { data.success_signals = "bad"; }],
  ["数组包含对象", (data) => { data.confirmed_facts = [{ fact: "责任不清" }]; }],
  ["数组包含空字符串", (data) => { data.open_questions = [""]; }],
  ["主推荐方案为空", (data) => { data.recommended_solution = ""; }],
];

for (const mode of ["problem-definition", "direction-correction", "unknown"]) {
  const errors = validate(fixture(mode));
  if (errors.length) throw new Error(`正向 fixture 失败：${mode}：${errors.join("；")}`);
}

const emptyArrays = fixture();
for (const field of [
  "source_refs", "primary_roles", "success_signals", "recommendation_basis",
  "business_solution_points", "handoff_requirements", "hard_constraints", "out_of_scope",
  "confirmed_facts", "working_assumptions", "open_questions",
]) {
  emptyArrays[field] = [];
}
const emptyErrors = validate(emptyArrays);
if (emptyErrors.length) throw new Error(`合法空数组 fixture 失败：${emptyErrors.join("；")}`);

for (const [name, mutate] of negativeCases) {
  const data = fixture();
  mutate(data);
  if (validate(data).length === 0) throw new Error(`反向 fixture 未失败：${name}`);
}

console.log(`problem-framing context tests passed: 4 positive, ${negativeCases.length} negative`);
