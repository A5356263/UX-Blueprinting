"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ALLOWED_LANE_TYPES = new Set(["human", "team", "system"]);
const ALLOWED_NODE_TYPES = new Set(["action", "system_process", "decision", "result"]);
const ALLOWED_EDGE_TYPES = new Set(["normal", "conditional", "return", "exception"]);
const ALLOWED_FLOW_TYPES = new Set(["main", "secondary", "exception"]);
const ALLOWED_DISPOSITIONS = new Set([
  "rendered",
  "merged",
  "detail",
  "excluded_by_rule",
  "blocked",
]);
const ALLOWED_RULE_IDS = new Set([
  "MERGE_DUPLICATE_EVIDENCE",
  "DETAIL_NODE_CONTEXT",
  "DETAIL_OPEN_QUESTION",
  "EXCLUDE_PAGE_DETAIL",
  "EXCLUDE_COPY_DETAIL",
  "EXCLUDE_ANALYSIS_ONLY",
  "EXCLUDE_VISUAL_SKETCH",
  "EXCLUDE_NON_SEMANTIC",
  "EXCLUDE_DUPLICATE_CONTAINER",
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
      if (key !== "model_hash") result[key] = stableValue(value[key]);
      return result;
    }, {});
  }
  return value;
}

function stableStringify(value) {
  return JSON.stringify(stableValue(value));
}

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function computedModelHash(model) {
  return sha256(stableStringify(model));
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function unique(values) {
  return [...new Set(values)];
}

function difference(left, right) {
  const rightSet = new Set(right);
  return unique(left).filter((item) => !rightSet.has(item));
}

function sameSet(left, right) {
  return difference(left, right).length === 0 && difference(right, left).length === 0;
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

function collectDomIds(html, attribute) {
  const pattern = new RegExp(`${attribute}="([^"]+)"`, "g");
  const values = [];
  let match;
  while ((match = pattern.exec(html))) values.push(match[1]);
  return unique(values);
}

function collectDomFlowMeta(html, attribute) {
  const pattern = new RegExp(
    `<g[^>]*${attribute}="([^"]+)"[^>]*data-flow-types="([^"]*)"[^>]*data-primary-flow-type="([^"]+)"[^>]*>`,
    "g",
  );
  const values = new Map();
  let match;
  while ((match = pattern.exec(html))) {
    values.set(match[1], {
      flowTypes: match[2].split(",").filter(Boolean),
      primaryFlowType: match[3],
    });
  }
  return values;
}

function collectFlowFilterTypes(html) {
  const pattern = /<button[^>]*data-flow-filter="([^"]+)"[^>]*data-flow-type="([^"]+)"[^>]*>/g;
  const values = new Map();
  let match;
  while ((match = pattern.exec(html))) values.set(match[1], match[2]);
  return values;
}

function extractJsonScript(html, id, errors) {
  const pattern = new RegExp(
    `<script\\s+type="application/json"\\s+id="${id}">([\\s\\S]*?)<\\/script>`,
  );
  const match = html.match(pattern);
  if (!match) {
    errors.push(`HTML 缺少内嵌数据块：${id}`);
    return null;
  }
  try {
    return JSON.parse(match[1]);
  } catch (error) {
    errors.push(`HTML 数据块 ${id} 无法解析：${error.message}`);
    return null;
  }
}

function collectGeometry(html, attribute) {
  const pattern = new RegExp(
    `<g[^>]*${attribute}="([^"]+)"[^>]*data-x="([\\d.-]+)"[^>]*data-y="([\\d.-]+)"[^>]*data-width="([\\d.-]+)"[^>]*data-height="([\\d.-]+)"[^>]*>`,
    "g",
  );
  const values = new Map();
  let match;
  while ((match = pattern.exec(html))) {
    values.set(match[1], {
      x: Number(match[2]),
      y: Number(match[3]),
      width: Number(match[4]),
      height: Number(match[5]),
    });
  }
  return values;
}

function collectLaneGeometry(html) {
  const pattern = /<g[^>]*data-lane-id="([^"]+)"[^>]*data-y="([\d.-]+)"[^>]*data-height="([\d.-]+)"[^>]*>/g;
  const values = new Map();
  let match;
  while ((match = pattern.exec(html))) {
    values.set(match[1], { y: Number(match[2]), height: Number(match[3]) });
  }
  return values;
}

function collectEdgeLabelGeometry(html) {
  const pattern = /<foreignObject[^>]*data-edge-label-for="([^"]+)"[^>]*data-x="([\d.-]+)"[^>]*data-y="([\d.-]+)"[^>]*data-width="([\d.-]+)"[^>]*data-height="([\d.-]+)"[^>]*>/g;
  const values = new Map();
  let match;
  while ((match = pattern.exec(html))) {
    values.set(match[1], {
      x: Number(match[2]),
      y: Number(match[3]),
      width: Number(match[4]),
      height: Number(match[5]),
    });
  }
  return values;
}

function rectanglesOverlap(left, right) {
  const padding = 1;
  return (
    left.x + padding < right.x + right.width
    && left.x + left.width > right.x + padding
    && left.y + padding < right.y + right.height
    && left.y + left.height > right.y + padding
  );
}

function parsePathSegments(d) {
  const tokens = String(d).match(/[MHV]|-?\d+(?:\.\d+)?/g) || [];
  const segments = [];
  let index = 0;
  let x = 0;
  let y = 0;
  while (index < tokens.length) {
    const command = tokens[index++];
    if (command === "M") {
      x = Number(tokens[index++]);
      y = Number(tokens[index++]);
    } else if (command === "H") {
      const nextX = Number(tokens[index++]);
      segments.push({ x1: x, y1: y, x2: nextX, y2: y });
      x = nextX;
    } else if (command === "V") {
      const nextY = Number(tokens[index++]);
      segments.push({ x1: x, y1: y, x2: x, y2: nextY });
      y = nextY;
    }
  }
  return segments;
}

function segmentIntersectsRect(segment, rect) {
  const margin = 4;
  const left = rect.x + margin;
  const right = rect.x + rect.width - margin;
  const top = rect.y + margin;
  const bottom = rect.y + rect.height - margin;
  if (segment.y1 === segment.y2) {
    const minX = Math.min(segment.x1, segment.x2);
    const maxX = Math.max(segment.x1, segment.x2);
    return segment.y1 > top && segment.y1 < bottom && maxX > left && minX < right;
  }
  if (segment.x1 === segment.x2) {
    const minY = Math.min(segment.y1, segment.y2);
    const maxY = Math.max(segment.y1, segment.y2);
    return segment.x1 > left && segment.x1 < right && maxY > top && minY < bottom;
  }
  return false;
}

function overlappingSegmentLength(left, right) {
  if (left.y1 === left.y2 && right.y1 === right.y2 && left.y1 === right.y1) {
    return Math.max(
      0,
      Math.min(Math.max(left.x1, left.x2), Math.max(right.x1, right.x2))
        - Math.max(Math.min(left.x1, left.x2), Math.min(right.x1, right.x2)),
    );
  }
  if (left.x1 === left.x2 && right.x1 === right.x2 && left.x1 === right.x1) {
    return Math.max(
      0,
      Math.min(Math.max(left.y1, left.y2), Math.max(right.y1, right.y2))
        - Math.max(Math.min(left.y1, left.y2), Math.min(right.y1, right.y2)),
    );
  }
  return 0;
}

function collectEdgePaths(html) {
  const pattern = /<g class="swim-edge[^"]*" data-edge-id="([^"]+)"[\s\S]*?<path class="edge-line" d="([^"]+)"/g;
  const values = new Map();
  let match;
  while ((match = pattern.exec(html))) values.set(match[1], match[2]);
  return values;
}

function collectSvgBounds(html) {
  const match = html.match(
    /<svg id="swimlane-svg"[\s\S]*?data-base-width="([^"]+)" data-base-height="([^"]+)"/,
  );
  if (!match) return null;
  return { width: Number(match[1]), height: Number(match[2]) };
}

function validateElementSources(elements, name, inventoryIds, coverageById, mappedKey, errors) {
  for (const [index, element] of elements.entries()) {
    const field = `${name}[${index}]`;
    requireString(element.id, `${field}.id`, errors);
    if (!requireArray(element.source_item_ids, `${field}.source_item_ids`, errors)) continue;
    if (element.source_item_ids.length === 0) errors.push(`${field}.source_item_ids 不得为空`);
    for (const sourceId of element.source_item_ids) {
      if (!inventoryIds.has(sourceId)) errors.push(`${field} 引用不存在的源项：${sourceId}`);
      const coverage = coverageById.get(sourceId);
      if (coverage && !asArray(coverage[mappedKey]).includes(element.id)) {
        errors.push(`${field} 与覆盖记录 ${sourceId}.${mappedKey} 不是双向映射`);
      }
    }
  }
}

function validateFlowReachability(flow, nodeById, edgeById, errors) {
  if (!flow.node_ids.length) {
    errors.push(`流程 ${flow.id} 没有节点`);
    return;
  }
  const graph = new Map(flow.node_ids.map((id) => [id, []]));
  for (const edgeId of flow.edge_ids) {
    const edge = edgeById.get(edgeId);
    if (!edge) continue;
    if (!graph.has(edge.from) || !graph.has(edge.to)) {
      errors.push(`流程 ${flow.id} 的关系 ${edgeId} 端点未同时属于该流程`);
      continue;
    }
    graph.get(edge.from).push(edge.to);
  }
  const reached = new Set([flow.node_ids[0]]);
  const queue = [flow.node_ids[0]];
  while (queue.length) {
    const current = queue.shift();
    for (const next of graph.get(current) || []) {
      if (!reached.has(next)) {
        reached.add(next);
        queue.push(next);
      }
    }
  }
  const missing = flow.node_ids.filter((id) => !reached.has(id));
  if (missing.length) errors.push(`流程 ${flow.id} 存在不可达节点：${missing.join(", ")}`);

  const hasResult = flow.node_ids.some((id) => nodeById.get(id)?.node_type === "result");
  const returnsToMain = flow.flow_type !== "main" && flow.edge_ids.some((id) => {
    const edge = edgeById.get(id);
    return edge?.edge_type === "return";
  });
  if (flow.flow_type === "main" && !hasResult) {
    errors.push(`主流程 ${flow.id} 必须包含 result 节点`);
  }
  if (flow.flow_type === "secondary" && !hasResult && !returnsToMain) {
    errors.push(`次流程 ${flow.id} 必须回接或到达 result 节点`);
  }
  if (flow.flow_type === "exception") {
    const hasExceptionEdge = flow.edge_ids.some((id) => {
      const type = edgeById.get(id)?.edge_type;
      return type === "exception" || type === "return";
    });
    if (!hasExceptionEdge) errors.push(`异常流程 ${flow.id} 必须包含 exception 或 return 关系`);
    if (!hasResult && !returnsToMain) {
      errors.push(`异常流程 ${flow.id} 必须恢复主流程或到达 result 节点`);
    }
  }
}

function validateModel(inventory, model, html = null) {
  const errors = [];
  const summary = {
    source_items_total: asArray(inventory?.items).length,
    required_lanes_total: 0,
    required_nodes_total: 0,
    required_edges_total: 0,
    required_flows_total: 0,
    covered_lanes_total: 0,
    covered_nodes_total: 0,
    covered_edges_total: 0,
    covered_flows_total: 0,
    blocked_total: 0,
    unmapped_total: 0,
    dom_missing_lanes_total: 0,
    dom_missing_nodes_total: 0,
    dom_missing_edges_total: 0,
    dom_extra_lanes_total: 0,
    dom_extra_nodes_total: 0,
    dom_extra_edges_total: 0,
    geometry_overlap_total: 0,
    geometry_out_of_lane_total: 0,
    geometry_text_risk_total: 0,
    geometry_edge_through_node_total: 0,
    geometry_edge_label_overlap_total: 0,
    geometry_edge_shared_segment_total: 0,
    geometry_edge_out_of_bounds_total: 0,
    geometry_return_margin_total: 0,
  };

  if (!isObject(inventory)) errors.push("inventory 必须是对象");
  if (!isObject(model)) errors.push("model 必须是对象");
  if (errors.length) return { ok: false, errors, summary, model_hash: "" };

  if (inventory.schema_version !== "1.0") errors.push("inventory.schema_version 必须为 1.0");
  if (model.schema_version !== "1.0") errors.push("model.schema_version 必须为 1.0");
  requireString(inventory.source_hash, "inventory.source_hash", errors);
  requireString(model.source_hash, "model.source_hash", errors);
  if (model.source_hash !== inventory.source_hash) errors.push("model.source_hash 与 inventory 不一致");
  requireString(model.title, "model.title", errors);
  requireString(model.subtitle, "model.subtitle", errors);

  const inventoryItems = asArray(inventory.items);
  const inventoryIdsArray = inventoryItems.map((item) => item.source_item_id);
  const inventoryIds = new Set(inventoryIdsArray);
  const duplicateSourceIds = duplicateValues(inventoryIdsArray);
  if (duplicateSourceIds.length) errors.push(`源清单 ID 重复：${duplicateSourceIds.join(", ")}`);
  if (inventory.source_items_total !== inventoryItems.length) {
    errors.push("inventory.source_items_total 与 items 数量不一致");
  }

  const lanes = asArray(model.lanes);
  const nodes = asArray(model.nodes);
  const edges = asArray(model.edges);
  const flows = asArray(model.flows);
  const questions = asArray(model.open_questions);
  const coverage = asArray(model.coverage_manifest);
  for (const field of ["lanes", "nodes", "edges", "flows", "open_questions", "coverage_manifest"]) {
    requireArray(model[field], `model.${field}`, errors);
  }

  const collections = [
    ["lanes", lanes],
    ["nodes", nodes],
    ["edges", edges],
    ["flows", flows],
    ["open_questions", questions],
  ];
  for (const [name, values] of collections) {
    const duplicates = duplicateValues(values.map((item) => item.id));
    if (duplicates.length) errors.push(`${name} ID 重复：${duplicates.join(", ")}`);
  }

  const laneById = new Map(lanes.map((item) => [item.id, item]));
  const nodeById = new Map(nodes.map((item) => [item.id, item]));
  const edgeById = new Map(edges.map((item) => [item.id, item]));
  const flowById = new Map(flows.map((item) => [item.id, item]));
  const coverageIds = coverage.map((item) => item.source_item_id);
  const duplicateCoverageIds = duplicateValues(coverageIds);
  if (duplicateCoverageIds.length) {
    errors.push(`覆盖记录重复：${duplicateCoverageIds.join(", ")}`);
  }
  const coverageById = new Map(coverage.map((item) => [item.source_item_id, item]));

  const missingCoverage = inventoryIdsArray.filter((id) => !coverageById.has(id));
  const extraCoverage = coverageIds.filter((id) => !inventoryIds.has(id));
  if (missingCoverage.length) errors.push(`源项缺少覆盖记录：${missingCoverage.join(", ")}`);
  if (extraCoverage.length) errors.push(`覆盖记录引用不存在源项：${extraCoverage.join(", ")}`);
  summary.unmapped_total += missingCoverage.length + extraCoverage.length;

  for (const [index, lane] of lanes.entries()) {
    if (!ALLOWED_LANE_TYPES.has(lane.lane_type)) errors.push(`lanes[${index}].lane_type 非法`);
    if (!Number.isInteger(lane.order)) errors.push(`lanes[${index}].order 必须是整数`);
    requireString(lane.name, `lanes[${index}].name`, errors);
  }
  for (const [index, node] of nodes.entries()) {
    if (!laneById.has(node.lane_id)) errors.push(`nodes[${index}].lane_id 不存在：${node.lane_id}`);
    if (!ALLOWED_NODE_TYPES.has(node.node_type)) errors.push(`nodes[${index}].node_type 非法`);
    if (node.certainty !== "confirmed") errors.push(`nodes[${index}].certainty 必须为 confirmed`);
    requireString(node.label, `nodes[${index}].label`, errors);
    requireString(node.summary, `nodes[${index}].summary`, errors);
    requireArray(node.flow_ids, `nodes[${index}].flow_ids`, errors);
  }
  for (const [index, edge] of edges.entries()) {
    if (!nodeById.has(edge.from)) errors.push(`edges[${index}].from 不存在：${edge.from}`);
    if (!nodeById.has(edge.to)) errors.push(`edges[${index}].to 不存在：${edge.to}`);
    if (!ALLOWED_EDGE_TYPES.has(edge.edge_type)) errors.push(`edges[${index}].edge_type 非法`);
    if (edge.certainty !== "confirmed") errors.push(`edges[${index}].certainty 必须为 confirmed`);
    requireString(edge.label, `edges[${index}].label`, errors);
    requireArray(edge.flow_ids, `edges[${index}].flow_ids`, errors);
  }

  validateElementSources(lanes, "lanes", inventoryIds, coverageById, "mapped_lane_ids", errors);
  validateElementSources(nodes, "nodes", inventoryIds, coverageById, "mapped_node_ids", errors);
  validateElementSources(edges, "edges", inventoryIds, coverageById, "mapped_edge_ids", errors);
  validateElementSources(flows, "flows", inventoryIds, coverageById, "mapped_flow_ids", errors);

  for (const [index, question] of questions.entries()) {
    requireString(question.question, `open_questions[${index}].question`, errors);
    requireString(question.impact, `open_questions[${index}].impact`, errors);
    if (requireArray(question.source_item_ids, `open_questions[${index}].source_item_ids`, errors)) {
      for (const sourceId of question.source_item_ids) {
        if (!inventoryIds.has(sourceId)) errors.push(`open_questions[${index}] 源项不存在：${sourceId}`);
      }
    }
  }

  const requiredByKind = { lane: [], node: [], edge: [], flow: [] };
  for (const [index, item] of coverage.entries()) {
    const field = `coverage_manifest[${index}]`;
    requireString(item.source_item_id, `${field}.source_item_id`, errors);
    requireString(item.semantic_kind, `${field}.semantic_kind`, errors);
    if (typeof item.required_in_diagram !== "boolean") {
      errors.push(`${field}.required_in_diagram 必须是布尔值`);
    }
    if (!ALLOWED_DISPOSITIONS.has(item.disposition)) errors.push(`${field}.disposition 非法`);
    for (const key of ["mapped_lane_ids", "mapped_node_ids", "mapped_edge_ids", "mapped_flow_ids"]) {
      requireArray(item[key], `${field}.${key}`, errors);
    }
    if (item.disposition === "blocked") summary.blocked_total += 1;
    if (item.required_in_diagram && !["rendered", "merged"].includes(item.disposition)) {
      errors.push(`${field} 为必画项但 disposition=${item.disposition}`);
    }
    if (item.disposition === "excluded_by_rule" && !ALLOWED_RULE_IDS.has(item.rule_id)) {
      errors.push(`${field}.rule_id 不在允许列表`);
    }
    if (item.disposition === "merged" && item.rule_id !== "MERGE_DUPLICATE_EVIDENCE") {
      errors.push(`${field} 使用 merged 时 rule_id 必须为 MERGE_DUPLICATE_EVIDENCE`);
    }

    const maps = [
      ["mapped_lane_ids", laneById],
      ["mapped_node_ids", nodeById],
      ["mapped_edge_ids", edgeById],
      ["mapped_flow_ids", flowById],
    ];
    for (const [key, map] of maps) {
      for (const id of asArray(item[key])) {
        if (!map.has(id)) errors.push(`${field}.${key} 引用不存在 ID：${id}`);
        else if (!asArray(map.get(id).source_item_ids).includes(item.source_item_id)) {
          errors.push(`${field}.${key} 与模型元素 ${id}.source_item_ids 不是双向映射`);
        }
      }
    }

    if (item.required_in_diagram && requiredByKind[item.semantic_kind]) {
      requiredByKind[item.semantic_kind].push(item.source_item_id);
      const requiredMap = {
        lane: "mapped_lane_ids",
        node: "mapped_node_ids",
        edge: "mapped_edge_ids",
        flow: "mapped_flow_ids",
      }[item.semantic_kind];
      if (asArray(item[requiredMap]).length === 0) {
        errors.push(`${field} 必画 ${item.semantic_kind} 没有映射`);
        summary.unmapped_total += 1;
      }
    }
  }

  summary.required_lanes_total = unique(requiredByKind.lane).length;
  summary.required_nodes_total = unique(requiredByKind.node).length;
  summary.required_edges_total = unique(requiredByKind.edge).length;
  summary.required_flows_total = unique(requiredByKind.flow).length;
  const coveredByKind = {
    lane: unique(lanes.flatMap((item) => asArray(item.source_item_ids))),
    node: unique(nodes.flatMap((item) => asArray(item.source_item_ids))),
    edge: unique(edges.flatMap((item) => asArray(item.source_item_ids))),
    flow: unique(flows.flatMap((item) => asArray(item.source_item_ids))),
  };
  summary.covered_lanes_total = coveredByKind.lane.length;
  summary.covered_nodes_total = coveredByKind.node.length;
  summary.covered_edges_total = coveredByKind.edge.length;
  summary.covered_flows_total = coveredByKind.flow.length;
  for (const kind of ["lane", "node", "edge", "flow"]) {
    const required = unique(requiredByKind[kind]);
    const coveredRequired = coveredByKind[kind].filter((id) => required.includes(id));
    if (!sameSet(required, coveredRequired)) {
      errors.push(`必画 ${kind} 来源集合与模型覆盖集合不相等`);
    }
  }

  const mainFlows = flows.filter((flow) => flow.flow_type === "main");
  if (mainFlows.length === 0) errors.push("必须至少存在一条 main 流程");
  const defaultFlows = flows.filter((flow) => flow.default_visible === true);
  if (defaultFlows.length !== 1) errors.push("必须且只能有一条 default_visible=true 的流程");
  if (defaultFlows[0] && defaultFlows[0].flow_type !== "main") {
    errors.push("默认流程必须是 main");
  }

  for (const [index, flow] of flows.entries()) {
    if (!ALLOWED_FLOW_TYPES.has(flow.flow_type)) errors.push(`flows[${index}].flow_type 非法`);
    requireString(flow.name, `flows[${index}].name`, errors);
    requireArray(flow.node_ids, `flows[${index}].node_ids`, errors);
    requireArray(flow.edge_ids, `flows[${index}].edge_ids`, errors);
    if (typeof flow.default_visible !== "boolean") {
      errors.push(`flows[${index}].default_visible 必须是布尔值`);
    }
    for (const nodeId of asArray(flow.node_ids)) {
      const node = nodeById.get(nodeId);
      if (!node) errors.push(`流程 ${flow.id} 引用不存在节点：${nodeId}`);
      else if (!asArray(node.flow_ids).includes(flow.id)) {
        errors.push(`流程 ${flow.id} 与节点 ${nodeId}.flow_ids 不是双向成员关系`);
      }
    }
    for (const edgeId of asArray(flow.edge_ids)) {
      const edge = edgeById.get(edgeId);
      if (!edge) errors.push(`流程 ${flow.id} 引用不存在关系：${edgeId}`);
      else if (!asArray(edge.flow_ids).includes(flow.id)) {
        errors.push(`流程 ${flow.id} 与关系 ${edgeId}.flow_ids 不是双向成员关系`);
      }
    }
    validateFlowReachability(flow, nodeById, edgeById, errors);
  }
  for (const node of nodes) {
    for (const flowId of asArray(node.flow_ids)) {
      if (!flowById.has(flowId)) errors.push(`节点 ${node.id} 引用不存在流程：${flowId}`);
      else if (!flowById.get(flowId).node_ids.includes(node.id)) {
        errors.push(`节点 ${node.id}.flow_ids 与流程 ${flowId} 不是双向成员关系`);
      }
    }
  }
  for (const edge of edges) {
    for (const flowId of asArray(edge.flow_ids)) {
      if (!flowById.has(flowId)) errors.push(`关系 ${edge.id} 引用不存在流程：${flowId}`);
      else if (!flowById.get(flowId).edge_ids.includes(edge.id)) {
        errors.push(`关系 ${edge.id}.flow_ids 与流程 ${flowId} 不是双向成员关系`);
      }
    }
  }

  const modelHash = computedModelHash(model);
  if (html !== null) {
    if (typeof html !== "string" || !html.includes("<svg")) errors.push("HTML 缺少 SVG");
    if (/<script\b[^>]*\bsrc\s*=/i.test(html)) errors.push("HTML 存在外部 script src");
    if (/<link\b[^>]*\bhref\s*=/i.test(html)) errors.push("HTML 存在外部 link href");
    if (/(?:src|href)\s*=\s*["'](?:https?:)?\/\//i.test(html)) errors.push("HTML 存在远程资源");
    if (/__SWIMLANE_[A-Z_]+__/.test(html)) errors.push("HTML 存在未替换模板占位符");
    if (!html.includes('id="export-svg"')) errors.push("HTML 缺少导出 SVG 控件");

    const embeddedInventory = extractJsonScript(html, "swimlane-source-inventory", errors);
    const embeddedModel = extractJsonScript(html, "swimlane-diagram-model", errors);
    const embeddedReport = extractJsonScript(html, "swimlane-validation-report", errors);
    if (embeddedInventory?.source_hash !== inventory.source_hash) {
      errors.push("HTML 内嵌源清单哈希不一致");
    }
    if (embeddedModel && computedModelHash(embeddedModel) !== modelHash) {
      errors.push("HTML 内嵌模型哈希不一致");
    }
    if (embeddedReport && embeddedReport.model_hash !== modelHash) {
      errors.push("HTML 内嵌校验摘要的模型哈希不一致");
    }

    const domLanes = collectDomIds(html, "data-lane-id");
    const domNodes = collectDomIds(html, "data-node-id");
    const domEdges = collectDomIds(html, "data-edge-id");
    const domFlows = collectDomIds(html, "data-flow-filter").filter((id) => id !== "__all__");
    const modelLanes = lanes.map((item) => item.id);
    const modelNodes = nodes.map((item) => item.id);
    const modelEdges = edges.map((item) => item.id);
    const modelFlows = flows.map((item) => item.id);
    summary.dom_missing_lanes_total = difference(modelLanes, domLanes).length;
    summary.dom_missing_nodes_total = difference(modelNodes, domNodes).length;
    summary.dom_missing_edges_total = difference(modelEdges, domEdges).length;
    summary.dom_extra_lanes_total = difference(domLanes, modelLanes).length;
    summary.dom_extra_nodes_total = difference(domNodes, modelNodes).length;
    summary.dom_extra_edges_total = difference(domEdges, modelEdges).length;
    if (!sameSet(modelLanes, domLanes)) errors.push("模型与 SVG DOM 的泳道集合不相等");
    if (!sameSet(modelNodes, domNodes)) errors.push("模型与 SVG DOM 的节点集合不相等");
    if (!sameSet(modelEdges, domEdges)) errors.push("模型与 SVG DOM 的关系集合不相等");
    if (!sameSet(modelFlows, domFlows)) errors.push("模型与 HTML 的流程筛选集合不相等");

    const flowTypeById = new Map(flows.map((flow) => [flow.id, flow.flow_type]));
    const flowTypeWeight = { main: 0, secondary: 1, exception: 2 };
    const expectedFlowTypes = (flowIds) => [...new Set(flowIds.map((id) => flowTypeById.get(id)).filter(Boolean))]
      .sort((left, right) => flowTypeWeight[left] - flowTypeWeight[right]);
    const domNodeFlowMeta = collectDomFlowMeta(html, "data-node-id");
    const domEdgeFlowMeta = collectDomFlowMeta(html, "data-edge-id");
    for (const node of nodes) {
      const expected = expectedFlowTypes(node.flow_ids);
      const actual = domNodeFlowMeta.get(node.id);
      if (!actual || !sameSet(expected, actual.flowTypes) || actual.primaryFlowType !== expected[0]) {
        errors.push(`节点 ${node.id} 的流程类别元数据与模型不一致`);
      }
    }
    for (const edge of edges) {
      const expected = expectedFlowTypes(edge.flow_ids);
      const actual = domEdgeFlowMeta.get(edge.id);
      if (!actual || !sameSet(expected, actual.flowTypes) || actual.primaryFlowType !== expected[0]) {
        errors.push(`关系 ${edge.id} 的流程类别元数据与模型不一致`);
      }
    }
    const flowFilterTypes = collectFlowFilterTypes(html);
    for (const flow of flows) {
      if (flowFilterTypes.get(flow.id) !== flow.flow_type) {
        errors.push(`流程 ${flow.id} 的筛选按钮类别与模型不一致`);
      }
    }
    if (flowFilterTypes.get("__all__") !== "all") errors.push("显示全部按钮缺少 all 类别");

    const allFilterIndex = html.indexOf('data-flow-filter="__all__"');
    const firstFlowFilterIndex = Math.min(
      ...flows.map((flow) => html.indexOf(`data-flow-filter="${flow.id}"`)).filter((index) => index >= 0),
    );
    if (allFilterIndex < 0 || allFilterIndex > firstFlowFilterIndex) {
      errors.push("全部流程按钮必须位于流程选择区首位");
    }
    if (!html.includes("setHoverFlowFocus") || !html.includes(".is-hover-focus")) {
      errors.push("全部视角缺少关系流程聚焦能力");
    }

    const nodeGeometry = collectGeometry(html, "data-node-id");
    const laneGeometry = collectLaneGeometry(html);
    for (let leftIndex = 0; leftIndex < nodes.length; leftIndex += 1) {
      const leftNode = nodes[leftIndex];
      const leftRect = nodeGeometry.get(leftNode.id);
      if (!leftRect) continue;
      const laneRect = laneGeometry.get(leftNode.lane_id);
      if (
        laneRect
        && (leftRect.y < laneRect.y || leftRect.y + leftRect.height > laneRect.y + laneRect.height)
      ) {
        summary.geometry_out_of_lane_total += 1;
        errors.push(`节点 ${leftNode.id} 超出泳道边界`);
      }
      const estimatedHeight = Math.max(
        84,
        26 + Math.max(1, Math.ceil([...leftNode.label].length / 10)) * 19
          + Math.max(1, Math.ceil([...leftNode.summary].length / 18)) * 16,
      );
      if (leftRect.height < estimatedHeight) {
        summary.geometry_text_risk_total += 1;
        errors.push(`节点 ${leftNode.id} 高度不足，存在文字溢出风险`);
      }
      for (let rightIndex = leftIndex + 1; rightIndex < nodes.length; rightIndex += 1) {
        const rightNode = nodes[rightIndex];
        const rightRect = nodeGeometry.get(rightNode.id);
        if (rightRect && rectanglesOverlap(leftRect, rightRect)) {
          summary.geometry_overlap_total += 1;
          errors.push(`节点重叠：${leftNode.id} 与 ${rightNode.id}`);
        }
      }
    }

    const edgePaths = collectEdgePaths(html);
    const svgBounds = collectSvgBounds(html);
    if (!sameSet(modelEdges, [...edgePaths.keys()])) {
      errors.push("模型与 SVG 可见关系路径集合不相等");
    }
    if (!svgBounds || !Number.isFinite(svgBounds.width) || !Number.isFinite(svgBounds.height)) {
      errors.push("SVG 缺少有效画布边界");
    }
    for (const edge of edges) {
      const d = edgePaths.get(edge.id);
      if (!d) continue;
      const segments = parsePathSegments(d);
      const points = segments.flatMap((segment) => [
        { x: segment.x1, y: segment.y1 },
        { x: segment.x2, y: segment.y2 },
      ]);
      if (svgBounds && points.some((point) => (
        point.x < 0 || point.x > svgBounds.width || point.y < 0 || point.y > svgBounds.height
      ))) {
        summary.geometry_edge_out_of_bounds_total += 1;
        errors.push(`关系 ${edge.id} 超出 SVG 画布边界`);
      }
      const sourceRect = nodeGeometry.get(edge.from);
      const targetRect = nodeGeometry.get(edge.to);
      if (svgBounds && sourceRect && targetRect && targetRect.x <= sourceRect.x) {
        const maxY = Math.max(...points.map((point) => point.y));
        if (maxY > svgBounds.height - 48) {
          summary.geometry_return_margin_total += 1;
          errors.push(`回流关系 ${edge.id} 距画布底部不足 48px`);
        }
      }
      for (const node of nodes) {
        if (node.id === edge.from || node.id === edge.to) continue;
        const rect = nodeGeometry.get(node.id);
        if (rect && segments.some((segment) => segmentIntersectsRect(segment, rect))) {
          summary.geometry_edge_through_node_total += 1;
          errors.push(`关系 ${edge.id} 穿过非端点节点 ${node.id}`);
          break;
        }
      }
    }

    const edgeLabelGeometry = collectEdgeLabelGeometry(html);
    const edgeLabelEntries = [...edgeLabelGeometry.entries()];
    for (let labelIndex = 0; labelIndex < edgeLabelEntries.length; labelIndex += 1) {
      const [edgeId, labelRect] = edgeLabelEntries[labelIndex];
      for (const node of nodes) {
        const nodeRect = nodeGeometry.get(node.id);
        if (nodeRect && rectanglesOverlap(labelRect, nodeRect)) {
          summary.geometry_edge_label_overlap_total += 1;
          errors.push(`关系 ${edgeId} 的标签遮挡节点 ${node.id}`);
          break;
        }
      }
      for (let otherIndex = labelIndex + 1; otherIndex < edgeLabelEntries.length; otherIndex += 1) {
        const [otherEdgeId, otherRect] = edgeLabelEntries[otherIndex];
        if (rectanglesOverlap(labelRect, otherRect)) {
          summary.geometry_edge_label_overlap_total += 1;
          errors.push(`关系标签重叠：${edgeId} 与 ${otherEdgeId}`);
        }
      }
    }

    for (let edgeIndex = 0; edgeIndex < edges.length; edgeIndex += 1) {
      const leftEdge = edges[edgeIndex];
      const leftPath = edgePaths.get(leftEdge.id);
      if (!leftPath) continue;
      const leftSegments = parsePathSegments(leftPath);
      for (let otherIndex = edgeIndex + 1; otherIndex < edges.length; otherIndex += 1) {
        const rightEdge = edges[otherIndex];
        const sharesEndpoint = [leftEdge.from, leftEdge.to].some((id) => (
          id === rightEdge.from || id === rightEdge.to
        ));
        if (sharesEndpoint) continue;
        const rightPath = edgePaths.get(rightEdge.id);
        if (!rightPath) continue;
        const rightSegments = parsePathSegments(rightPath);
        const sharedLength = Math.max(
          0,
          ...leftSegments.flatMap((leftSegment) => (
            rightSegments.map((rightSegment) => overlappingSegmentLength(leftSegment, rightSegment))
          )),
        );
        if (sharedLength > 8) {
          summary.geometry_edge_shared_segment_total += 1;
          errors.push(`关系线段重叠：${leftEdge.id} 与 ${rightEdge.id}，长度 ${sharedLength}`);
        }
      }
    }
  }

  return {
    ok: errors.length === 0,
    errors,
    summary,
    source_hash: inventory.source_hash,
    model_hash: modelHash,
  };
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(path.resolve(filePath), "utf8").replace(/^\uFEFF/, ""));
}

function main() {
  let report = null;
  let args = {};
  try {
    args = parseArgs(process.argv.slice(2));
    if (!args.inventory || !args.model) {
      throw new Error(
        "用法：node validate-solution-swimlane.js --inventory <file> --model <file> [--html <file>] [--report <file>]",
      );
    }
    const inventory = readJson(args.inventory);
    const model = readJson(args.model);
    const html = args.html ? fs.readFileSync(path.resolve(args.html), "utf8") : null;
    report = validateModel(inventory, model, html);
  } catch (error) {
    report = {
      ok: false,
      errors: [error.message],
      summary: {},
      source_hash: "",
      model_hash: "",
    };
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
  console.log("方案协同图完整性校验通过");
  console.log(JSON.stringify(report.summary, null, 2));
}

if (require.main === module) main();

module.exports = {
  collectDomIds,
  computedModelHash,
  parseArgs,
  stableStringify,
  validateModel,
};
