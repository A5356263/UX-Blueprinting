"use strict";

const { validate } = require("./validate-context");

function fixture() {
  return {
    skill: "uxb",
    version: "5.0",
    generated_at: "2026-07-20",
    project_name: "测试项目",
    artifact_md: "spark-output/uxb_output.md",
    source_refs: ["input/test.md"],
    key_design_judgments: [{
      judgment: "在既有权限模型内增加复制能力",
      impact: "减少重复配置",
      recommended_approach: "复用既有权限规则",
      not_recommended: "不新增权限模型",
      open_question: "unknown",
    }],
    input_summary: {
      raw_request: "支持复制权限",
      confirmed_facts: ["复制来源为已有管理员"],
      explicit_constraints: ["单次最多 200 人"],
      missing_information: [],
    },
    business_scenario_judgment: {
      scenario: "批量配置权限",
      role: "权限管理员",
      task: "复制已有权限",
      value: "减少重复操作",
    },
    viability_judgment: {
      is_valid: "有条件成立",
      reason: "既有权限规则可以承接",
      blocking_issues: [],
      assumptions: ["现有校验能力可复用"],
    },
    business_boundary: {
      in_scope: ["复制已有权限"],
      out_of_scope: ["新增权限类型"],
      boundary_reason: ["本次只解决重复配置"],
    },
    roles: [{
      name: "权限管理员",
      type: "primary",
      responsibility: "发起复制",
      needs: ["快速完成配置"],
    }],
    features: [{
      name: "权限复制",
      input: "来源管理员与目标用户",
      process: "按既有规则校验并复制",
      output: "复制结果",
      result: "目标用户获得权限",
      boundary: "不改变权限模型",
    }],
    business_rules: [{
      rule: "目标数量限制",
      trigger: "提交复制",
      result: "数量合规则继续",
      fallback: "超限时阻断提交",
    }],
    states: [{
      state: "待提交",
      meaning: "复制内容尚未提交",
      system_result: "保留当前选择",
      user_next_step: "确认并提交",
    }],
    exceptions: [{
      exception: "目标数量超限",
      trigger: "选择超过 200 人",
      handling: "阻断提交",
      recovery: "减少目标后重试",
    }],
    experience_handoff_requirements: [{
      requirement: "区分直接生效与待审批",
      business_judgment: "治理模式决定生效路径",
      experience_impact: "用户需要理解当前结果是否已生效",
      must_address: ["明确展示当前生效状态"],
      do_not_rejudge: ["不得改变既有治理模式"],
    }],
    constraints: {
      hard_constraints: ["单次最多 200 人"],
      dependencies: ["复用既有权限校验"],
      do_not_do: ["不新增权限类型"],
      safety_or_business_boundaries: ["不得超出管理员可授权范围"],
    },
    open_questions: [{
      question: "部分失败是否支持重试",
      impact: "影响恢复路径",
      owner: "产品",
      level: "层级二",
    }],
  };
}

const negativeCases = [
  ["缺根字段", (data) => delete data.features],
  ["多余根字段", (data) => { data.knowledge_trace = []; }],
  ["版本错误", (data) => { data.version = "4.0"; }],
  ["产物路径错误", (data) => { data.artifact_md = "wrong.md"; }],
  ["旧紧凑字段", (data) => { data.decision_summary = "旧字段"; }],
  ["对象缺字段", (data) => { delete data.features[0].boundary; }],
  ["对象多余字段", (data) => { data.roles[0].id = "R1"; }],
  ["数组字段类型错误", (data) => { data.business_rules = "bad"; }],
  ["数组项类型错误", (data) => { data.source_refs = [{}]; }],
  ["嵌套数组项类型错误", (data) => { data.constraints.dependencies = [1]; }],
  ["字符串为空", (data) => { data.features[0].name = ""; }],
  ["成立性类型错误", (data) => { data.viability_judgment.is_valid = true; }],
  ["旧异常结构", (data) => {
    data.exceptions = [{
      name: "旧异常",
      trigger: "提交时",
      system_result: "阻断",
      user_next_step: "重试",
      recovery: "重试",
    }];
  }],
  ["旧承接结构", (data) => {
    data.experience_handoff_requirements = [{
      business_judgment: "旧结构",
      experience_impact: "影响",
      must_continue: "继续",
      forbidden_rejudge: "禁止",
    }];
  }],
];

const positiveErrors = validate(fixture());
if (positiveErrors.length) throw new Error(`正向 fixture 失败：${positiveErrors.join("；")}`);

const emptyCollections = fixture();
for (const field of [
  "source_refs", "key_design_judgments", "roles", "features", "business_rules",
  "states", "exceptions", "experience_handoff_requirements", "open_questions",
]) {
  emptyCollections[field] = [];
}
for (const value of [
  emptyCollections.input_summary,
  emptyCollections.business_boundary,
  emptyCollections.constraints,
]) {
  for (const key of Object.keys(value)) {
    if (Array.isArray(value[key])) value[key] = [];
  }
}
emptyCollections.viability_judgment.blocking_issues = [];
emptyCollections.viability_judgment.assumptions = [];
const emptyErrors = validate(emptyCollections);
if (emptyErrors.length) throw new Error(`合法空数组 fixture 失败：${emptyErrors.join("；")}`);

for (const [name, mutate] of negativeCases) {
  const data = fixture();
  mutate(data);
  if (validate(data).length === 0) throw new Error(`反向 fixture 未失败：${name}`);
}

console.log(`uxb context tests passed: 2 positive, ${negativeCases.length} negative`);
