"use strict";

const { validate } = require("./validate-context");

function fixture() {
  return {
    skill: "uxb",
    version: "8.0",
    generated_at: "2026-07-29T10:00:00+08:00",
    project_name: "订单作废",
    artifact_md: "spark-output/uxb_output.md",
    experience_scope: {
      tasks: ["管理员作废订单"],
      roles: ["管理员"],
      business_objects: ["订单"],
      key_nodes: ["确认作废资格", "提交作废", "确认作废结果"],
      relevant_states: ["未结算", "已作废"],
      relevant_results: ["作废成功", "不允许作废"],
      unaffected_scope: ["订单创建"],
    },
    task_experience_decisions: [{
      id: "TE-001",
      task: "管理员作废订单",
      roles: ["管理员"],
      business_objects: ["订单"],
      business_nodes: ["确认作废资格", "提交作废", "记录作废结果"],
      perceived_stage: "确认影响并完成作废",
      orchestration_actions: ["merge"],
      orchestration_reason: "三个节点由同一角色连续完成，且共同服务于确认并完成作废的目标",
      experience_breakpoint: "资格、影响和结果分散时，用户无法形成连续决策",
      user_must_understand: ["当前订单是否允许作废", "作废不可恢复", "作废后的业务限制"],
      experience_decision: "将资格确认、影响解释和结果确认组织为连续任务阶段",
      information_order: ["作废资格", "不可逆影响", "作废原因", "最终结果"],
      explanation_timing: {
        before: ["解释作废条件和不可逆影响"],
        during: ["反馈处理状态"],
        after: ["说明最终状态和后续限制"],
      },
      state_result_requirements: ["区分处理中、已作废和不允许作废"],
      continuity_requirements: ["全过程保持同一订单上下文"],
      blueprint_requirements: ["按资格、影响、提交和结果的顺序落实任务"],
    }],
    cross_stage_decisions: [{
      id: "CS-001",
      task: "管理员作废订单",
      from_stage: "确认影响并完成作废",
      to_stage: "查看作废结果",
      transition_trigger: "系统完成作废处理",
      context_to_preserve: ["订单标识", "作废原因"],
      transition_decision: "结果阶段承接原订单并明确交代状态变化",
      blueprint_requirements: ["保留订单识别信息并说明后续限制"],
    }],
    state_recovery_decisions: [{
      id: "SR-001",
      task: "管理员作废订单",
      business_states: ["未结算", "已作废"],
      user_visible_meaning: "订单已完成不可恢复的作废处理",
      result_or_next_action: "查看作废记录，不再进入报销或结算",
      experience_decision: "明确区分处理中、已作废和不允许作废",
      blueprint_requirements: ["每类结果都给出明确行动认知"],
    }],
    blueprint_requirements: [{
      id: "BR-001",
      task: "管理员作废订单",
      roles: ["管理员"],
      perceived_stage: "确认影响并完成作废",
      requirement: "落实操作前、中、后的连续解释",
      purpose: "保证用户理解不可逆影响和最终结果",
      must_preserve: ["不可逆影响必须在提交前被理解"],
    }],
    upstream_trace: [{
      id: "UT-001",
      source_type: "requirements_baseline",
      source_name: "订单作废正式需求基线",
      status: "formal",
      source_path: "spark-output/requirements_baseline.md",
      used_for: ["业务任务和目标状态"],
    }, {
      id: "UT-002",
      source_type: "business_knowledge",
      source_name: "订单业务知识",
      status: "formal",
      used_for: ["理解订单状态和业务约束"],
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

const noPressure = fixture();
noPressure.task_experience_decisions = [];
noPressure.cross_stage_decisions = [];
noPressure.state_recovery_decisions = [];
noPressure.blueprint_requirements = [{
  id: "BR-001",
  task: "现有任务",
  roles: ["管理员"],
  perceived_stage: "沿用现有任务",
  requirement: "忠实落实需求基线",
  purpose: "保持已确定业务事实",
  must_preserve: ["需求基线中的任务结果"],
}];
assertValid(noPressure, "无体验压力的合法结构");

const semanticBoundary = fixture();
semanticBoundary.task_experience_decisions[0].experience_decision = "页面顶部使用三张卡片";
assertValid(semanticBoundary, "脚本不执行语义越界判断");

const missingField = fixture();
delete missingField.cross_stage_decisions;
assertInvalid(missingField, "缺少根字段");

const extraField = fixture();
extraField.open_questions = [];
assertInvalid(extraField, "多余根字段");

const wrongVersion = fixture();
wrongVersion.version = "7.0";
assertInvalid(wrongVersion, "错误版本");

const emptyRequiredArray = fixture();
emptyRequiredArray.task_experience_decisions[0].roles = [];
assertInvalid(emptyRequiredArray, "必填数组为空");

const wrongAction = fixture();
wrongAction.task_experience_decisions[0].orchestration_actions = ["combine"];
assertInvalid(wrongAction, "错误编排枚举");

const wrongTiming = fixture();
wrongTiming.task_experience_decisions[0].explanation_timing = { unknown: ["说明"] };
assertInvalid(wrongTiming, "错误解释时机字段");

const wrongSourceStatus = fixture();
wrongSourceStatus.upstream_trace[0].status = "draft";
assertInvalid(wrongSourceStatus, "错误来源状态");

const duplicateId = fixture();
duplicateId.blueprint_requirements.push({ ...duplicateId.blueprint_requirements[0] });
assertInvalid(duplicateId, "重复编号");

const missingNestedField = fixture();
delete missingNestedField.task_experience_decisions[0].experience_decision;
assertInvalid(missingNestedField, "缺少对象字段");

const emptyString = fixture();
emptyString.state_recovery_decisions[0].experience_decision = "";
assertInvalid(emptyString, "空字符串");

console.log("UXB Context 8.0 结构测试通过：3 个正向用例，10 个反向用例。");
