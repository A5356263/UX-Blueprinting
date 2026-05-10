from __future__ import annotations

from pathlib import Path


BUSINESS_SECTIONS: list[tuple[str, list[str]]] = [
    ("背景层", ["项目背景"]),
    ("平台公共域", ["工作台与全局入口", "账户与企业生命周期"]),
    (
        "平台治理域",
        [
            "权限管理",
            "组织架构",
            "成员管理",
            "应用管理",
            "审批管理",
            "安全管理",
            "企业设置",
            "服务管理",
        ],
    ),
]


def append_summary_links(
    lines: list[str],
    wiki: Path,
    base_dir: Path,
    files: list[Path],
    heading_level: str,
) -> None:
    current_heading: str | None = None
    for file in files:
        rel_from_base = file.relative_to(base_dir).as_posix()
        heading_prefix = rel_from_base.rsplit("/", 1)[0] if "/" in rel_from_base else ""
        if heading_prefix:
            section_heading = f"{heading_level} {heading_prefix}"
            if current_heading != section_heading:
                if lines[-1] != "":
                    lines.append("")
                lines.append(section_heading)
                lines.append("")
                current_heading = section_heading
        rel = file.relative_to(wiki).as_posix()
        lines.append(f"- [{file.stem}]({rel})")
    lines.append("")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wiki = root / "wiki"
    summaries_root = wiki / "summaries"
    lines: list[str] = [
        "# Knowledge Wiki Index",
        "",
        "- page_id: PG-SYSTEM-INDEX",
        "- page_type: system",
        "- status: active",
        "- confidence: medium",
        "- related_summaries: []",
        "",
        "## System Pages",
        "",
        "- [overview](overview.md)",
        "- [questions](questions.md)",
        "- [log](log.md)",
        "",
    ]

    groups = [p for p in summaries_root.iterdir() if p.is_dir()] if summaries_root.exists() else []
    for group_dir in sorted(groups, key=lambda p: p.name):
        lines.append(f"## {group_dir.name}")
        lines.append("")
        if group_dir.name == "business":
            domain_dirs = {p.name: p for p in group_dir.iterdir() if p.is_dir()}
            emitted: set[str] = set()
            for section_title, domains in BUSINESS_SECTIONS:
                existing_domains = [name for name in domains if name in domain_dirs]
                if not existing_domains:
                    continue
                lines.append(f"### {section_title}")
                lines.append("")
                for domain in existing_domains:
                    emitted.add(domain)
                    lines.append(f"#### {domain}")
                    lines.append("")
                    append_summary_links(lines, wiki, domain_dirs[domain], sorted(domain_dirs[domain].rglob("*.md")), "#####")
            remaining = sorted(name for name in domain_dirs if name not in emitted)
            if remaining:
                lines.append("### 其他")
                lines.append("")
                for domain in remaining:
                    lines.append(f"#### {domain}")
                    lines.append("")
                    append_summary_links(lines, wiki, domain_dirs[domain], sorted(domain_dirs[domain].rglob("*.md")), "#####")
            continue

        summary_files = sorted(group_dir.rglob("*.md"))
        if not summary_files:
            lines.append("- none")
            lines.append("")
            continue
        append_summary_links(lines, wiki, group_dir, summary_files, "###")

    (wiki / "index.md").write_text("\n".join(lines), encoding="utf-8")
    print("reindexed=knowledge/wiki/index.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
