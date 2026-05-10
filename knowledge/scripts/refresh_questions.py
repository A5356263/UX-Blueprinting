from __future__ import annotations

import re
from datetime import date
from pathlib import Path


TAG_PATTERN = re.compile(r"^\s*(?:-\s+)?\[(GAP|CONFLICT|QUESTION)\]\s*(.+?)\s*$")


def extract_questions(file: Path, root: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for line in file.read_text(encoding="utf-8").splitlines():
        match = TAG_PATTERN.match(line.strip())
        if not match:
            continue
        items.append(
            {
                "question_type": match.group(1),
                "text": match.group(2).strip(),
                "source_path": file.relative_to(root).as_posix(),
            }
        )
    return items


def summary_path_for_raw(root: Path, raw_file: Path) -> str:
    rel = raw_file.relative_to(root / "raw").as_posix()
    return f"knowledge/wiki/summaries/{rel}"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    raw_root = root / "raw"
    wiki_root = root / "wiki"
    items: list[dict[str, str]] = []

    for file in sorted(p for p in raw_root.rglob("*.md") if p.is_file() and "清单" not in p.parts):
        extracted = extract_questions(file, root.parent)
        for entry in extracted:
            entry["summary_path"] = summary_path_for_raw(root, file)
        items.extend(extracted)

    for file in sorted(p for p in (wiki_root / "summaries").rglob("*.md") if p.is_file()):
        extracted = extract_questions(file, root.parent)
        for entry in extracted:
            source_path = entry["source_path"].replace("knowledge/wiki/summaries/", "knowledge/raw/")
            entry["summary_path"] = entry["source_path"]
            entry["source_path"] = source_path
        items.extend(extracted)

    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (item["source_path"], item["question_type"], item["text"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    lines = [
        "# Knowledge Wiki Questions",
        "",
        "- page_id: PG-SYSTEM-QUESTIONS",
        "- page_type: system",
        "- status: active",
        "- confidence: medium",
        f"- updated_at: {date.today().isoformat()}",
        "",
        "## 显式未决项",
        "",
    ]

    if deduped:
        for idx, item in enumerate(deduped, start=1):
            lines.extend(
                [
                    f"### Q-{idx:04d}",
                    "",
                    f"- question_id: Q-{idx:04d}",
                    f"- source_path: {item['source_path']}",
                    f"- summary_path: {item['summary_path']}",
                    f"- question_type: {item['question_type']}",
                    f"- text: {item['text']}",
                    f"- updated_at: {date.today().isoformat()}",
                    "",
                ]
            )
    else:
        lines.extend(["- none", ""])

    out = wiki_root / "questions.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"questions={out}")
    print(f"question_count={len(deduped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
