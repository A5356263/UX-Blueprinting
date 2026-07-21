"use strict";

function normalizeBlueprint(input) {
  if (!input || !["1.0", "2.0", "3.0"].includes(input.version)) {
    throw new Error(`不支持的 Experience Blueprint 版本：${input && input.version}`);
  }
  const v1 = input.version === "1.0";
  const v3 = input.version === "3.0";
  const surfaces = v1
    ? {
        pages: (input.pages || []).map((item) => ({ name: item.page_name })),
        modals: (input.modals || []).map((item) => ({ name: item.modal_name })),
        drawers: (input.drawers || []).map((item) => ({ name: item.drawer_name })),
      }
    : input.surfaces;
  const flowName = (item, legacyKey) => v3 ? item.name : item[legacyKey];
  return {
    mainFlow: (input.main_flow || []).map((item) => flowName(item, "node_name")).sort(),
    subFlows: (input.sub_flows || []).map((item) => flowName(item, "flow_name")).sort(),
    exceptions: (input.exceptions || []).map((item) => item.name).sort(),
    surfaces: ["pages", "modals", "drawers"].flatMap((kind) =>
      (surfaces[kind] || []).map((item) => `${kind}:${item.name}`)).sort(),
    states: (input.states || []).map((item) => item.state).sort(),
  };
}

const v1 = {
  version: "1.0",
  main_flow: [{ node_name: "提交申请" }],
  sub_flows: [{ flow_name: "编辑配置" }],
  exceptions: [{ name: "内容为空" }],
  pages: [{ page_id: "page-request", page_name: "申请页" }],
  modals: [{ modal_id: "modal-confirm", modal_name: "确认弹窗" }],
  drawers: [],
  states: [{ state: "待审批" }],
};
const v2 = {
  version: "2.0",
  main_flow: [{ node_id: "node-request", node_name: "提交申请" }],
  sub_flows: [{ flow_id: "flow-edit", flow_name: "编辑配置" }],
  exceptions: [{ exception_id: "exception-empty", name: "内容为空" }],
  surfaces: {
    pages: [{ surface_id: "page-request", name: "申请页" }],
    modals: [{ surface_id: "modal-confirm", name: "确认弹窗" }],
    drawers: [],
  },
  states: [{ state_id: "state-pending", state: "待审批" }],
};
const v3 = {
  version: "3.0",
  main_flow: [{ name: "提交申请" }],
  sub_flows: [{ name: "编辑配置" }],
  exceptions: [{ name: "内容为空" }],
  surfaces: {
    pages: [{ name: "申请页", markdown_heading: "6.1 申请页" }],
    modals: [{ name: "确认弹窗", markdown_heading: "6.2 确认弹窗" }],
    drawers: [],
  },
  states: [{ state: "待审批" }],
};

const normalized = [v1, v2, v3].map((item) => JSON.stringify(normalizeBlueprint(item)));
if (new Set(normalized).size !== 1) {
  throw new Error(`Blueprint v1/v2/v3 核心页面语义集合不一致\n${normalized.join("\n")}`);
}
let rejected = false;
try {
  normalizeBlueprint({ version: "4.0" });
} catch {
  rejected = true;
}
if (!rejected) throw new Error("未知 Blueprint 版本未被拒绝");
console.log("page-spec input compatibility passed: Blueprint v1/v2/v3 equivalent, unknown rejected");

module.exports = { normalizeBlueprint };
