from __future__ import annotations

import re
from pathlib import Path

import yaml


BEGIN_RE = re.compile(
    r"<!-- AUTO-SYNC:BEGIN block_id=(?P<block_id>[a-zA-Z0-9_\-]+) "
    r"source=(?P<source>[^ ]+) mode=(?P<mode>[a-z_]+) -->"
)
END_RE = re.compile(r"<!-- AUTO-SYNC:END block_id=(?P<block_id>[a-zA-Z0-9_\-]+) -->")
SUPPORTED_MODES = {"replace_block", "merge_unique_list"}


def read_registry(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return []
    if payload is None:
        return []
    domains = payload.get("domains")
    if not isinstance(domains, dict):
        return []
    mappings: list[dict[str, object]] = []
    for domain_payload in domains.values():
        if not isinstance(domain_payload, dict):
            continue
        domain_mappings = domain_payload.get("mappings")
        if not isinstance(domain_mappings, list):
            continue
        for item in domain_mappings:
            if isinstance(item, dict):
                mappings.append(item)
    return mappings


def collect_page_blocks(text: str) -> tuple[list[dict[str, str]], list[str]]:
    blocks: list[dict[str, str]] = []
    issues: list[str] = []
    stack: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for line in text.splitlines():
        begin = BEGIN_RE.fullmatch(line.strip())
        if begin:
            block = begin.groupdict()
            block_id = block["block_id"]
            if block_id in seen_ids:
                issues.append(f"duplicate_block_id:{block_id}")
            seen_ids.add(block_id)
            if block["mode"] not in SUPPORTED_MODES:
                issues.append(f"unsupported_mode:{block['mode']}:{block_id}")
            stack.append(block)
            blocks.append(block)
            continue
        end = END_RE.fullmatch(line.strip())
        if end:
            block_id = end.group("block_id")
            if not stack:
                issues.append(f"end_without_begin:{block_id}")
                continue
            current = stack.pop()
            if current["block_id"] != block_id:
                issues.append(f"mismatched_block:{current['block_id']}:{block_id}")
    if stack:
        issues.extend([f"unclosed_block:{item['block_id']}" for item in stack])
    return blocks, issues


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    root = Path(__file__).resolve().parents[1]
    wiki = root / "wiki"
    files = sorted(p for p in wiki.rglob("*.md") if p.is_file())
    missing_source_refs: list[str] = []
    sync_issues: list[str] = []
    page_block_map: dict[str, set[str]] = {}
    for file in files:
        text = file.read_text(encoding="utf-8")
        if "source_refs" not in text and file.name not in {"README.md", "log.md"}:
            missing_source_refs.append(file.relative_to(wiki).as_posix())
        blocks, issues = collect_page_blocks(text)
        rel = file.relative_to(repo_root).as_posix()
        page_block_map[rel] = {item["block_id"] for item in blocks}
        sync_issues.extend([f"{rel}: {issue}" for issue in issues])

    registry_path = root / "wiki_sync" / "registry.yaml"
    mappings = read_registry(registry_path)
    for mapping in mappings:
        target_page = str(mapping.get("target_page") or "")
        block_id = str(mapping.get("block_id") or "")
        if not target_page or not block_id:
            sync_issues.append("registry: missing target_page or block_id")
            continue
        target_file = repo_root / target_page
        if not target_file.exists():
            sync_issues.append(f"registry: target_missing:{target_page}")
            continue
        if block_id not in page_block_map.get(target_page, set()):
            sync_issues.append(f"registry: block_missing:{target_page}#{block_id}")
    report = root / "outputs" / "lint" / "latest_lint_report.md"
    lines = [
        "# Wiki Lint Report",
        "",
        f"- total_pages: {len(files)}",
        f"- missing_source_refs: {len(missing_source_refs)}",
        f"- sync_issues: {len(sync_issues)}",
        "",
        "## missing_source_refs_pages",
        "",
        *([f"- {x}" for x in missing_source_refs] if missing_source_refs else ["- none"]),
        "",
        "## sync_issues",
        "",
        *([f"- {x}" for x in sync_issues] if sync_issues else ["- none"]),
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"report={report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
