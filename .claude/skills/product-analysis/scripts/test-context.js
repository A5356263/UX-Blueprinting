"use strict";

const { validate } = require("./validate-context");

function fixture() {
  return {
    skill: "product-analysis",
    version: "2.0",
    generated_at: "2026-07-20",
    project_name: "测试项目",
    artifact_md: "spark-output/product_analysis.md",
    source_refs: ["input/test.md"],
    source_mode: "direct-input",
    decision_summary: "当前方案只处理表象问题",
    failure_summary: "方案没有建立可追踪的申请入口",
    reframed_problem: "用户缺少正式完成权限申请的路径",
    skipped_premises: ["申请入口必须受现有权限模型约束"],
    recommended_direction: "建立受约束的自助申请能力",
    next_step: "返回 UXB 完成需求定案",
    out_of_scope: ["本轮不重构审批引擎"],
    open_questions: ["审批范围如何确定"],
  };
}

const negativeCases = [
  ["缺根字段", (data) => delete data.failure_summary],
  ["多余字段", (data) => { data.extra = true; }],
  ["错误类型", (data) => { data.skipped_premises = "bad"; }],
  ["版本错误", (data) => { data.version = "1.0"; }],
  ["产物路径错误", (data) => { data.artifact_md = "wrong.md"; }],
  ["非法来源模式", (data) => { data.source_mode = "bad"; }],
  ["旧 key_judgments 字段", (data) => { data.key_judgments = []; }],
  ["旧 alternative_directions 字段", (data) => { data.alternative_directions = []; }],
  ["数组包含对象", (data) => { data.skipped_premises = [{ premise: "约束" }]; }],
  ["数组包含空字符串", (data) => { data.open_questions = [""]; }],
  ["失败摘要为空字符串", (data) => { data.failure_summary = ""; }],
];

const positiveErrors = validate(fixture());
if (positiveErrors.length) throw new Error(`正向 fixture 失败：${positiveErrors.join("；")}`);

const emptyArrays = fixture();
for (const field of ["source_refs", "skipped_premises", "out_of_scope", "open_questions"]) {
  emptyArrays[field] = [];
}
const emptyErrors = validate(emptyArrays);
if (emptyErrors.length) throw new Error(`合法空数组 fixture 失败：${emptyErrors.join("；")}`);

for (const [name, mutate] of negativeCases) {
  const data = fixture();
  mutate(data);
  if (validate(data).length === 0) throw new Error(`反向 fixture 未失败：${name}`);
}

console.log(`product-analysis context tests passed: 2 positive, ${negativeCases.length} negative`);
