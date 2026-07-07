#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assemble a full HTML page from shell + formal decisions + content assets.

This is the engineering assembler for xft-design:
requirement -> ROUTE_DECISION -> CONTENT_ASSET_DECISION -> ICON_DECISION ->
asset reads -> HTML assembly.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
SHELLS_DIR = ROOT / "assets" / "shells"
DESIGN_SYSTEM_DIR = ROOT / "design-systems"
DEFAULT_OUTPUT_DIR = ROOT.parents[2] / "output"


LAYOUT_SLOTS = {
    "layout.settings-anchor.basic": "SETTINGS_CONTENT_SLOT",
    "layout.detail-side.basic": "DETAIL_MAIN_SLOT",
    "layout.tabs.basic": "TAB_PANELS_SLOT",
    "layout.master-detail.basic": "DETAIL_SLOT",
}

SLOT_TEXT_ALIASES = {
    "PAGE_CONTENT_SLOT": "page-content-slot",
    "OVERLAY_SLOT": "overlay-slot",
    "TOP_NAV_SLOT": "top-nav-slot",
    "SIDER_SLOT": "sider-slot",
    "CONTEXT_NAV_SLOT": "context-nav-slot",
    "CONTENT_SLOT": "content-slot",
}


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def derive_title(query: str) -> str:
    primary = re.split(r"[，,。；;、\n]", query, maxsplit=1)[0].strip()
    return primary or "XFT 页面"


def slugify(text: str) -> str:
    base = normalize_whitespace(text).lower()
    mapping = {
        "员工台账列表页": "employee-roster",
        "员工花名册列表页": "employee-roster",
        "审批详情页": "approval-detail",
        "参数配置设置页": "settings-config",
        "成员编辑弹窗": "member-edit-modal",
        "弹窗编辑成员信息": "member-edit-modal",
    }
    for key, value in mapping.items():
        if key in text:
            return value
    slug = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return slug or "xft-page"


def extract_style_block(html: str) -> str:
    match = re.search(r"<style[^>]*>(.*?)</style>", html, flags=re.S | re.I)
    if not match:
        raise RuntimeError("No <style> block found in components.html")
    return match.group(1).strip()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def format_route_comment(route: Dict[str, Any]) -> str:
    lines = ["<!-- XFT_ROUTE"]
    for key in ["scope", "overlay_type", "page_type", "recipe_id", "shell", "page_block"]:
        if key in route:
            lines.append(f"{key}: {route.get(key, '')}")
    lines.append("-->")
    return "\n".join(lines)


def format_json_comment(label: str, data: Dict[str, Any]) -> str:
    return f"<!-- {label}\n{json.dumps(data, ensure_ascii=False, indent=2)}\n-->"


def sanitize_comment_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize_comment_payload(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_comment_payload(item) for item in value]
    if isinstance(value, str):
        out = value
        for source, target in SLOT_TEXT_ALIASES.items():
            out = out.replace(source, target)
        return out
    return value


def inject_head_styles(shell_html: str, style_blocks: List[str]) -> str:
    insertion = "".join(f"\n  <style>\n{block}\n  </style>" for block in style_blocks)
    return shell_html.replace("</title>", "</title>" + insertion, 1)


def personalize_asset_html(asset_id: str, html: str, query: str, route: Dict[str, Any]) -> str:
    title = derive_title(query)
    page_type = str(route.get("page_type", ""))
    if asset_id in {"region.page-header.basic", "region.page-header.with-actions"}:
        html = html.replace("页面标题", title)
        if page_type == "TablePage" or "列表页" in title or "台账" in title or "花名册" in title:
            html = html.replace("业务后台 / 企业管理", "组织管理 / 成员台账")
            html = html.replace("业务对象 / 详情中心", "组织管理 / 成员详情")
            html = html.replace(
                "用于承接本页的业务目标、使用范围和关键操作说明，帮助用户快速进入任务上下文。",
                "用于统一查看成员台账、按组织和状态筛选数据，并从列表直接进入详情或发起新增维护。",
            )
        elif page_type == "DetailPage" or "审批详情" in title:
            html = html.replace("业务对象 / 详情中心", "审批中心 / 单据详情")
            html = html.replace("业务后台 / 企业管理", "审批中心 / 单据详情")
            html = html.replace(
                "用于承接本页的业务目标、使用范围和关键操作说明，帮助用户快速进入任务上下文。",
                "本页用于查看审批单据的核心字段、流程状态、附件材料和处理记录，便于在完整上下文中完成审批动作。",
            )
        elif page_type == "SettingsPage" or "设置" in title or "配置" in title:
            html = html.replace("业务后台 / 企业管理", "系统设置 / 参数中心")
            html = html.replace(
                "用于承接本页的业务目标、使用范围和关键操作说明，帮助用户快速进入任务上下文。",
                "用于维护系统参数、生效范围和配置规则，并在不离开当前上下文的前提下完成变更管理。",
            )
    if asset_id == "region.table-toolbar.basic":
        html = html.replace("成员列表", title.replace("页", ""))
    if asset_id == "region.filter-bar.basic" and page_type == "SettingsPage":
        html = html.replace("请输入成员名称、编号或手机号", "请输入参数名称、配置编码或关键字")
        html = html.replace("<label class=\"field-label\">组织</label>", "<label class=\"field-label\">分组</label>")
        html = html.replace("全部组织", "全部分组")
    if asset_id == "region.detail-info-section.basic" and page_type == "DetailPage":
        html = html.replace("差旅报销审批", "供应商付款审批")
        html = html.replace("华东事业部 / 销售一部", "共享服务中心 / 财务支持")
        html = html.replace("CNY 12,860.00", "CNY 58,400.00")
        html = html.replace("2026-06-24 09:30", "2026-06-26 10:15")
        html = html.replace("差旅交通 / 住宿 / 客户拜访", "供应商付款 / 市场投放 / 服务采购")
        html = html.replace(
            "本次申请用于 6 月客户拜访差旅结算，附件已包含机票、酒店和打车发票。",
            "本次申请用于 6 月市场项目付款结算，附件已包含合同扫描件、付款申请单和发票归档材料。",
        )
    html = html.replace("当前页面", "本页")
    return html


def expand_settings_sections(base_html: str) -> str:
    variants = [
        (
            "settings-basic",
            "基础设置",
            "启用成员自动同步",
            "开启后，组织架构调整会自动同步到成员台账，并在次日生效。",
            "字段展示规则",
            "控制成员列表默认字段、详情展示顺序以及导出模板字段范围。",
            "进入配置",
        ),
        (
            "settings-scope",
            "生效范围",
            "默认适用组织",
            "限定当前配置默认作用于哪些组织、业务线或租户环境，避免跨范围误生效。",
            "灰度发布策略",
            "支持按部门、角色或站点逐步开放，变更前可先在目标范围内试运行。",
            "管理范围",
        ),
        (
            "settings-history",
            "最近变更",
            "最近一次发布时间",
            "2026-06-26 14:30 已由系统管理员发布到生产环境，并同步通知配置负责人。",
            "影响说明",
            "本次变更将更新导出字段模板和审批抄送规则，预计 10 分钟内全量生效。",
            "查看记录",
        ),
    ]
    sections: List[str] = []
    for section_id, title, title_a, desc_a, title_b, desc_b, cta in variants:
        html = base_html
        html = html.replace("基础设置", title, 1)
        html = html.replace("启用成员自动同步", title_a, 1)
        html = html.replace("开启后，组织架构调整会自动同步到成员台账，并在次日生效。", desc_a, 1)
        html = html.replace("字段展示规则", title_b, 1)
        html = html.replace("控制成员列表默认字段、详情展示顺序以及导出模板字段范围。", desc_b, 1)
        html = html.replace("进入配置", cta, 1)
        html = html.replace("<section class=\"settings-section\"", f"<section id=\"{section_id}\" class=\"settings-section\"", 1)
        sections.append(html)
    return "\n".join(sections)


def read_asset_html(asset: Dict[str, Any], query: str, route: Dict[str, Any]) -> str:
    html_path = asset.get("html_path", "")
    if not html_path:
        return ""
    html = read_text(ROOT / html_path)
    asset_id = str(asset.get("asset_id", ""))
    html = personalize_asset_html(asset_id, html, query, route)
    if asset_id == "region.setting-section.basic" and str(route.get("page_type", "")) == "SettingsPage":
        return expand_settings_sections(html)
    return html


def default_render_assets(decision: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    assets = decision.get("required_assets") or decision.get("assets") or []
    page_assets: List[Dict[str, Any]] = []
    overlay_assets: List[Dict[str, Any]] = []
    for asset in assets:
        insert_slot = str(asset.get("insert_slot", "")).lower()
        if insert_slot == "overlay-slot":
            overlay_assets.append(asset)
        else:
            page_assets.append(asset)
    return page_assets, overlay_assets


def compose_page_content(page_assets: List[Dict[str, Any]], query: str, route: Dict[str, Any]) -> str:
    if not page_assets:
        return '<div class="page-card"><div class="card-body"></div></div>'

    ordered = sorted(page_assets, key=lambda item: int(item.get("order", 9999)))
    first_layout_index = next(
        (idx for idx, asset in enumerate(ordered) if str(asset.get("asset_layer")) == "layout"),
        None,
    )
    if first_layout_index is None:
        return "\n".join(read_asset_html(asset, query, route) for asset in ordered)

    before_layout = ordered[:first_layout_index]
    layout_asset = ordered[first_layout_index]
    after_layout = ordered[first_layout_index + 1 :]

    before_html = "\n".join(read_asset_html(asset, query, route) for asset in before_layout if asset.get("html_path"))
    layout_html = read_asset_html(layout_asset, query, route)
    inner_html = "\n".join(read_asset_html(asset, query, route) for asset in after_layout if asset.get("html_path"))
    slot_name = LAYOUT_SLOTS.get(str(layout_asset.get("asset_id", "")))
    if slot_name:
        layout_html = layout_html.replace(f"<!-- {slot_name} -->", inner_html)
    else:
        layout_html = layout_html + ("\n" + inner_html if inner_html else "")

    return "\n".join(part for part in [before_html, layout_html] if part.strip())


def compose_overlay_content(overlay_assets: List[Dict[str, Any]], query: str, route: Dict[str, Any]) -> str:
    return "\n".join(read_asset_html(asset, query, route) for asset in overlay_assets if asset.get("html_path"))


def assemble_html(query: str) -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    content_module = load_module("search_content_assets", SCRIPTS_DIR / "search_content_assets.py")
    icon_module = load_module("search_icons", SCRIPTS_DIR / "search_icons.py")

    content_decision: Dict[str, Any] = content_module.build_decision(query, content_module.DATA_DIR)
    icon_decision: Dict[str, Any] = icon_module.build_decision(query)
    route = {
        "scope": content_decision.get("scope", "Full Page"),
        "overlay_type": content_decision.get("overlay_type", "None") or "None",
        "page_type": content_decision.get("page_type", "Unknown"),
        "recipe_id": content_decision.get("recipe_id", ""),
        "shell": content_decision.get("shell", "admin-side-shell"),
        "page_block": content_decision.get("page_block", "None"),
    }

    shell_path = SHELLS_DIR / f"{route['shell']}.html"
    shell_html = read_text(shell_path)
    tokens_css = read_text(DESIGN_SYSTEM_DIR / "tokens.css").strip()
    components_css = extract_style_block(read_text(DESIGN_SYSTEM_DIR / "components.html"))
    support_css_blocks = [
        read_text(ROOT / css_path).strip()
        for css_path in content_decision.get("support_css", [])
        if css_path and (ROOT / css_path).exists()
    ]

    shell_html = inject_head_styles(shell_html, [tokens_css, components_css, *support_css_blocks])

    page_assets, overlay_assets = default_render_assets(content_decision)
    page_content_html = compose_page_content(page_assets, query, route)
    overlay_html = compose_overlay_content(overlay_assets, query, route)

    shell_html = shell_html.replace("<!-- PAGE_CONTENT_SLOT -->", page_content_html, 1)
    shell_html = shell_html.replace("<!-- OVERLAY_SLOT -->", overlay_html, 1)
    shell_html = shell_html.replace("<title>Enterprise Admin Side Shell</title>", f"<title>{derive_title(query)}</title>", 1)

    route_comment = format_route_comment(route)
    content_comment = format_json_comment("CONTENT_ASSET_DECISION", sanitize_comment_payload(content_decision))
    icon_comment = format_json_comment("ICON_DECISION", sanitize_comment_payload(icon_decision))

    final_html = shell_html.replace(
        "<!DOCTYPE html>",
        "<!DOCTYPE html>\n" + route_comment,
        1,
    )
    final_html = final_html.replace("<body>", "<body>\n  " + content_comment + "\n  " + icon_comment, 1)
    return final_html, route, content_decision, icon_decision


def write_output(html: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble an XFT page from formal decisions and local assets.")
    parser.add_argument("query", help="页面需求")
    parser.add_argument("--output", help="输出 HTML 路径")
    parser.add_argument("--slug", help="输出 slug")
    args = parser.parse_args()

    html, route, content_decision, icon_decision = assemble_html(args.query)
    slug = args.slug or slugify(args.query)
    output_path = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR / f"{slug}-{date.today().isoformat()}-v1.html"
    write_output(html, output_path)
    print(
        json.dumps(
            {
                "output": str(output_path),
                "route": route,
                "recipe_id": content_decision.get("recipe_id", ""),
                "icon_count": len(icon_decision.get("icons", [])),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
