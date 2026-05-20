from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from packages.common import (
    get_project_gates_dir,
    get_project_remediation_dir,
    get_project_runtime_dir,
    get_project_workspace_dir,
    get_repo_root,
)


SEVERITY_BUCKETS = {
    "blockers": "blocker",
    "warnings": "warning",
}

STATUS_SPECS = (
    ("facts_gate", "facts", "facts_gate_status.json", "facts_gate_report.md"),
    ("business_gate", "business", "business_gate_status.json", "business_gate_report.md"),
    ("experience_gate", "experience", "experience_gate_status.json", "experience_gate_report.md"),
    ("final_validate", "final", "check_status.json", "check_report.md"),
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def repo_rel(path: Path) -> str:
    try:
        return str(path.relative_to(get_repo_root())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def ensure_remediation_dir(project_id: str) -> Path:
    directory = get_project_remediation_dir(project_id)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def severity_sort_key(value: str) -> int:
    return {"blocker": 0, "warning": 1, "info": 2}.get(value, 9)


def _status_and_report_path(project_id: str, source: str, status_name: str, report_name: str) -> tuple[Path, Path]:
    if source == "final_validate":
        workspace_dir = get_project_workspace_dir(project_id)
        return workspace_dir / status_name, workspace_dir / report_name
    gates_dir = get_project_gates_dir(project_id)
    return gates_dir / status_name, gates_dir / report_name


def _coerce_messages(payload: dict[str, Any], bucket_name: str) -> list[str]:
    issues = payload.get("issues", {})
    if not isinstance(issues, dict):
        return []
    values = issues.get(bucket_name, [])
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def _coerce_issue_details(payload: dict[str, Any]) -> list[dict[str, Any]]:
    values = payload.get("issue_details", [])
    if not isinstance(values, list):
        return []
    details: list[dict[str, Any]] = []
    for item in values:
        if not isinstance(item, dict):
            continue
        message = str(item.get("message", "")).strip()
        if not message:
            continue
        checked_files = item.get("checked_files", [])
        target_artifacts = item.get("target_artifacts", [])
        violated_refs = item.get("violated_contract_refs", [])
        evidence = item.get("evidence", [])
        details.append(
            {
                "source": str(item.get("source") or ""),
                "stage": str(item.get("stage") or ""),
                "severity": str(item.get("severity") or ""),
                "category": str(item.get("category") or ""),
                "message": message,
                "checked_files": [str(value) for value in checked_files if isinstance(value, str)],
                "target_artifacts": [str(value) for value in target_artifacts if isinstance(value, str)],
                "violated_contract_refs": [str(value) for value in violated_refs if isinstance(value, str)],
                "evidence": evidence if isinstance(evidence, list) else [],
            }
        )
    return [item for item in details if item["severity"] in {"blocker", "warning"}]


def _map_final_source(source: str, message: str) -> str:
    if source != "final_validate":
        return source
    if message.lower().startswith("coverage:"):
        return "coverage"
    return "validate"


def _skip_redundant_final_issue(message: str) -> bool:
    lowered = message.lower()
    return " gate " in lowered or lowered.startswith("facts gate") or lowered.startswith("business gate") or lowered.startswith("experience gate")


def collect_issue_sources(project_id: str) -> dict[str, Any]:
    ensure_remediation_dir(project_id)
    runtime_dir = get_project_runtime_dir(project_id)
    workspace_dir = get_project_workspace_dir(project_id)

    raw_issues: list[dict[str, Any]] = []
    source_artifacts: list[dict[str, Any]] = []

    for source_name, stage_name, status_name, report_name in STATUS_SPECS:
        status_path, report_path = _status_and_report_path(project_id, source_name, status_name, report_name)
        status_payload = read_json(status_path)
        source_artifacts.append(
            {
                "source": "validate" if source_name == "final_validate" else source_name,
                "stage": stage_name,
                "status_path": repo_rel(status_path),
                "report_path": repo_rel(report_path),
                "status_exists": status_path.exists(),
                "report_exists": report_path.exists(),
            }
        )
        if not status_payload:
            raw_issues.append(
                {
                    "source": "runtime",
                    "stage": "runtime",
                    "severity": "blocker",
                    "message": f"missing status artifact: {repo_rel(status_path)}",
                    "status_path": repo_rel(status_path),
                    "report_path": repo_rel(report_path),
                    "checked_files": [],
                }
            )
            continue

        checked_files = [str(item) for item in status_payload.get("checked_files", []) if isinstance(item, str)]
        extracted_count = 0
        structured_details = _coerce_issue_details(status_payload)
        if structured_details:
            for detail in structured_details:
                source = detail["source"] or _map_final_source(source_name, detail["message"])
                if source == "validate" and _skip_redundant_final_issue(detail["message"]):
                    continue
                raw_issues.append(
                    {
                        "source": source,
                        "stage": detail["stage"] or stage_name,
                        "severity": detail["severity"] or "warning",
                        "category": detail["category"],
                        "message": detail["message"],
                        "status_path": repo_rel(status_path),
                        "report_path": repo_rel(report_path),
                        "checked_files": detail["checked_files"] or checked_files,
                        "target_artifacts": detail["target_artifacts"],
                        "violated_contract_refs": detail["violated_contract_refs"],
                        "evidence": detail["evidence"],
                    }
                )
                extracted_count += 1
        else:
            for bucket_name, severity in SEVERITY_BUCKETS.items():
                for message in _coerce_messages(status_payload, bucket_name):
                    source = _map_final_source(source_name, message)
                    if source == "validate" and _skip_redundant_final_issue(message):
                        continue
                    raw_issues.append(
                        {
                            "source": source,
                            "stage": stage_name,
                            "severity": severity,
                            "message": message,
                            "status_path": repo_rel(status_path),
                            "report_path": repo_rel(report_path),
                            "checked_files": checked_files,
                            "target_artifacts": [],
                            "violated_contract_refs": [],
                            "evidence": [],
                        }
                    )
                    extracted_count += 1

        if status_payload.get("status") == "failed" and extracted_count == 0:
            raw_issues.append(
                {
                    "source": _map_final_source(source_name, "status"),
                    "stage": stage_name,
                    "severity": "blocker",
                    "message": f"status file reports failed without structured blocker details: {repo_rel(status_path)}",
                    "status_path": repo_rel(status_path),
                    "report_path": repo_rel(report_path),
                    "checked_files": checked_files,
                }
            )

    for path in [
        runtime_dir / "uxb_route_decision.json",
        runtime_dir / "context_manifest.json",
        runtime_dir / "trace_index.json",
        runtime_dir / "gate_metrics.json",
    ]:
        if not path.exists():
            raw_issues.append(
                {
                    "source": "runtime",
                    "stage": "runtime",
                    "severity": "warning",
                    "message": f"missing runtime support artifact: {repo_rel(path)}",
                    "status_path": repo_rel(path),
                    "report_path": repo_rel(path),
                    "checked_files": [],
                }
            )

    if not (workspace_dir / "check_status.json").exists():
        raw_issues.append(
            {
                "source": "runtime",
                "stage": "runtime",
                "severity": "blocker",
                "message": f"missing machine check status: {repo_rel(workspace_dir / 'check_status.json')}",
                "status_path": repo_rel(workspace_dir / "check_status.json"),
                "report_path": repo_rel(workspace_dir / "check_report.md"),
                "checked_files": [],
            }
        )

    unique: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for item in raw_issues:
        key = (
            item["source"],
            item["stage"],
            item["severity"],
            item["message"],
            ",".join(item.get("target_artifacts", [])),
        )
        unique[key] = item

    deduped_issues = sorted(
        unique.values(),
        key=lambda item: (severity_sort_key(item["severity"]), item["stage"], item["source"], item["message"]),
    )

    return {
        "project_id": project_id,
        "generated_at": now_iso(),
        "source_artifacts": source_artifacts,
        "raw_issues": deduped_issues,
    }
