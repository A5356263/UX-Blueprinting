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
    """生成语义待处理报告，基于 semantic_status 分类。"""
    PLACEHOLDER = "待 AI Code 读取 raw 后生成。"

    pending_generate: list[str] = []
    pending_review: list[str] = []
    completed: list[str] = []

    for sf in summary_files:
        text = sf.read_text(encoding="utf-8")
        rel = sf.relative_to(root).as_posix()
        has_placeholder = PLACEHOLDER in text
        semantic_status = ""
        for line in text.splitlines():
            if line.strip().startswith("- semantic_status:"):
                semantic_status = line.split(":", 1)[1].strip()

        if not semantic_status or semantic_status == "pending" or has_placeholder:
            reason = "missing" if not semantic_status else semantic_status
            pending_generate.append(f"- summary_path: knowledge/{rel}\n  - reason: semantic_status={reason}")
        elif semantic_status == "needs_review":
            pending_review.append(f"- summary_path: knowledge/{rel}\n  - reason: semantic_status=needs_review")
        elif semantic_status == "ai_generated" and not has_placeholder:
            completed.append(f"- knowledge/{rel}")
        else:
            pending_review.append(f"- summary_path: knowledge/{rel}\n  - reason: unexpected state")

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
