"use strict";

const { validate } = require("./validate-context");

function fixture() {
  return {
    skill: "uxb",
    version: "6.0",
    generated_at: "2026-07-28T10:00:00+08:00",
    project_name: "订单作废",
    artifact_md: "spark-output/uxb_output.md",
    baseline_ref: {
      artifact_md: "spark-output/requirements_baseline.md",
      status: "formal",
    },
    core_experience_decision: {
      direction: "先建立不可逆影响认知，再完成作废任务",
      primary_tradeoff: "风险解释优先于操作效率",
      blueprint_principle: "始终让用户理解当前结果和下一步",
    },
    experience_impact_scope: {
      tasks: ["订单作废"],
      role_perspectives: ["管理员"],
      key_nodes: ["发起作废", "作废结果"],
      unaffected_scope: ["订单创建"],
    },
    experience_goals: [{
      id: "EG-001",
      goal: "降低不可逆操作误判",
      priority: "P0",
      pressure: "用户需要理解作废后的业务影响",
      conflict_principle: "风险认知优先于操作速度",
    }],
    information_architecture_directions: [{
      id: "IA-001",
      scope: "作废信息",
      direction: "按条件、影响和结果组织",
      rationale: "符合决策顺序",
      stable_relationships: ["原因与作废记录保持关联"],
    }],
    interaction_flow_directions: [{
      id: "FL-001",
      task: "标记订单作废",
      direction: "先确认资格和影响，再提交不可逆操作",
      sequence_principles: ["资格判断早于提交"],
      exception_continuity: "失败后保留用户对当前订单状态的理解",
    }],
    node_explanation_strategies: [{
      id: "NE-001",
      node: "提交作废",
      before: ["解释不可逆影响"],
      during: ["反馈处理状态"],
      after: ["说明作废结果和后续限制"],
      purpose: "避免误操作和结果误解",
    }],
    information_reading_strategies: [{
      id: "IR-001",
      scope: "作废决策信息",
      reading_order: ["资格", "影响", "原因", "结果"],
      clarity_principles: ["区分当前状态和操作后状态"],
      concept_distinctions: ["作废不同于删除"],
    }],
    state_feedback_and_role_continuity: [{
      id: "SF-001",
      scenario: "订单作废成功",
      feedback_strategy: "明确结果、影响和后续不可执行动作",
      action_understanding: "用户知道无需继续报销或结算",
      role_continuity: "不同角色对已作废含义保持一致",
      cross_node_or_channel_continuity: "",
    }],
    experience_tradeoffs: [{
      id: "TD-001",
      topic: "风险解释与操作效率",
      chosen_direction: "优先完成风险解释",
      rejected_directions: ["直接提交后再说明"],
      reason: "操作不可逆",
      impact_scope: ["发起作废"],
    }],
    blueprint_handoff_requirements: [{
      id: "BH-001",
      requirement: "落实操作前、中、后的连续解释",
      purpose: "保证用户理解不可逆影响和最终结果",
      must_preserve: ["不可逆影响必须在提交前被理解"],
      solution_space: "蓝图自行决定具体页面和交互载体",
    }],
  };
}

function assertValid(data, name) {
  const errors = validate(data);
  if (errors.length > 0) throw new Error(`${name} 应通过：${errors.join("；")}`);
}

function assertInvalid(data, name) {
  if (validate(data).length === 0) throw new Error(`${name} 应失败`);
}

assertValid(fixture(), "完整结构");

const emptyArrays = fixture();
for (const field of [
  "experience_goals",
  "information_architecture_directions",
  "interaction_flow_directions",
  "node_explanation_strategies",
  "information_reading_strategies",
  "state_feedback_and_role_continuity",
  "experience_tradeoffs",
  "blueprint_handoff_requirements",
]) {
  emptyArrays[field] = [];
}
assertValid(emptyArrays, "合法空数组");

const semanticBoundary = fixture();
semanticBoundary.information_architecture_directions[0].direction = "页面顶部使用三张卡片";
assertValid(semanticBoundary, "脚本不执行语义越界判断");

const missingField = fixture();
delete missingField.experience_tradeoffs;
assertInvalid(missingField, "缺少根字段");

const extraField = fixture();
extraField.open_questions = [];
assertInvalid(extraField, "多余根字段");

const wrongVersion = fixture();
wrongVersion.version = "5.0";
assertInvalid(wrongVersion, "错误版本");

const wrongPriority = fixture();
wrongPriority.experience_goals[0].priority = "high";
assertInvalid(wrongPriority, "错误优先级");

const duplicateId = fixture();
duplicateId.experience_tradeoffs.push({ ...duplicateId.experience_tradeoffs[0] });
assertInvalid(duplicateId, "重复编号");

const missingNestedField = fixture();
delete missingNestedField.node_explanation_strategies[0].purpose;
assertInvalid(missingNestedField, "缺少对象字段");

const emptyString = fixture();
emptyString.core_experience_decision.direction = "";
assertInvalid(emptyString, "空字符串");

console.log("UXB Context 结构测试通过：3 个正向用例，7 个反向用例。");
