from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_HEADINGS = {
    "facts.md": ["## 任务目标", "## 业务事实清单", "## 已知约束", "## 输入来源", "## 开放问题"],
    "business_blueprint.md": ["## 场景定义", "## 核心判断", "## 关键规则与约束", "## 决策链路与依赖", "## 风险与缺口", "## 开放问题"],
    "experience_blueprint.md": ["## 体验目标", "## 关键场景", "## 体验要求", "## 原则引用", "## 风险与保护", "## 开放问题"],
    "gap_list.md": ["## Blockers", "## Warnings", "## 待补信息"],
}

FORBIDDEN_TERMS = {
    "facts.md": ["高保真", "视觉稿", "页面布局"],
    "business_blueprint.md": ["高保真", "视觉稿", "组件样式"],
    "experience_blueprint.md": ["数据库表", "接口字段", "SQL"],
}


def add_issue(issues: list[tuple[str, str]], level: str, message: str) -> None:
    issues.append((level, message))


def render_report(issues: list[tuple[str, str]]) -> str:
    blockers = [message for level, message in issues if level == "blocker"]
    warnings = [message for level, message in issues if level == "warning"]
    infos = [message for level, message in issues if level == "info"]

    status = "pass"
    if blockers:
        status = "blocker"
    elif warnings:
        status = "warning"

    lines = [
        "# Check Report",
        "",
        "## Summary",
        "",
        f"- status: {status}",
        "",
        "## Blockers",
        "",
    ]
    lines.extend([f"- {item}" for item in blockers] or ["- none"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in warnings] or ["- none"])
    lines.extend(["", "## Infos", ""])
    lines.extend([f"- {item}" for item in infos] or ["- none"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    workspace_dir = repo_root / "tasks" / "active" / args.task_id / "workspace"
    report_path = workspace_dir / "check_report.md"
    issues: list[tuple[str, str]] = []

    for file_name, headings in REQUIRED_HEADINGS.items():
        file_path = workspace_dir / file_name
        if not file_path.exists():
            add_issue(issues, "blocker", f"{file_name} 缺失")
            continue

        content = file_path.read_text(encoding="utf-8")
        for heading in headings:
            if heading not in content:
                add_issue(issues, "blocker", f"{file_name} 缺少栏目：{heading}")

        for term in FORBIDDEN_TERMS.get(file_name, []):
            if term in content:
                add_issue(issues, "warning", f"{file_name} 可能越过阶段边界：包含 {term}")

        if "<填写" in content or "{{TASK_ID}}" in content:
            add_issue(issues, "warning", f"{file_name} 仍包含占位内容")

    add_issue(issues, "info", "结构检查已执行")
    report_path.write_text(render_report(issues), encoding="utf-8")
    print(f"Validation finished: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
