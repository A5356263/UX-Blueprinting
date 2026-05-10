from __future__ import annotations

import json


def _render_string_list(items: list[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" if not item.startswith("- ") else item for item in items)


def render_gap_list() -> str:
    return """# Gap List

## Blockers

- none

## Warnings

- 当前产物生成已切到真正按输入与命中知识推理的方向，但如果来源证据不足，输出会主动变"保守"而不是回退到旧模板。

## 待补信息

- 补充更具体的任务原始输入，以便 facts / business / experience 形成更稳定的动态结论。
"""


def render_check_report() -> str:
    return """# Check Report｜人读说明版

> 本文件是 `projects/<project-id>/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。

## Summary

- status: pending
- has_blocker: false
- blocker_count: 0
- warning_count: 0
- info_count: 0

## Output Status

- facts.md: present
- business_blueprint.md: present
- experience_blueprint.md: present
- gap_list.md: present
- check_report.md: present
- check_status.json: present

## Blockers

- none

## Warnings

- 当前是 generate 阶段初始报告，仍需继续运行 gate / validate / coverage 完成正式检查。

## Infos

- generate-* 已完成正式初稿写入。

## 自然语言承接检查

- not_run

## Machine Status

- 机器可读状态文件：`workspace/check_status.json`
"""


def render_check_status(project_id: str) -> str:
    payload = {
        "task_id": project_id,
        "status": "pending",
        "has_blocker": False,
        "blocker_count": 0,
        "warning_count": 0,
        "info_count": 0,
        "completed_outputs": [
            f"projects/{project_id}/workspace/facts.md",
            f"projects/{project_id}/workspace/business_blueprint.md",
            f"projects/{project_id}/workspace/experience_blueprint.md",
            f"projects/{project_id}/workspace/gap_list.md",
            f"projects/{project_id}/workspace/check_report.md",
            f"projects/{project_id}/workspace/check_status.json",
        ],
        "issues": {"blockers": [], "warnings": [], "infos": []},
        "checked_files": [
            f"projects/{project_id}/workspace/facts.md",
            f"projects/{project_id}/workspace/business_blueprint.md",
            f"projects/{project_id}/workspace/experience_blueprint.md",
            f"projects/{project_id}/workspace/gap_list.md",
        ],
        "generated_by": "packages.generation",
        "updated_at": "",
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
