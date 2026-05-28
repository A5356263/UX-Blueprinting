from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from _write_if_changed import write_text_if_changed


REPORT_PATH = Path("outputs/reports/orphan_summaries.md")


@dataclass
class OrphanSummary:
    summary_file: Path
    source_path: str


def parse_source_path(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("- source_path:"):
            return line.split(":", 1)[1].strip()
    return None


def collect_orphans(root: Path) -> list[OrphanSummary]:
    repo_root = root.parent
    summaries_root = root / "wiki" / "summaries"
    orphans: list[OrphanSummary] = []

    for summary_file in sorted(summaries_root.rglob("*.md")):
        text = summary_file.read_text(encoding="utf-8")
        source_path = parse_source_path(text)
        if not source_path:
            continue
        source_file = repo_root / source_path
        if not source_file.exists():
            orphans.append(OrphanSummary(summary_file=summary_file, source_path=source_path))
    return orphans


def build_report(root: Path, orphans: list[OrphanSummary], mode: str) -> str:
    lines: list[str] = [
        "# Orphan Summaries Report",
        "",
        f"- mode: {mode}",
        f"- orphan_count: {len(orphans)}",
        "",
        "## Items",
        "",
    ]
    if not orphans:
        lines.append("- none")
        lines.append("")
        return "\n".join(lines)

    for orphan in orphans:
        rel_summary = orphan.summary_file.relative_to(root).as_posix()
        lines.extend(
            [
                f"- orphan summary path: knowledge/{rel_summary}",
                f"  - missing source_path: {orphan.source_path}",
                "  - suggested_action: remove summary and refresh wiki indexes",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def write_report(root: Path, content: str) -> Path:
    report_path = root / REPORT_PATH
    write_text_if_changed(report_path, content, encoding="utf-8")
    return report_path


def remove_orphans(orphans: list[OrphanSummary]) -> list[str]:
    removed: list[str] = []
    for orphan in orphans:
        orphan.summary_file.unlink(missing_ok=True)
        removed.append(orphan.summary_file.as_posix())
    return removed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.dry_run == args.apply:
        raise SystemExit("Choose exactly one of --dry-run or --apply")

    root = Path(__file__).resolve().parents[1]
    orphans = collect_orphans(root)
    mode = "apply" if args.apply else "dry-run"
    removed: list[str] = []

    if args.apply:
        removed = remove_orphans(orphans)

    report_path = write_report(root, build_report(root, orphans, mode))
    print(f"report={report_path}")
    print(f"orphan_count={len(orphans)}")
    for item in removed:
        print(f"removed={item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
