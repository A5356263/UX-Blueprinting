"use strict";

function normalizeBlueprint(input) {
  if (!input || !["1.0", "2.0"].includes(input.version)) {
    throw new Error(`不支持的 Experience Blueprint 版本：${input && input.version}`);
  }
  const v2 = input.version === "2.0";
  const surfaces = v2
    ? input.surfaces
    : {
        pages: (input.pages || []).map((item) => ({ surface_id: item.page_id, name: item.page_name })),
        modals: (input.modals || []).map((item) => ({ surface_id: item.modal_id, name: item.modal_name })),
        drawers: (input.drawers || []).map((item) => ({ surface_id: item.drawer_id, name: item.drawer_name })),
      };
  return {
    sourceMode: v2 ? input.source_status.source_mode : input.source_mode,
    mainFlow: (input.main_flow || []).map((item) => item.node_name).sort(),
    subFlows: (input.sub_flows || []).map((item) => item.flow_name).sort(),
    exceptions: (input.exceptions || []).map((item) => item.name).sort(),
    surfaces: ["pages", "modals", "drawers"].flatMap((kind) =>
      (surfaces[kind] || []).map((item) => `${kind}:${item.name}`)).sort(),
    states: (input.states || []).map((item) => item.state).sort(),
  };
}

const v1 = {
  version: "1.0",
  source_mode: "uxb-mode",
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
  source_status: { source_mode: "uxb-mode" },
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

const left = JSON.stringify(normalizeBlueprint(v1));
const right = JSON.stringify(normalizeBlueprint(v2));
if (left !== right) throw new Error(`Blueprint v1/v2 语义集合不一致\n${left}\n${right}`);
let rejected = false;
try {
  normalizeBlueprint({ version: "3.0" });
} catch {
  rejected = true;
}
if (!rejected) throw new Error("未知 Blueprint 版本未被拒绝");
console.log("page-spec input compatibility passed: Blueprint v1/v2 equivalent, unknown rejected");

module.exports = { normalizeBlueprint };
