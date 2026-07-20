"use strict";

const { validate } = require("./validate-context");

function fixture() {
  return {
    skill: "problem-framing",
    version: "2.0",
    generated_at: "2026-07-20",
    project_name: "测试项目",
    artifact_md: "spark-output/problem_framing.md",
    source_refs: ["input/test.md"],
    decision_summary: "当前应先解决申请入口缺失",
    problem_statement: "用户无法在权限不足时进入正式申请流程",
    primary_roles: ["申请人"],
    recommended_direction: "建立可追踪的自助申请入口",
    handoff_requirements: ["保留待确认审批范围"],
    hard_constraints: ["不得绕过现有权限模型"],
    out_of_scope: ["本轮不重构审批引擎"],
    confirmed_facts: ["当前入口不可用"],
    working_assumptions: ["沿用现有审批人范围"],
    open_questions: ["审批范围是否允许跨组织"],
  };
}

const negativeCases = [
  ["缺根字段", (data) => delete data.problem_statement],
  ["多余字段", (data) => { data.extra = true; }],
  ["错误类型", (data) => { data.primary_roles = "bad"; }],
  ["版本错误", (data) => { data.version = "1.0"; }],
  ["产物路径错误", (data) => { data.artifact_md = "wrong.md"; }],
  ["旧 key_judgments 字段", (data) => { data.key_judgments = []; }],
  ["旧 candidate_directions 字段", (data) => { data.candidate_directions = []; }],
  ["数组包含对象", (data) => { data.confirmed_facts = [{ fact: "入口缺失" }]; }],
  ["数组包含空字符串", (data) => { data.open_questions = [""]; }],
  ["问题为空字符串", (data) => { data.problem_statement = ""; }],
];

const positiveErrors = validate(fixture());
if (positiveErrors.length) throw new Error(`正向 fixture 失败：${positiveErrors.join("；")}`);

const emptyArrays = fixture();
for (const field of [
  "source_refs", "primary_roles", "handoff_requirements", "hard_constraints",
  "out_of_scope", "confirmed_facts", "working_assumptions", "open_questions",
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

console.log(`problem-framing context tests passed: 2 positive, ${negativeCases.length} negative`);
