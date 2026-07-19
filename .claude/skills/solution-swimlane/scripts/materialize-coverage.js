"use strict";

const fs = require("fs");
const path = require("path");
const { parseArgs } = require("./validate-solution-swimlane");

const MAPPING_KEYS = {
  lane: "mapped_lane_ids",
  node: "mapped_node_ids",
  edge: "mapped_edge_ids",
  flow: "mapped_flow_ids",
};

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function matchesSelector(item, selector) {
  const checks = [];
  if (selector.id) checks.push(item.source_item_id === selector.id);
  if (selector.source_ref) checks.push(item.source_ref === selector.source_ref);
  if (selector.source_ref_prefix) checks.push(item.source_ref.startsWith(selector.source_ref_prefix));
  if (selector.source_file) checks.push(item.source_file === selector.source_file);
  if (selector.source_kind) checks.push(item.source_kind === selector.source_kind);
  if (selector.context) checks.push(item.context === selector.context);
  if (selector.context_prefix) checks.push(item.context.startsWith(selector.context_prefix));
  if (selector.raw_text_equals) checks.push(item.raw_text === selector.raw_text_equals);
  if (selector.raw_text_includes) checks.push(item.raw_text.includes(selector.raw_text_includes));
  if (!checks.length) throw new Error("来源选择器至少需要一个条件");
  return checks.every(Boolean);
}

function selectItems(items, selector, label) {
  const matches = items.filter((item) => matchesSelector(item, selector));
  if (!matches.length) throw new Error(`${label} 的来源选择器没有匹配任何源项：${JSON.stringify(selector)}`);
  return matches;
}

function addUnique(target, values) {
  const seen = new Set(target);
  for (const value of values) {
    if (!seen.has(value)) {
      seen.add(value);
      target.push(value);
    }
  }
}

function expandElementSources(elements, items, type) {
  return asArray(elements).map((element, index) => {
    const copy = { ...element, source_item_ids: [...asArray(element.source_item_ids)] };
    for (const selector of asArray(element.source_selectors)) {
      const matches = selectItems(items, selector, `${type}[${index}]`);
      addUnique(copy.source_item_ids, matches.map((item) => item.source_item_id));
    }
    delete copy.source_selectors;
    return copy;
  });
}

function defaultDisposition(item) {
  const ref = item.source_ref;
  const context = item.context || "";
  const isProcessJson = /#\$\.(main_flow|sub_flows|exceptions|states)(?:\[|\.|$)/.test(ref);
  const isProcessMarkdown = /§[2345]\b/.test(context);
  if (isProcessJson || isProcessMarkdown) {
    return {
      semantic_kind: "detail",
      required_in_diagram: false,
      disposition: "blocked",
      rule_id: "",
      reason: "流程语义尚未映射或显式处置",
    };
  }
  if (/#\$\.open_questions(?:\[|\.|$)/.test(ref) || /§8\b/.test(context)) {
    return {
      semantic_kind: "detail",
      required_in_diagram: false,
      disposition: "detail",
      rule_id: "DETAIL_OPEN_QUESTION",
      reason: "正式蓝图开放问题，保留在待确认区域",
    };
  }
  if (
    /#\$\.(pages|modals|drawers|interaction_overview)(?:\[|\.|$)/.test(ref)
    || /§[67]\b/.test(context)
  ) {
    return {
      semantic_kind: "detail",
      required_in_diagram: false,
      disposition: "excluded_by_rule",
      rule_id: "EXCLUDE_PAGE_DETAIL",
      reason: "页面、控件、文案或反馈细节不提升为方案主图元素",
    };
  }
  if (
    /#\$\.(journey_consumption|critical_design_judgments|uxb_mapping|problem_framing_mapping|stories_consumption|knowledge_consumption)(?:\[|\.|$)/.test(ref)
    || /§[019]\b/.test(context)
  ) {
    return {
      semantic_kind: "excluded",
      required_in_diagram: false,
      disposition: "excluded_by_rule",
      rule_id: "EXCLUDE_ANALYSIS_ONLY",
      reason: "分析、知识消费或追踪信息不属于方案主图语义",
    };
  }
  if (["json-object", "json-array"].includes(item.source_kind)) {
    return {
      semantic_kind: "excluded",
      required_in_diagram: false,
      disposition: "excluded_by_rule",
      rule_id: "EXCLUDE_DUPLICATE_CONTAINER",
      reason: "容器结构由其子项承载，不重复提升",
    };
  }
  if (item.source_kind === "md-heading") {
    return {
      semantic_kind: "excluded",
      required_in_diagram: false,
      disposition: "excluded_by_rule",
      rule_id: "EXCLUDE_NON_SEMANTIC",
      reason: "标题仅用于文档结构导航",
    };
  }
  return {
    semantic_kind: "excluded",
    required_in_diagram: false,
    disposition: "excluded_by_rule",
    rule_id: "EXCLUDE_NON_SEMANTIC",
    reason: "不构成角色、任务、关系或流程语义",
  };
}

function materializeCoverage(inventory, draft) {
  const items = asArray(inventory.items);
  const model = {
    ...draft,
    source_hash: inventory.source_hash,
    lanes: expandElementSources(draft.lanes, items, "lanes"),
    nodes: expandElementSources(draft.nodes, items, "nodes"),
    edges: expandElementSources(draft.edges, items, "edges"),
    flows: expandElementSources(draft.flows, items, "flows"),
    open_questions: expandElementSources(draft.open_questions, items, "open_questions"),
  };

  const coverageRules = asArray(draft.coverage_rules);
  const explicitCoverage = new Map(
    asArray(draft.coverage_manifest).map((item) => [item.source_item_id, item]),
  );
  delete model.coverage_rules;
  delete model.coverage_manifest;

  const mappings = new Map(items.map((item) => [
    item.source_item_id,
    {
      lane: [],
      node: [],
      edge: [],
      flow: [],
      question: [],
    },
  ]));
  for (const [type, elements] of [
    ["lane", model.lanes],
    ["node", model.nodes],
    ["edge", model.edges],
    ["flow", model.flows],
    ["question", model.open_questions],
  ]) {
    for (const element of elements) {
      for (const sourceId of asArray(element.source_item_ids)) {
        if (!mappings.has(sourceId)) throw new Error(`${type} ${element.id} 引用不存在源项：${sourceId}`);
        mappings.get(sourceId)[type].push(element.id);
      }
    }
  }

  const ruleBySource = new Map();
  for (const [index, rule] of coverageRules.entries()) {
    const matches = selectItems(items, rule.selector || {}, `coverage_rules[${index}]`);
    for (const item of matches) {
      if (ruleBySource.has(item.source_item_id)) {
        throw new Error(`源项同时命中多个 coverage_rules：${item.source_item_id}`);
      }
      ruleBySource.set(item.source_item_id, rule);
    }
  }

  model.coverage_manifest = items.map((item) => {
    const mapping = mappings.get(item.source_item_id);
    const mappedTypes = ["lane", "node", "edge", "flow"].filter((type) => mapping[type].length);
    if (mappedTypes.length > 1) {
      throw new Error(`源项跨多种图元素类型映射，请拆分证据：${item.source_item_id} -> ${mappedTypes.join(",")}`);
    }
    if (mappedTypes.length === 1) {
      const semanticKind = mappedTypes[0];
      const mappedCount = mapping[semanticKind].length;
      return {
        source_item_id: item.source_item_id,
        semantic_kind: semanticKind,
        required_in_diagram: true,
        disposition: mappedCount > 1 ? "merged" : "rendered",
        mapped_lane_ids: mapping.lane,
        mapped_node_ids: mapping.node,
        mapped_edge_ids: mapping.edge,
        mapped_flow_ids: mapping.flow,
        rule_id: mappedCount > 1 ? "MERGE_DUPLICATE_EVIDENCE" : "",
        reason: mappedCount > 1 ? "同一正式来源支撑多个同类图元素" : "已映射到正式图元素",
      };
    }
    if (mapping.question.length) {
      return {
        source_item_id: item.source_item_id,
        semantic_kind: "detail",
        required_in_diagram: false,
        disposition: "detail",
        mapped_lane_ids: [],
        mapped_node_ids: [],
        mapped_edge_ids: [],
        mapped_flow_ids: [],
        rule_id: "DETAIL_OPEN_QUESTION",
        reason: "保留在待确认区域",
      };
    }

    const override = explicitCoverage.get(item.source_item_id) || ruleBySource.get(item.source_item_id);
    const base = override || defaultDisposition(item);
    return {
      source_item_id: item.source_item_id,
      semantic_kind: base.semantic_kind,
      required_in_diagram: Boolean(base.required_in_diagram),
      disposition: base.disposition,
      mapped_lane_ids: [],
      mapped_node_ids: [],
      mapped_edge_ids: [],
      mapped_flow_ids: [],
      rule_id: base.rule_id || "",
      reason: base.reason || "已按明确规则处置",
    };
  });

  return model;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(path.resolve(filePath), "utf8").replace(/^\uFEFF/, ""));
}

function main() {
  try {
    const args = parseArgs(process.argv.slice(2));
    if (!args.inventory || !args.draft || !args.out) {
      throw new Error(
        "用法：node materialize-coverage.js --inventory <file> --draft <file> --out <file>",
      );
    }
    const inventory = readJson(args.inventory);
    const draft = readJson(args.draft);
    const model = materializeCoverage(inventory, draft);
    const outputPath = path.resolve(args.out);
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, `${JSON.stringify(model, null, 2)}\n`, "utf8");
    const blocked = model.coverage_manifest.filter((item) => item.disposition === "blocked").length;
    console.log(`完整覆盖清单已物化：${outputPath}`);
    console.log(`覆盖记录：${model.coverage_manifest.length}`);
    console.log(`阻断项：${blocked}`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (require.main === module) main();

module.exports = {
  materializeCoverage,
  matchesSelector,
};
