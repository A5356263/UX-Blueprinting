from __future__ import annotations

import argparse
import re
from pathlib import Path


FACT_ID_PATTERN = re.compile(r"\bF-\d+\b")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def extract_fact_ids(text: str) -> list[str]:
    return sorted(set(FACT_ID_PATTERN.findall(text)))


def append_section(report_path: Path, section_title: str, lines: list[str]) -> None:
    if report_path.exists():
        original = report_path.read_text(encoding="utf-8").rstrip()
    else:
        original = "# Check Report"
    section = "\n".join(["", f"## {section_title}", ""] + [f"- {line}" for line in lines] + [""])
    report_path.write_text(original + section, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    workspace_dir = repo_root / "tasks" / "active" / args.task_id / "workspace"
    report_path = workspace_dir / "check_report.md"

    facts_text = read_text(workspace_dir / "facts.md")
    business_text = read_text(workspace_dir / "business_blueprint.md")
    experience_text = read_text(workspace_dir / "experience_blueprint.md")

    lines: list[str] = []
    fact_ids = extract_fact_ids(facts_text)

    if not fact_ids:
        lines.append("warning: facts.md 中未找到事实 ID")
    else:
        for fact_id in fact_ids:
            in_business = fact_id in business_text
            in_experience = fact_id in experience_text
            if in_business or in_experience:
                lines.append(f"info: {fact_id} 已被蓝图承接")
            else:
                lines.append(f"warning: {fact_id} 未在业务蓝图或体验蓝图中引用")

    if not business_text:
        lines.append("blocker: business_blueprint.md 缺失")
    if not experience_text:
        lines.append("blocker: experience_blueprint.md 缺失")

    append_section(report_path, "Coverage Check", lines or ["info: 无可检查项"])
    print(f"Coverage check finished: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
