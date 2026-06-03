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
def build_knowledge_consumption_plan(task_id: str) -> dict[str, object]:
    decision = load_uxb_execution_decision(task_id)
    if str(decision.get("status") or "") != "confirmed":
        return {
            "selection_source": _selection_source(task_id),
            "files": [],
            "reasoning": "",
            "warnings": [],
            "errors": [str(item) for item in decision.get("validation_errors", []) if str(item).strip()],
        }

    knowledge_selection = decision.get("knowledge_selection")
    if not isinstance(knowledge_selection, dict):
        knowledge_selection = {}

    files = _dedupe_keep_order([str(item) for item in knowledge_selection.get("files", []) if isinstance(item, str)])
    reasoning = str(knowledge_selection.get("reasoning") or "").strip()

    return {
        "selection_source": _selection_source(task_id),
        "files": files,
        "reasoning": reasoning,
        "warnings": [],
        "errors": [],
    }
