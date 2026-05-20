from __future__ import annotations

from typing import Any


def infer_task_type_tags(project_id: str) -> list[str]:
    lowered = project_id.lower()
    tags: list[str] = []
    if "self-apply" in lowered or "self_apply" in lowered:
        tags.append("self_apply")
    if "admin" in lowered:
        tags.append("admin_config")
    if "audit" in lowered:
        tags.append("audit_view")
    if "approval" in lowered:
        tags.append("approval_flow")
    return tags


def classify_candidate(candidate: dict[str, Any], task_context: dict[str, Any]) -> dict[str, Any]:
    domain = str(task_context.get("domain") or "").strip()
    guideline_refs = [str(value) for value in task_context.get("guideline_refs", []) if isinstance(value, str)]
    project_id = str(task_context.get("project_id") or "")

    classification_basis = [str(value) for value in candidate.get("classification_basis", []) if str(value).strip()]
    domain_tags = [str(value) for value in candidate.get("domain_tags", []) if str(value).strip()]
    task_type_tags = [str(value) for value in candidate.get("task_type_tags", []) if str(value).strip()]

    if not task_type_tags:
        task_type_tags = infer_task_type_tags(project_id)

    if candidate.get("scope") == "domain":
        if domain and not domain_tags:
            domain_tags = [domain]
        if domain:
            basis = f"context_manifest.task_contract.domain={domain}"
            if basis not in classification_basis:
                classification_basis.append(basis)
        for guideline_ref in guideline_refs:
            basis = f"guideline_ref={guideline_ref}"
            if basis not in classification_basis:
                classification_basis.append(basis)
    else:
        domain_tags = []

    if not classification_basis:
        classification_basis.append("fallback=generic")

    candidate["domain_tags"] = domain_tags
    candidate["task_type_tags"] = task_type_tags
    candidate["classification_basis"] = classification_basis
    candidate["confidence"] = str(candidate.get("confidence") or "medium")
    return candidate
