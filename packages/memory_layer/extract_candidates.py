from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.common import get_project_memory_dir, get_project_runtime_dir, get_project_workspace_dir
from packages.memory_layer.classify_memory import classify_candidate
from packages.memory_layer.memory_index import now_iso, read_json, repo_rel, write_json


def _load_task_context(project_id: str) -> dict[str, Any]:
    runtime_dir = get_project_runtime_dir(project_id)
    source_payload = read_json(runtime_dir / "task_card_resolved.json")
    return {
        "project_id": project_id,
        "domain": str(source_payload.get("domain") or ""),
        "wiki_refs": [str(value) for value in source_payload.get("wiki_refs", []) if isinstance(value, str)],
        "knowledge_refs": [str(value) for value in source_payload.get("knowledge_refs", []) if isinstance(value, str)],
    }


def _read_check_status(project_id: str) -> dict[str, Any]:
    return read_json(get_project_workspace_dir(project_id) / "check_status.json")


def _read_issue_index(project_id: str) -> dict[str, Any]:
    return read_json(get_project_runtime_dir(project_id) / "remediation" / "issue_index.json")


def _collect_source_artifacts(project_id: str, issue_index: dict[str, Any]) -> list[str]:
    artifacts = {
        f"projects/{project_id}/source/task_card.md",
        f"projects/{project_id}/workspace/check_status.json",
        f"projects/{project_id}/workspace/check_report.md",
    }
    for issue in issue_index.get("issues", []):
        if not isinstance(issue, dict):
            continue
        for path in issue.get("target_artifacts", []):
            if isinstance(path, str) and path.strip():
                artifacts.add(path)
    return sorted(artifacts)


def _build_generic_pattern(project_id: str, task_context: dict[str, Any], check_status: dict[str, Any]) -> dict[str, Any] | None:
    if str(check_status.get("status") or "") != "passed":
        return None
    return classify_candidate(
        {
            "memory_id": "pattern_generic_trace_and_state_matrix",
            "kind": "pattern",
            "scope": "generic",
            "title": "业务追踪映射与体验状态矩阵需要同时显式展开",
            "rule": "当任务进入完整 business / experience 主链时，业务蓝图保持 judgement trace 显式展开，体验蓝图保持状态与反馈矩阵、关键页面蓝图显式展开。",
            "why_it_helps": "这类结构能同时降低 trace missing、coverage gap 与 experience gate 的结构缺项。",
            "anti_pattern": "business 只有立场摘要，experience 只有页面清单，没有状态矩阵、关键页面蓝图与追踪映射。",
            "applies_to_stage": "cross_stage",
            "domain_tags": [],
            "task_type_tags": [],
            "classification_basis": [
                "check_status.status=passed",
                "validated_chain=business+experience",
            ],
            "confidence": "high",
            "source_tasks": [project_id],
            "source_artifacts": [
                f"projects/{project_id}/workspace/business_blueprint.md",
                f"projects/{project_id}/workspace/experience_blueprint.md",
                f"projects/{project_id}/workspace/check_status.json",
            ],
            "source_issue_ids": [],
            "status": "candidate",
        },
        task_context,
    )


def _build_domain_pattern(project_id: str, task_context: dict[str, Any], check_status: dict[str, Any]) -> dict[str, Any] | None:
    domain = str(task_context.get("domain") or "").strip()
    if not domain:
        return None
    if str(check_status.get("status") or "") != "passed":
        return None
    return classify_candidate(
        {
            "memory_id": f"pattern_{domain}_judgment_trace",
            "kind": "pattern",
            "scope": "domain",
            "title": f"{domain} 任务需要显式展开业务判断追踪映射",
            "rule": f"{domain} 任务的 business blueprint 需要把关键判断与决策依据显式追到具体节点，而不是只给结论。",
            "why_it_helps": "这能为 experience 转译提供稳定依据，并减少 orphan judgment 与 coverage gap。",
            "anti_pattern": "只写策略立场，不写判断链路、依据与被下游消费的追踪映射。",
            "applies_to_stage": "business",
            "domain_tags": [domain],
            "task_type_tags": [],
            "classification_basis": [],
            "confidence": "high",
            "source_tasks": [project_id],
            "source_artifacts": [
                f"projects/{project_id}/source/task_card.md",
                f"projects/{project_id}/workspace/business_blueprint.md",
                f"projects/{project_id}/workspace/check_status.json",
            ],
            "source_issue_ids": [],
            "status": "candidate",
        },
        task_context,
    )


def _build_failure_mode(project_id: str, task_context: dict[str, Any], issue_index: dict[str, Any]) -> dict[str, Any] | None:
    issues = [item for item in issue_index.get("issues", []) if isinstance(item, dict)]
    coverage_issue = next((item for item in issues if str(item.get("category") or "") == "coverage_gap"), None)
    if coverage_issue is None:
        return None
    issue_id = str(coverage_issue.get("issue_id") or "")
    return classify_candidate(
        {
            "memory_id": "failure_mode_orphan_judgment_coverage_gap",
            "kind": "failure_mode",
            "scope": "generic",
            "title": "未被体验层消费的业务判断会形成 coverage gap",
            "rule": "当 experience blueprint 没有承接关键业务判断时，最终检查很容易暴露 orphan judgment 或 coverage gap。",
            "why_it_helps": "提前检查 judgment-to-experience trace 能减少 validate / coverage 的反复重跑。",
            "anti_pattern": "business judgment 已写出，但 experience 没有对应页面、状态或追踪映射消费。",
            "applies_to_stage": "experience",
            "domain_tags": [],
            "task_type_tags": [],
            "classification_basis": [
                f"issue.category={coverage_issue.get('category')}",
                f"issue.source={coverage_issue.get('source')}",
            ],
            "confidence": "high",
            "source_tasks": [project_id],
            "source_artifacts": _collect_source_artifacts(project_id, issue_index),
            "source_issue_ids": [issue_id] if issue_id else [],
            "status": "candidate",
        },
        task_context,
    )


def _build_capability_insight(project_id: str, task_context: dict[str, Any], issue_index: dict[str, Any]) -> dict[str, Any] | None:
    issues = [item for item in issue_index.get("issues", []) if isinstance(item, dict)]
    coverage_issue = next((item for item in issues if str(item.get("category") or "") == "coverage_gap"), None)
    if coverage_issue is None:
        return None
    issue_id = str(coverage_issue.get("issue_id") or "")
    return classify_candidate(
        {
            "memory_id": "capability_insight_coverage_check_judgment_gap",
            "kind": "capability_insight",
            "scope": "domain" if task_context.get("domain") else "generic",
            "title": "coverage_check 能快速暴露未被体验层消费的业务判断",
            "rule": "在完整主链任务里，coverage_check 适合用来检查 business judgment 是否被 experience 页面、状态与追踪映射真正消费。",
            "why_it_helps": "把 coverage_check 放在归档前固定执行，有助于尽早发现 orphan judgment。",
            "anti_pattern": "只看 gate 通过就跳过 validate / coverage，导致 judgment coverage 缺口在归档前未暴露。",
            "applies_to_stage": "cross_stage",
            "domain_tags": [str(task_context.get("domain") or "")] if task_context.get("domain") else [],
            "task_type_tags": [],
            "classification_basis": [
                "capability_id=coverage_check",
                f"issue.category={coverage_issue.get('category')}",
            ],
            "confidence": "high" if task_context.get("domain") else "medium",
            "source_tasks": [project_id],
            "source_artifacts": [
                f"projects/{project_id}/workspace/check_status.json",
                f"projects/{project_id}/runtime/remediation/issue_index.json",
            ],
            "source_issue_ids": [issue_id] if issue_id else [],
            "status": "candidate",
            "capability_id": "coverage_check",
            "recommended_followup": [
                "优先核对 business judgment trace 与 experience trace mapping 的消费关系",
                "如发现 orphan judgment，先补 experience 页面与状态反馈映射，再重跑 validate / coverage",
            ],
        },
        task_context,
    )


def _build_candidates(project_id: str) -> list[dict[str, Any]]:
    task_context = _load_task_context(project_id)
    check_status = _read_check_status(project_id)
    issue_index = _read_issue_index(project_id)
    candidates = [
        _build_generic_pattern(project_id, task_context, check_status),
        _build_domain_pattern(project_id, task_context, check_status),
        _build_failure_mode(project_id, task_context, issue_index),
        _build_capability_insight(project_id, task_context, issue_index),
    ]
    return [candidate for candidate in candidates if isinstance(candidate, dict)]


def run_memory_extract(project_id: str) -> int:
    runtime_memory_dir = get_project_memory_dir(project_id)
    runtime_memory_dir.mkdir(parents=True, exist_ok=True)

    candidates = _build_candidates(project_id)
    extracted_payload = {
        "project_id": project_id,
        "generated_at": now_iso(),
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    trace_payload = {
        "project_id": project_id,
        "generated_at": now_iso(),
        "consumed_memory_ids": [],
        "extracted_candidate_ids": [str(item.get("memory_id") or "") for item in candidates],
        "accepted_memory_ids": [],
        "rejected_memory_ids": [],
        "deferred_memory_ids": [],
        "source_artifacts": [
            repo_rel(get_project_runtime_dir(project_id) / "task_card_resolved.json"),
            repo_rel(get_project_workspace_dir(project_id) / "check_status.json"),
            repo_rel(get_project_runtime_dir(project_id) / "remediation" / "issue_index.json"),
        ],
    }
    accepted_path = runtime_memory_dir / "accepted_memory_items.json"
    if not accepted_path.exists():
        write_json(
            accepted_path,
            {
                "project_id": project_id,
                "generated_at": "",
                "accepted_count": 0,
                "items": [],
            },
        )
    write_json(runtime_memory_dir / "extracted_memory_candidates.json", extracted_payload)
    write_json(runtime_memory_dir / "memory_trace.json", trace_payload)

    print(f"Extracted memory candidates: {runtime_memory_dir / 'extracted_memory_candidates.json'}")
    print(f"Memory trace written: {runtime_memory_dir / 'memory_trace.json'}")
    return 0
