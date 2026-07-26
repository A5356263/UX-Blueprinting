from __future__ import annotations

from datetime import date
from pathlib import Path

from _write_if_changed import parse_metadata_value, replace_metadata_value, write_text_if_changed


def count_markers(files: list[Path], marker: str) -> int:
    count = 0
    for file in files:
        for line in file.read_text(encoding="utf-8").splitlines():
            if line.strip().lstrip("- ").strip().startswith(marker):
                count += 1
    return count


def report_metrics(root: Path) -> dict[str, int]:
    report = root / "outputs" / "lint" / "latest_lint_report.md"
    metrics: dict[str, int] = {}
    if not report.exists():
        return metrics
    for line in report.read_text(encoding="utf-8").splitlines():
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        value = value.strip()
        if value.isdigit():
            metrics[key] = int(value)
    return metrics


def with_stable_timestamp(content: str, existing_text: str | None) -> str:
    if not existing_text:
        return content
    existing_updated = parse_metadata_value(existing_text, "updated_at")
    stable = replace_metadata_value(content, "updated_at", existing_updated) if existing_updated else content
    return existing_text if stable == existing_text else content


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    raw_files = sorted(path for path in (root / "raw").rglob("*.md") if path.is_file())
    domain_readmes = sorted(
        path
        for path in (root / "raw").rglob("README.md")
        if path.parent.name != "交互模式"
    )
    latest_raw = sorted(raw_files, key=lambda path: path.stat().st_mtime, reverse=True)[:5]
    question_file = root / "wiki" / "questions.md"
    question_total = 0
    if question_file.exists():
        question_total = sum(1 for line in question_file.read_text(encoding="utf-8").splitlines() if line.startswith("- question_id:"))
    metrics = report_metrics(root)

    tracked = [
        "domain_readme_missing_count",
        "unindexed_domain_count",
        "unrouted_raw_count",
        "broken_raw_path_count",
        "broken_section_anchor_count",
        "duplicate_route_target_count",
        "long_raw_without_navigation_count",
        "forbidden_summary_reference_count",
        "numbered_business_file_count",
        "encoding_issue_count",
    ]
    lines = [
        "# Knowledge Wiki Overview",
        "",
        f"- updated_at: {date.today().isoformat()}",
        "",
        "## 当前概况",
        "",
        f"- raw_total: {len(raw_files)}",
        f"- domain_readme_total: {len(domain_readmes)}",
        f"- gap_count: {count_markers(raw_files, '[GAP]')}",
        f"- conflict_count: {count_markers(raw_files, '[CONFLICT]')}",
        f"- question_marker_count: {count_markers(raw_files, '[QUESTION]')}",
        f"- questions_total: {question_total}",
        "",
        "## 路由健康",
        "",
        *[f"- {key}: {metrics.get(key, 0)}" for key in tracked],
        "",
        "## 最近更新的 Raw",
        "",
        *([f"- {path.relative_to(root).as_posix()}" for path in latest_raw] if latest_raw else ["- none"]),
        "",
    ]
    out = root / "wiki" / "overview.md"
    content = "\n".join(lines)
    existing = out.read_text(encoding="utf-8") if out.exists() else None
    changed = write_text_if_changed(out, with_stable_timestamp(content, existing), encoding="utf-8")
    print("refreshed=knowledge/wiki/overview.md")
    print(f"changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
