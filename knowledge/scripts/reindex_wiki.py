from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wiki = root / "wiki"
    content_dirs = ["sources", "concepts", "entities", "topics", "relations", "synthesis", "templates", "archive"]
    lines: list[str] = [
        "# Knowledge Wiki Index",
        "",
        "- page_id: PG-SYSTEM-INDEX",
        "- page_type: system",
        "- status: stable",
        "- confidence: medium",
        "- source_refs: [SRC-BIZ-0001, SRC-GDL-0001]",
        "- related_pages: [overview.md, questions.md, log.md]",
        "",
    ]
    for section in content_dirs:
        lines.append(f"## {section}")
        lines.append("")
        paths = sorted((wiki / section).glob("*.md"))
        if paths:
            for p in paths:
                if p.name == "README.md":
                    continue
                lines.append(f"- [{p.stem}]({section}/{p.name})")
        else:
            lines.append("- none")
        lines.append("")
    (wiki / "index.md").write_text("\n".join(lines), encoding="utf-8")
    print("reindexed=knowledge/wiki/index.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
