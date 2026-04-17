from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BEGIN_RE = re.compile(r"<!-- AUTO-SYNC:BEGIN (?P<meta>.+?) -->")
END_RE = re.compile(r"<!-- AUTO-SYNC:END block_id=(?P<block_id>[a-zA-Z0-9_\-]+) -->")
AUTO_LINE_RE = re.compile(
    r"<!-- AUTO-SYNC:BEGIN block_id=(?P<block_id>[a-zA-Z0-9_\-]+) "
    r"source=(?P<source>[^ ]+) mode=(?P<mode>[a-z_]+) -->"
)
SUPPORTED_SYNC_MODES = {"replace_block", "merge_unique_list"}
SUPPORTED_CREATE_POLICIES = {"must_exist", "create_if_missing"}
SUPPORTED_DELETION_POLICIES = {"mark_gap", "deprecated", "clear_block_keep_page", "skip_with_warning"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_registry(registry_path: Path, domain: str | None) -> list[dict[str, Any]]:
    payload = read_json_file(registry_path, {})
    domains = payload.get("domains")
    if not isinstance(domains, dict):
        raise ValueError("registry.yaml 缺少 domains")
    mappings: list[dict[str, Any]] = []
    for domain_name, domain_payload in domains.items():
        if domain and domain_name != domain:
            continue
        if not isinstance(domain_payload, dict):
            continue
        if not bool(domain_payload.get("enabled", True)):
            continue
        domain_mappings = domain_payload.get("mappings")
        if not isinstance(domain_mappings, list):
            continue
        for item in domain_mappings:
            if isinstance(item, dict):
                mapping = dict(item)
                mapping["domain"] = domain_name
                mappings.append(mapping)
    mappings.sort(key=lambda item: int(item.get("priority", 0)), reverse=True)
    return mappings


def validate_registry(mappings: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    for item in mappings:
        label = f"{item.get('raw_source')} -> {item.get('target_page')}#{item.get('block_id')}"
        if str(item.get("sync_mode") or "") not in SUPPORTED_SYNC_MODES:
            issues.append(f"registry 非法 sync_mode: {label}")
        if str(item.get("create_policy") or "") not in SUPPORTED_CREATE_POLICIES:
            issues.append(f"registry 非法 create_policy: {label}")
        if str(item.get("deletion_policy") or "") not in SUPPORTED_DELETION_POLICIES:
            issues.append(f"registry 非法 deletion_policy: {label}")
        if not str(item.get("extract_rule") or "").strip():
            issues.append(f"registry 缺少 extract_rule: {label}")
        if not str(item.get("raw_source") or "").startswith("knowledge/"):
            issues.append(f"registry raw_source 必须是仓库相对路径: {label}")
        if not str(item.get("target_page") or "").startswith("knowledge/"):
            issues.append(f"registry target_page 必须是仓库相对路径: {label}")
    return issues


def changed_raw_files(knowledge_root: Path, last_run_utc: str | None) -> list[str]:
    raw_root = knowledge_root / "raw"
    files = sorted(p for p in raw_root.rglob("*.md") if p.is_file() and "manifests" not in p.parts)
    if not last_run_utc:
        return [f"knowledge/{p.relative_to(knowledge_root).as_posix()}" for p in files]
    try:
        last_dt = datetime.fromisoformat(last_run_utc.replace("Z", "+00:00"))
    except ValueError:
        return [f"knowledge/{p.relative_to(knowledge_root).as_posix()}" for p in files]
    changed: list[str] = []
    for file in files:
        modified = datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc)
        if modified > last_dt:
            changed.append(f"knowledge/{file.relative_to(knowledge_root).as_posix()}")
    return changed


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = "_root"
    sections[current] = []
    for line in text.splitlines():
        if line.startswith("## "):
            current = line.strip()
            sections[current] = []
            continue
        sections.setdefault(current, []).append(line)
    return sections


def extract_page_cards(text: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    cards: list[dict[str, Any]] = []
    current_section = ""
    current_card: dict[str, Any] | None = None
    for raw_line in lines:
        line = raw_line.rstrip()
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue
        if line.startswith("### "):
            if current_card:
                cards.append(current_card)
            current_card = {"section": current_section, "title": line[4:].strip(), "fields": {}}
            continue
        if current_card is None:
            continue
        if not line.startswith("- "):
            continue
        body = line[2:]
        if "：" not in body:
            continue
        key, value = body.split("：", 1)
        current_card["fields"][key.strip()] = value.strip()
    if current_card:
        cards.append(current_card)
    return cards


def extract_gap_lines(text: str) -> list[str]:
    sections = split_sections(text)
    for heading, body in sections.items():
        if heading.startswith("## 8."):
            return [line[2:].strip() for line in body if line.startswith("- ")]
    return []


def build_permission_intermediate(raw_text: str, raw_source: str) -> dict[str, Any]:
    cards = extract_page_cards(raw_text)
    groups: dict[str, list[str]] = {}
    for card in cards:
        section = str(card.get("section") or "").split(" ", 1)[-1]
        page_name = str(card.get("fields", {}).get("页面名") or card.get("title") or "").strip()
        if not page_name:
            continue
        groups.setdefault(section, []).append(page_name)
    for value in groups.values():
        value[:] = sorted(dict.fromkeys(value))
    page_groups = [{"group": key, "pages": groups[key]} for key in sorted(groups)]
    gaps = extract_gap_lines(raw_text)
    detail_related = [gap for gap in gaps if "权限明细" in gap or "明细视图" in gap]
    return {
        "raw_source": raw_source,
        "page_groups": page_groups,
        "page_names": sorted({name for item in page_groups for name in item["pages"]}),
        "gaps": gaps,
        "detail_view_gaps": detail_related or ["[GAP] 原始页面语义材料中尚未完整展开权限明细视图。"],
        "sources": [raw_source],
    }


def render_permission_page_group_inventory(data: dict[str, Any], target_page: str) -> str:
    title = "### 托管同步结果"
    intro = [
        title,
        "",
        f"- 来源真源：`{data['raw_source']}`",
        f"- 同步页面数：{len(data['page_names'])}",
        "",
    ]
    lines = intro
    if target_page.endswith("page-carrier-semantics-map.md"):
        lines.append("#### 页面分组清单")
        lines.append("")
        for group in data["page_groups"]:
            lines.append(f"- {group['group']}：{ '、'.join(group['pages']) }")
    else:
        lines.append("#### 由页面语义真源补充的相关入口")
        lines.append("")
        for group in data["page_groups"]:
            lines.append(f"- {group['group']}")
            for page in group["pages"]:
                lines.append(f"  - `{page}`")
    return "\n".join(lines)


def render_permission_evidence_sources(data: dict[str, Any]) -> str:
    return "\n".join([f"- `{source}`" for source in data["sources"]])


def render_permission_gap_summary(data: dict[str, Any], target_page: str) -> str:
    lines = ["### 托管同步缺口", ""]
    if target_page.endswith("permission-detail-view.md"):
        gaps = data["detail_view_gaps"]
    else:
        gaps = data["gaps"]
    for gap in gaps:
        if gap.startswith("["):
            lines.append(f"- {gap}")
        else:
            lines.append(f"- [GAP] {gap}")
    return "\n".join(lines)


def compile_block(mapping: dict[str, Any], raw_text: str, raw_source: str) -> str:
    extract_rule = str(mapping["extract_rule"])
    data = build_permission_intermediate(raw_text, raw_source)
    target_page = str(mapping["target_page"])
    if extract_rule == "permission.page_group_inventory":
        return render_permission_page_group_inventory(data, target_page)
    if extract_rule == "permission.evidence_sources":
        return render_permission_evidence_sources(data)
    if extract_rule == "permission.gap_summary":
        return render_permission_gap_summary(data, target_page)
    if extract_rule == "permission.detail_view_gap_summary":
        return render_permission_gap_summary(data, target_page)
    raise ValueError(f"未知 extract_rule: {extract_rule}")


def find_block_bounds(text: str, block_id: str) -> tuple[int, int, str, str]:
    lines = text.splitlines()
    begin_idx = -1
    end_idx = -1
    begin_line = ""
    end_line = ""
    for idx, line in enumerate(lines):
        match = AUTO_LINE_RE.fullmatch(line.strip())
        if match and match.group("block_id") == block_id:
            begin_idx = idx
            begin_line = line
            break
    if begin_idx < 0:
        raise ValueError(f"缺少 BEGIN 锚点: {block_id}")
    for idx in range(begin_idx + 1, len(lines)):
        match = END_RE.fullmatch(lines[idx].strip())
        if match and match.group("block_id") == block_id:
            end_idx = idx
            end_line = lines[idx]
            break
    if end_idx < 0:
        raise ValueError(f"缺少 END 锚点: {block_id}")
    return begin_idx, end_idx, begin_line, end_line


def merge_unique_list(existing: str, generated: str) -> str:
    values: list[str] = []
    seen: set[str] = set()
    for line in (existing.splitlines() + generated.splitlines()):
        normalized = line.strip()
        if not normalized.startswith("- "):
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        values.append(normalized)
    return "\n".join(values)


def apply_block_update(page_text: str, block_id: str, mode: str, generated: str) -> str:
    begin_idx, end_idx, begin_line, end_line = find_block_bounds(page_text, block_id)
    lines = page_text.splitlines()
    existing_inner = "\n".join(lines[begin_idx + 1 : end_idx]).strip()
    generated_inner = generated.strip()
    if mode == "merge_unique_list":
        merged = merge_unique_list(existing_inner, generated_inner)
    else:
        merged = generated_inner
    new_lines = lines[: begin_idx + 1]
    if merged:
        new_lines.extend(merged.splitlines())
    new_lines.extend([end_line])
    new_lines.extend(lines[end_idx + 1 :])
    return "\n".join(new_lines).rstrip() + "\n"


def unified_diff(old_text: str, new_text: str, path: str) -> list[str]:
    return list(
        difflib.unified_diff(
            old_text.splitlines(),
            new_text.splitlines(),
            fromfile=path,
            tofile=path,
            lineterm="",
        )
    )


def build_plan(
    repo_root: Path,
    mappings: list[dict[str, Any]],
    changed_raw: list[str],
    strict: bool,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    plans: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []
    changed_set = set(changed_raw)
    for mapping in mappings:
        raw_source = str(mapping["raw_source"])
        if changed_set and raw_source not in changed_set:
            continue
        raw_path = repo_root / raw_source
        target_page = repo_root / str(mapping["target_page"])
        if not raw_path.exists():
            policy = str(mapping.get("deletion_policy") or "mark_gap")
            if policy == "skip_with_warning":
                warnings.append(f"raw 删除，跳过同步: {raw_source}")
                continue
            generated = f"[GAP] 源文件缺失：`{raw_source}`"
        else:
            generated = compile_block(mapping, raw_path.read_text(encoding="utf-8"), raw_source)
        if not target_page.exists():
            if str(mapping.get("create_policy") or "must_exist") == "must_exist":
                errors.append(f"target page 不存在: {mapping['target_page']}")
                continue
            target_page.parent.mkdir(parents=True, exist_ok=True)
            target_page.write_text("", encoding="utf-8")
        old_text = target_page.read_text(encoding="utf-8")
        try:
            new_text = apply_block_update(old_text, str(mapping["block_id"]), str(mapping["sync_mode"]), generated)
        except ValueError as exc:
            errors.append(f"{mapping['target_page']}#{mapping['block_id']}: {exc}")
            continue
        diff_lines = unified_diff(old_text, new_text, str(mapping["target_page"]))
        plans.append(
            {
                "mapping": mapping,
                "generated": generated,
                "diff": diff_lines,
                "changed": old_text != new_text,
                "new_text": new_text,
                "raw_hash": sha256_text(raw_path.read_text(encoding="utf-8")) if raw_path.exists() else "missing",
                "output_hash": sha256_text(generated),
            }
        )
    uncovered = sorted(set(changed_raw) - {str(item["raw_source"]) for item in mappings})
    for raw_source in uncovered:
        warnings.append(f"raw 变化但无注册映射: {raw_source}")
    if strict and warnings:
        errors.extend([f"strict 模式阻断: {item}" for item in warnings])
    return plans, warnings, errors


def load_existing_state(path: Path) -> dict[tuple[str, str, str], dict[str, Any]]:
    payload = read_json_file(path, {"items": []})
    items = payload.get("items")
    if not isinstance(items, list):
        return {}
    result: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        key = (str(item.get("raw_path")), str(item.get("target_page")), str(item.get("block_id")))
        result[key] = item
    return result


def build_state(plans: list[dict[str, Any]], applied: bool, existing: dict[tuple[str, str, str], dict[str, Any]]) -> dict[str, Any]:
    items: list[dict[str, Any]] = list(existing.values())
    index = {(item["raw_path"], item["target_page"], item["block_id"]): idx for idx, item in enumerate(items) if isinstance(item, dict)}
    synced_at = now_iso()
    for plan in plans:
        mapping = plan["mapping"]
        item = {
            "raw_path": str(mapping["raw_source"]),
            "raw_hash": plan["raw_hash"],
            "target_page": str(mapping["target_page"]),
            "block_id": str(mapping["block_id"]),
            "output_hash": plan["output_hash"],
            "last_sync_status": "applied" if applied else "planned",
            "synced_at": synced_at,
        }
        key = (item["raw_path"], item["target_page"], item["block_id"])
        if key in index:
            items[index[key]] = item
        else:
            items.append(item)
    items.sort(key=lambda item: (item["raw_path"], item["target_page"], item["block_id"]))
    return {"version": 1, "items": items}


def build_report(
    changed_raw: list[str],
    plans: list[dict[str, Any]],
    warnings: list[str],
    errors: list[str],
    apply_mode: bool,
) -> str:
    planned = [plan for plan in plans if plan["changed"]]
    skipped = [plan for plan in plans if not plan["changed"]]
    lines = [
        "# Wiki Sync Report",
        "",
        f"- generated_at_utc: {now_iso()}",
        f"- mode: {'apply' if apply_mode else 'dry-run'}",
        f"- changed_raw_count: {len(changed_raw)}",
        f"- planned_update_count: {len(planned)}",
        f"- unchanged_count: {len(skipped)}",
        f"- warning_count: {len(warnings)}",
        f"- error_count: {len(errors)}",
        "",
        "## Changed Raw",
        "",
        *([f"- {item}" for item in changed_raw] if changed_raw else ["- none"]),
        "",
        "## Planned Updates",
        "",
    ]
    if planned:
        for plan in planned:
            mapping = plan["mapping"]
            lines.append(f"- {mapping['raw_source']} -> {mapping['target_page']}#{mapping['block_id']}")
    else:
        lines.append("- none")
    lines.extend(["", "## Unchanged Updates", ""])
    if skipped:
        for plan in skipped:
            mapping = plan["mapping"]
            lines.append(f"- {mapping['target_page']}#{mapping['block_id']}")
    else:
        lines.append("- none")
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in warnings] if warnings else ["- none"])
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {item}" for item in errors] if errors else ["- none"])
    lines.extend(["", "## Diff Preview", ""])
    if plans:
        for plan in plans:
            mapping = plan["mapping"]
            lines.append(f"### {mapping['target_page']}#{mapping['block_id']}")
            lines.append("")
            lines.append("```diff")
            lines.extend(plan["diff"][:120] if plan["diff"] else ["(no diff)"])
            lines.append("```")
            lines.append("")
    else:
        lines.extend(["- none", ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--only")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--domain")
    args = parser.parse_args()

    apply_mode = args.apply
    repo_root = Path(__file__).resolve().parents[2]
    knowledge_root = repo_root / "knowledge"
    reports_root = knowledge_root / "outputs" / "reports"
    registry_path = knowledge_root / "wiki_sync" / "registry.yaml"
    state_path = reports_root / "wiki_sync_state.json"
    report_path = reports_root / "wiki_sync_report.md"
    update_state_path = reports_root / "update_wiki_state.json"

    mappings = load_registry(registry_path, args.domain)
    registry_issues = validate_registry(mappings)
    update_state = read_json_file(update_state_path, {})
    last_run = str(update_state.get("last_run_utc") or "")
    changed_raw = changed_raw_files(knowledge_root, last_run or None)
    if args.only:
        raw_source = args.only.replace("\\", "/")
        if not raw_source.startswith("knowledge/"):
            raw_source = f"knowledge/{raw_source.lstrip('./')}"
        changed_raw = [raw_source]

    plans, warnings, errors = build_plan(repo_root, mappings, changed_raw, args.strict)
    errors = registry_issues + errors

    if apply_mode and not errors:
        for plan in plans:
            if not plan["changed"]:
                continue
            target_path = repo_root / str(plan["mapping"]["target_page"])
            write_text_file(target_path, plan["new_text"])

    existing_state = load_existing_state(state_path)
    write_json_file(state_path, build_state(plans, apply_mode and not errors, existing_state))
    write_text_file(report_path, build_report(changed_raw, plans, warnings, errors, apply_mode))

    print(f"wiki_sync_report={report_path}")
    print(f"wiki_sync_state={state_path}")
    print(f"mode={'apply' if apply_mode else 'dry-run'}")
    print(f"changed_raw={len(changed_raw)}")
    print(f"planned_updates={len([plan for plan in plans if plan['changed']])}")
    print(f"errors={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
