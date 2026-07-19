"use strict";

const fs = require("fs");
const path = require("path");
const {
  computedModelHash,
  parseArgs,
  validateModel,
} = require("./validate-solution-swimlane");

const NODE_WIDTH = 180;
const COLUMN_GAP = 88;
const HEADER_WIDTH = 168;
const TOP_PADDING = 64;
const LANE_PADDING = 14;
const SLOT_GAP = 14;
const NODE_X_OFFSET = 28;
const TRAILING_SPACE = 64;
const EDGE_LABEL_WIDTH = 80;
const EDGE_LABEL_HEIGHT = 32;
const RETURN_ROUTE_TOP_GAP = 48;
const RETURN_ROUTE_BOTTOM_GAP = 48;
const RETURN_ROUTE_CHANNEL_GAP = 10;

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("\n", " ");
}

function jsonForScript(value) {
  return JSON.stringify(value).replaceAll("<", "\\u003c").replaceAll(">", "\\u003e");
}

function estimateNodeHeight(node) {
  const labelLines = Math.max(1, Math.ceil([...node.label].length / 10));
  const summaryLines = Math.max(1, Math.ceil([...node.summary].length / 18));
  return Math.max(84, 26 + labelLines * 19 + summaryLines * 16);
}

function computeRanks(model) {
  const ranks = new Map();
  const orderedFlows = [...model.flows].sort((a, b) => {
    const weight = { main: 0, secondary: 1, exception: 2 };
    return weight[a.flow_type] - weight[b.flow_type] || a.id.localeCompare(b.id);
  });
  let tail = 0;
  for (const flow of orderedFlows) {
    let cursor = flow.node_ids
      .map((id) => ranks.get(id))
      .find((rank) => Number.isInteger(rank));
    if (!Number.isInteger(cursor)) cursor = tail;
    for (const nodeId of flow.node_ids) {
      if (!ranks.has(nodeId)) ranks.set(nodeId, cursor);
      cursor = Math.max(cursor + 1, ranks.get(nodeId) + 1);
    }
    tail = Math.max(tail, cursor);
  }
  for (const node of model.nodes) {
    if (!ranks.has(node.id)) {
      ranks.set(node.id, tail);
      tail += 1;
    }
  }
  return ranks;
}

function computeLayout(model) {
  const ranks = computeRanks(model);
  const lanes = [...model.lanes].sort((a, b) => a.order - b.order || a.id.localeCompare(b.id));
  const laneGroups = new Map(lanes.map((lane) => [lane.id, new Map()]));
  for (const node of model.nodes) {
    const rank = ranks.get(node.id);
    const group = laneGroups.get(node.lane_id);
    if (!group.has(rank)) group.set(rank, []);
    group.get(rank).push(node);
  }

  const laneLayouts = [];
  let laneTop = 0;
  for (const lane of lanes) {
    const groups = laneGroups.get(lane.id);
    let required = 0;
    for (const nodes of groups.values()) {
      const height = nodes
        .map(estimateNodeHeight)
        .reduce((sum, value) => sum + value, 0) + Math.max(0, nodes.length - 1) * SLOT_GAP;
      required = Math.max(required, height);
    }
    const height = Math.max(132, required + LANE_PADDING * 2);
    laneLayouts.push({ ...lane, y: laneTop, height });
    laneTop += height;
  }

  const laneById = new Map(laneLayouts.map((lane) => [lane.id, lane]));
  const nodeLayouts = new Map();
  for (const lane of laneLayouts) {
    const groups = laneGroups.get(lane.id);
    for (const [rank, nodes] of groups.entries()) {
      let y = lane.y + LANE_PADDING;
      for (const node of nodes.sort((a, b) => a.id.localeCompare(b.id))) {
        const height = estimateNodeHeight(node);
        nodeLayouts.set(node.id, {
          ...node,
          rank,
          x: HEADER_WIDTH + NODE_X_OFFSET + rank * (NODE_WIDTH + COLUMN_GAP),
          y,
          width: NODE_WIDTH,
          height,
        });
        y += height + SLOT_GAP;
      }
    }
  }

  const maxRank = Math.max(0, ...ranks.values());
  const width = HEADER_WIDTH + TRAILING_SPACE + (maxRank + 1) * (NODE_WIDTH + COLUMN_GAP);
  const backwardEdgeCount = model.edges.filter((edge) => (
    ranks.get(edge.to) <= ranks.get(edge.from)
  )).length;
  const returnRouteHeight = backwardEdgeCount
    ? RETURN_ROUTE_TOP_GAP + RETURN_ROUTE_BOTTOM_GAP
      + Math.max(0, backwardEdgeCount - 1) * RETURN_ROUTE_CHANNEL_GAP
    : TOP_PADDING;
  const height = laneTop + returnRouteHeight;
  return {
    width,
    height,
    lanes: laneLayouts,
    laneById,
    nodes: nodeLayouts,
    laneBottom: laneTop,
    returnRouteStartY: laneTop + RETURN_ROUTE_TOP_GAP,
  };
}

function flowNames(model, ids) {
  const map = new Map(model.flows.map((flow) => [flow.id, flow.name]));
  return ids.map((id) => map.get(id)).filter(Boolean).join("、");
}

function flowTypes(model, ids) {
  const typeById = new Map(model.flows.map((flow) => [flow.id, flow.flow_type]));
  const weight = { main: 0, secondary: 1, exception: 2 };
  return [...new Set(ids.map((id) => typeById.get(id)).filter(Boolean))]
    .sort((a, b) => weight[a] - weight[b]);
}

function primaryFlowType(model, ids) {
  return flowTypes(model, ids)[0] || "secondary";
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

function rectanglesOverlap(left, right) {
  const padding = 1;
  return (
    left.x + padding < right.x + right.width
    && left.x + left.width > right.x + padding
    && left.y + padding < right.y + right.height
    && left.y + left.height > right.y + padding
  );
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

function createEdgeRoute(edge, layout, offset, returnOrder) {
  const source = layout.nodes.get(edge.from);
  const target = layout.nodes.get(edge.to);
  const sourceLane = layout.laneById.get(source.lane_id);
  const targetLane = layout.laneById.get(target.lane_id);
  const sourceCenterY = source.y + source.height / 2;
  const targetCenterY = target.y + target.height / 2;
  let d;
  let labelX;
  let labelY;

  if (target.x > source.x && source.lane_id === target.lane_id) {
    const startX = source.x + source.width;
    const endX = target.x;
    const sourceBendX = startX + 6;
    const targetBendX = endX - 6;
    const routeY = Math.round((sourceCenterY + targetCenterY) / 2 + offset);
    d = `M ${startX} ${sourceCenterY} H ${sourceBendX} V ${routeY} H ${targetBendX} V ${targetCenterY} H ${endX}`;
    labelX = Math.round((startX + endX) / 2) - EDGE_LABEL_WIDTH / 2;
    labelY = routeY - EDGE_LABEL_HEIGHT - 2;
  } else if (target.x > source.x) {
    const startX = source.x + source.width;
    const endX = target.x;
    const sourceBendX = startX + 6;
    const targetBendX = endX - 6;
    const sourceTrackY = sourceCenterY + offset;
    const targetTrackY = targetCenterY + offset;
    const sourceCorridor = startX + COLUMN_GAP / 2 + offset;
    const targetCorridor = endX - COLUMN_GAP / 2 + offset;
    const movingDown = targetLane.y > sourceLane.y;
    const laneBoundary = movingDown ? sourceLane.y + sourceLane.height : sourceLane.y;
    const routeY = laneBoundary + offset / 2;
    d = `M ${startX} ${sourceCenterY} H ${sourceBendX} V ${sourceTrackY} H ${sourceCorridor} V ${routeY} H ${targetCorridor} V ${targetTrackY} H ${targetBendX} V ${targetCenterY} H ${endX}`;
    labelX = endX - COLUMN_GAP / 2 - EDGE_LABEL_WIDTH / 2;
    labelY = targetCenterY - EDGE_LABEL_HEIGHT / 2;
  } else {
    const startX = source.x;
    const endX = target.x + target.width;
    const sourceBendX = startX - 6;
    const targetBendX = endX + 6;
    const sourceTrackY = sourceCenterY + offset;
    const targetTrackY = targetCenterY + offset;
    const routeY = layout.returnRouteStartY + returnOrder * RETURN_ROUTE_CHANNEL_GAP;
    const leftX = Math.max(HEADER_WIDTH + 4, startX - COLUMN_GAP / 2 + offset);
    const rightX = endX + COLUMN_GAP / 2 + offset;
    d = `M ${startX} ${sourceCenterY} H ${sourceBendX} V ${sourceTrackY} H ${leftX} V ${routeY} H ${rightX} V ${targetTrackY} H ${targetBendX} V ${targetCenterY} H ${endX}`;
    labelX = Math.round((leftX + rightX) / 2) - EDGE_LABEL_WIDTH / 2;
    labelY = routeY - EDGE_LABEL_HEIGHT - 2;
  }

  return { d, labelX, labelY, offset };
}

function buildEdgeRoutes(model, layout) {
  const offsets = [0, -6, 6, -12, 12, -18, 18, -24, 24, -30, 30, -36, 36];
  const labelShifts = [0, -40, 40, -80, 80, -120, 120, -160, 160, -200, 200];
  const nodeRects = [...layout.nodes.values()].map((node) => ({
    id: node.id,
    x: node.x,
    y: node.y,
    width: node.width,
    height: node.height,
  }));
  const backwardEdges = model.edges.filter((edge) => (
    layout.nodes.get(edge.to).x <= layout.nodes.get(edge.from).x
  ));
  const returnOrderById = new Map(backwardEdges.map((edge, index) => [edge.id, index]));
  const assignedRoutes = [];
  const assignedLabels = [];
  const routeByEdgeId = new Map();

  for (const edge of model.edges) {
    const returnOrder = returnOrderById.get(edge.id) || 0;
    const isBackward = returnOrderById.has(edge.id);
    let selectedRoute = null;
    for (const offset of offsets) {
      const candidate = createEdgeRoute(edge, layout, offset, returnOrder);
      const segments = parsePathSegments(candidate.d);
      const crossesNode = nodeRects.some((rect) => (
        rect.id !== edge.from
        && rect.id !== edge.to
        && segments.some((segment) => segmentIntersectsRect(segment, rect))
      ));
      if (crossesNode) continue;
      const sharesLongSegment = assignedRoutes.some((assigned) => {
        const sharesEndpoint = [edge.from, edge.to].some((id) => (
          id === assigned.from || id === assigned.to
        ));
        if (sharesEndpoint) return false;
        return segments.some((segment) => (
          assigned.segments.some((other) => overlappingSegmentLength(segment, other) > 8)
        ));
      });
      if (sharesLongSegment) continue;
      selectedRoute = candidate;
      selectedRoute.segments = segments;
      break;
    }
    if (!selectedRoute) {
      selectedRoute = createEdgeRoute(edge, layout, offsets[offsets.length - 1], returnOrder);
      selectedRoute.segments = parsePathSegments(selectedRoute.d);
    }

    const baseLabel = {
      x: selectedRoute.labelX,
      y: selectedRoute.labelY,
      width: EDGE_LABEL_WIDTH,
      height: EDGE_LABEL_HEIGHT,
    };
    let selectedLabel = null;
    const labelXShifts = isBackward ? [0, -60, 60, -120, 120, -180, 180] : [0];
    for (const xShift of labelXShifts) {
      for (const yShift of labelShifts) {
        const candidate = { ...baseLabel, x: baseLabel.x + xShift, y: baseLabel.y + yShift };
        if (candidate.x < 2 || candidate.x + candidate.width > layout.width - 2) continue;
        if (candidate.y < 2 || candidate.y + candidate.height > layout.height - 2) continue;
        if (nodeRects.some((rect) => rectanglesOverlap(candidate, rect))) continue;
        if (assignedLabels.some((rect) => rectanglesOverlap(candidate, rect))) continue;
        selectedLabel = candidate;
        break;
      }
      if (selectedLabel) break;
    }
    selectedRoute.labelX = selectedLabel?.x ?? baseLabel.x;
    selectedRoute.labelY = selectedLabel?.y ?? baseLabel.y;
    selectedRoute.from = edge.from;
    selectedRoute.to = edge.to;
    assignedRoutes.push(selectedRoute);
    assignedLabels.push(selectedLabel || baseLabel);
    routeByEdgeId.set(edge.id, selectedRoute);
  }
  return routeByEdgeId;
}

function renderNode(node, model) {
  const typeLabels = {
    action: "角色任务",
    system_process: "系统处理",
    decision: "条件判断",
    result: "业务结果",
  };
  const types = flowTypes(model, node.flow_ids);
  const primaryType = primaryFlowType(model, node.flow_ids);
  return `
    <g class="swim-node node-${node.node_type} flow-primary-${primaryType}" data-node-id="${escapeAttr(node.id)}"
       data-flow-ids="${escapeAttr(node.flow_ids.join(","))}" data-flow-types="${escapeAttr(types.join(","))}"
       data-primary-flow-type="${escapeAttr(primaryType)}" role="button" tabindex="0"
       data-node-label="${escapeAttr(node.label)}" data-node-summary="${escapeAttr(node.summary)}"
       data-flow-names="${escapeAttr(flowNames(model, node.flow_ids))}"
       data-source-count="${node.source_item_ids.length}" data-x="${node.x}" data-y="${node.y}"
       data-width="${node.width}" data-height="${node.height}" aria-label="${escapeAttr(node.label)}">
      <rect x="${node.x}" y="${node.y}" width="${node.width}" height="${node.height}" rx="10"></rect>
      <foreignObject x="${node.x + 9}" y="${node.y + 8}" width="${node.width - 18}" height="${node.height - 16}">
        <div xmlns="http://www.w3.org/1999/xhtml" class="node-copy">
          <span class="node-kind">${typeLabels[node.node_type]}</span>
          <strong>${escapeHtml(node.label)}</strong>
          <span>${escapeHtml(node.summary)}</span>
        </div>
      </foreignObject>
    </g>`;
}

function renderEdge(edge, route, model) {
  const types = flowTypes(model, edge.flow_ids);
  const primaryType = primaryFlowType(model, edge.flow_ids);
  return `
    <g class="swim-edge edge-${edge.edge_type} flow-primary-${primaryType}" data-edge-id="${escapeAttr(edge.id)}"
       data-flow-ids="${escapeAttr(edge.flow_ids.join(","))}" data-flow-types="${escapeAttr(types.join(","))}"
       data-primary-flow-type="${escapeAttr(primaryType)}" data-route-channel="${route.offset}"
       role="button" tabindex="0" aria-label="${escapeAttr(edge.label)}">
      <path class="edge-line" d="${route.d}" marker-end="url(#arrow-flow-${primaryType})"></path>
      <path class="edge-hit" d="${route.d}"></path>
      <foreignObject data-edge-label-for="${escapeAttr(edge.id)}" data-x="${route.labelX}" data-y="${route.labelY}"
        data-width="${EDGE_LABEL_WIDTH}" data-height="${EDGE_LABEL_HEIGHT}"
        x="${route.labelX}" y="${route.labelY}" width="${EDGE_LABEL_WIDTH}" height="${EDGE_LABEL_HEIGHT}">
        <div xmlns="http://www.w3.org/1999/xhtml" class="edge-label">${escapeHtml(edge.label)}</div>
      </foreignObject>
    </g>`;
}

function renderSvg(model, layout) {
  const laneFills = { human: "#f7fbff", team: "#fffaf2", system: "#f3faf7" };
  const lanes = layout.lanes.map((lane, index) => `
    <g class="swim-lane lane-${lane.lane_type}" data-lane-id="${escapeAttr(lane.id)}"
       data-y="${lane.y}" data-height="${lane.height}">
      <rect x="0" y="${lane.y}" width="${layout.width}" height="${lane.height}" fill="${laneFills[lane.lane_type]}"></rect>
      <line x1="0" x2="${layout.width}" y1="${lane.y + lane.height}" y2="${lane.y + lane.height}"></line>
      <rect class="lane-head" x="0" y="${lane.y}" width="${HEADER_WIDTH}" height="${lane.height}"></rect>
      <text class="lane-order" x="18" y="${lane.y + 24}">${String(index + 1).padStart(2, "0")}</text>
      <foreignObject x="16" y="${lane.y + 32}" width="${HEADER_WIDTH - 28}" height="${lane.height - 38}">
        <div xmlns="http://www.w3.org/1999/xhtml" class="lane-title">
          <strong>${escapeHtml(lane.name)}</strong>
          <span>${lane.lane_type === "system" ? "系统自动处理" : "参与方职责"}</span>
        </div>
      </foreignObject>
    </g>`).join("");
  const edgeRoutes = buildEdgeRoutes(model, layout);
  const edges = model.edges.map((edge) => renderEdge(edge, edgeRoutes.get(edge.id), model)).join("");
  const nodes = model.nodes.map((node) => renderNode(layout.nodes.get(node.id), model)).join("");

  return `<svg id="swimlane-svg" xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 ${layout.width} ${layout.height}" width="${layout.width}" height="${layout.height}"
    data-base-width="${layout.width}" data-base-height="${layout.height}" role="img"
    aria-labelledby="svg-title svg-desc">
    <title id="svg-title">${escapeHtml(model.title)}</title>
    <desc id="svg-desc">${escapeHtml(model.subtitle)}。严格横向泳道，流程从左到右。</desc>
    <style>
      .swim-lane > line { stroke: #c8d3e1; stroke-width: 1; }
      .lane-head { fill: rgba(255,255,255,.8); stroke: #aab9ca; }
      .lane-order { fill: #8a9bad; font: 700 10px ui-monospace, monospace; letter-spacing: .08em; }
      .lane-title { display:flex; height:100%; flex-direction:column; justify-content:center; color:#17304f; font:12px/1.35 "Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }
      .lane-title strong { font-size:15px; line-height:1.3; }
      .lane-title span { margin-top:3px; color:#6c7b8f; font-size:10px; }
      .swim-node { cursor:pointer; transition:opacity .18s ease, filter .18s ease; }
      .swim-node > rect { fill:#fff; stroke-width:2.2; filter:drop-shadow(0 3px 6px rgba(28,52,84,.11)); }
      .swim-node:focus > rect, .swim-node:hover > rect { stroke-width:2.6; filter:drop-shadow(0 6px 10px rgba(28,52,84,.18)); }
      .flow-primary-main > rect { stroke:#165dff; fill:#eef4ff; }
      .flow-primary-secondary > rect { stroke:#0b8f78; fill:#ecfaf6; }
      .flow-primary-exception > rect { stroke:#d33e50; fill:#fff0f2; }
      body[data-active-flow-type="main"] .swim-node:not(.is-muted) > rect { stroke:#165dff; fill:#eef4ff; }
      body[data-active-flow-type="secondary"] .swim-node:not(.is-muted) > rect { stroke:#0b8f78; fill:#ecfaf6; }
      body[data-active-flow-type="exception"] .swim-node:not(.is-muted) > rect { stroke:#d33e50; fill:#fff0f2; }
      .node-copy { display:flex; width:100%; height:100%; flex-direction:column; justify-content:center; overflow-wrap:anywhere; color:#17304f; font:12px/1.32 "Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }
      .node-copy strong { margin:3px 0 2px; font-size:14px; line-height:1.28; }
      .node-copy > span:last-child { color:#617186; }
      .node-kind { align-self:flex-start; padding:1px 6px; border-radius:999px; color:#52657b; background:#eef3f8; font-size:9px; line-height:1.35; letter-spacing:.03em; }
      .flow-primary-main .node-kind { color:#124dcc; background:#dce8ff; }
      .flow-primary-secondary .node-kind { color:#08715f; background:#d7f3eb; }
      .flow-primary-exception .node-kind { color:#ad2738; background:#ffe0e4; }
      .swim-edge { cursor:pointer; transition:opacity .18s ease; }
      .swim-edge foreignObject { transition:opacity .18s ease; }
      .swim-edge .edge-line { fill:none; stroke:#425871; stroke-width:1.8; }
      .flow-primary-main .edge-line { stroke:#165dff; marker-end:url(#arrow-flow-main); }
      .flow-primary-secondary .edge-line { stroke:#0b8f78; marker-end:url(#arrow-flow-secondary); }
      .flow-primary-exception .edge-line { stroke:#d33e50; marker-end:url(#arrow-flow-exception); }
      body[data-active-flow-type="main"] .swim-edge:not(.is-muted) .edge-line { stroke:#165dff; marker-end:url(#arrow-flow-main); }
      body[data-active-flow-type="secondary"] .swim-edge:not(.is-muted) .edge-line { stroke:#0b8f78; marker-end:url(#arrow-flow-secondary); }
      body[data-active-flow-type="exception"] .swim-edge:not(.is-muted) .edge-line { stroke:#d33e50; marker-end:url(#arrow-flow-exception); }
      .edge-conditional .edge-line { stroke-dasharray:7 5; }
      .edge-return .edge-line { stroke-dasharray:3 5; }
      .edge-exception .edge-line { stroke-dasharray:9 5; }
      .swim-edge .edge-hit { fill:none; stroke:transparent !important; stroke-width:12; stroke-dasharray:none !important; marker-end:none !important; pointer-events:stroke; }
      body[data-active-flow-type="all"] .swim-edge { opacity:.36; }
      body[data-active-flow-type="all"] .swim-edge.flow-primary-main { opacity:.88; }
      body[data-active-flow-type="all"] .swim-edge foreignObject { opacity:0; pointer-events:none; }
      body[data-active-flow-type="all"] .swim-edge.flow-primary-main foreignObject { opacity:1; }
      body[data-active-flow-type="all"] .is-hover-focus { opacity:1; }
      body[data-active-flow-type="all"] .swim-edge.is-hover-focus foreignObject { opacity:1; }
      body[data-active-flow-type="all"] .is-hover-muted { opacity:.025; }
      .edge-label { box-sizing:border-box; display:flex; width:100%; height:100%; align-items:center; justify-content:center; padding:2px 5px; border:1px solid #d6dee8; border-radius:6px; color:#334a63; background:rgba(255,255,255,.96); font:10px/1.2 "Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; text-align:center; overflow-wrap:anywhere; }
      .is-muted { opacity:.035; }
      .swim-node.is-muted { filter:saturate(.2); }
    </style>
    <defs>
      <marker id="arrow-flow-main" markerWidth="8" markerHeight="8" refX="7.5" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,4 L0,8 z" fill="#165dff"></path></marker>
      <marker id="arrow-flow-secondary" markerWidth="8" markerHeight="8" refX="7.5" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,4 L0,8 z" fill="#0b8f78"></path></marker>
      <marker id="arrow-flow-exception" markerWidth="8" markerHeight="8" refX="7.5" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,4 L0,8 z" fill="#d33e50"></path></marker>
    </defs>
    ${lanes}
    ${edges}
    ${nodes}
  </svg>`;
}

function renderFlowButtons(model) {
  return model.flows.map((flow) => {
    const selected = flow.default_visible ? " is-selected" : "";
    return `<button class="control flow-filter${selected}" type="button" data-flow-filter="${escapeAttr(flow.id)}" data-flow-type="${escapeAttr(flow.flow_type)}">${escapeHtml(flow.name)}</button>`;
  }).join("\n");
}

function renderQuestions(model) {
  if (!model.open_questions.length) return "<p>当前正式蓝图没有需要在图中保留的开放问题。</p>";
  const items = model.open_questions.map((item) => (
    `<li><strong>${escapeHtml(item.question)}</strong><br><span>${escapeHtml(item.impact)}</span></li>`
  )).join("");
  return `<ul class="question-list">${items}</ul>`;
}

function renderMetrics(report) {
  const metrics = [
    ["源项", report.summary.source_items_total],
    ["必画节点", report.summary.required_nodes_total],
    ["必画关系", report.summary.required_edges_total],
    ["阻断项", report.summary.blocked_total],
  ];
  return metrics.map(([label, value]) => (
    `<div class="metric"><strong>${Number(value) || 0}</strong><span>${escapeHtml(label)}</span></div>`
  )).join("");
}

function replaceRequired(template, marker, value) {
  if (!template.includes(marker)) throw new Error(`模板缺少占位符：${marker}`);
  return template.replaceAll(marker, value);
}

function buildHtml(inventory, model, template) {
  const modelReport = validateModel(inventory, model);
  if (!modelReport.ok) {
    throw new Error(`模型校验失败：\n${modelReport.errors.join("\n")}`);
  }
  const layout = computeLayout(model);
  const replacements = {
    "__SWIMLANE_TITLE__": escapeHtml(model.title),
    "__SWIMLANE_SUBTITLE__": escapeHtml(model.subtitle),
    "__SWIMLANE_SOURCE_HASH__": inventory.source_hash,
    "__SWIMLANE_SOURCE_HASH_SHORT__": inventory.source_hash.slice(0, 12),
    "__SWIMLANE_MODEL_HASH__": modelReport.model_hash,
    "__SWIMLANE_MODEL_HASH_SHORT__": modelReport.model_hash.slice(0, 12),
    "__SWIMLANE_FLOW_BUTTONS__": renderFlowButtons(model),
    "__SWIMLANE_SVG__": renderSvg(model, layout),
    "__SWIMLANE_QUESTIONS__": renderQuestions(model),
    "__SWIMLANE_VALIDATION_METRICS__": renderMetrics(modelReport),
    "__SWIMLANE_INVENTORY_JSON__": jsonForScript(inventory),
    "__SWIMLANE_MODEL_JSON__": jsonForScript(model),
    "__SWIMLANE_REPORT_JSON__": jsonForScript(modelReport),
  };
  let html = template;
  for (const [marker, value] of Object.entries(replacements)) {
    html = replaceRequired(html, marker, value);
  }
  const htmlReport = validateModel(inventory, model, html);
  if (!htmlReport.ok) {
    throw new Error(`HTML 校验失败：\n${htmlReport.errors.join("\n")}`);
  }
  return { html, report: htmlReport, layout };
}

function commitAtomically(outputPath, html) {
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  const tempPath = `${outputPath}.${process.pid}.tmp`;
  const backupPath = `${outputPath}.${process.pid}.bak`;
  fs.writeFileSync(tempPath, html, "utf8");
  const existed = fs.existsSync(outputPath);
  try {
    if (existed) fs.renameSync(outputPath, backupPath);
    fs.renameSync(tempPath, outputPath);
    if (existed) fs.unlinkSync(backupPath);
  } catch (error) {
    if (fs.existsSync(tempPath)) fs.unlinkSync(tempPath);
    if (fs.existsSync(backupPath) && !fs.existsSync(outputPath)) {
      fs.renameSync(backupPath, outputPath);
    }
    throw error;
  }
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(path.resolve(filePath), "utf8").replace(/^\uFEFF/, ""));
}

function main() {
  try {
    const args = parseArgs(process.argv.slice(2));
    if (!args.inventory || !args.model || !args.template || !args.out) {
      throw new Error(
        "用法：node render-solution-swimlane.js --inventory <file> --model <file> --template <file> --out <file>",
      );
    }
    const inventory = readJson(args.inventory);
    const model = readJson(args.model);
    const template = fs.readFileSync(path.resolve(args.template), "utf8");
    const result = buildHtml(inventory, model, template);
    const outputPath = path.resolve(args.out);
    commitAtomically(outputPath, result.html);
    console.log(`方案协同图已生成：${outputPath}`);
    console.log(`画布：${result.layout.width} × ${result.layout.height}`);
    console.log(`模型哈希：${computedModelHash(model)}`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (require.main === module) main();

module.exports = {
  buildHtml,
  commitAtomically,
  computeLayout,
  renderSvg,
};
