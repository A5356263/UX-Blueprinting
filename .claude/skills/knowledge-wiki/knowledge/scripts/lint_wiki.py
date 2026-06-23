from __future__ import annotations

from pathlib import Path

from _write_if_changed import write_text_if_changed


REQUIRED_SUMMARY_FIELDS = [
    "source_path:",
    "domain:",
    "summary_role: light_route_card",
    "updated_at:",
]

REQUIRED_SUMMARY_HEADINGS = [
    "## 定位",
    "## 触发信号",
    "## 稳定结论",
    "## 已知缺口",
]

FORBIDDEN_LEGACY_MARKERS = [
    "page_id:",
    "page_type: summary",
    "source_group:",
    "source_refs:",
    "related_summaries:",
    "## 1. 知识定位",
    "## 2. 任务触发线索",
    "## 3. 覆盖内容",
    "## 5. 必须回查 raw 的情况",
    "## 7. 邻近阅读",
]

def summary_path_for(root: Path, raw_file: Path) -> Path:
    rel = raw_file.relative_to(root / "raw")
    return root / "wiki" / "summaries" / rel


def parse_source_path(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("- source_path:"):
            return line.split(":", 1)[1].strip()
    return None


def _has_bullets_after_heading(text: str, heading: str) -> bool:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != heading:
            continue
        for follow in lines[index + 1 :]:
            stripped = follow.strip()
            if not stripped:
                continue
            if stripped.startswith("## "):
                return False
            return stripped.startswith("- ")
    return False


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    repo_root = root.parent
    raw_files = sorted(path for path in (root / "raw").rglob("*.md") if path.is_file())
    summary_files = sorted(path for path in (root / "wiki" / "summaries").rglob("*.md") if path.is_file())
    issues: list[str] = []

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
        for heading in REQUIRED_SUMMARY_HEADINGS:
            if heading not in text:
                issues.append(f"missing_heading:{rel}:{heading}")

        source_path = parse_source_path(text)
        if not source_path:
            issues.append(f"missing_source_path:{rel}")
        else:
            source_file = repo_root / source_path
            if not source_file.exists():
                issues.append(f"broken_source_path:{rel}:{source_path}")

        if not _has_bullets_after_heading(text, "## 触发信号"):
            issues.append(f"missing_trigger_bullets:{rel}")
        if not _has_bullets_after_heading(text, "## 稳定结论"):
            issues.append(f"missing_conclusion_bullets:{rel}")
        if not _has_bullets_after_heading(text, "## 已知缺口"):
            issues.append(f"missing_gap_bullets:{rel}")

        for marker in FORBIDDEN_LEGACY_MARKERS:
            if marker in text:
                issues.append(f"forbidden_legacy_marker:{rel}:{marker}")

    index_file = root / "wiki" / "index.md"
    if not index_file.exists():
        issues.append("missing_index:knowledge/wiki/index.md")

    for required in [root / "wiki" / "overview.md", root / "wiki" / "questions.md"]:
        if not required.exists():
            issues.append(f"missing_system_page:{required.relative_to(repo_root).as_posix()}")

    report = root / "outputs" / "lint" / "latest_lint_report.md"
    orphan_report = root / "outputs" / "reports" / "orphan_summaries.md"
    lines = [
        "# Wiki Lint Report",
        "",
        f"- raw_total: {len(raw_files)}",
        f"- summary_total: {len(summary_files)}",
        f"- issue_total: {len(issues)}",
        f"- orphan_report: {orphan_report.relative_to(repo_root).as_posix() if orphan_report.exists() else 'missing'}",
        "",
        "## Issues",
        "",
        *([f"- {issue}" for issue in issues] if issues else ["- none"]),
        "",
    ]
    changed = write_text_if_changed(report, "\n".join(lines), encoding="utf-8")
    print(f"raw_total={len(raw_files)}")
    print(f"summary_total={len(summary_files)}")
    print(f"issue_total={len(issues)}")
    print(f"changed={str(changed).lower()}")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
