from __future__ import annotations

from packages.common import get_project_memory_dir, get_project_workspace_dir
from packages.memory_layer.memory_index import now_iso, read_json


def _titles(items: list[dict[str, object]]) -> list[str]:
    return [str(item.get("title") or item.get("memory_id") or "") for item in items if isinstance(item, dict)]


def _render_section(title: str, items: list[str]) -> list[str]:
    lines = [f"## {title}", ""]
    if not items:
        lines.append("- none")
    else:
        lines.extend(f"- {item}" for item in items)
    lines.append("")
    return lines


def run_memory_summary(project_id: str) -> int:
    runtime_memory_dir = get_project_memory_dir(project_id)
    workspace_dir = get_project_workspace_dir(project_id)
    extracted_payload = read_json(runtime_memory_dir / "extracted_memory_candidates.json")
    accepted_payload = read_json(runtime_memory_dir / "accepted_memory_items.json")

    candidates = [item for item in extracted_payload.get("candidates", []) if isinstance(item, dict)]
    accepted_items = [item for item in accepted_payload.get("items", []) if isinstance(item, dict)]
    accepted_ids = {str(item.get("memory_id") or "") for item in accepted_items}

    generic_patterns = [item for item in candidates if item.get("kind") == "pattern" and item.get("scope") == "generic"]
    domain_patterns = [item for item in candidates if item.get("kind") == "pattern" and item.get("scope") == "domain"]
    failure_modes = [item for item in candidates if item.get("kind") == "failure_mode"]
    capability_insights = [item for item in candidates if item.get("kind") == "capability_insight"]
    candidate_only = [item for item in candidates if str(item.get("memory_id") or "") not in accepted_ids]

    lines = [
        "# Memory Summary",
        "",
        f"- project_id: {project_id}",
        f"- generated_at: {now_iso()}",
        "",
    ]
    lines.extend(_render_section("本次新增的通用模式", _titles(generic_patterns)))
    lines.extend(_render_section("本次新增的领域模式", _titles(domain_patterns)))
    lines.extend(_render_section("本次识别的失败模式", _titles(failure_modes)))
    lines.extend(_render_section("本次新增的 capability insight", _titles(capability_insights)))
    lines.extend(_render_section("进入长期 memory 的条目", _titles(accepted_items)))
    lines.extend(_render_section("仅作为候选、未进入长期 memory 的条目", _titles(candidate_only)))
    lines.extend(
        _render_section(
            "当前偏好骨架位置",
            [
                "memory/preferences/quality_preferences.md",
                "memory/preferences/preference_rules.yaml",
            ],
        )
    )

    workspace_dir.mkdir(parents=True, exist_ok=True)
    output_path = workspace_dir / "memory_summary.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Memory summary written: {output_path}")
    return 0
