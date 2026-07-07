#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XFT 内容资产检索脚本。

用途：
- 根据用户需求选择 page_type、recipe_id。
- 根据 recipe-asset-map 补齐必选资产。
- 根据关键词和规则选择可选资产。
- 输出 step11 所需的 CONTENT_ASSET_DECISION JSON。
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "content-assets"
ASSET_ID_ALIASES = {
    "region.page-header.detail": "region.page-header.with-actions",
    "module.detail-summary.basic": "region.detail-summary.basic",
    "module.approval-flow.basic": "module-approval-flow-basic",
    "region.detail-section-stack": "region.detail-info-section.basic",
    "module.operation-log.basic": "module-operation-log-basic",
    "module.setting-item.basic": "region.setting-section.basic",
    "region.settings-layout.anchor": "layout.settings-anchor.basic",
    "region.detail-side-layout.basic": "layout.detail-side.basic",
    "region.tabs.basic": "layout.tabs.basic",
    "region.split-layout.master-detail": "layout.master-detail.basic",
    "region.split-layout.tree-table": "layout.master-detail.basic",
    "region.config-layout.split": "layout.master-detail.basic",
    "region.detail-two-column": "layout.detail-side.basic",
}
OVERLAY_ROUTE_KEYWORDS = [
    "弹窗",
    "对话框",
    "modal",
    "浮层",
    "弹出编辑",
    "弹窗编辑",
]
RECIPE_OPTIONAL_ASSET_ALIASES = {
    "attachment-list": "module-upload-file-basic",
    "batch-action-footer": "module.batch-action-footer",
    "confirm-modal": "OV_MODAL_CONFIRM",
    "detail-drawer": "overlay.detail-drawer",
    "drawer-config": "OV_DRAWER_BASIC",
    "empty-state": "ST_EMPTY_BASIC",
    "operation-log": "module-operation-log-basic",
    "related-table": "module-related-table-basic",
    "table-column-settings": "module-table-header-settings-panel",
}


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normalize(text: Any) -> str:
    return str(text or "").lower().strip()


def tokenize(text: Any) -> List[str]:
    raw = normalize(text)
    if not raw:
        return []
    parts = re.split(r"[\s,，;；/、>｜|:：()（）\[\]{}<>《》\-]+", raw)
    tokens: List[str] = []
    for part in parts:
        if not part:
            continue
        tokens.append(part)
        if re.search(r"[\u4e00-\u9fff]", part) and len(part) >= 3:
            for n in (2, 3):
                tokens.extend(part[i : i + n] for i in range(0, len(part) - n + 1))
    return [t for t in tokens if len(t) >= 2]


class BM25:
    def __init__(self, docs: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs_tokens = [tokenize(d) for d in docs]
        self.doc_lens = [len(d) for d in self.docs_tokens]
        self.avgdl = sum(self.doc_lens) / len(self.doc_lens) if self.doc_lens else 0
        self.idf: Dict[str, float] = {}
        df: Counter[str] = Counter()
        for doc in self.docs_tokens:
            for token in set(doc):
                df[token] += 1
        n_docs = len(self.docs_tokens)
        for token, freq in df.items():
            self.idf[token] = math.log((n_docs - freq + 0.5) / (freq + 0.5) + 1)

    def scores(self, query: str) -> List[float]:
        query_tokens = tokenize(query)
        out: List[float] = []
        for doc, doc_len in zip(self.docs_tokens, self.doc_lens):
            tf = Counter(doc)
            score = 0.0
            for token in query_tokens:
                if token not in self.idf:
                    continue
                freq = tf[token]
                denom = freq + self.k1 * (1 - self.b + self.b * doc_len / (self.avgdl or 1))
                score += self.idf[token] * (freq * (self.k1 + 1)) / (denom or 1)
            out.append(score)
        return out


def weighted_doc(row: Dict[str, str], fields: Iterable[str]) -> str:
    return " ".join(str(row.get(f, "") or "") for f in fields)


def keyword_bonus(query: str, row: Dict[str, str], fields: Iterable[str], weight: float = 1.0) -> float:
    q_tokens = set(tokenize(query))
    text = normalize(" ".join(str(row.get(f, "") or "") for f in fields))
    score = 0.0
    for token in q_tokens:
        if token and token in text:
            score += weight
    return score


def negative_penalty(query: str, row: Dict[str, str], field: str = "negative_keywords") -> float:
    q = normalize(query)
    negs = tokenize(row.get(field, ""))
    if any(n in q for n in negs):
        return -100.0
    return 0.0


def rank_rows(
    query: str,
    rows: List[Dict[str, str]],
    fields: List[str],
    max_results: int = 5,
) -> List[Tuple[float, Dict[str, str]]]:
    if not rows:
        return []
    docs = [weighted_doc(r, fields) for r in rows]
    bm25 = BM25(docs)
    bm25_scores = bm25.scores(query)
    ranked: List[Tuple[float, Dict[str, str]]] = []
    for row, bm25_score in zip(rows, bm25_scores):
        score = bm25_score + keyword_bonus(query, row, fields, 1.5) + negative_penalty(query, row)
        try:
            score += float(row.get("priority", 0)) / 100.0
        except ValueError:
            pass
        ranked.append((score, row))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [item for item in ranked[:max_results] if item[0] > 0]


def load_data(data_dir: Path) -> Dict[str, List[Dict[str, str]]]:
    return {
        "page_router": read_csv(data_dir / "page-type-router.csv"),
        "recipes": read_csv(data_dir / "recipe-rules.csv"),
        "recipe_asset_map": read_csv(data_dir / "recipe-asset-map.csv"),
        "assets": read_csv(data_dir / "content-assets.csv"),
        "asset_keywords": read_csv(data_dir / "asset-keywords.csv"),
        "rules": read_csv(data_dir / "asset-rules.csv"),
        "support_css": read_csv(data_dir / "support-css-manifest.csv"),
    }


def contains_any(text: str, phrases: Iterable[str]) -> bool:
    haystack = normalize(text)
    return any(normalize(phrase) in haystack for phrase in phrases)


def select_overlay_route(query: str) -> Dict[str, str] | None:
    if not contains_any(query, OVERLAY_ROUTE_KEYWORDS):
        return None
    return {
        "scope": "Page Overlay",
        "overlay_type": "Modal",
        "page_type": "Overlay",
        "output_page_type": "None",
        "recipe_id": "overlay.modal.functional",
        "shell": "admin-side-shell",
        "page_block": "None",
    }


def explicit_page_type(query: str) -> str | None:
    q = normalize(query)
    if any(k in q for k in ["审批详情", "流程详情", "审批记录"]):
        return "ApprovalDetailPage"
    if any(k in q for k in ["列表页", "表格页", "台账", "花名册", "数据管理", "查询页"]):
        if not any(k in q for k in ["详情页", "审批详情页", "单据详情页"]):
            return "TablePage"
    if any(k in q for k in ["详情页", "单据详情页", "查看页"]):
        return "DetailPage"
    if any(k in q for k in ["标签内表格", "表格详情", "关联表详情", "多标签详情", "tab详情", "分tab查看", "多tab详情"]):
        return "DetailPage"
    if any(k in q for k in ["表单页", "新建页", "创建页", "申请页", "提单"]):
        return "CreatePage"
    if any(k in q for k in ["编辑页", "修改页", "维护页"]):
        return "EditPage"
    if any(k in q for k in ["设置页", "配置页", "参数配置", "权限配置", "公式配置"]):
        return "SettingsPage"
    if any(k in q for k in ["业务首页", "运营首页", "门户首页", "业务门户"]):
        return "BusinessHomePage"
    if any(k in q for k in ["首页", "工作台", "仪表盘", "看板"]):
        return "HomePage"
    if any(k in q for k in ["报表页", "统计分析", "查询报表"]):
        return "ReportPage"
    return None


def select_page_route(query: str, data: Dict[str, List[Dict[str, str]]]) -> Dict[str, str]:
    overlay_route = select_overlay_route(query)
    if overlay_route:
        return overlay_route
    explicit = explicit_page_type(query)
    routers = data["page_router"]
    if explicit:
        routers = [r for r in routers if r.get("page_type") == explicit] or data["page_router"]
    ranked = rank_rows(query, routers, ["match_keywords", "page_type", "recipe_id", "notes"], 5)
    if ranked:
        return ranked[0][1]
    return {
        "page_type": "TablePage",
        "recipe_id": "recipe.table.basic",
        "scope": "Full Page",
        "shell": "admin-side-shell",
        "page_block": "ListPageBlock",
    }


def explicit_recipe_id(query: str, page_type: str) -> str | None:
    q = normalize(query)
    if page_type == "TablePage":
        if any(k in q for k in ["卡片表格", "卡片列表", "图文列表"]):
            return "recipe.table.card"
        if any(k in q for k in ["可编辑表格", "行内编辑", "批量录入", "明细维护"]):
            return "recipe.table.editable"
        if any(k in q for k in ["父子", "主从", "左树右表", "树表", "左侧树"]):
            return "recipe.table.parent-child"
        if any(k in q for k in ["汇总", "总览", "指标+表格", "多栏表格", "复杂表格", "宽表"]):
            return "recipe.table.standard"
        if any(k in q for k in ["列表页", "表格页", "花名册", "台账", "数据管理", "crud", "增删改查", "页内闭环"]):
            return "recipe.table.standard"
    if page_type == "CreatePage" and any(k in q for k in ["高级表单", "多分组", "动态字段", "明细录入", "批量录入"]):
        return "recipe.form.advanced"
    if page_type == "CreatePage" and any(k in q for k in ["分步", "步骤", "多步骤"]):
        return "recipe.form.step"
    if page_type == "DetailPage" and any(k in q for k in ["表格详情", "关联表详情", "多tab表格", "标签内表格"]):
        return "recipe.detail.table-tabs"
    if page_type == "DetailPage" and any(k in q for k in ["多标签详情", "tab详情", "复杂详情", "分tab查看", "多tab详情"]):
        return "recipe.detail.tabs"
    if page_type == "SettingsPage" and any(
        k in q for k in ["复杂配置", "字段配置", "表头设置", "筛选项配置", "预览保存", "规则配置"]
    ):
        return "recipe.complex.config"
    if page_type == "SettingsPage" and any(k in q for k in ["公式", "公式配置", "公式编辑"]):
        return "recipe.settings.basic"
    return None


def select_recipe(query: str, page_type: str, preferred_recipe_id: str, data: Dict[str, List[Dict[str, str]]]) -> Dict[str, str]:
    recipes = [r for r in data["recipes"] if r.get("page_type") == page_type]
    explicit_recipe = explicit_recipe_id(query, page_type) or preferred_recipe_id
    for row in recipes:
        if row.get("recipe_id") == explicit_recipe:
            return row
    ranked = rank_rows(
        query,
        recipes,
        ["recipe_name", "keywords", "default_region_order", "required_regions", "optional_modules"],
        5,
    )
    if ranked:
        return ranked[0][1]
    for row in data["recipes"]:
        if row.get("recipe_id") == preferred_recipe_id:
            return row
    return {"recipe_id": preferred_recipe_id, "page_type": page_type, "recipe_name": preferred_recipe_id}


def assets_by_id(data: Dict[str, List[Dict[str, str]]]) -> Dict[str, Dict[str, str]]:
    return {r.get("asset_id", ""): r for r in data["assets"] if r.get("asset_id")}


def canonical_asset_id(asset_id: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize(asset_id))


def resolve_asset(asset_index: Dict[str, Dict[str, str]], candidate_asset_id: str) -> Dict[str, str] | None:
    if candidate_asset_id in asset_index:
        return asset_index[candidate_asset_id]
    alias = ASSET_ID_ALIASES.get(candidate_asset_id)
    if alias and alias in asset_index:
        return asset_index[alias]
    target = canonical_asset_id(candidate_asset_id)
    for asset_id, asset in asset_index.items():
        if canonical_asset_id(asset_id) == target:
            return asset
    return None


def page_type_matches(asset_page_type: str, target_page_type: str) -> bool:
    values = {normalize(item) for item in str(asset_page_type or "").split("|") if item.strip()}
    if not values or "any" in values or "all" in values:
        return True
    target = normalize(target_page_type)
    aliases = {
        "overlay": {"overlay", "page overlay", "modal", "drawer"},
        "modal": {"overlay", "page overlay", "modal"},
        "drawer": {"overlay", "page overlay", "drawer"},
        "createpage": {"createpage", "formpage"},
        "editpage": {"editpage", "formpage"},
        "detailpage": {"detailpage"},
        "tablepage": {"tablepage"},
        "settingspage": {"settingspage"},
        "resultpage": {"resultpage"},
        "reportpage": {"reportpage"},
        "homepage": {"homepage"},
    }
    target_aliases = aliases.get(target, {target})
    return bool(values & target_aliases)


def normalize_asset_path(path: str) -> str:
    if not path:
        return ""
    path = path.replace("\\", "/")
    if path.startswith("assets/content-assets/"):
        return path
    if path.startswith("assets/regions/"):
        if path.endswith("/_region-support.css"):
            return "assets/content-assets/_support/region-support.css"
        return "assets/content-assets/" + path[len("assets/") :]
    if path.startswith("assets/modules/"):
        if path.endswith("/_module-support.css"):
            return "assets/content-assets/_support/module-support.css"
        return "assets/content-assets/" + path[len("assets/") :]
    if path.startswith("assets/layouts/"):
        if path.endswith("/_layout-support.css"):
            return "assets/content-assets/_support/layout-support.css"
        return "assets/content-assets/" + path[len("assets/") :]
    if path.startswith("assets/feedback/"):
        if path.endswith("/_feedback-support.css"):
            return "assets/content-assets/_support/feedback-support.css"
        return "assets/content-assets/" + path[len("assets/") :]
    if path.startswith("assets/states/") or path.startswith("assets/overlays/") or path.startswith("assets/component-combos/"):
        if path.endswith("/_component-combo-support.css"):
            return "assets/content-assets/_support/component-combo-support.css"
        return "assets/content-assets/" + path[len("assets/") :]
    return path


def output_slot(asset_type: str, mapped_slot: str, fallback_slot: str) -> str:
    if mapped_slot:
        return mapped_slot
    if normalize(asset_type) in {"overlay", "drawer", "modal", "confirm-modal", "popconfirm"}:
        return "OVERLAY_SLOT"
    return fallback_slot or "PAGE_CONTENT_SLOT"


def make_selected_asset(
    asset: Dict[str, str],
    *,
    order: int,
    insert_slot: str,
    required: bool,
    reason: str,
    variant_options: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        "asset_id": asset.get("asset_id"),
        "asset_name": asset.get("asset_name"),
        "asset_layer": asset.get("asset_layer"),
        "asset_type": asset.get("asset_type"),
        "variant": asset.get("variant"),
        "html_path": normalize_asset_path(asset.get("html_path", "")),
        "css_path": normalize_asset_path(asset.get("css_path", "")),
        "insert_slot": insert_slot,
        "order": order,
        "required": required,
        "reason": reason,
    }
    if variant_options:
        entry["variant_options"] = variant_options
    return entry


def select_required_assets(recipe: Dict[str, str], data: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, Any]]:
    asset_index = assets_by_id(data)
    rows = [
        r
        for r in data["recipe_asset_map"]
        if r.get("recipe_id") == recipe.get("recipe_id") and r.get("required", "").lower() == "true"
    ]
    rows.sort(key=lambda r: int(r.get("asset_order") or 999))
    selected: List[Dict[str, Any]] = []
    fallback_slot = recipe.get("slot_output", "PAGE_CONTENT_SLOT")
    for row in rows:
        asset = resolve_asset(asset_index, row.get("candidate_asset_id", ""))
        if not asset:
            selected.append(
                {
                    "asset_id": row.get("candidate_asset_id"),
                    "html_path": "",
                    "insert_slot": row.get("slot") or fallback_slot,
                    "order": int(row.get("asset_order") or 999) * 10,
                    "required": row.get("required", "").lower() == "true",
                    "status": "missing",
                    "reason": "recipe_required_but_not_found",
                }
            )
            continue
        variant_meta = _build_variant_options(row)
        selected.append(
            make_selected_asset(
                asset,
                order=int(row.get("asset_order") or 999) * 10,
                insert_slot=output_slot(asset.get("asset_type", ""), row.get("slot", ""), fallback_slot),
                required=row.get("required", "").lower() == "true",
                reason=row.get("notes", "recipe asset map"),
                variant_options=variant_meta,
            )
        )
    return selected


def _build_variant_options(row: Dict[str, str]) -> Dict[str, Any] | None:
    asset_family = row.get("asset_family", "").strip()
    available_raw = row.get("available_variants", "").strip()
    if not asset_family or not available_raw:
        return None
    available = [v.strip() for v in available_raw.split(";") if v.strip()]
    if not available:
        return None
    return {
        "asset_family": asset_family,
        "default_variant": row.get("default_variant", available[0] if available else "").strip(),
        "available_variants": available,
        "variant_dimension": row.get("variant_dimension", "").strip(),
    }


def recipe_optional_asset_ids(recipe: Dict[str, str], data: Dict[str, List[Dict[str, str]]]) -> set[str]:
    asset_index = assets_by_id(data)
    allowed: set[str] = set()
    for row in data["recipe_asset_map"]:
        if row.get("recipe_id") != recipe.get("recipe_id"):
            continue
        if row.get("required", "").lower() == "true":
            continue
        asset = resolve_asset(asset_index, row.get("candidate_asset_id", ""))
        if asset and asset.get("asset_id"):
            allowed.add(str(asset.get("asset_id")))

    optional_modules = [item.strip() for item in str(recipe.get("optional_modules", "")).split(";") if item.strip()]
    if not optional_modules:
        return allowed

    for token in optional_modules:
        alias_id = RECIPE_OPTIONAL_ASSET_ALIASES.get(token)
        if alias_id:
            asset = resolve_asset(asset_index, alias_id)
            if asset and asset.get("asset_id"):
                allowed.add(str(asset.get("asset_id")))
            continue
        token_canonical = canonical_asset_id(token)
        for asset_id, asset in asset_index.items():
            if token_canonical and (
                token_canonical in canonical_asset_id(asset_id)
                or token_canonical in canonical_asset_id(asset.get("asset_name", ""))
            ):
                allowed.add(asset_id)
    return allowed


def asset_keyword_weight(query: str, asset_id: str, page_type: str, data: Dict[str, List[Dict[str, str]]]) -> float:
    q = normalize(query)
    total = 0.0
    for row in data.get("asset_keywords", []):
        if row.get("asset_id") != asset_id:
            continue
        if not page_type_matches(row.get("page_type", ""), page_type):
            continue
        keyword = normalize(row.get("keyword", ""))
        if keyword and keyword in q:
            try:
                total += float(row.get("weight", 0) or 0)
            except ValueError:
                total += 0.0
    return total


def asset_keyword_match(query: str, asset: Dict[str, str], page_type: str, data: Dict[str, List[Dict[str, str]]]) -> bool:
    if asset_keyword_weight(query, str(asset.get("asset_id", "")), page_type, data) > 0:
        return True
    fields = ["asset_name", "keywords", "conditions", "validation", "notes"]
    return keyword_bonus(query, asset, fields, 1.0) > 0


def select_optional_assets(
    query: str,
    recipe: Dict[str, str],
    required_ids: set[str],
    data: Dict[str, List[Dict[str, str]]],
) -> List[Dict[str, Any]]:
    page_type = recipe.get("page_type", "")
    allowed_ids = recipe_optional_asset_ids(recipe, data)
    candidates = [
        a
        for a in data["assets"]
        if page_type_matches(a.get("page_type", ""), page_type)
        and a.get("asset_id") not in required_ids
        and a.get("asset_id") in allowed_ids
    ]
    ranked = rank_rows(query, candidates, ["asset_name", "keywords", "conditions", "validation", "notes"], 12)
    optional: List[Dict[str, Any]] = []
    base_order = 1000
    fallback_slot = recipe.get("slot_output", "PAGE_CONTENT_SLOT")
    for index, (score, asset) in enumerate(ranked, start=1):
        if not asset_keyword_match(query, asset, page_type, data):
            continue
        score += asset_keyword_weight(query, str(asset.get("asset_id", "")), page_type, data)
        threshold = 3.0 if page_type == "TablePage" else 2.2
        if score < threshold:
            continue
        optional.append(
            make_selected_asset(
                asset,
                order=base_order + index * 10,
                insert_slot=output_slot(asset.get("asset_type", ""), "", fallback_slot),
                required=False,
                reason="keyword/rule matched optional asset",
            )
        )
    return optional[:8]


def matched_rules(query: str, page_type: str, asset_ids: set[str], data: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, str]]:
    rows = []
    for row in data["rules"]:
        if row.get("page_type") not in (page_type, "Any", ""):
            continue
        if row.get("asset_id") and row.get("asset_id") not in asset_ids:
            continue
        rows.append(row)
    ranked = rank_rows(query, rows, ["rule_name", "rule", "keywords", "recommended_position"], 20)
    return [row for score, row in ranked]


def support_css_paths(assets: List[Dict[str, Any]]) -> List[str]:
    seen: List[str] = []
    for asset in assets:
        css = asset.get("css_path", "")
        if css and css not in seen:
            seen.append(css)
    return seen


def validate_paths(root: Path, assets: List[Dict[str, Any]], support_css: List[str]) -> Tuple[List[Dict[str, str]], List[str]]:
    unsupported: List[Dict[str, str]] = []
    validation_targets: List[str] = []
    for asset in assets:
        html_path = asset.get("html_path", "")
        if html_path and not (root / html_path).exists():
            unsupported.append(
                {
                    "asset_id": str(asset.get("asset_id", "")),
                    "reason": "html_path_missing",
                    "html_path": html_path,
                }
            )
    for css_path in support_css:
        if not (root / css_path).exists():
            validation_targets.append(f"missing_support_css:{css_path}")
    return unsupported, validation_targets


def build_overlay_decision(query: str, route: Dict[str, str], data: Dict[str, List[Dict[str, str]]]) -> Dict[str, Any]:
    asset_index = assets_by_id(data)
    overlay_asset = resolve_asset(asset_index, "OV_MODAL_FUNCTIONAL")
    required_assets: List[Dict[str, Any]] = []
    if overlay_asset:
        required_assets.append(
            make_selected_asset(
                overlay_asset,
                order=10,
                insert_slot="OVERLAY_SLOT",
                required=True,
                reason="overlay route matched modal editing intent",
            )
        )
    support_css = support_css_paths(required_assets)
    unsupported, validation_notes = validate_paths(ROOT, required_assets, support_css)
    read_order = [
        {
            "asset_id": asset.get("asset_id"),
            "html_path": asset.get("html_path"),
            "insert_slot": asset.get("insert_slot"),
            "order": asset.get("order"),
            "required": asset.get("required"),
        }
        for asset in required_assets
    ]
    return {
        "decision_type": "CONTENT_ASSET_DECISION",
        "query": query,
        "scope": route.get("scope", "Page Overlay"),
        "overlay_type": route.get("overlay_type", "Modal"),
        "page_type": route.get("output_page_type", "None"),
        "recipe_id": route.get("recipe_id", "overlay.modal.functional"),
        "shell": route.get("shell", "admin-side-shell"),
        "page_block": route.get("page_block", "None"),
        "recipe": {
            "recipe_id": route.get("recipe_id", "overlay.modal.functional"),
            "recipe_name": "Functional Modal Overlay",
            "default_region_order": "modal",
            "slot_output": "OVERLAY_SLOT",
            "validation": "Must mount to OVERLAY_SLOT and must not become CreatePage/EditPage.",
        },
        "required_assets": required_assets,
        "optional_assets": [],
        "selected_assets": required_assets,
        "assets": required_assets,
        "support_css": support_css,
        "unsupported": unsupported,
        "read_order": read_order,
        "matched_rules": [
            {
                "rule_id": "overlay_mount",
                "asset_id": "OV_MODAL_FUNCTIONAL",
                "rule_type": "feedback_state_overlay",
                "rule": "Modal must mount to OVERLAY_SLOT and keep page context intact.",
                "recommended_position": "OVERLAY_SLOT",
            }
        ],
        "validation_targets": [
            "overlay_route_priority",
            "modal_mounted_to_overlay_slot",
            "support_css_exists",
            "read_order_paths_exist",
            *validation_notes,
        ],
    }


def build_decision(query: str, data_dir: Path = DATA_DIR) -> Dict[str, Any]:
    data = load_data(data_dir)
    route = select_page_route(query, data)
    if route.get("scope") == "Page Overlay":
        return build_overlay_decision(query, route, data)
    page_type = route.get("page_type", "TablePage")
    recipe = select_recipe(query, page_type, route.get("recipe_id", ""), data)
    required_assets = select_required_assets(recipe, data)
    required_ids = {str(asset.get("asset_id", "")) for asset in required_assets}
    optional_assets = select_optional_assets(query, recipe, required_ids, data)
    selected_assets = sorted(required_assets + optional_assets, key=lambda item: int(item.get("order", 9999)))
    supported_assets = [asset for asset in selected_assets if asset.get("html_path")]
    asset_ids = {str(asset.get("asset_id", "")) for asset in supported_assets}
    rules = matched_rules(query, page_type, asset_ids, data)
    support_css = support_css_paths(supported_assets)
    unsupported, validation_notes = validate_paths(ROOT, supported_assets, support_css)
    unsupported.extend(asset for asset in required_assets if asset.get("status") == "missing")
    read_order = [
        {
            "asset_id": asset.get("asset_id"),
            "html_path": asset.get("html_path"),
            "insert_slot": asset.get("insert_slot"),
            "order": asset.get("order"),
            "required": asset.get("required"),
        }
        for asset in supported_assets
    ]
    # Collect variant options from required assets that have an asset_family with multiple variants
    variant_options = [
        asset.get("variant_options")
        for asset in required_assets
        if asset.get("variant_options")
    ]
    validation_targets = [
        "route_matches_recipe",
        "all_required_assets_present",
        "support_css_exists",
        "read_order_paths_exist",
        "no_unknown_classes",
        "no_unplanned_layout",
    ]
    validation_targets.extend(validation_notes)
    return {
        "decision_type": "CONTENT_ASSET_DECISION",
        "query": query,
        "scope": route.get("scope", "Full Page"),
        "overlay_type": route.get("overlay_type", ""),
        "page_type": page_type,
        "recipe_id": recipe.get("recipe_id"),
        "shell": route.get("shell", "admin-side-shell"),
        "page_block": route.get("page_block", "None"),
        "recipe": {
            "recipe_id": recipe.get("recipe_id"),
            "recipe_name": recipe.get("recipe_name"),
            "default_region_order": recipe.get("default_region_order"),
            "slot_output": recipe.get("slot_output", "PAGE_CONTENT_SLOT"),
            "validation": recipe.get("validation", ""),
        },
        "required_assets": required_assets,
        "optional_assets": optional_assets,
        "selected_assets": supported_assets,
        "assets": supported_assets,
        "support_css": support_css,
        "variant_options": variant_options,
        "unsupported": unsupported,
        "read_order": read_order,
        "matched_rules": [
            {
                "rule_id": row.get("rule_id"),
                "asset_id": row.get("asset_id"),
                "rule_type": row.get("rule_type"),
                "rule": row.get("rule"),
                "recommended_position": row.get("recommended_position"),
            }
            for row in rules[:12]
        ],
        "validation_targets": validation_targets,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Search XFT content assets and output CONTENT_ASSET_DECISION JSON.")
    parser.add_argument("query", help="用户页面需求")
    parser.add_argument("--data-dir", default=str(DATA_DIR), help="数据表目录")
    parser.add_argument("--pretty", action="store_true", help="格式化 JSON 输出")
    args = parser.parse_args()

    decision = build_decision(args.query, Path(args.data_dir))
    print(json.dumps(decision, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
