"use strict";

const { validate } = require("./validate-context");

function fixture() {
  return {
    skill: "stories",
    version: "2.0",
    generated_at: "2026-07-20",
    project_name: "测试项目",
    artifact_md: "spark-output/stories.md",
    source_refs: ["spark-output/uxb_output.md"],
    source_mode: "uxb",
    direction_summary: "围绕权限申请建立完整任务链",
    primary_roles: ["申请人"],
    story_titles: ["发起权限申请", "查看申请结果"],
    p0_story_titles: ["发起权限申请"],
    critical_assumptions: ["审批人范围已确定"],
    out_of_scope: ["移动端申请"],
    open_questions: ["是否支持撤回申请"],
  };
}

const negativeCases = [
  ["缺根字段", (data) => delete data.story_titles],
  ["多余字段", (data) => { data.extra = true; }],
  ["错误类型", (data) => { data.primary_roles = "bad"; }],
  ["版本错误", (data) => { data.version = "1.0"; }],
  ["产物路径错误", (data) => { data.artifact_md = "wrong.md"; }],
  ["旧 stories 字段", (data) => { data.stories = []; }],
  ["旧 story_index 字段", (data) => { data.story_index = []; }],
  ["数组包含对象", (data) => { data.story_titles = [{ title: "申请" }]; }],
  ["数组包含空字符串", (data) => { data.open_questions = [""]; }],
  ["方向为空字符串", (data) => { data.direction_summary = ""; }],
];

const positiveErrors = validate(fixture());
if (positiveErrors.length) throw new Error(`正向 fixture 失败：${positiveErrors.join("；")}`);

const emptyArrays = fixture();
for (const field of [
  "source_refs", "primary_roles", "story_titles", "p0_story_titles",
  "critical_assumptions", "out_of_scope", "open_questions",
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

console.log(`stories context tests passed: 2 positive, ${negativeCases.length} negative`);
