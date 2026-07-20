"use strict";

const { validateRoot } = require("./validate_context");

function fixture() {
  return {
    skill: "journey-analysis",
    version: "2.0",
    generated_at: "2026-07-20",
    project_name: "测试项目",
    artifact_md: "spark-output/journey_analysis.md",
    source_refs: ["input/test.md"],
    mode: "uxb-chain",
    result_level: "完整旅程",
    journey_summary: "申请人完成权限申请与结果确认",
    primary_roles: ["申请人"],
    stage_names: ["发现问题", "提交申请", "等待结果"],
    lowest_confidence_stages: ["等待结果"],
    key_transition_summaries: ["提交后进入审批等待"],
    critical_gaps: ["审批时限未确认"],
    open_questions: ["审批超时后如何处理"],
  };
}

const negativeCases = [
  ["缺根字段", (data) => delete data.stage_names],
  ["多余字段", (data) => { data.extra = true; }],
  ["错误类型", (data) => { data.primary_roles = "bad"; }],
  ["版本错误", (data) => { data.version = "1.0"; }],
  ["产物路径错误", (data) => { data.artifact_md = "wrong.md"; }],
  ["非法模式", (data) => { data.mode = "bad"; }],
  ["旧 stages 字段", (data) => { data.stages = []; }],
  ["旧 readiness 字段", (data) => { data.readiness = {}; }],
  ["数组包含对象", (data) => { data.stage_names = [{ name: "提交申请" }]; }],
  ["数组包含空字符串", (data) => { data.critical_gaps = [""]; }],
  ["摘要为空字符串", (data) => { data.journey_summary = ""; }],
];

const positiveErrors = validateRoot(fixture());
if (positiveErrors.length) throw new Error(`正向 fixture 失败：${positiveErrors.join("；")}`);

const emptyArrays = fixture();
for (const field of [
  "source_refs", "primary_roles", "stage_names", "lowest_confidence_stages",
  "key_transition_summaries", "critical_gaps", "open_questions",
]) {
  emptyArrays[field] = [];
}
const emptyErrors = validateRoot(emptyArrays);
if (emptyErrors.length) throw new Error(`合法空数组 fixture 失败：${emptyErrors.join("；")}`);

for (const [name, mutate] of negativeCases) {
  const data = fixture();
  mutate(data);
  if (validateRoot(data).length === 0) throw new Error(`反向 fixture 未失败：${name}`);
}

console.log(`journey-analysis context tests passed: 2 positive, ${negativeCases.length} negative`);
