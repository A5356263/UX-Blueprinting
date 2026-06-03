from __future__ import annotations

from datetime import date
from pathlib import Path

from _write_if_changed import parse_metadata_value, replace_metadata_value, write_text_if_changed

def count_markers(files: list[Path], marker: str) -> int:
    """只统计以 [MARKER] 开头的真实问题标记行，忽略正文中普通提及。"""
    count = 0
    for file in files:
        try:
            for line in file.read_text(encoding="utf-8").splitlines():
                stripped = line.strip().lstrip("- ").strip()
                if stripped.startswith(marker):
                    count += 1
        except UnicodeDecodeError:
            continue
    return count


def with_stable_timestamp(content: str, existing_text: str | None, today_str: str) -> str:
    if not existing_text:
        return content
    existing_updated = parse_metadata_value(existing_text, "updated_at")
    stable = content
    if existing_updated:
        stable = replace_metadata_value(stable, "updated_at", existing_updated)
    if stable == existing_text:
        return existing_text
    return content


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    raw_files = sorted(p for p in (root / "raw").rglob("*.md") if p.is_file())
    summary_files = sorted(p for p in (root / "wiki" / "summaries").rglob("*.md") if p.is_file())
    raw_set = {p.relative_to(root / "raw").as_posix() for p in raw_files}
    summary_set = {p.relative_to(root / "wiki" / "summaries").as_posix() for p in summary_files}
    missing = sorted(raw_set - summary_set)
    latest_raw = sorted(raw_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    question_file = root / "wiki" / "questions.md"
    question_count = 0
    if question_file.exists():
        question_count = sum(1 for line in question_file.read_text(encoding="utf-8").splitlines() if line.startswith("- question_id:"))

    content = "\n".join(
        [
            "# Knowledge Wiki Overview",
            "",
            f"- updated_at: {date.today().isoformat()}",
            "",
            "## 当前概况",
            "",
            f"- raw_total: {len(raw_files)}",
            f"- summary_total: {len(summary_files)}",
            f"- summary_coverage: {len(summary_files)}/{len(raw_files) if raw_files else 0}",
            f"- gap_count: {count_markers(raw_files + summary_files, '[GAP]')}",
            f"- conflict_count: {count_markers(raw_files + summary_files, '[CONFLICT]')}",
            f"- question_marker_count: {count_markers(raw_files + summary_files, '[QUESTION]')}",
            f"- raw_without_summary: {len(missing)}",
            f"- questions_total: {question_count}",
            "",
            "## 最近更新的 Raw",
            "",
            *([f"- {item.relative_to(root).as_posix()}" for item in latest_raw] if latest_raw else ["- none"]),
            "",
            "## 无 Summary 的 Raw",
            "",
            *([f"- knowledge/raw/{item}" for item in missing] if missing else ["- none"]),
            "",
        ]
    )
    overview_path = root / "wiki" / "overview.md"
    existing_text = overview_path.read_text(encoding="utf-8") if overview_path.exists() else None
    content = with_stable_timestamp(content, existing_text, date.today().isoformat())
    changed = write_text_if_changed(overview_path, content, encoding="utf-8")
    print("refreshed=knowledge/wiki/overview.md")
    print(f"changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
