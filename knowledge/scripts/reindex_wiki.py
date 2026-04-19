from __future__ import annotations

from pathlib import Path


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
        summary_files = sorted(group_dir.rglob("*.md"))
        if not summary_files:
            lines.append("- none")
            lines.append("")
            continue
        current_heading: str | None = None
        for file in summary_files:
            rel_from_group = file.relative_to(group_dir).as_posix()
            heading_prefix = rel_from_group.rsplit("/", 1)[0] if "/" in rel_from_group else ""
            if heading_prefix:
                section_heading = f"### {heading_prefix}"
                if current_heading != section_heading:
                    if lines[-1] != "":
                        lines.append("")
                    lines.append(section_heading)
                    lines.append("")
                    current_heading = section_heading
            rel = file.relative_to(wiki).as_posix()
            lines.append(f"- [{file.stem}]({rel})")
        lines.append("")

    (wiki / "index.md").write_text("\n".join(lines), encoding="utf-8")
    print("reindexed=knowledge/wiki/index.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
