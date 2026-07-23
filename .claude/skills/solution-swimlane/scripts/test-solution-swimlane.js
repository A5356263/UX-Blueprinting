"use strict";

const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { buildInventory } = require("./build-source-inventory");
const { buildHtml, computeLayout, renderSvg } = require("./render-solution-swimlane");
const { materializeCoverage } = require("./materialize-coverage");
const { validateModel } = require("./validate-solution-swimlane");

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function sourceItem(id) {
  return {
    source_item_id: id,
    source_file: "fixture",
    source_ref: `fixture#${id}`,
    source_kind: "json-value",
    raw_text: id,
    context: "",
    content_hash: id.padEnd(64, "0").slice(0, 64),
  };
}

function coverage(sourceId, semanticKind, mappedKey, mappedId) {
  const item = {
    source_item_id: sourceId,
    semantic_kind: semanticKind,
    required_in_diagram: true,
    disposition: "rendered",
    mapped_lane_ids: [],
    mapped_node_ids: [],
    mapped_edge_ids: [],
    mapped_flow_ids: [],
    rule_id: "",
    reason: "回归测试必画项",
  };
  item[mappedKey].push(mappedId);
  return item;
}

function fixture() {
  const ids = [
    "src-lane-user",
    "src-lane-system",
    "src-node-start",
    "src-node-process",
    "src-node-result",
    "src-edge-submit",
    "src-edge-finish",
    "src-flow-main",
  ];
  const inventory = {
    schema_version: "1.0",
    source_hash: "fixture-source-hash",
    files: [],
    source_items_total: ids.length,
    items: ids.map(sourceItem),
  };
  const model = {
    schema_version: "1.0",
    title: "回归测试 · 方案协同图",
    subtitle: "验证节点、关系、流程和来源覆盖门禁",
    source_hash: inventory.source_hash,
    lanes: [
      {
        id: "lane-user",
        name: "用户",
        lane_type: "human",
        order: 1,
        source_item_ids: ["src-lane-user"],
      },
      {
        id: "lane-system",
        name: "系统",
        lane_type: "system",
        order: 2,
        source_item_ids: ["src-lane-system"],
      },
    ],
    nodes: [
      {
        id: "node-start",
        lane_id: "lane-user",
        label: "提交任务",
        node_type: "action",
        summary: "用户提交需要处理的业务任务",
        certainty: "confirmed",
        source_item_ids: ["src-node-start"],
        flow_ids: ["flow-main"],
      },
      {
        id: "node-process",
        lane_id: "lane-system",
        label: "系统处理",
        node_type: "system_process",
        summary: "系统校验并完成处理",
        certainty: "confirmed",
        source_item_ids: ["src-node-process"],
        flow_ids: ["flow-main"],
      },
      {
        id: "node-result",
        lane_id: "lane-user",
        label: "获得结果",
        node_type: "result",
        summary: "用户获得明确业务结果",
        certainty: "confirmed",
        source_item_ids: ["src-node-result"],
        flow_ids: ["flow-main"],
      },
    ],
    edges: [
      {
        id: "edge-submit",
        from: "node-start",
        to: "node-process",
        label: "提交后",
        edge_type: "normal",
        certainty: "confirmed",
        source_item_ids: ["src-edge-submit"],
        flow_ids: ["flow-main"],
      },
      {
        id: "edge-finish",
        from: "node-process",
        to: "node-result",
        label: "处理完成",
        edge_type: "normal",
        certainty: "confirmed",
        source_item_ids: ["src-edge-finish"],
        flow_ids: ["flow-main"],
      },
    ],
    flows: [
      {
        id: "flow-main",
        name: "主流程",
        flow_type: "main",
        node_ids: ["node-start", "node-process", "node-result"],
        edge_ids: ["edge-submit", "edge-finish"],
        default_visible: true,
        source_item_ids: ["src-flow-main"],
      },
    ],
    open_questions: [],
    coverage_manifest: [
      coverage("src-lane-user", "lane", "mapped_lane_ids", "lane-user"),
      coverage("src-lane-system", "lane", "mapped_lane_ids", "lane-system"),
      coverage("src-node-start", "node", "mapped_node_ids", "node-start"),
      coverage("src-node-process", "node", "mapped_node_ids", "node-process"),
      coverage("src-node-result", "node", "mapped_node_ids", "node-result"),
      coverage("src-edge-submit", "edge", "mapped_edge_ids", "edge-submit"),
      coverage("src-edge-finish", "edge", "mapped_edge_ids", "edge-finish"),
      coverage("src-flow-main", "flow", "mapped_flow_ids", "flow-main"),
    ],
  };
  return { inventory, model };
}

function expectFailure(name, inventory, model, html, pattern) {
  const report = validateModel(inventory, model, html);
  assert.strictEqual(report.ok, false, `${name} 应当失败`);
  assert(
    report.errors.some((message) => pattern.test(message)),
    `${name} 未出现预期错误；实际：${report.errors.join(" | ")}`,
  );
}

function run() {
  const templatePath = path.resolve(__dirname, "../assets/solution-swimlane.template.html");
  const template = fs.readFileSync(templatePath, "utf8");
  const { inventory, model } = fixture();

  const validReport = validateModel(inventory, model);
  assert.strictEqual(validReport.ok, true, validReport.errors.join("\n"));
  const result = buildHtml(inventory, model, template);
  const htmlReport = validateModel(inventory, model, result.html);
  assert.strictEqual(htmlReport.ok, true, htmlReport.errors.join("\n"));
  assert(!result.html.includes('class="page-header"'), "画布优先布局不得恢复常驻页头");
  assert(!result.html.includes("<footer"), "画布优先布局不得恢复常驻 footer");
  const toolbarCss = result.html.match(/\.toolbar\s*\{([\s\S]*?)\}/)?.[1] || "";
  assert(toolbarCss.includes("position: relative"), "操作栏必须进入文档流");
  assert(!toolbarCss.includes("position: fixed"), "操作栏不得浮动覆盖画布");
  assert(!toolbarCss.includes("z-index"), "操作栏不得依赖高层级覆盖画布");
  assert(result.html.includes("flex-direction: column"), "页面必须使用纵向 flex 分配真实空间");
  assert(/main\s*\{\s*position:\s*relative;\s*flex:\s*1;/.test(result.html), "画布主区必须占用操作栏之外的剩余高度");
  assert(result.html.includes("height: 100%;"), "画布滚动区必须填满主区");
  assert(result.html.includes('id="toggle-toolbar"'), "紧凑工具栏必须可收起");
  assert(result.html.includes('id="info-drawer" hidden'), "辅助信息必须放入默认关闭的抽屉");
  assert(result.html.includes('data-flow-types="main"'), "节点和关系必须包含流程类别元数据");
  assert(result.html.includes('id="arrow-flow-main"'), "必须定义主流程箭头");
  assert(result.html.includes('id="arrow-flow-secondary"'), "必须定义次流程箭头");
  assert(result.html.includes('id="arrow-flow-exception"'), "必须定义异常流程箭头");
  assert(result.html.includes('body[data-active-flow-type="main"]'), "必须按所选流程统一卡片和连线颜色");
  assert(result.html.includes('data-route-channel='), "每条关系必须包含稳定走线通道");
  assert(result.html.includes('data-edge-label-for='), "关系标签必须包含可校验几何信息");
  assert(
    result.html.indexOf('data-flow-filter="__all__"') < result.html.indexOf('data-flow-filter="flow-main"'),
    "全部流程按钮必须位于首位",
  );
  assert(result.html.includes("function setHoverFlowFocus"), "全部视角必须支持按关系聚焦完整流程");
  assert(result.html.includes('class="edge-hit"'), "每条细线必须包含透明悬停命中轨道");
  assert(result.html.includes("stroke:transparent !important"), "透明命中轨道不得被流程颜色覆盖");
  assert(result.html.includes(".is-muted { opacity:.035; }"), "聚焦流程时非当前内容必须充分降噪");
  assert(result.html.includes('body[data-active-flow-type="all"] .swim-edge foreignObject'), "全部视角必须分层隐藏非主流程关系标签");
  assert(result.html.includes('data-width="80" data-height="32"'), "关系标签必须使用宽版可读尺寸");
  assert([...result.layout.nodes.values()].every((node) => node.width === 180), "节点宽度必须使用高密度基线");
  assert([...result.layout.nodes.values()].every((node) => node.height >= 84), "节点不得低于最小可读高度");
  assert(result.layout.width <= 1040, "回归夹具的画布宽度超过可读密度上限");
  assert(result.layout.height <= 328, "回归夹具的画布高度超过高密度上限");
  assert(result.html.includes("const initialZoom = scroll.clientWidth >= 1440 ? .92 : 1;"), "大视口必须采用可读的高密度初始缩放");

  const sharedRouteModel = clone(model);
  sharedRouteModel.edges.push({
    ...clone(model.edges[0]),
    id: "edge-submit-shared",
    label: "共享提交路径",
  });
  const sharedRouteSvg = renderSvg(sharedRouteModel, computeLayout(sharedRouteModel));
  const edgePath = (html, edgeId) => html.match(
    new RegExp(`data-edge-id="${edgeId}"[\\s\\S]*?<path class="edge-line" d="([^"]+)"`),
  )?.[1];
  assert.strictEqual(
    edgePath(sharedRouteSvg, "edge-submit"),
    edgePath(sharedRouteSvg, "edge-submit-shared"),
    "具有共同端点和走向的关系必须允许复用共同路径",
  );

  const returnRouteModel = clone(model);
  returnRouteModel.edges.push({
    ...clone(model.edges[0]),
    id: "edge-return-test",
    from: "node-result",
    to: "node-start",
    label: "回到起点",
    edge_type: "return",
  });
  const returnLayout = computeLayout(returnRouteModel);
  assert(returnLayout.height - returnLayout.laneBottom >= 96, "回流线路必须拥有独立的底部缓冲区");
  assert(returnLayout.returnRouteStartY - returnLayout.laneBottom >= 48, "首条回流线不得贴近泳道正文");

  const missingCoverage = clone(model);
  missingCoverage.coverage_manifest.pop();
  expectFailure("缺少覆盖记录", inventory, missingCoverage, null, /缺少覆盖记录/);

  const missingMapping = clone(model);
  missingMapping.coverage_manifest.find((item) => item.source_item_id === "src-node-process").mapped_node_ids = [];
  expectFailure("缺少节点映射", inventory, missingMapping, null, /没有映射|不是双向映射/);

  const danglingEdge = clone(model);
  danglingEdge.edges[0].to = "node-missing";
  expectFailure("关系端点不存在", inventory, danglingEdge, null, /to 不存在/);

  const brokenFlowMembership = clone(model);
  brokenFlowMembership.nodes[1].flow_ids = [];
  expectFailure("流程成员不对称", inventory, brokenFlowMembership, null, /不是双向成员关系/);

  const missingDomNode = result.html.replace('data-node-id="node-process"', 'data-node-removed="node-process"');
  expectFailure("DOM 缺少节点", inventory, model, missingDomNode, /节点集合不相等/);

  const missingDomEdge = result.html.replace('data-edge-id="edge-finish"', 'data-edge-removed="edge-finish"');
  expectFailure("DOM 缺少关系", inventory, model, missingDomEdge, /关系集合不相等/);

  const missingFlowTypeMeta = result.html.replace('data-flow-types="main"', 'data-flow-types=""');
  expectFailure("流程类别元数据缺失", inventory, model, missingFlowTypeMeta, /流程类别元数据与模型不一致/);

  const overlappingEdgeLabel = result.html.replace(
    /data-edge-label-for="edge-submit" data-x="[^"]+" data-y="[^"]+"/,
    'data-edge-label-for="edge-submit" data-x="196" data-y="14"',
  );
  expectFailure("关系标签遮挡节点", inventory, model, overlappingEdgeLabel, /标签遮挡节点/);

  const outOfBoundsEdge = result.html.replace(
    /(<g class="swim-edge[^"]*" data-edge-id="edge-submit"[\s\S]*?<path class="edge-line" d=")[^"]+"/,
    '$1M 196 14 H 99999"',
  );
  expectFailure("关系超出画布", inventory, model, outOfBoundsEdge, /超出 SVG 画布边界/);

  const externalDependency = result.html.replace("</head>", '<script src="https://example.com/x.js"></script></head>');
  expectFailure("外部依赖", inventory, model, externalDependency, /外部 script src|远程资源/);

  const sourceFixtureDir = fs.mkdtempSync(path.join(os.tmpdir(), "solution-swimlane-source-"));
  const sourceFixtureMd = path.join(sourceFixtureDir, "experience_blueprint.md");
  const sourceFixtureJson = path.join(sourceFixtureDir, "experience-blueprint.json");
  fs.writeFileSync(sourceFixtureMd, "# 体验蓝图\n\n## §3 主交互流程\n\n提交申请。\n", "utf8");
  fs.writeFileSync(sourceFixtureJson, JSON.stringify({
    version: "3.0",
    main_flow: [{ name: "提交申请" }],
  }), "utf8");
  const inventoryA = buildInventory(sourceFixtureMd, sourceFixtureJson);
  const inventoryB = buildInventory(sourceFixtureMd, sourceFixtureJson);
  assert.strictEqual(inventoryA.source_hash, inventoryB.source_hash, "相同输入应产生相同来源哈希");
  assert.deepStrictEqual(inventoryA.items, inventoryB.items, "相同输入应产生稳定源清单");
  fs.rmSync(sourceFixtureDir, { recursive: true, force: true });

  const draft = clone(model);
  delete draft.coverage_manifest;
  const materialized = materializeCoverage(inventory, draft);
  assert.strictEqual(materialized.coverage_manifest.length, inventory.items.length, "覆盖清单必须覆盖全部源项");
  assert.strictEqual(
    materialized.coverage_manifest.filter((item) => item.disposition === "blocked").length,
    0,
    "已完整映射的草稿不应产生阻断项",
  );

  const blueprintV3Inventory = {
    schema_version: "1.0",
    source_hash: "blueprint-v3-source-hash",
    files: [],
    source_items_total: 4,
    items: [
      { ...sourceItem("v3-main"), source_ref: "spark-output/context/experience-blueprint.json#$.main_flow[0].name" },
      { ...sourceItem("v3-surface"), source_ref: "spark-output/context/experience-blueprint.json#$.surfaces.pages[0].name" },
      { ...sourceItem("v3-overview"), source_ref: "spark-output/context/experience-blueprint.json#$.interaction_overview[0].name" },
      { ...sourceItem("v3-trace"), source_ref: "spark-output/context/experience-blueprint.json#$.upstream_trace[0].design_decision" },
    ],
  };
  const blueprintV3Draft = {
    schema_version: "1.0",
    title: "Blueprint 3.0 输入兼容",
    subtitle: "只验证上游字段分类",
    lanes: [],
    nodes: [],
    edges: [],
    flows: [],
    open_questions: [],
  };
  const blueprintV3Coverage = materializeCoverage(blueprintV3Inventory, blueprintV3Draft).coverage_manifest;
  assert.strictEqual(
    blueprintV3Coverage.find((item) => item.source_item_id === "v3-main").disposition,
    "blocked",
    "Blueprint 3.0 主流程语义未映射时必须阻断",
  );
  for (const id of ["v3-surface", "v3-overview", "v3-trace"]) {
    assert.strictEqual(
      blueprintV3Coverage.find((item) => item.source_item_id === id).disposition,
      "excluded_by_rule",
      `Blueprint 3.0 非主图字段必须按规则排除：${id}`,
    );
  }

  const conflictInventory = {
    schema_version: "1.0",
    source_hash: "conflict-source-hash",
    files: [],
    source_items_total: 2,
    items: [
      {
        ...sourceItem("conflict"),
        source_ref: "spark-output/context/experience-blueprint.json#$.main_flow[0].name",
      },
      {
        ...sourceItem("unresolved"),
        source_ref: "spark-output/context/experience-blueprint.json#$.exceptions[0].name",
      },
    ],
  };
  const conflictDraft = {
    schema_version: "1.0",
    title: "冲突预检",
    subtitle: "一次报告全部草稿覆盖问题",
    lanes: [{
      id: "lane-conflict",
      name: "冲突泳道",
      lane_type: "human",
      order: 1,
      source_item_ids: ["conflict"],
    }],
    nodes: [{
      id: "node-conflict",
      lane_id: "lane-conflict",
      label: "冲突节点",
      node_type: "action",
      summary: "同一证据被错误复用",
      certainty: "confirmed",
      source_item_ids: ["conflict"],
      flow_ids: [],
    }],
    edges: [],
    flows: [],
    open_questions: [],
  };
  assert.throws(
    () => materializeCoverage(conflictInventory, conflictDraft),
    (error) => (
      /跨图元素类型冲突 1 项/.test(error.message)
      && /未显式处置流程源项 1 项：exceptions=1/.test(error.message)
      && /不要逐项试错/.test(error.message)
    ),
    "草稿预检必须一次报告跨类型冲突和未处置流程源项",
  );

  console.log("solution-swimlane 回归测试通过：13 项");
}

try {
  run();
} catch (error) {
  console.error(error.stack || error.message);
  process.exit(1);
}
