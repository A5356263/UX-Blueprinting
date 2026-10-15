"use strict";

const { validate } = require("./validate-context");

function fixture() {
  return {
    skill: "page-spec",
    version: "2.0",
    generated_at: "2026-07-19T00:00:00+08:00",
    project_name: "测试项目",
    artifact_md: "spark-output/page_spec.md",
    source_refs: ["spark-output/experience_blueprint.md"],
    page_summary: {
      product_domain: "权限管理", page_type: "管理页", user_role: "管理员", core_task: "配置权限",
    },
    generation_scope: { generate: ["page-request"], reference_only: [], do_not_generate: [] },
    entities: [{
      entity_id: "page-request", name: "申请页", type: "page", generate_mode: "generate", md_anchor: "§2",
    }],
    entity_relationships: [{
      from_entity_id: "page-request", to_entity_id: "page-request", relation: "提交后刷新",
    }],
    coverage: {
      pages: 1, entities: 1, flows: 1, validation_rules: 1, states: 1,
      exceptions: 1, result_states: 1, copy_items: 1, template_variables: 0,
    },
    open_questions: [],
    edge_consumed: false,
    edge_trace: [],
  };
}
function clone(value) { return JSON.parse(JSON.stringify(value)); }

const negatives = [
  ["缺根字段", (data) => delete data.page_summary],
  ["多余字段", (data) => { data.copy_pool = {}; }],
  ["错误类型", (data) => { data.coverage.pages = "1"; }],
  ["非法枚举", (data) => { data.entities[0].generate_mode = "maybe"; }],
  ["重复 ID", (data) => { data.entities.push(clone(data.entities[0])); }],
  ["引用不存在", (data) => { data.entity_relationships[0].to_entity_id = "missing"; }],
  ["核心数组为空", (data) => { data.entities = []; data.generation_scope.generate = []; }],
  ["版本错误", (data) => { data.version = "1.0"; }],
  ["产物路径错误", (data) => { data.artifact_md = "wrong.md"; }],
];

const positiveErrors = validate(fixture());
if (positiveErrors.length) throw new Error(`正向 fixture 失败：${positiveErrors.join("；")}`);
for (const [name, mutate] of negatives) {
  const data = fixture();
  mutate(data);
  if (validate(data).length === 0) throw new Error(`反向 fixture 未失败：${name}`);
}
console.log(`page-spec context tests passed: 1 positive, ${negatives.length} negative`);
