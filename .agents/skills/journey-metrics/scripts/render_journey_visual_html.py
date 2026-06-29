#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_nodes(visual_md: Path) -> list[dict[str, str]]:
    text = visual_md.read_text(encoding="utf-8")
    in_appendix = False
    nodes: list[dict[str, str]] = []
    headers: list[str] = []

    for line in text.splitlines():
        if "节点-埋点对照" in line:
            in_appendix = True
            continue
        if in_appendix and line.startswith("## "):
            break
        if not in_appendix:
            continue

        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or all(re.fullmatch(r"-+", cell or "-") for cell in cells):
            continue
        if "节点标识" in cells:
            headers = cells
            continue
        if not headers or len(cells) < len(headers):
            continue

        row = {headers[index]: cells[index] for index in range(len(headers))}
        nodes.append({
            "node_id": row.get("节点标识", ""),
            "node_name": row.get("节点名称", ""),
            "role": row.get("角色", "未知角色"),
            "source": row.get("来源", "confirmed"),
            "node_type": row.get("节点类型", ""),
            "taskNodeName": row.get("关联 taskNodeName", ""),
        })

    return nodes


def group_by_role(nodes: list[dict[str, str]]) -> list[dict[str, object]]:
    roles: dict[str, list[dict[str, str]]] = {}
    for node in nodes:
        roles.setdefault(node["role"], []).append(node)

    def sort_key(node: dict[str, str]) -> tuple[int, str]:
        match = re.match(r"N(\d+)", node.get("node_id", ""))
        return (int(match.group(1)) if match else 999999, node.get("node_id", ""))

    return [
        {"role": role, "nodes": sorted(role_nodes, key=sort_key)}
        for role, role_nodes in roles.items()
    ]


def render(template: Path, output: Path, project_name: str, title: str, summary: str, roles: list[dict[str, object]]) -> None:
    html = template.read_text(encoding="utf-8")
    html = html.replace("{{PROJECT_NAME}}", project_name)
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{SUMMARY}}", summary)
    html = html.replace("{{JOURNEY_ROLES_JSON}}", json.dumps(roles, ensure_ascii=False, indent=2))
    output.write_text(html, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render journey_visual.html from journey_visual.md appendix.")
    parser.add_argument("journey_metrics_dir", type=Path)
    parser.add_argument("--template", type=Path, default=Path(__file__).resolve().parents[1] / "assets" / "templates" / "journey_visual.html.template")
    parser.add_argument("--project-name", default="")
    args = parser.parse_args()

    root = args.journey_metrics_dir
    visual_md = root / "journey_visual.md"
    output = root / "journey_visual.html"

    if not visual_md.exists():
        raise SystemExit(f"ERROR: missing {visual_md}")
    if not args.template.exists():
        raise SystemExit(f"ERROR: missing template {args.template}")

    nodes = parse_nodes(visual_md)
    if not nodes:
        raise SystemExit("ERROR: no nodes parsed from journey_visual.md appendix")

    project_name = args.project_name or root.parents[1].name if len(root.parents) > 1 else root.name
    title = f"可视化用户旅程 - {project_name}"
    summary = f"从 journey_visual.md 附录解析 {len(nodes)} 个节点，按角色分组渲染。"
    render(args.template, output, project_name, title, summary, group_by_role(nodes))
    print(f"OK: wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
