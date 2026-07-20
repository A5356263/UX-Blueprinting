"use strict";

const { validate } = require("./validate-context");

function fixture() {
  return {
    skill: "stories",
    version: "3.0",
    generated_at: "2026-07-20",
    project_name: "测试项目",
    artifact_md: "spark-output/stories.md",
    source_refs: ["spark-output/context/uxb.json"],
    source_mode: "uxb",
    direction_summary: "围绕权限申请建立完整任务链",
    stories: [
      {
        title: "发起权限申请",
        granularity: "story",
        persona: "申请人",
        scenario: "缺少完成工作所需权限",
        goal: "提交权限申请并进入审批",
        priority: "P0",
        source_basis: ["UXB 功能与规则"],
        user_story: "作为申请人，我想提交权限申请，从而获得工作所需权限。",
        acceptance_criteria: ["只能选择允许范围内的权限", "提交后进入审批"],
        design_touchpoints: {
          pages_or_scenarios: ["权限申请场景"],
          component_types: ["申请表单"],
          states: ["提交中", "审批中"],
          interaction_patterns: ["选择并提交"],
        },
        risks_or_validation: ["审批人范围尚待确认"],
        critical_assumptions: [],
      },
    ],
    out_of_scope: ["移动端申请"],
    open_questions: ["是否支持撤回申请"],
  };
}

const negativeCases = [
  ["缺根字段", (data) => delete data.stories],
  ["多余根字段", (data) => { data.story_titles = []; }],
  ["版本错误", (data) => { data.version = "2.0"; }],
  ["产物路径错误", (data) => { data.artifact_md = "wrong.md"; }],
  ["stories 为空", (data) => { data.stories = []; }],
  ["stories 类型错误", (data) => { data.stories = "bad"; }],
  ["Story 缺字段", (data) => { delete data.stories[0].goal; }],
  ["Story 多余字段", (data) => { data.stories[0].id = "S-1"; }],
  ["Story 字符串类型错误", (data) => { data.stories[0].priority = []; }],
  ["完成标准包含对象", (data) => { data.stories[0].acceptance_criteria = [{ text: "提交" }]; }],
  ["触点对象缺字段", (data) => { delete data.stories[0].design_touchpoints.states; }],
  ["触点对象多余字段", (data) => { data.stories[0].design_touchpoints.copy = []; }],
  ["触点数组类型错误", (data) => { data.stories[0].design_touchpoints.component_types = "bad"; }],
  ["待确认问题包含空字符串", (data) => { data.open_questions = [""]; }],
  ["方向为空字符串", (data) => { data.direction_summary = ""; }],
  ["旧 story_index 字段", (data) => { data.story_index = []; }],
];

const positiveErrors = validate(fixture());
if (positiveErrors.length) throw new Error(`正向 fixture 失败：${positiveErrors.join("；")}`);

const optionalArraysEmpty = fixture();
optionalArraysEmpty.source_refs = [];
optionalArraysEmpty.out_of_scope = [];
optionalArraysEmpty.open_questions = [];
optionalArraysEmpty.stories[0].source_basis = [];
optionalArraysEmpty.stories[0].acceptance_criteria = [];
optionalArraysEmpty.stories[0].risks_or_validation = [];
optionalArraysEmpty.stories[0].critical_assumptions = [];
for (const field of [
  "pages_or_scenarios", "component_types", "states", "interaction_patterns",
]) {
  optionalArraysEmpty.stories[0].design_touchpoints[field] = [];
}
const emptyErrors = validate(optionalArraysEmpty);
if (emptyErrors.length) throw new Error(`合法空数组 fixture 失败：${emptyErrors.join("；")}`);

for (const [name, mutate] of negativeCases) {
  const data = fixture();
  mutate(data);
  if (validate(data).length === 0) throw new Error(`反向 fixture 未失败：${name}`);
}

console.log(`stories context tests passed: 2 positive, ${negativeCases.length} negative`);
