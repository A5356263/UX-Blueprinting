"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const LANE_TYPES = new Set(["human", "team", "system"]);
const NODE_TYPES = new Set(["start", "action", "system_process", "decision", "result", "end", "pending"]);
const EDGE_TYPES = new Set(["normal", "conditional", "handoff", "exception", "return", "terminate"]);
const FLOW_TYPES = new Set(["main", "secondary", "exception"]);
const CERTAINTIES = new Set(["confirmed", "uncertain"]);
const FORBIDDEN_KEYS = new Set([
  "coverage_manifest",
  "coverage_rules",
  "source_inventory",
  "source_item_ids",
  "source_selectors",
]);

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`参数 --${key} 缺少值`);
    args[key] = value;
    index += 1;
  }
  return args;
}

function stableValue(value) {
  if (Array.isArray(value)) return value.map(stableValue);
  if (value && typeof value === "object") {
    return Object.keys(value).sort().reduce((result, key) => {
      result[key] = stableValue(value[key]);
      return result;
    }, {});
  }
  return value;
}

function computedModelHash(model) {
  return crypto.createHash("sha256").update(JSON.stringify(stableValue(model))).digest("hex");
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function requireString(value, field, errors) {
  if (typeof value !== "string" || !value.trim()) errors.push(`${field} 必须是非空字符串`);
}

function requireArray(value, field, errors) {
  if (!Array.isArray(value)) {
    errors.push(`${field} 必须是数组`);
    return false;
  }
  return true;
}

function duplicateValues(values) {
  const seen = new Set();
  const duplicates = new Set();
  for (const value of values) {
    if (seen.has(value)) duplicates.add(value);
    seen.add(value);
  }
  return [...duplicates];
}

function sameSet(left, right) {
  const leftSet = new Set(left);
  const rightSet = new Set(right);
  return leftSet.size === rightSet.size && [...leftSet].every((value) => rightSet.has(value));
}

function collectForbiddenKeys(value, location, errors) {
  if (Array.isArray(value)) {
    value.forEach((item, index) => collectForbiddenKeys(item, `${location}[${index}]`, errors));
    return;
  }
  if (!isObject(value)) return;
  for (const [key, child] of Object.entries(value)) {
    if (FORBIDDEN_KEYS.has(key)) errors.push(`禁止字段 ${location}.${key}`);
    collectForbiddenKeys(child, `${location}.${key}`, errors);
  }
}

function collectDomIds(html, attribute) {
  const pattern = new RegExp(`${attribute}="([^"]+)"`, "g");
  const values = [];
  let match;
  while ((match = pattern.exec(html))) values.push(match[1]);
  return [...new Set(values)];
}

function extractJsonScript(html, id, errors) {
  const pattern = new RegExp(
    `<script[^>]*id="${id}"[^>]*>([\\s\\S]*?)<\\/script>`,
    "i",
  );
  const match = html.match(pattern);
  if (!match) {
    errors.push(`HTML 缺少 ${id}`);
    return null;
  }
  try {
    return JSON.parse(match[1]);
  } catch (error) {
    errors.push(`${id} 不是合法 JSON：${error.message}`);
    return null;
  }
}

function validateModel(model, html = null) {
  const errors = [];
  const summary = {
    lanes_total: 0,
    nodes_total: 0,
    edges_total: 0,
    flows_total: 0,
    pending_total: 0,
    open_questions_total: 0,
    dom_missing_total: 0,
    dom_extra_total: 0,
  };

  if (!isObject(model)) {
    return { ok: false, errors: ["model 必须是对象"], summary, model_hash: "" };
  }

  collectForbiddenKeys(model, "model", errors);
  if (model.schema_version !== "2.0") errors.push("model.schema_version 必须为 2.0");
  requireString(model.title, "model.title", errors);
  requireString(model.scope, "model.scope", errors);
  requireString(model.start_condition, "model.start_condition", errors);
  if (requireArray(model.end_conditions, "model.end_conditions", errors) && model.end_conditions.length === 0) {
    errors.push("model.end_conditions 至少包含一项");
  } else {
    asArray(model.end_conditions).forEach((item, index) => {
      requireString(item, `model.end_conditions[${index}]`, errors);
    });
  }

  for (const field of ["lanes", "nodes", "edges", "flows", "open_questions"]) {
    requireArray(model[field], `model.${field}`, errors);
  }

  const lanes = asArray(model.lanes);
  const nodes = asArray(model.nodes);
  const edges = asArray(model.edges);
  const flows = asArray(model.flows);
  const questions = asArray(model.open_questions);
  summary.lanes_total = lanes.length;
  summary.nodes_total = nodes.length;
  summary.edges_total = edges.length;
  summary.flows_total = flows.length;
  summary.pending_total = nodes.filter((node) => node.type === "pending").length;
  summary.open_questions_total = questions.length;

  for (const [name, values] of [
    ["lanes", lanes],
    ["nodes", nodes],
    ["edges", edges],
    ["flows", flows],
    ["open_questions", questions],
  ]) {
    const duplicates = duplicateValues(values.map((item) => item?.id).filter(Boolean));
    if (duplicates.length) errors.push(`${name} ID 重复：${duplicates.join(", ")}`);
  }

  const laneById = new Map(lanes.map((item) => [item.id, item]));
  const nodeById = new Map(nodes.map((item) => [item.id, item]));
  const edgeById = new Map(edges.map((item) => [item.id, item]));
  const flowById = new Map(flows.map((item) => [item.id, item]));

  for (const [index, lane] of lanes.entries()) {
    const field = `lanes[${index}]`;
    requireString(lane.id, `${field}.id`, errors);
    requireString(lane.name, `${field}.name`, errors);
    requireString(lane.responsibility, `${field}.responsibility`, errors);
    if (!LANE_TYPES.has(lane.type)) errors.push(`${field}.type 非法`);
    if (!Number.isInteger(lane.order)) errors.push(`${field}.order 必须是整数`);
    if (lane.source_refs !== undefined) requireArray(lane.source_refs, `${field}.source_refs`, errors);
  }

  for (const [index, node] of nodes.entries()) {
    const field = `nodes[${index}]`;
    requireString(node.id, `${field}.id`, errors);
    requireString(node.label, `${field}.label`, errors);
    requireString(node.summary, `${field}.summary`, errors);
    if (!laneById.has(node.lane_id)) errors.push(`${field}.lane_id 不存在：${node.lane_id}`);
    if (!NODE_TYPES.has(node.type)) errors.push(`${field}.type 非法`);
    if (!CERTAINTIES.has(node.certainty)) errors.push(`${field}.certainty 非法`);
    requireArray(node.flow_ids, `${field}.flow_ids`, errors);
    if (asArray(node.flow_ids).length === 0) errors.push(`${field}.flow_ids 至少包含一项`);
    if (node.source_refs !== undefined) requireArray(node.source_refs, `${field}.source_refs`, errors);
  }

  for (const [index, edge] of edges.entries()) {
    const field = `edges[${index}]`;
    requireString(edge.id, `${field}.id`, errors);
    if (!nodeById.has(edge.from)) errors.push(`${field}.from 不存在：${edge.from}`);
    if (!nodeById.has(edge.to)) errors.push(`${field}.to 不存在：${edge.to}`);
    if (nodeById.get(edge.from)?.type === "end") {
      errors.push(`关系 ${edge.id || index} 不得从 end 节点 ${edge.from} 发出`);
    }
    if (!EDGE_TYPES.has(edge.type)) errors.push(`${field}.type 非法`);
    if (!CERTAINTIES.has(edge.certainty)) errors.push(`${field}.certainty 非法`);
    if (edge.type === "conditional" && (typeof edge.label !== "string" || !edge.label.trim())) {
      errors.push(`条件关系 ${edge.id || index} 必须具有标签`);
    } else {
      requireString(edge.label, `${field}.label`, errors);
    }
    requireArray(edge.flow_ids, `${field}.flow_ids`, errors);
    if (asArray(edge.flow_ids).length === 0) errors.push(`${field}.flow_ids 至少包含一项`);
    if (edge.source_refs !== undefined) requireArray(edge.source_refs, `${field}.source_refs`, errors);
  }

  for (const [index, flow] of flows.entries()) {
    const field = `flows[${index}]`;
    requireString(flow.id, `${field}.id`, errors);
    requireString(flow.name, `${field}.name`, errors);
    if (!FLOW_TYPES.has(flow.type)) errors.push(`${field}.type 非法`);
    if (typeof flow.default_visible !== "boolean") errors.push(`${field}.default_visible 必须是布尔值`);
    requireArray(flow.node_ids, `${field}.node_ids`, errors);
    requireArray(flow.edge_ids, `${field}.edge_ids`, errors);
    for (const id of asArray(flow.node_ids)) {
      if (!nodeById.has(id)) errors.push(`${field}.node_ids 引用不存在节点：${id}`);
      else if (!asArray(nodeById.get(id).flow_ids).includes(flow.id)) {
        errors.push(`${field} 与节点 ${id} 成员关系不一致`);
      }
    }
    for (const id of asArray(flow.edge_ids)) {
      if (!edgeById.has(id)) errors.push(`${field}.edge_ids 引用不存在关系：${id}`);
      else if (!asArray(edgeById.get(id).flow_ids).includes(flow.id)) {
        errors.push(`${field} 与关系 ${id} 成员关系不一致`);
      }
    }
    for (const edgeId of asArray(flow.edge_ids)) {
      const edge = edgeById.get(edgeId);
      if (edge && (!asArray(flow.node_ids).includes(edge.from) || !asArray(flow.node_ids).includes(edge.to))) {
        errors.push(`${field} 未包含关系 ${edgeId} 的两个端点`);
      }
    }

    const flowEdges = asArray(flow.edge_ids).map((edgeId) => edgeById.get(edgeId)).filter(Boolean);
    const derivedNodeIds = [];
    const endpointPairs = new Set();
    for (const [edgeIndex, edge] of flowEdges.entries()) {
      const pair = `${edge.from}\u0000${edge.to}`;
      if (endpointPairs.has(pair)) {
        errors.push(`流程 ${flow.id} 存在重复端点：${edge.from} → ${edge.to}`);
      }
      endpointPairs.add(pair);
      if (edgeIndex === 0) {
        derivedNodeIds.push(edge.from, edge.to);
      } else {
        const previous = flowEdges[edgeIndex - 1];
        if (edge.from !== previous.to) {
          errors.push(
            `流程 ${flow.id} 关系不连续：${previous.id} 的终点 ${previous.to} 与 ${edge.id} 的起点 ${edge.from} 不一致`,
          );
        }
        derivedNodeIds.push(edge.to);
      }
    }
    if (
      flowEdges.length === asArray(flow.edge_ids).length
      && JSON.stringify(derivedNodeIds) !== JSON.stringify(asArray(flow.node_ids))
    ) {
      errors.push(`流程 ${flow.id} 的 node_ids 与有序 edge_ids 推导结果不一致`);
    }

    const interiorEnds = asArray(flow.node_ids)
      .slice(0, -1)
      .filter((nodeId) => nodeById.get(nodeId)?.type === "end");
    for (const nodeId of interiorEnds) {
      errors.push(`流程 ${flow.id} 的 end 节点 ${nodeId} 只能位于最后`);
    }

    const lastNode = nodeById.get(asArray(flow.node_ids).at(-1));
    const lastEdge = flowEdges.at(-1);
    if (flow.type === "secondary") {
      const hasExit = ["result", "end", "pending"].includes(lastNode?.type)
        || ["return", "terminate"].includes(lastEdge?.type);
      if (!hasExit) errors.push(`次流程 ${flow.id} 缺少有效出口`);
    }
    if (flow.type === "exception") {
      const hasExit = ["pending", "result", "end"].includes(lastNode?.type)
        || ["return", "terminate"].includes(lastEdge?.type);
      if (!hasExit) errors.push(`异常流程 ${flow.id} 缺少恢复、终止或待确认出口`);
    }
  }

  const mainFlows = flows.filter((flow) => flow.type === "main");
  if (mainFlows.length !== 1) errors.push("必须且只能存在一条 main 流程");
  const defaultFlows = flows.filter((flow) => flow.default_visible);
  if (defaultFlows.length !== 1 || defaultFlows[0]?.type !== "main") {
    errors.push("必须且只能将 main 流程设为默认可见");
  }
  if (mainFlows.length === 1) {
    const main = mainFlows[0];
    const first = nodeById.get(asArray(main.node_ids)[0]);
    const last = nodeById.get(asArray(main.node_ids).at(-1));
    if (first?.type !== "start") errors.push("main 流程首节点必须为 start");
    if (last?.type !== "end") errors.push("main 流程末节点必须为 end");
  }

  for (const node of nodes) {
    for (const flowId of asArray(node.flow_ids)) {
      const flow = flowById.get(flowId);
      if (!flow) errors.push(`节点 ${node.id} 引用不存在流程：${flowId}`);
      else if (!asArray(flow.node_ids).includes(node.id)) errors.push(`节点 ${node.id} 与流程 ${flowId} 成员关系不一致`);
    }
  }
  for (const edge of edges) {
    for (const flowId of asArray(edge.flow_ids)) {
      const flow = flowById.get(flowId);
      if (!flow) errors.push(`关系 ${edge.id} 引用不存在流程：${flowId}`);
      else if (!asArray(flow.edge_ids).includes(edge.id)) errors.push(`关系 ${edge.id} 与流程 ${flowId} 成员关系不一致`);
    }
  }

  const elementIds = new Set([...laneById.keys(), ...nodeById.keys(), ...edgeById.keys(), ...flowById.keys()]);
  for (const [index, question] of questions.entries()) {
    const field = `open_questions[${index}]`;
    requireString(question.id, `${field}.id`, errors);
    requireString(question.question, `${field}.question`, errors);
    requireString(question.impact, `${field}.impact`, errors);
    requireString(question.fallback, `${field}.fallback`, errors);
    if (requireArray(question.related_element_ids, `${field}.related_element_ids`, errors)) {
      for (const id of question.related_element_ids) {
        if (!elementIds.has(id)) errors.push(`${field}.related_element_ids 引用不存在元素：${id}`);
      }
    }
  }

  const modelHash = computedModelHash(model);
  if (typeof html === "string") {
    if (/__SWIMLANE_[A-Z_]+__/.test(html)) errors.push("HTML 存在未替换模板占位符");
    const embeddedModel = extractJsonScript(html, "swimlane-semantic-model", errors);
    if (embeddedModel && computedModelHash(embeddedModel) !== modelHash) errors.push("HTML 内嵌语义模型与输入模型不一致");

    for (const [label, attribute, ids] of [
      ["泳道", "data-lane-id", lanes.map((item) => item.id)],
      ["节点", "data-node-id", nodes.map((item) => item.id)],
      ["关系", "data-edge-id", edges.map((item) => item.id)],
    ]) {
      const domIds = collectDomIds(html, attribute);
      if (!sameSet(domIds, ids)) {
        const missing = ids.filter((id) => !domIds.includes(id));
        const extra = domIds.filter((id) => !ids.includes(id));
        summary.dom_missing_total += missing.length;
        summary.dom_extra_total += extra.length;
        errors.push(`DOM ${label}集合与模型不一致：缺少 ${missing.join(", ") || "无"}；多出 ${extra.join(", ") || "无"}`);
      }
    }
    const domFlows = collectDomIds(html, "data-flow-filter").filter((id) => id !== "__all__");
    if (!sameSet(domFlows, flows.map((item) => item.id))) errors.push("DOM 流程集合与模型不一致");
  }

  return {
    ok: errors.length === 0,
    errors,
    summary,
    model_hash: modelHash,
  };
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(path.resolve(filePath), "utf8").replace(/^\uFEFF/, ""));
}

function main() {
  let args = {};
  let report;
  try {
    args = parseArgs(process.argv.slice(2));
    if (!args.model) {
      throw new Error("用法：node validate-semantic-model.js --model <file> [--html <file>] [--report <file>]");
    }
    const model = readJson(args.model);
    const html = args.html ? fs.readFileSync(path.resolve(args.html), "utf8") : null;
    report = validateModel(model, html);
  } catch (error) {
    report = { ok: false, errors: [error.message], summary: {}, model_hash: "" };
  }

  if (args.report) {
    const reportPath = path.resolve(args.report);
    fs.mkdirSync(path.dirname(reportPath), { recursive: true });
    fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  }
  if (!report.ok) {
    report.errors.forEach((error) => console.error(error));
    process.exit(1);
  }
  console.log("语义模型校验通过");
  console.log(JSON.stringify(report.summary, null, 2));
}

if (require.main === module) main();

module.exports = {
  collectDomIds,
  computedModelHash,
  parseArgs,
  validateModel,
};
