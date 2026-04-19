from __future__ import annotations

from pathlib import Path


REQUIRED_SUMMARY_FIELDS = [
    "page_id:",
    "page_type: summary",
    "source_path:",
    "source_group:",
    "status:",
    "confidence:",
    "updated_at:",
    "source_refs:",
    "related_summaries:",
]


def summary_path_for(root: Path, raw_file: Path) -> Path:
    rel = raw_file.relative_to(root / "raw")
    return root / "wiki" / "summaries" / rel


def parse_source_path(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("- source_path:"):
            return line.split(":", 1)[1].strip()
    return None


def parse_related_summaries(text: str) -> list[str]:
    items: list[str] = []
    in_block = False
    for line in text.splitlines():
        if line.startswith("- related_summaries:"):
            in_block = True
            continue
        if in_block:
            if line.startswith("  - "):
                items.append(line[4:].strip())
                continue
            if line.strip() == "":
                continue
            break
    return items


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    repo_root = root.parent
    raw_files = sorted(p for p in (root / "raw").rglob("*.md") if p.is_file() and "manifests" not in p.parts)
    summary_files = sorted(p for p in (root / "wiki" / "summaries").rglob("*.md") if p.is_file())
    issues: list[str] = []

    summary_lookup = {p.relative_to(root / "wiki" / "summaries").as_posix(): p for p in summary_files}

    for raw_file in raw_files:
        summary_file = summary_path_for(root, raw_file)
        if not summary_file.exists():
            issues.append(f"missing_summary:{raw_file.relative_to(repo_root).as_posix()}")

    for summary_file in summary_files:
        text = summary_file.read_text(encoding="utf-8")
        rel = summary_file.relative_to(repo_root).as_posix()
        for field in REQUIRED_SUMMARY_FIELDS:
            if field not in text:
                issues.append(f"missing_field:{rel}:{field}")
        source_path = parse_source_path(text)
        if not source_path:
            issues.append(f"missing_source_path:{rel}")
        else:
            source_file = repo_root / source_path
            if not source_file.exists():
                issues.append(f"broken_source_path:{rel}:{source_path}")
        for related in parse_related_summaries(text):
            if related == "none":
                continue
            related_rel = related.replace("knowledge/wiki/summaries/", "")
            if related_rel not in summary_lookup:
                issues.append(f"broken_related_summary:{rel}:{related}")

    index_file = root / "wiki" / "index.md"
    if index_file.exists():
        index_text = index_file.read_text(encoding="utf-8")
        for forbidden in ["concepts/", "entities/", "topics/", "relations/", "synthesis/", "sources/"]:
            if forbidden in index_text:
                issues.append(f"forbidden_index_reference:{forbidden}")
    else:
        issues.append("missing_index:knowledge/wiki/index.md")

    for required in [root / "wiki" / "overview.md", root / "wiki" / "questions.md"]:
        if not required.exists():
            issues.append(f"missing_system_page:{required.relative_to(repo_root).as_posix()}")

    report = root / "outputs" / "lint" / "latest_lint_report.md"
    lines = [
        "# Wiki Lint Report",
        "",
        f"- raw_total: {len(raw_files)}",
        f"- summary_total: {len(summary_files)}",
        f"- issue_total: {len(issues)}",
        "",
        "## Issues",
        "",
        *([f"- {issue}" for issue in issues] if issues else ["- none"]),
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"report={report}")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
