const fs = require('fs');

const model = JSON.parse(fs.readFileSync('.claude/temp/swimlane/diagram-model.json', 'utf8'));
const inv = JSON.parse(fs.readFileSync('C:/Users/HP/AppData/Local/Temp/tmp.vsWfUCEjwo/source-inventory.json', 'utf8'));

// Find available detail items from coverage_manifest
const availableDetail = model.coverage_manifest.filter(c =>
  c.disposition === 'excluded_by_rule' && !c.source_item_id.includes('json-')
).map(c => c.source_item_id);

// Items for lanes (pick 3 unique ones with role references)
const laneItemIds = [];
// Find items mentioning specific roles
inv.items.forEach(item => {
  if (item.raw_text && item.raw_text.includes('权限管理员') && availableDetail.includes(item.source_item_id)) {
    if (!laneItemIds[0]) laneItemIds[0] = item.source_item_id;
  }
});
inv.items.forEach(item => {
  if (item.raw_text && item.raw_text.includes('系统') && availableDetail.includes(item.source_item_id) && !laneItemIds.includes(item.source_item_id)) {
    if (!laneItemIds[1]) laneItemIds[1] = item.source_item_id;
  }
});
inv.items.forEach(item => {
  if (item.raw_text && item.raw_text.includes('审批') && availableDetail.includes(item.source_item_id) && !laneItemIds.includes(item.source_item_id)) {
    if (!laneItemIds[2]) laneItemIds[2] = item.source_item_id;
  }
});

// Assign lane items
model.lanes.forEach((lane, i) => {
  if (laneItemIds[i]) {
    lane.source_item_ids = [laneItemIds[i]];
  } else if (availableDetail.length > i) {
    lane.source_item_ids = [availableDetail[i]];
  }
});

// Assign edge items (each edge gets a unique available item)
const usedIds = new Set(model.lanes.flatMap(l => l.source_item_ids));
let edgeIdx = 0;
model.edges.forEach(edge => {
  // Find unused item
  while (edgeIdx < availableDetail.length && usedIds.has(availableDetail[edgeIdx])) edgeIdx++;
  if (edgeIdx < availableDetail.length) {
    edge.source_item_ids = [availableDetail[edgeIdx]];
    usedIds.add(availableDetail[edgeIdx]);
    edgeIdx++;
  }
});

// Fix flow membership issues

// node-review-result should be in flow-main
const nodeReview = model.nodes.find(n => n.id === 'node-review-result');
if (nodeReview && !nodeReview.flow_ids.includes('flow-main')) nodeReview.flow_ids.push('flow-main');

// node-present-picker should be in flow-main
const nodePicker = model.nodes.find(n => n.id === 'node-present-picker');
if (nodePicker && !nodePicker.flow_ids.includes('flow-main')) nodePicker.flow_ids.push('flow-main');

// node-notify-result should be in flow-main
const nodeNotify = model.nodes.find(n => n.id === 'node-notify-result');
if (nodeNotify && !nodeNotify.flow_ids.includes('flow-main')) nodeNotify.flow_ids.push('flow-main');

// res-effective should be in flow-exception-3
const resEffect = model.nodes.find(n => n.id === 'res-effective');
if (resEffect && !resEffect.flow_ids.includes('flow-exception-3')) resEffect.flow_ids.push('flow-exception-3');

// res-not-executed should be in flow-exception-4
const resNotExec = model.nodes.find(n => n.id === 'res-not-executed');
if (resNotExec && !resNotExec.flow_ids.includes('flow-exception-4')) resNotExec.flow_ids.push('flow-exception-4');

// e-audit-effective should be in flow-exception-3
const edgeAudit = model.edges.find(e => e.id === 'e-audit-effective');
if (edgeAudit && !edgeAudit.flow_ids.includes('flow-exception-3')) edgeAudit.flow_ids.push('flow-exception-3');

// e-submit-process should be in flow-exception-5
const edgeSubmit = model.edges.find(e => e.id === 'e-submit-process');
if (edgeSubmit && !edgeSubmit.flow_ids.includes('flow-exception-5')) edgeSubmit.flow_ids.push('flow-exception-5');

// Also fix node-submit - it should be in flow-exception-3 and flow-exception-4
const nodeSubmit = model.nodes.find(n => n.id === 'node-submit');
if (nodeSubmit) {
  if (!nodeSubmit.flow_ids.includes('flow-exception-3')) nodeSubmit.flow_ids.push('flow-exception-3');
  if (!nodeSubmit.flow_ids.includes('flow-exception-4')) nodeSubmit.flow_ids.push('flow-exception-4');
}

// Add node-review-result to flow-secondary's edges
const flowSec = model.flows.find(f => f.id === 'flow-secondary');
const nodeCheckAudit = model.nodes.find(n => n.id === 'node-check-audit');
if (flowSec && nodeCheckAudit && !nodeCheckAudit.flow_ids.includes('flow-secondary')) {
  nodeCheckAudit.flow_ids.push('flow-secondary');
}

// Flow source_item_ids - flows need at least one item each
model.flows.forEach((flow, i) => {
  if (flow.source_item_ids.length === 0 && i < availableDetail.length) {
    flow.source_item_ids = [availableDetail[Math.min(availableDetail.length - 1, i + 20)]];
  }
});

// Update coverage_manifest for newly assigned items
// For each item assigned to a lane/edge/flow, update its manifest entry
const updateManifest = (itemId, laneIds, edgeIds, flowIds, nodeIds) => {
  const entry = model.coverage_manifest.find(c => c.source_item_id === itemId);
  if (entry) {
    entry.semantic_kind = 'rendered';
    entry.disposition = 'rendered';
    entry.required_in_diagram = true;
    if (laneIds) entry.mapped_lane_ids = laneIds;
    if (edgeIds) entry.mapped_edge_ids = edgeIds;
    if (flowIds) entry.mapped_flow_ids = flowIds;
    if (nodeIds) entry.mapped_node_ids = nodeIds;
  }
};

model.lanes.forEach(lane => {
  lane.source_item_ids.forEach(sid => updateManifest(sid, [lane.id], [], [], []));
});
model.edges.forEach(edge => {
  edge.source_item_ids.forEach(sid => updateManifest(sid, [], [edge.id], edge.flow_ids, []));
});
model.flows.forEach(flow => {
  flow.source_item_ids.forEach(sid => updateManifest(sid, [], [], [flow.id], []));
});

// Write patched model
fs.writeFileSync('.claude/temp/swimlane/diagram-model.json', JSON.stringify(model, null, 2));
console.log('Patched model:');
console.log('Lanes with items:', model.lanes.filter(l => l.source_item_ids.length > 0).length);
console.log('Edges with items:', model.edges.filter(e => e.source_item_ids.length > 0).length);
console.log('Nodes with items:', model.nodes.filter(n => n.source_item_ids.length > 0).length);
console.log('Flows with items:', model.flows.filter(f => f.source_item_ids.length > 0).length);
