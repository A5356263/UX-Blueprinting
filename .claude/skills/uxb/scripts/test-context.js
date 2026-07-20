"use strict";

const { validate } = require("./validate-context");

function fixture() {
  return {
    skill: "uxb",
    version: "4.0",
    generated_at: "2026-07-19",
    project_name: "测试项目",
    artifact_md: "spark-output/uxb_output.md",
    source_refs: ["input/test.md"],
    decision_summary: "在现有权限模型内增加受约束的批量复制能力",
    primary_roles: ["管理员"],
    in_scope: ["复制当前可管理范围内的权限"],
    out_of_scope: ["编辑来源账号的权限配置"],
    hard_constraints: ["一次最多选择 200 个目标账号"],
    confirmed_decisions: ["沿用现有权限范围校验"],
    open_questions: ["部分目标失败时是否允许只重试失败项"],
  };
}

const negativeCases = [
  ["缺根字段", (data) => delete data.in_scope],
  ["多余字段", (data) => { data.extra = true; }],
  ["错误类型", (data) => { data.primary_roles = "bad"; }],
  ["版本错误", (data) => { data.version = "3.0"; }],
  ["产物路径错误", (data) => { data.artifact_md = "wrong.md"; }],
  ["旧 summary 字段", (data) => { data.summary = {}; }],
  ["旧 features 字段", (data) => { data.features = []; }],
  ["旧 handoff 字段", (data) => { data.handoff = {}; }],
  ["数组包含对象", (data) => { data.primary_roles = [{ name: "管理员" }]; }],
  ["问题使用对象", (data) => { data.open_questions = [{ question: "待确认" }]; }],
  ["数组包含空字符串", (data) => { data.in_scope = [""]; }],
  ["摘要为空字符串", (data) => { data.decision_summary = ""; }],
];

const positiveErrors = validate(fixture());
if (positiveErrors.length) throw new Error(`正向 fixture 失败：${positiveErrors.join("；")}`);
const emptyArrays = fixture();
for (const field of [
  "source_refs", "primary_roles", "in_scope", "out_of_scope",
  "hard_constraints", "confirmed_decisions", "open_questions",
]) {
  emptyArrays[field] = [];
}
const emptyArrayErrors = validate(emptyArrays);
if (emptyArrayErrors.length) {
  throw new Error(`合法空数组 fixture 失败：${emptyArrayErrors.join("；")}`);
}
for (const [name, mutate] of negativeCases) {
  const data = fixture();
  mutate(data);
  if (validate(data).length === 0) throw new Error(`反向 fixture 未失败：${name}`);
}
console.log(`uxb context tests passed: 2 positive, ${negativeCases.length} negative`);
