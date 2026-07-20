"use strict";

const { validate } = require("./validate-context");

function fixture() {
  return {
    skill: "experience-blueprint",
    version: "2.0",
    generated_at: "2026-07-19T00:00:00+08:00",
    project_name: "测试项目",
    artifact_md: "spark-output/experience_blueprint.md",
    source_refs: ["spark-output/uxb_output.md"],
    source_status: { source_mode: "uxb-mode", expansion_mode: "full", usable: true, missing_inputs: [] },
    critical_design_judgments: [{
      judgment_id: "judgment-entry", judgment: "入口需可发现", decision: "无权限时展示申请入口",
      open_question: "unknown", source_anchor: "§0",
    }],
    main_flow: [{
      node_id: "node-request", node_name: "提交申请", user_action: "填写并提交",
      system_feedback: "创建申请", state_change: "进入待审批", next_step: "明确结果", source_anchor: "§3",
    }],
    sub_flows: [{
      flow_id: "flow-edit", flow_name: "编辑配置", trigger_condition: "管理员编辑",
      user_action: "保存", system_feedback: "保存成功", next_step: "返回申请",
      end_type: "return", end_target: "node-request", source_anchor: "§4",
    }],
    exceptions: [{
      exception_id: "exception-empty", name: "内容为空", timing: "提交前",
      trigger_condition: "必填项为空", system_feedback: "阻止提交", user_next_step: "补充内容",
      recovery_path: "补齐后重试", end_type: "return", end_target: "node-request", source_anchor: "§5",
    }],
    surfaces: {
      pages: [{ surface_id: "page-request", name: "申请页", goal: "提交申请", entry_condition: "无权限", md_anchor: "§6" }],
      modals: [],
      drawers: [],
    },
    states: [{
      state_id: "state-pending", state: "待审批", meaning: "申请已提交",
      applies_to: ["node-request"], user_action_available: "查看进度",
      feedback_standard: "显示待审批", source_anchor: "§7",
    }],
    open_questions: [],
  };
}
function clone(value) { return JSON.parse(JSON.stringify(value)); }

const negatives = [
  ["缺根字段", (data) => delete data.source_status],
  ["多余字段", (data) => { data.lanes = []; }],
  ["错误类型", (data) => { data.states = "bad"; }],
  ["非法枚举", (data) => { data.source_status.source_mode = "bad"; }],
  ["重复 ID", (data) => { data.main_flow.push(clone(data.main_flow[0])); }],
  ["引用不存在", (data) => { data.sub_flows[0].end_target = "node-missing"; }],
  ["核心数组为空", (data) => { data.main_flow = []; }],
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
console.log(`experience-blueprint context tests passed: 1 positive, ${negatives.length} negative`);
