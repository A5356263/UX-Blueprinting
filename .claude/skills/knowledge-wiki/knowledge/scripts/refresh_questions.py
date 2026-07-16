from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from _write_if_changed import parse_metadata_value, replace_metadata_value, write_text_if_changed


TAG_PATTERN = re.compile(r"^\s*(?:-\s+)?\[(GAP|CONFLICT|QUESTION)\]\s*(.+?)\s*$")


def with_stable_timestamp(content: str, existing_text: str | None) -> str:
    if not existing_text:
        return content
    existing_updated = parse_metadata_value(existing_text, "updated_at")
    stable = replace_metadata_value(content, "updated_at", existing_updated) if existing_updated else content
    return existing_text if stable == existing_text else content


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    raw_root = root / "raw"
    items: list[tuple[str, str, str]] = []
    for file in sorted(path for path in raw_root.rglob("*.md") if path.is_file()):
        for line in file.read_text(encoding="utf-8").splitlines():
            match = TAG_PATTERN.match(line.strip())
            if match:
                items.append((file.relative_to(root).as_posix(), match.group(1), match.group(2).strip()))

    deduped = list(dict.fromkeys(items))
    lines = ["# Knowledge Wiki Questions", "", f"- updated_at: {date.today().isoformat()}", "", "## 显式未决项", ""]
    for index, (source_path, question_type, text) in enumerate(deduped, start=1):
        lines.extend(
            [
                f"### Q-{index:04d}",
                "",
                f"- question_id: Q-{index:04d}",
                f"- source_path: knowledge/{source_path}",
                f"- question_type: {question_type}",
                f"- text: {text}",
                "",
            ]
        )
    if not deduped:
        lines.extend(["- none", ""])

    out = root / "wiki" / "questions.md"
    content = "\n".join(lines)
    existing = out.read_text(encoding="utf-8") if out.exists() else None
    changed = write_text_if_changed(out, with_stable_timestamp(content, existing), encoding="utf-8")
    print("questions=knowledge/wiki/questions.md")
    print(f"question_count={len(deduped)}")
    print(f"changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
