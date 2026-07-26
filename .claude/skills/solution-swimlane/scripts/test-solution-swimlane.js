"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { normalizeDraft } = require("./normalize-semantic-model");
const { buildHtml } = require("./render-solution-swimlane");
const { validateModel } = require("./validate-semantic-model");

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function fixture() {
  return {
    schema_version: "2.0",
    title: "权限申请方案协同图",
    scope: "员工发起权限申请至系统完成授权",
    start_condition: "员工需要新增业务权限",
    end_conditions: ["授权完成", "申请终止"],
    lanes: [
      {
        id: "employee",
        name: "员工",
        type: "human",
        order: 1,
        responsibility: "发起申请并处理退回",
        source_refs: ["§3 主流程"],
      },
      {
        id: "system",
        name: "权限系统",
        type: "system",
        order: 2,
        responsibility: "校验申请并执行授权",
        source_refs: ["§3 主流程"],
      },
    ],
    nodes: [
      {
        id: "start",
        lane_id: "employee",
        label: "需要新增权限",
        type: "start",
        summary: "员工产生权限申请需求",
        certainty: "confirmed",
        source_refs: ["§3 P1"],
        flow_ids: ["main"],
      },
      {
        id: "submit",
        lane_id: "employee",
        label: "提交权限申请",
        type: "action",
        summary: "填写申请原因并提交",
        certainty: "confirmed",
        source_refs: ["§3 P2"],
        flow_ids: ["main"],
      },
      {
        id: "check",
        lane_id: "system",
        label: "校验申请",
        type: "decision",
        summary: "判断申请信息是否完整",
        certainty: "confirmed",
        source_refs: ["§3 P3"],
        flow_ids: ["main", "exception-return"],
      },
      {
        id: "grant",
        lane_id: "system",
        label: "执行授权",
        type: "system_process",
        summary: "写入权限并记录结果",
        certainty: "confirmed",
        source_refs: ["§3 P4"],
        flow_ids: ["main"],
      },
      {
        id: "done",
        lane_id: "employee",
        label: "获得权限",
        type: "end",
        summary: "员工可使用目标功能",
        certainty: "confirmed",
        source_refs: ["§3 P5"],
        flow_ids: ["main"],
      },
      {
        id: "pending-return",
        lane_id: "employee",
        label: "补充材料方式待确认",
        type: "pending",
        summary: "原文未说明从何处补充材料",
        certainty: "uncertain",
        source_refs: ["§5 异常"],
        flow_ids: ["exception-return"],
      },
    ],
    edges: [
      {
        id: "need-submit",
        from: "start",
        to: "submit",
        label: "开始申请",
        type: "normal",
        certainty: "confirmed",
        source_refs: ["§3 P1-P2"],
        flow_ids: ["main"],
      },
      {
        id: "submit-check",
        from: "submit",
        to: "check",
        label: "提交后",
        type: "handoff",
        certainty: "confirmed",
        source_refs: ["§3 P2-P3"],
        flow_ids: ["main"],
      },
      {
        id: "check-grant",
        from: "check",
        to: "grant",
        label: "信息完整",
        type: "conditional",
        certainty: "confirmed",
        source_refs: ["§3 P3-P4"],
        flow_ids: ["main"],
      },
      {
        id: "grant-done",
        from: "grant",
        to: "done",
        label: "授权成功",
        type: "handoff",
        certainty: "confirmed",
        source_refs: ["§3 P4-P5"],
        flow_ids: ["main"],
      },
      {
        id: "check-pending",
        from: "check",
        to: "pending-return",
        label: "信息不完整",
        type: "exception",
        certainty: "uncertain",
        source_refs: ["§5 异常"],
        flow_ids: ["exception-return"],
      },
    ],
    flows: [
      {
        id: "main",
        name: "主流程",
        type: "main",
        node_ids: ["start", "submit", "check", "grant", "done"],
        edge_ids: ["need-submit", "submit-check", "check-grant", "grant-done"],
        default_visible: true,
      },
      {
        id: "exception-return",
        name: "材料不完整",
        type: "exception",
        node_ids: ["check", "pending-return"],
        edge_ids: ["check-pending"],
        default_visible: false,
      },
    ],
    open_questions: [
      {
        id: "question-return-entry",
        question: "员工从哪个入口补充材料？",
        impact: "影响异常流程的恢复路径",
        related_element_ids: ["pending-return"],
        fallback: "以 pending 节点表达",
      },
    ],
  };
}

function draftFixture() {
  const draft = clone(fixture());
  delete draft.schema_version;
  draft.draft_version = "1.1";
  for (const lane of draft.lanes) delete lane.source_refs;
  for (const node of draft.nodes) {
    delete node.flow_ids;
    delete node.source_refs;
    if (node.certainty === "confirmed") delete node.certainty;
  }
  delete draft.nodes[0].summary;
  for (const edge of draft.edges) {
    delete edge.flow_ids;
    delete edge.source_refs;
    if (edge.certainty === "confirmed") delete edge.certainty;
  }
  for (const flow of draft.flows) {
    delete flow.node_ids;
    delete flow.default_visible;
  }
  return JSON.parse(JSON.stringify(draft));
}

function expectFailure(name, model, pattern, html = null) {
  const report = validateModel(model, html);
  assert.strictEqual(report.ok, false, `${name} 应当失败`);
  assert(
    report.errors.some((message) => pattern.test(message)),
    `${name} 未出现预期错误；实际：${report.errors.join(" | ")}`,
  );
}

function run() {
  const templatePath = path.resolve(__dirname, "../assets/solution-swimlane.template.html");
  const template = fs.readFileSync(templatePath, "utf8");
  const draft = draftFixture();
  const model = normalizeDraft(draft);

  assert.strictEqual(model.schema_version, "2.0");
  assert.strictEqual(model.draft_version, undefined);
  assert.deepStrictEqual(model.lanes[0].source_refs, []);
  assert.strictEqual(model.nodes[0].summary, model.nodes[0].label);
  assert.strictEqual(model.nodes[0].certainty, "confirmed");
  assert.deepStrictEqual(model.nodes[0].source_refs, []);
  assert.strictEqual(model.edges[0].certainty, "confirmed");
  assert.deepStrictEqual(model.edges[0].source_refs, []);
  assert.deepStrictEqual(model.nodes.find((node) => node.id === "check").flow_ids, [
    "main",
    "exception-return",
  ]);
  assert.deepStrictEqual(model.edges.find((edge) => edge.id === "check-pending").flow_ids, [
    "exception-return",
  ]);
  assert.deepStrictEqual(model.flows.find((flow) => flow.id === "main").node_ids, [
    "start",
    "submit",
    "check",
    "grant",
    "done",
  ]);
  assert.strictEqual(model.flows.find((flow) => flow.id === "main").default_visible, true);
  assert.strictEqual(
    model.flows.find((flow) => flow.id === "exception-return").default_visible,
    false,
  );
  assert.strictEqual(
    `${JSON.stringify(normalizeDraft(draft), null, 2)}\n`,
    `${JSON.stringify(normalizeDraft(clone(draft)), null, 2)}\n`,
    "相同草稿必须生成逐字节一致的规范模型",
  );

  const nodeWithFlowIds = draftFixture();
  nodeWithFlowIds.nodes[0].flow_ids = ["main"];
  assert.throws(() => normalizeDraft(nodeWithFlowIds), /禁止字段.*flow_ids/);

  const laneWithSourceRefs = draftFixture();
  laneWithSourceRefs.lanes[0].source_refs = ["§3"];
  assert.throws(() => normalizeDraft(laneWithSourceRefs), /禁止字段.*source_refs/);

  const flowWithNodeIds = draftFixture();
  flowWithNodeIds.flows[0].node_ids = ["start", "submit"];
  assert.throws(() => normalizeDraft(flowWithNodeIds), /禁止字段.*node_ids/);

  const flowWithDefault = draftFixture();
  flowWithDefault.flows[0].default_visible = true;
  assert.throws(() => normalizeDraft(flowWithDefault), /禁止字段.*default_visible/);

  const unknownField = draftFixture();
  unknownField.unplanned = true;
  assert.throws(() => normalizeDraft(unknownField), /未知字段.*unplanned/);

  const missingNodeReference = draftFixture();
  missingNodeReference.edges[0].from = "missing-node";
  assert.throws(() => normalizeDraft(missingNodeReference), /from.*missing-node/);

  const missingEdgeReference = draftFixture();
  missingEdgeReference.flows[0].edge_ids[0] = "missing-edge";
  assert.throws(() => normalizeDraft(missingEdgeReference), /edge_ids.*missing-edge/);

  const disconnected = draftFixture();
  disconnected.flows[0].edge_ids = ["need-submit", "check-grant"];
  assert.throws(() => normalizeDraft(disconnected), /流程 main 关系不连续/);

  const middleEnd = draftFixture();
  middleEnd.nodes.find((node) => node.id === "submit").type = "end";
  assert.throws(() => normalizeDraft(middleEnd), /流程 main.*end.*最后/);

  const edgeFromEnd = draftFixture();
  edgeFromEnd.nodes.find((node) => node.id === "submit").type = "end";
  assert.throws(() => normalizeDraft(edgeFromEnd), /关系 submit-check.*end.*发出/);

  const invalidSecondary = draftFixture();
  invalidSecondary.flows.push({
    id: "secondary-review",
    name: "次流程：查看校验",
    type: "secondary",
    edge_ids: ["submit-check"],
  });
  assert.throws(() => normalizeDraft(invalidSecondary), /次流程 secondary-review.*出口/);

  const invalidException = draftFixture();
  invalidException.edges.push({
    id: "pending-to-submit",
    from: "pending-return",
    to: "submit",
    label: "继续处理",
    type: "normal",
  });
  invalidException.flows[1].edge_ids.push("pending-to-submit");
  assert.throws(() => normalizeDraft(invalidException), /异常流程 exception-return.*出口/);

  const duplicateEndpoints = draftFixture();
  duplicateEndpoints.edges.push({
    id: "grant-done-duplicate",
    from: "grant",
    to: "done",
    label: "重复完成",
    type: "terminate",
  });
  duplicateEndpoints.flows[0].edge_ids.push("grant-done-duplicate");
  assert.throws(() => normalizeDraft(duplicateEndpoints), /流程 main.*重复端点.*grant.*done/);

  const report = validateModel(model);
  assert.strictEqual(report.ok, true, report.errors.join("\n"));
  assert.strictEqual(report.summary.pending_total, 1);
  assert.strictEqual(report.summary.open_questions_total, 1);

  const first = buildHtml(model, template);
  const second = buildHtml(clone(model), template);
  assert.strictEqual(first.html, second.html, "相同语义模型必须生成完全一致的 HTML");
  assert.strictEqual(validateModel(model, first.html).ok, true);
  assert(first.html.includes('data-node-id="pending-return"'), "pending 节点必须进入正式 SVG");
  assert(first.html.includes('data-node-type="pending"'), "pending 节点必须有明确类型");
  assert(!first.html.includes("swimlane-source-inventory"), "HTML 不得嵌入旧来源清单");
  assert(!first.html.includes("coverage_manifest"), "HTML 不得包含旧覆盖字段");
  assert(!first.html.includes("__SWIMLANE_"), "模板占位符必须全部替换");

  const legacy = clone(model);
  legacy.coverage_manifest = [];
  expectFailure("旧覆盖字段", legacy, /禁止字段.*coverage_manifest/);

  const duplicate = clone(model);
  duplicate.nodes[1].id = "start";
  expectFailure("重复节点 ID", duplicate, /nodes ID 重复/);

  const missingLane = clone(model);
  missingLane.nodes[0].lane_id = "missing";
  expectFailure("不存在泳道", missingLane, /lane_id 不存在/);

  const unlabeledDecision = clone(model);
  unlabeledDecision.edges[2].label = "";
  expectFailure("判断分支无标签", unlabeledDecision, /条件关系.*标签/);

  const brokenException = clone(model);
  brokenException.flows[1].node_ids = ["check"];
  brokenException.flows[1].edge_ids = [];
  expectFailure("异常无出口", brokenException, /异常流程.*出口/);

  const modelWithMiddleEnd = clone(model);
  modelWithMiddleEnd.nodes.find((node) => node.id === "submit").type = "end";
  expectFailure("主流程中途结束", modelWithMiddleEnd, /流程 main.*end.*最后/);

  const modelWithDisconnectedFlow = clone(model);
  modelWithDisconnectedFlow.flows[0].edge_ids = ["need-submit", "check-grant"];
  expectFailure("规范模型关系不连续", modelWithDisconnectedFlow, /流程 main 关系不连续/);

  const wrongDefault = clone(model);
  wrongDefault.flows[0].default_visible = false;
  wrongDefault.flows[1].default_visible = true;
  expectFailure("默认流程错误", wrongDefault, /main 流程设为默认可见/);

  const brokenHtml = first.html.replace('data-node-id="submit"', 'data-node-id="missing-submit"');
  expectFailure("DOM 节点不一致", model, /DOM 节点集合/, brokenHtml);

  const escaped = clone(model);
  escaped.nodes[1].label = "<script>alert(1)</script>";
  const escapedHtml = buildHtml(escaped, template).html;
  assert(!escapedHtml.includes("<script>alert(1)</script>"), "业务文本必须转义");

  console.log("solution-swimlane 语义模型 2.0 测试通过");
}

if (require.main === module) run();

module.exports = { draftFixture, fixture, run };
