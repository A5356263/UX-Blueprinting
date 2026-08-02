"use strict";

const assert = require("assert");
const { REQUIRED_FIELDS, validate } = require("./validate-context");

function fixture() {
  return {
    schema_version: "2.0",
    project_name: "测试项目",
    baseline_status: "formal",
    source_trace: {
      prd: [{ type: "prd", reference: "prd.md", location: "功能说明" }],
      formal_knowledge: [],
      product_responses: ["Q-001"],
    },
    goal_and_scope: {
      business_problem: ["需要支持订单作废"],
      goals: ["完成订单作废闭环"],
      in_scope: ["管理员作废订单"],
      out_of_scope: [],
      success_results: ["订单进入已作废状态"],
    },
    business_objects: [{
      id: "BO-001",
      name: "订单",
      definition: "公司授信订单",
      relations: [],
      entry_conditions: ["未结算"],
      exclusion_conditions: [],
      change_type: "modify",
      sources: [{ type: "prd", reference: "prd.md", location: "订单作废功能" }],
    }],
    roles_and_permissions: [],
    functions_and_task_closure: [{
      id: "FN-001",
      name: "标记订单作废",
      actor: "管理员",
      trigger_conditions: ["具备订单作废权限"],
      main_steps: ["提交作废"],
      success_results: ["订单已作废"],
      failure_or_rejection_results: ["不满足条件时拒绝"],
      next_business_nodes: [],
      existing_task_location: "消费平台 > 月结对账 > 公司授信订单",
      existing_carriers: ["公司授信订单列表"],
      existing_entry: "公司授信订单列表操作列",
      sources: [{ type: "product_response", reference: "Q-001", location: "产品回复" }],
    }],
    business_rules: [],
    states_and_transitions: [{
      id: "ST-001",
      business_object: "订单",
      state: "已作废",
      meaning: "订单不可继续报销或结算",
      entry_conditions: ["作废成功"],
      allowed_actions: [],
      forbidden_actions: ["报销"],
      next_states: [],
      irreversible: true,
      sources: [{ type: "prd", reference: "prd.md", location: "已作废订单" }],
    }],
    exceptions_and_business_results: [],
    data_system_and_audit: {
      data_changes: [],
      system_impacts: [],
      synchronization_and_failures: [],
      audit_facts: ["记录操作人和时间"],
      historical_data: [],
    },
    constraints_and_out_of_scope: {
      business_constraints: [],
      dependencies: [],
      explicitly_out_of_scope: [],
      future_considerations: [],
    },
    completion_criteria: [{
      id: "AC-001",
      related_ids: ["FN-001", "ST-001"],
      preconditions: ["订单满足作废条件"],
      actions: ["管理员确认标记订单作废"],
      observable_results: ["订单状态更新为已作废"],
      sources: [{ type: "prd", reference: "prd.md", location: "订单作废功能" }],
    }],
  };
}

assert.deepStrictEqual(validate(fixture()), []);

const missing = fixture();
delete missing.project_name;
assert(validate(missing).some((item) => item.includes("project_name")));

const invalidType = fixture();
invalidType.schema_version = 1;
assert(validate(invalidType).some((item) => item.includes("schema_version")));

const invalidEnum = fixture();
invalidEnum.business_objects[0].change_type = "update";
assert(validate(invalidEnum).some((item) => item.includes("change_type")));

const duplicateId = fixture();
duplicateId.states_and_transitions.push({ ...duplicateId.states_and_transitions[0] });
assert(validate(duplicateId).some((item) => item.includes("编号重复")));

const unknownReference = fixture();
unknownReference.completion_criteria[0].related_ids = ["FN-999"];
assert(validate(unknownReference).some((item) => item.includes("不存在的编号")));

const optionalExistingContext = fixture();
delete optionalExistingContext.functions_and_task_closure[0].existing_task_location;
delete optionalExistingContext.functions_and_task_closure[0].existing_carriers;
delete optionalExistingContext.functions_and_task_closure[0].existing_entry;
assert.deepStrictEqual(validate(optionalExistingContext), []);

const invalidExistingCarriers = fixture();
invalidExistingCarriers.functions_and_task_closure[0].existing_carriers = "公司授信订单列表";
assert(validate(invalidExistingCarriers).some((item) => item.includes("existing_carriers")));

const semanticText = fixture();
semanticText.goal_and_scope.goals = ["待确认是否支持撤销"];
assert.deepStrictEqual(validate(semanticText), []);

console.log("PRD Review Context 结构测试通过。");
