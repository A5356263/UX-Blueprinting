from __future__ import annotations

from pathlib import Path

from _write_if_changed import write_text_if_changed


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    summary_files = sorted(p for p in (root / "wiki" / "summaries").rglob("*.md") if p.is_file())
    build_pending_semantic_report(root, summary_files)
    print("refreshed=knowledge/outputs/reports/pending_semantic_summaries.md")
    return 0


def build_pending_semantic_report(root: Path, summary_files: list[Path]) -> None:
    """生成语义待处理报告，基于轻路由卡占位内容分类。"""
    placeholders = {
        "待 AI Code 读取 raw 后补充这份知识的定位。",
        "待 AI Code 读取 raw 后补充触发信号。",
        "待 AI Code 读取 raw 后补充稳定结论。",
    }

    pending_generate: list[str] = []
    pending_review: list[str] = []
    completed: list[str] = []

    for sf in summary_files:
        text = sf.read_text(encoding="utf-8")
        rel = sf.relative_to(root).as_posix()
        has_placeholder = any(item in text for item in placeholders)
        if has_placeholder:
            pending_generate.append(f"- summary_path: knowledge/{rel}\n  - reason: 仍包含轻路由卡占位内容")
        else:
            completed.append(f"- knowledge/{rel}")

    report_lines = [
        "# Pending Semantic Summaries",
        "",
        f"- total: {len(summary_files)}",
        f"- pending_generate: {len(pending_generate)}",
        f"- pending_review: {len(pending_review)}",
        f"- completed: {len(completed)}",
        "",
        "## 待 AI 生成",
        "",
        *(pending_generate if pending_generate else ["- none"]),
        "",
        "## 待 AI 复核",
        "",
        *(pending_review if pending_review else ["- none"]),
        "",
        "## 已完成",
        "",
        *(completed if completed else ["- none"]),
        "",
    ]

    report_path = root / "outputs" / "reports" / "pending_semantic_summaries.md"
    changed = write_text_if_changed(report_path, "\n".join(report_lines), encoding="utf-8")
    print(f"changed={str(changed).lower()}")


if __name__ == "__main__":
    raise SystemExit(main())
