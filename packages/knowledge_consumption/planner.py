from __future__ import annotations

from packages.route_decision import load_uxb_execution_decision


def _selection_source(task_id: str) -> str:
    return f"projects/{task_id}/runtime/uxb_route_decision.json"


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = value.replace("\\", "/").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _stage_summary_refs(summary_refs: dict[str, list[str]]) -> dict[str, dict[str, list[str]]]:
    business_refs = _dedupe_keep_order(summary_refs.get("business", []))
    guideline_refs = _dedupe_keep_order(summary_refs.get("guideline", []))
    complexity_refs = _dedupe_keep_order(summary_refs.get("complexity", []))
    return {
        "facts": {
            "summary_refs": complexity_refs,
            "raw_refs": [],
        },
        "business": {
            "summary_refs": business_refs + [item for item in complexity_refs if item not in business_refs],
            "raw_refs": [],
        },
        "experience": {
            "summary_refs": guideline_refs,
            "raw_refs": [],
        },
    }


def build_knowledge_consumption_plan(task_id: str) -> dict[str, object]:
    decision = load_uxb_execution_decision(task_id)
    if str(decision.get("status") or "") != "confirmed":
        return {
            "selection_source": _selection_source(task_id),
            "summary_refs": {"business": [], "guideline": [], "complexity": []},
            "raw_escalation_plan": [],
            "stage_refs": {stage: {"summary_refs": [], "raw_refs": []} for stage in ("facts", "business", "experience")},
            "selection_reasons": [],
            "warnings": [],
            "errors": [str(item) for item in decision.get("validation_errors", []) if str(item).strip()],
        }

    knowledge_selection = decision.get("knowledge_selection")
    if not isinstance(knowledge_selection, dict):
        knowledge_selection = {}

    summary_refs = knowledge_selection.get("summary_refs")
    if not isinstance(summary_refs, dict):
        summary_refs = {}
    normalized_summary_refs = {
        "business": _dedupe_keep_order([str(item) for item in summary_refs.get("business", []) if isinstance(item, str)]),
        "guideline": _dedupe_keep_order([str(item) for item in summary_refs.get("guideline", []) if isinstance(item, str)]),
        "complexity": _dedupe_keep_order([str(item) for item in summary_refs.get("complexity", []) if isinstance(item, str)]),
    }

    raw_escalation_plan_raw = knowledge_selection.get("raw_escalation_plan")
    raw_escalation_plan = raw_escalation_plan_raw if isinstance(raw_escalation_plan_raw, list) else []
    stage_refs = _stage_summary_refs(normalized_summary_refs)

    for item in raw_escalation_plan:
        if not isinstance(item, dict):
            continue
        raw_ref = str(item.get("raw_ref") or "").replace("\\", "/").strip()
        if not raw_ref:
            continue
        for stage in [str(stage_name).strip() for stage_name in item.get("used_for_stage", []) if str(stage_name).strip()]:
            if stage not in stage_refs:
                continue
            stage_refs[stage]["raw_refs"].append(raw_ref)

    for stage_payload in stage_refs.values():
        stage_payload["summary_refs"] = _dedupe_keep_order(stage_payload.get("summary_refs", []))
        stage_payload["raw_refs"] = _dedupe_keep_order(stage_payload.get("raw_refs", []))

    selection_reasons_raw = knowledge_selection.get("selection_reasons")
    selection_reasons = selection_reasons_raw if isinstance(selection_reasons_raw, list) else []

    return {
        "selection_source": _selection_source(task_id),
        "summary_refs": normalized_summary_refs,
        "raw_escalation_plan": raw_escalation_plan,
        "stage_refs": stage_refs,
        "selection_reasons": selection_reasons,
        "warnings": [],
        "errors": [],
    }
