from __future__ import annotations

from pathlib import Path

from _write_if_changed import write_text_if_changed


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
        summary_files = sorted(group_dir.rglob("*.md"))
        if not summary_files:
            lines.append("- none")
            lines.append("")
            continue
        append_summary_links(lines, wiki, group_dir, summary_files, "###")

    changed = write_text_if_changed(wiki / "index.md", "\n".join(lines), encoding="utf-8")
    print("reindexed=knowledge/wiki/index.md")
    print(f"changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
