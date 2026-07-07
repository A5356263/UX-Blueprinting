#!/usr/bin/env python3
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List


BUNDLED_SKILL_ROOT = Path(__file__).resolve().parents[1]


OLD_TOKEN_VARS = [
    "--color-brand-primary",
    "--color-brand-primary-hover",
    "--color-brand-light",
    "--color-text-primary",
    "--color-text-regular",
    "--color-text-secondary",
    "--color-text-placeholder",
    "--color-text-disabled",
    "--color-bg-page",
    "--color-bg-container",
    "--color-bg-subtle",
    "--color-bg-hover",
    "--color-bg-active",
    "--color-border-light",
    "--color-border-regular",
    "--color-border-strong",
    "--color-danger",
    "--radius-sm",
    "--radius-md",
    "--radius-lg",
    "--radius-xl",
    "--shadow-small",
    "--shadow-medium",
    "--shadow-large",
]

PLACEHOLDER_TEXTS = [
    "页面主体内容将在这里填充",
    "页面标签",
    "当前页面",
    "字段名称",
    "页面标题",
]

FULL_PAGE_MARKERS = [
    'class="top-nav"',
    'class="side-nav"',
    'class="xft-tab-header"',
    'class="page-content"',
    'class="micro-wrapper"',
    'class="page-content-container"',
]

BANNED_CLASS_PREFIXES = ("custom", "new", "random")


class OverlayRootParser(HTMLParser):
    """Walk the HTML tree to check overlay-root contents.

    Only div tags are tracked for nesting depth, so void elements
    (input, br, img, svg, path, etc.) do not corrupt the counter.
    """

    def __init__(self):
        super().__init__()
        self.in_overlay_root = False
        self.depth = 0
        self.has_overlay_root = False
        self.has_data_overlay = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = dict(attrs)

        if self.in_overlay_root:
            if tag == "div":
                self.depth += 1
            if "data-overlay" in attrs_dict:
                self.has_data_overlay = True
            return

        if tag == "div" and attrs_dict.get("id") == "overlay-root":
            self.in_overlay_root = True
            self.has_overlay_root = True
            self.depth = 1
            if "data-overlay" in attrs_dict:
                self.has_data_overlay = True

    def handle_startendtag(self, tag, attrs):
        # XHTML-style self-closing tags (e.g. <br/>)
        if self.in_overlay_root:
            attrs_dict = dict(attrs)
            if "data-overlay" in attrs_dict:
                self.has_data_overlay = True

    def handle_endtag(self, tag):
        if self.in_overlay_root and tag.lower() == "div":
            self.depth -= 1
            if self.depth <= 0:
                self.in_overlay_root = False
                self.depth = 0


def extract_route(html: str) -> Dict[str, str]:
    match = re.search(r"<!--\s*XFT_ROUTE(?P<body>.*?)-->", html, flags=re.S)
    if not match:
        return {}
    route = {}
    for line in match.group("body").splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        route[key.strip()] = value.strip()
    return route


def strip_route(html: str) -> str:
    return re.sub(r"<!--\s*XFT_ROUTE.*?-->", "", html, flags=re.S)


def extract_content_asset_decision(html: str) -> Dict[str, object]:
    match = re.search(r"<!--\s*CONTENT_ASSET_DECISION(?P<body>.*?)-->", html, flags=re.S)
    if not match:
        return {}
    body = match.group("body").strip()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"_invalid_json": body}


def extract_icon_decision(html: str) -> Dict[str, object]:
    match = re.search(r"<!--\s*ICON_DECISION(?P<body>.*?)-->", html, flags=re.S)
    if not match:
        return {}
    body = match.group("body").strip()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"_invalid_json": body}


def main() -> int:
    args = sys.argv[1:]
    check_style_rgba = "--check-style-rgba" in args
    positional = [a for a in args if not a.startswith("--")]

    if len(positional) != 1:
        print("Usage: python3 scripts/check_skill_output.py output/<page-type>-<date>-v<N>.html [--check-style-rgba]")
        return 1

    html_path = Path(positional[0])
    if not html_path.exists():
        print("FAIL: check_skill_output")
        print(f"- [P0] file not found: {html_path}")
        print("- [P0] expected final artifact path: output/<slug>-<date>-v<N>.html")
        return 1

    if not html_path.is_file():
        print("FAIL: check_skill_output")
        print(f"- [P0] path is not a file: {html_path}")
        return 1

    html = html_path.read_text(encoding="utf-8")
    route = extract_route(html)
    html_without_route = strip_route(html)
    decision = extract_content_asset_decision(html)
    icon_decision = extract_icon_decision(html)

    errors: List[str] = []
    warnings: List[str] = []

    if not route:
        errors.append("[P0] missing XFT_ROUTE")
    if not decision:
        errors.append("[P0] missing CONTENT_ASSET_DECISION")
    elif "_invalid_json" in decision:
        errors.append("[P0] CONTENT_ASSET_DECISION is not valid JSON")
    if icon_decision and "_invalid_json" in icon_decision:
        errors.append("[P0] ICON_DECISION is not valid JSON")

    normalized_path = html_path.as_posix()
    if "output/archive/" in normalized_path:
        errors.append("[P0] output must not be written to output/archive/")
    elif not re.search(r"(?:^|/)output/[a-z0-9-]+-\d{4}-\d{2}-\d{2}-v\d+\.html$", normalized_path):
        errors.append("[P0] output filename must match output/{slug}-{YYYY-MM-DD}-v{N}.html")

    route_at_top = re.search(
        r"^\s*<!DOCTYPE html>\s*<!--\s*XFT_ROUTE.*?-->\s*<html\b",
        html,
        flags=re.S | re.I,
    )
    if route and not route_at_top:
        errors.append("[P0] XFT_ROUTE must appear at the top, immediately after <!DOCTYPE html>")

    if re.search(r"<link[^>]+rel=[\"']stylesheet[\"']", html, flags=re.I):
        errors.append("[P0] external stylesheet link found")

    if "../components.css" in html:
        errors.append("[P0] found ../components.css reference")

    if re.search(r"<!--\s*(TOP_NAV_SLOT|SIDER_SLOT|CONTEXT_NAV_SLOT|PAGE_CONTENT_SLOT|CONTENT_SLOT|OVERLAY_SLOT)\s*-->", html_without_route):
        errors.append("[P0] unresolved shell slot comment remains")

    if "TOP_NAV_SLOT" in html_without_route or "SIDER_SLOT" in html_without_route or "CONTEXT_NAV_SLOT" in html_without_route or "PAGE_CONTENT_SLOT" in html_without_route or "CONTENT_SLOT" in html_without_route:
        errors.append("[P0] unresolved content slot marker remains")

    if "BASIC_INTERACTION_RUNTIME" in html_without_route:
        errors.append("[P0] basic interaction runtime placeholder remains")

    for text in PLACEHOLDER_TEXTS:
        if text in html_without_route:
            errors.append(f"[P0] placeholder text remains: {text}")

    if re.search(r"\sstyle\s*=", html, flags=re.I):
        errors.append("[P0] inline style attribute remains")

    inline_styles = re.findall(r"style=[\"']([^\"']*)[\"']", html, flags=re.I)
    for value in inline_styles:
        lower = value.lower()
        if "rgba(" in lower:
            errors.append("[P0] inline style contains rgba()")
        if re.search(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b", value):
            errors.append("[P0] inline style contains bare color value")

    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.S | re.I)
    if not style_blocks:
        errors.append("[P0] no <style> blocks found")
    else:
        first_style = style_blocks[0]
        if "design-systems/xft/tokens.css" not in first_style:
            errors.append("[P0] first <style> block must be injected tokens.css")

    if check_style_rgba:
        for block in style_blocks[1:]:
            if "rgba(" in block.lower():
                block_label = "shell base CSS" if "--top-nav-height" in block else "non-token style block"
                warnings.append(f"[WARN] style block contains rgba(); verify it belongs to {block_label}")
                break

    for block in style_blocks:
        for token_var in OLD_TOKEN_VARS:
            pattern = r"(?<![A-Za-z0-9-])" + re.escape(token_var) + r"(?![A-Za-z0-9-])"
            if re.search(pattern, block):
                errors.append(f"[P0] legacy token variable found: {token_var}")

    for prefix in BANNED_CLASS_PREFIXES:
        if re.search(rf'class=["\'][^"\']*\b{re.escape(prefix)}[-_a-zA-Z0-9]*', html):
            errors.append(f"[P0] banned class prefix found: {prefix}")

    scope = route.get("scope")
    overlay_type = route.get("overlay_type")
    route_has_overlay = bool(overlay_type and overlay_type != "None")

    # Parse overlay-root with HTMLParser (avoids non-greedy regex truncation)
    overlay_parser = OverlayRootParser()
    overlay_parser.feed(html)

    if scope == "Full Page":
        for marker in FULL_PAGE_MARKERS:
            if marker not in html:
                errors.append(f"[P0] Full Page missing required structure: {marker}")

        if not overlay_parser.has_overlay_root:
            errors.append("[P0] Full Page missing overlay-root")

    if route_has_overlay:
        if not overlay_parser.has_overlay_root:
            errors.append("[P0] overlay-root missing for overlay route")
        elif not overlay_parser.has_data_overlay:
            errors.append("[P0] overlay is not mounted inside overlay-root (data-overlay attribute not found)")

    if decision and "_invalid_json" not in decision:
        root = BUNDLED_SKILL_ROOT
        support_css = decision.get("support_css", [])
        if isinstance(support_css, list):
            for css_path in support_css:
                if isinstance(css_path, str) and not (root / css_path).exists():
                    errors.append(f"[P0] support_css path not found: {css_path}")

        read_order = decision.get("read_order", [])
        if isinstance(read_order, list):
            for item in read_order:
                if not isinstance(item, dict):
                    continue
                html_ref = item.get("html_path")
                if isinstance(html_ref, str) and html_ref and not (root / html_ref).exists():
                    errors.append(f"[P0] read_order html_path not found: {html_ref}")

    if icon_decision and "_invalid_json" not in icon_decision:
        root = BUNDLED_SKILL_ROOT
        icons = icon_decision.get("icons", [])
        if isinstance(icons, list):
            for item in icons:
                if not isinstance(item, dict):
                    continue
                svg_path = item.get("svg_path")
                if isinstance(svg_path, str) and svg_path:
                    if not (root / svg_path).exists():
                        errors.append(f"[P0] ICON_DECISION svg_path not found: {svg_path}")

    if errors:
        print("FAIL: check_skill_output")
        for item in errors:
            print(f"- {item}")
        for item in dict.fromkeys(warnings):
            print(f"- {item}")
        return 1

    if warnings:
        print("WARN: check_skill_output")
        for item in dict.fromkeys(warnings):
            print(f"- {item}")
        return 0

    print("PASS: check_skill_output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
BUNDLED_SKILL_ROOT = Path(__file__).resolve().parents[1]
