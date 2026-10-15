"use strict";

const fs = require("fs");
const path = require("path");
const { validateModel } = require("./validate-semantic-model");

const LANE_TYPES = new Set(["human", "team", "system"]);
const NODE_TYPES = new Set(["start", "action", "system_process", "decision", "result", "end", "pending"]);
const EDGE_TYPES = new Set(["normal", "conditional", "handoff", "exception", "return", "terminate"]);
const FLOW_TYPES = new Set(["main", "secondary", "exception"]);
const CERTAINTIES = new Set(["confirmed", "uncertain"]);

const FIELDS = {
  draft: new Set([
    "draft_version",
    "title",
    "scope",
    "start_condition",
    "end_conditions",
    "lanes",
    "nodes",
    "edges",
    "flows",
    "open_questions",
  ]),
  lane: new Set(["id", "name", "type", "order", "responsibility"]),
  node: new Set(["id", "lane_id", "label", "type", "summary", "certainty"]),
  edge: new Set(["id", "from", "to", "label", "type", "certainty"]),
  flow: new Set(["id", "name", "type", "edge_ids"]),
  question: new Set(["id", "question", "impact", "related_element_ids", "fallback"]),
};

const FORBIDDEN_DRAFT_FIELDS = new Set([
  "source_refs",
  "node_ids",
  "flow_ids",
  "default_visible",
]);

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function assertObject(value, field) {
  if (!isObject(value)) throw new Error(`${field} 必须是对象`);
}

function assertAllowedFields(value, allowed, field) {
  assertObject(value, field);
  for (const key of Object.keys(value)) {
    if (FORBIDDEN_DRAFT_FIELDS.has(key)) throw new Error(`禁止字段 ${field}.${key}`);
    if (!allowed.has(key)) throw new Error(`未知字段 ${field}.${key}`);
  }
}

function requireString(value, field) {
  if (typeof value !== "string" || !value.trim()) throw new Error(`${field} 必须是非空字符串`);
}

function requireArray(value, field) {
  if (!Array.isArray(value)) throw new Error(`${field} 必须是数组`);
  return value;
}

function requireStringArray(value, field, minimum = 0) {
  const items = requireArray(value, field);
  if (items.length < minimum) throw new Error(`${field} 至少包含 ${minimum} 项`);
  items.forEach((item, index) => requireString(item, `${field}[${index}]`));
  return items;
}

function requireEnum(value, choices, field) {
  if (!choices.has(value)) throw new Error(`${field} 非法：${value}`);
}

function requireUniqueIds(items, field) {
  const seen = new Set();
  for (const [index, item] of items.entries()) {
    requireString(item.id, `${field}[${index}].id`);
    if (seen.has(item.id)) throw new Error(`${field} ID 重复：${item.id}`);
    seen.add(item.id);
  }
  return seen;
}

function validateDraft(draft) {
  assertAllowedFields(draft, FIELDS.draft, "draft");
  if (draft.draft_version !== "1.1") throw new Error("draft.draft_version 必须为 1.1");
  requireString(draft.title, "draft.title");
  requireString(draft.scope, "draft.scope");
  requireString(draft.start_condition, "draft.start_condition");
  requireStringArray(draft.end_conditions, "draft.end_conditions", 1);

  const lanes = requireArray(draft.lanes, "draft.lanes");
  const nodes = requireArray(draft.nodes, "draft.nodes");
  const edges = requireArray(draft.edges, "draft.edges");
  const flows = requireArray(draft.flows, "draft.flows");
  const questions = requireArray(draft.open_questions, "draft.open_questions");
  if (!lanes.length) throw new Error("draft.lanes 至少包含一项");
  if (!nodes.length) throw new Error("draft.nodes 至少包含一项");
  if (!flows.length) throw new Error("draft.flows 至少包含一项");

  for (const [index, lane] of lanes.entries()) {
    const field = `draft.lanes[${index}]`;
    assertAllowedFields(lane, FIELDS.lane, field);
    requireString(lane.id, `${field}.id`);
    requireString(lane.name, `${field}.name`);
    requireEnum(lane.type, LANE_TYPES, `${field}.type`);
    if (!Number.isInteger(lane.order)) throw new Error(`${field}.order 必须是整数`);
    requireString(lane.responsibility, `${field}.responsibility`);
  }

  for (const [index, node] of nodes.entries()) {
    const field = `draft.nodes[${index}]`;
    assertAllowedFields(node, FIELDS.node, field);
    requireString(node.id, `${field}.id`);
    requireString(node.lane_id, `${field}.lane_id`);
    requireString(node.label, `${field}.label`);
    requireEnum(node.type, NODE_TYPES, `${field}.type`);
    if (node.summary !== undefined) requireString(node.summary, `${field}.summary`);
    if (node.certainty !== undefined) requireEnum(node.certainty, CERTAINTIES, `${field}.certainty`);
  }

  for (const [index, edge] of edges.entries()) {
    const field = `draft.edges[${index}]`;
    assertAllowedFields(edge, FIELDS.edge, field);
    requireString(edge.id, `${field}.id`);
    requireString(edge.from, `${field}.from`);
    requireString(edge.to, `${field}.to`);
    requireString(edge.label, `${field}.label`);
    requireEnum(edge.type, EDGE_TYPES, `${field}.type`);
    if (edge.certainty !== undefined) requireEnum(edge.certainty, CERTAINTIES, `${field}.certainty`);
  }

  for (const [index, flow] of flows.entries()) {
    const field = `draft.flows[${index}]`;
    assertAllowedFields(flow, FIELDS.flow, field);
    requireString(flow.id, `${field}.id`);
    requireString(flow.name, `${field}.name`);
    requireEnum(flow.type, FLOW_TYPES, `${field}.type`);
    requireStringArray(flow.edge_ids, `${field}.edge_ids`, 1);
  }

  for (const [index, question] of questions.entries()) {
    const field = `draft.open_questions[${index}]`;
    assertAllowedFields(question, FIELDS.question, field);
    requireString(question.id, `${field}.id`);
    requireString(question.question, `${field}.question`);
    requireString(question.impact, `${field}.impact`);
    requireStringArray(question.related_element_ids, `${field}.related_element_ids`);
    requireString(question.fallback, `${field}.fallback`);
  }

  const laneIds = requireUniqueIds(lanes, "draft.lanes");
  const nodeIds = requireUniqueIds(nodes, "draft.nodes");
  const edgeIds = requireUniqueIds(edges, "draft.edges");
  const flowIds = requireUniqueIds(flows, "draft.flows");
  requireUniqueIds(questions, "draft.open_questions");

  for (const [index, node] of nodes.entries()) {
    if (!laneIds.has(node.lane_id)) {
      throw new Error(`draft.nodes[${index}].lane_id 引用不存在泳道：${node.lane_id}`);
    }
  }
  for (const [index, edge] of edges.entries()) {
    if (!nodeIds.has(edge.from)) {
      throw new Error(`draft.edges[${index}].from 引用不存在节点：${edge.from}`);
    }
    if (!nodeIds.has(edge.to)) {
      throw new Error(`draft.edges[${index}].to 引用不存在节点：${edge.to}`);
    }
  }
  for (const [index, flow] of flows.entries()) {
    for (const edgeId of flow.edge_ids) {
      if (!edgeIds.has(edgeId)) {
        throw new Error(`draft.flows[${index}].edge_ids 引用不存在关系：${edgeId}`);
      }
    }
  }

  const elementIds = new Set([...laneIds, ...nodeIds, ...edgeIds, ...flowIds]);
  for (const [index, question] of questions.entries()) {
    for (const elementId of question.related_element_ids) {
      if (!elementIds.has(elementId)) {
        throw new Error(
          `draft.open_questions[${index}].related_element_ids 引用不存在元素：${elementId}`,
        );
      }
    }
  }
}

function deriveFlowNodes(flows, edgeById) {
  const errors = [];
  const result = new Map();
  for (const flow of flows) {
    const edges = flow.edge_ids.map((edgeId) => edgeById.get(edgeId)).filter(Boolean);
    const endpointPairs = new Set();
    const nodeIds = [];
    for (const [index, edge] of edges.entries()) {
      const pair = `${edge.from}\u0000${edge.to}`;
      if (endpointPairs.has(pair)) {
        errors.push(`流程 ${flow.id} 存在重复端点：${edge.from} → ${edge.to}`);
      }
      endpointPairs.add(pair);
      if (index === 0) {
        nodeIds.push(edge.from, edge.to);
      } else {
        const previous = edges[index - 1];
        if (edge.from !== previous.to) {
          errors.push(
            `流程 ${flow.id} 关系不连续：${previous.id} 的终点 ${previous.to} 与 ${edge.id} 的起点 ${edge.from} 不一致`,
          );
        }
        nodeIds.push(edge.to);
      }
    }
    result.set(flow.id, nodeIds);
  }
  if (errors.length) throw new Error(`草稿流程结构失败：\n${errors.join("\n")}`);
  return result;
}

function memberships(flows, key) {
  const result = new Map();
  for (const flow of flows) {
    for (const elementId of flow[key]) {
      const ids = result.get(elementId) || [];
      if (!ids.includes(flow.id)) ids.push(flow.id);
      result.set(elementId, ids);
    }
  }
  return result;
}

function normalizeDraft(draft) {
  validateDraft(draft);
  const edgeById = new Map(draft.edges.map((edge) => [edge.id, edge]));
  const flowNodeIds = deriveFlowNodes(draft.flows, edgeById);
  const normalizedFlows = draft.flows.map((flow) => ({
    id: flow.id,
    name: flow.name,
    type: flow.type,
    node_ids: flowNodeIds.get(flow.id),
    edge_ids: [...flow.edge_ids],
    default_visible: flow.type === "main",
  }));
  const nodeFlowIds = memberships(normalizedFlows, "node_ids");
  const edgeFlowIds = memberships(normalizedFlows, "edge_ids");
  const model = {
    schema_version: "2.0",
    title: draft.title,
    scope: draft.scope,
    start_condition: draft.start_condition,
    end_conditions: [...draft.end_conditions],
    lanes: draft.lanes.map((lane) => ({
      id: lane.id,
      name: lane.name,
      type: lane.type,
      order: lane.order,
      responsibility: lane.responsibility,
      source_refs: [],
    })),
    nodes: draft.nodes.map((node) => ({
      id: node.id,
      lane_id: node.lane_id,
      label: node.label,
      type: node.type,
      summary: node.summary || node.label,
      certainty: node.certainty || "confirmed",
      source_refs: [],
      flow_ids: nodeFlowIds.get(node.id) || [],
    })),
    edges: draft.edges.map((edge) => ({
      id: edge.id,
      from: edge.from,
      to: edge.to,
      label: edge.label,
      type: edge.type,
      certainty: edge.certainty || "confirmed",
      source_refs: [],
      flow_ids: edgeFlowIds.get(edge.id) || [],
    })),
    flows: normalizedFlows,
    open_questions: draft.open_questions.map((question) => ({
      id: question.id,
      question: question.question,
      impact: question.impact,
      related_element_ids: [...question.related_element_ids],
      fallback: question.fallback,
    })),
  };
  const report = validateModel(model);
  if (!report.ok) throw new Error(`规范模型校验失败：\n${report.errors.join("\n")}`);
  return model;
}

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

function assertOutputPath(outputPath) {
  const allowedRoot = path.resolve(process.cwd(), "spark-output", "solution-swimlane");
  const relative = path.relative(allowedRoot, outputPath);
  if (relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error("输出路径必须位于 spark-output/solution-swimlane/");
  }
}

function writeAtomically(outputPath, content) {
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  const temporaryPath = `${outputPath}.${process.pid}.tmp`;
  const backupPath = `${outputPath}.${process.pid}.bak`;
  const existed = fs.existsSync(outputPath);
  fs.writeFileSync(temporaryPath, content, "utf8");
  try {
    if (existed) fs.renameSync(outputPath, backupPath);
    fs.renameSync(temporaryPath, outputPath);
    if (existed) fs.unlinkSync(backupPath);
  } catch (error) {
    if (fs.existsSync(temporaryPath)) fs.unlinkSync(temporaryPath);
    if (fs.existsSync(backupPath) && !fs.existsSync(outputPath)) fs.renameSync(backupPath, outputPath);
    throw error;
  }
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(path.resolve(filePath), "utf8").replace(/^\uFEFF/, ""));
}

function main() {
  try {
    const args = parseArgs(process.argv.slice(2));
    if (!args.draft || !args.out) {
      throw new Error("用法：node normalize-semantic-model.js --draft <file> --out <file>");
    }
    const outputPath = path.resolve(args.out);
    assertOutputPath(outputPath);
    const model = normalizeDraft(readJson(args.draft));
    writeAtomically(outputPath, `${JSON.stringify(model, null, 2)}\n`);
    console.log(`语义模型已规范化：${outputPath}`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (require.main === module) main();

module.exports = {
  deriveFlowNodes,
  normalizeDraft,
  parseArgs,
  validateDraft,
  writeAtomically,
};
