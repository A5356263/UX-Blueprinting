"use strict";

const { validate } = require("./validate-context");

function fixture() {
  return {
    skill: "experience-blueprint",
    version: "4.0",
    generated_at: "2026-07-20T00:00:00+08:00",
    project_name: "测试项目",
    artifact_md: "spark-output/experience_blueprint.md",
    source_refs: [
      "spark-output/requirements_baseline.md",
      "spark-output/context/requirements-baseline.json",
      "spark-output/uxb_output.md",
      "spark-output/context/uxb.json",
    ],
    upstream_contract: {
      mode: "uxb-mode",
      requirements_baseline_refs: [
        "spark-output/requirements_baseline.md",
        "spark-output/context/requirements-baseline.json",
      ],
      uxb_refs: [
        "spark-output/uxb_output.md",
        "spark-output/context/uxb.json",
      ],
    },
    critical_design_judgments: [{
      judgment: "入口需可发现",
      impacts: ["申请页", "权限入口"],
      recommended_approach: "无权限时展示申请入口",
      not_recommended: "不建议完全隐藏入口，用户无法理解下一步",
    }],
    journey_consumption: [{
      type: "关键转折",
      finding: "用户发现无权限后需要明确出口",
      source_stage: "员工 / 发起任务",
      blueprint_target: "申请入口与申请页",
    }],
    interaction_overview: [{
      name: "员工提交权限申请",
      path_type: "主路径",
      steps: ["进入申请页", "填写并提交", "看到待审批状态"],
      branches: ["内容为空 → 阻止提交并显示 InlineError"],
    }],
    main_flow: [{
      name: "提交申请",
      user_action: "填写并提交",
      system_feedback: "创建申请",
      pre_explanations: ["提交后进入审批"],
      copy_suggestions: ["申请已提交"],
      next_step: "进入待审批",
    }],
    sub_flows: [{
      name: "编辑申请",
      trigger_condition: "尚未提交",
      user_action: "修改申请内容",
      system_feedback: "保存修改",
      pre_explanations: [],
      copy_suggestions: [],
      next_step: "返回申请页",
    }],
    exceptions: [{
      name: "内容为空",
      timing: "提交前",
      trigger_condition: "必填项为空",
      basis: "必填校验未通过",
      feedback_type: "InlineError",
      system_feedback: "阻止提交",
      user_next_step: "补充内容",
      recovery_path: "补齐后重试，已填信息不丢失",
    }],
    surfaces: {
      pages: [{
        name: "申请页",
        goal: "提交申请",
        entry_condition: "无权限且允许申请",
        markdown_heading: "6.1 申请页",
        structure_notes: ["标题区、表单区、操作区"],
        fields: ["申请内容：Textarea"],
        validation_rules: ["申请内容必填"],
        state_feedback: ["提交后展示待审批"],
        exception_structure_changes: ["内容为空时输入区下方显示 InlineError"],
        copy_items: ["请填写申请内容"],
        buttons: ["提交申请"],
        success_feedback: ["Toast：申请已提交"],
        failure_feedback: ["InlineError：请填写申请内容"],
      }],
      modals: [],
      drawers: [],
    },
    states: [{
      state: "待审批",
      meaning: "申请已提交",
      applies_to: "申请记录",
      user_actions: ["查看进度"],
      feedback: "显示待审批",
    }],
    feedbacks: [{ scenario: "提交成功", type: "Toast", copy: "申请已提交" }],
    upstream_trace: [{
      upstream_judgment: "无权限用户需要申请出口",
      experience_meaning: "入口不能完全隐藏",
      design_decision: "展示申请入口",
      blueprint_target: "§3 / §6",
    }],
  };
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

const negatives = [
  ["缺根字段", (data) => delete data.interaction_overview],
  ["多余字段", (data) => { data.lanes = []; }],
  ["错误类型", (data) => { data.states = "bad"; }],
  ["已移除根字段", (data) => { data.open_questions = []; }],
  ["已移除判断字段", (data) => { data.critical_design_judgments[0].open_question = "unknown"; }],
  ["旧 source_status", (data) => { data.source_status = {}; }],
  ["旧 ID", (data) => { data.main_flow[0].node_id = "node-request"; }],
  ["旧 anchor", (data) => { data.surfaces.pages[0].md_anchor = "§6"; }],
  ["旧回接字段", (data) => { data.sub_flows[0].end_target = "提交申请"; }],
  ["核心数组为空", (data) => { data.main_flow = []; }],
  ["总览为空", (data) => { data.interaction_overview = []; }],
  ["载体为空", (data) => { data.surfaces.pages = []; }],
  ["嵌套字段缺失", (data) => delete data.surfaces.pages[0].validation_rules],
  ["字符串数组错误", (data) => { data.main_flow[0].copy_suggestions = "申请已提交"; }],
  ["版本错误", (data) => { data.version = "2.0"; }],
  ["产物路径错误", (data) => { data.artifact_md = "wrong.md"; }],
];

const positiveErrors = validate(fixture());
if (positiveErrors.length) throw new Error(`正向 fixture 失败：${positiveErrors.join("；")}`);

const baselineMode = clone(fixture());
baselineMode.upstream_contract.mode = "baseline-mode";
baselineMode.upstream_contract.uxb_refs = [];
baselineMode.source_refs = baselineMode.upstream_contract.requirements_baseline_refs;
const baselineErrors = validate(baselineMode);
if (baselineErrors.length) throw new Error(`baseline-mode 失败：${baselineErrors.join("；")}`);

for (const [name, mutate] of negatives) {
  const data = clone(fixture());
  mutate(data);
  const errors = validate(data);
  if (!errors.length) throw new Error(`反向 fixture 未失败：${name}`);
}
const oldContract = clone(fixture());
oldContract.version = "3.0";
if (!validate(oldContract).length) throw new Error("旧 3.0 合同应失败");

const incompleteUxbMode = clone(fixture());
incompleteUxbMode.upstream_contract.uxb_refs = ["spark-output/uxb_output.md"];
if (!validate(incompleteUxbMode).length) throw new Error("不完整 uxb-mode 应失败");

console.log(`experience-blueprint context tests passed: 2 positive, ${negatives.length + 2} negative`);

module.exports = { fixture };
