from __future__ import annotations

from pathlib import Path

from packages.common import get_repo_root

from .policy import DEFAULT_KNOWLEDGE_BUDGET, FACTS_REQUIRED_WIKI_BY_DOMAIN, STAGE_POLICIES
from .summary_parser import parse_summary_metadata


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


def _is_summary_ref(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized.startswith("knowledge/wiki/summaries/") and normalized.endswith(".md")


def _is_guideline_summary(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    return "/设计准则/" in normalized


def _is_business_summary(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    return "/业务/" in normalized


def _looks_like_experience_summary(path: str) -> bool:
    normalized = Path(path.replace("\\", "/")).name.lower()
    return any(token in normalized for token in ("experience", "copy", "carrier", "risk", "translation", "page"))


def _read_summary_metadata(repo_root: Path, summary_ref: str) -> dict[str, object]:
    path = repo_root / Path(summary_ref.replace("/", "\\"))
    if not path.exists() or not path.is_file():
        return {}
    return parse_summary_metadata(path.read_text(encoding="utf-8"))


def build_knowledge_consumption_plan(resolved: dict[str, object]) -> tuple[dict[str, object], list[dict[str, str]]]:
    repo_root = get_repo_root()
    domain = str(resolved.get("domain") or "").strip()
    task_refs = _dedupe_keep_order([*map(str, resolved.get("knowledge_refs", [])), *map(str, resolved.get("wiki_refs", []))])
    summary_refs = [ref for ref in task_refs if _is_summary_ref(ref)]
    guideline_entry_refs = _dedupe_keep_order([str(item) for item in resolved.get("guideline_refs", []) if isinstance(item, str)])

    summary_metadata: dict[str, dict[str, object]] = {}
    for summary_ref in _dedupe_keep_order(summary_refs + guideline_entry_refs):
        summary_metadata[summary_ref] = _read_summary_metadata(repo_root, summary_ref)

    facts_required_default = FACTS_REQUIRED_WIKI_BY_DOMAIN.get(domain, [])
    facts_required_wiki_refs = _dedupe_keep_order(facts_required_default[: DEFAULT_KNOWLEDGE_BUDGET["facts"]["max_summary_refs"]])

    business_summary_refs = _dedupe_keep_order([ref for ref in summary_refs if _is_business_summary(ref)])
    business_summary_refs = business_summary_refs[: DEFAULT_KNOWLEDGE_BUDGET["business"]["max_summary_refs"]]

    guideline_refs = _dedupe_keep_order([ref for ref in summary_refs if _is_guideline_summary(ref) and ref not in guideline_entry_refs])
    experience_summary_refs = _dedupe_keep_order([ref for ref in summary_refs if _looks_like_experience_summary(ref)])
    if not experience_summary_refs:
        experience_summary_refs = business_summary_refs[:]
    experience_summary_refs = experience_summary_refs[: DEFAULT_KNOWLEDGE_BUDGET["experience"]["max_summary_refs"]]

    def collect_related(seed_refs: list[str], limit: int) -> list[str]:
        candidates: list[str] = []
        for summary_ref in seed_refs:
            metadata = summary_metadata.get(summary_ref, {})
            for related in metadata.get("related_summaries", []):
                if not isinstance(related, str):
                    continue
                if _is_summary_ref(related):
                    candidates.append(related)
        return _dedupe_keep_order(candidates)[:limit]

    business_related = collect_related(business_summary_refs, DEFAULT_KNOWLEDGE_BUDGET["business"]["max_related_summaries"])
    experience_related = collect_related(
        _dedupe_keep_order(experience_summary_refs + guideline_refs),
        DEFAULT_KNOWLEDGE_BUDGET["experience"]["max_related_summaries"],
    )

    source_ref_chains: list[dict[str, str]] = []

    def collect_raw_from_summaries(stage: str, refs: list[str], related_refs: list[str], max_raw: int) -> list[str]:
        raw_refs: list[str] = []
        for summary_ref in _dedupe_keep_order(refs + related_refs):
            metadata = summary_metadata.get(summary_ref)
            if metadata is None:
                metadata = _read_summary_metadata(repo_root, summary_ref)
                summary_metadata[summary_ref] = metadata
            for raw_ref in metadata.get("source_refs", []):
                if not isinstance(raw_ref, str):
                    continue
                normalized = raw_ref.replace("\\", "/").strip()
                if not normalized.startswith("knowledge/raw/"):
                    continue
                if normalized.endswith("/") or "." not in Path(normalized).name:
                    continue
                if normalized not in raw_refs:
                    raw_refs.append(normalized)
                    source_ref_chains.append(
                        {
                            "stage": stage,
                            "summary": summary_ref,
                            "raw": normalized,
                            "reason": "source_refs",
                        }
                    )
                if len(raw_refs) >= max_raw:
                    return raw_refs
        return raw_refs

    business_raw_refs = collect_raw_from_summaries(
        "business",
        business_summary_refs,
        business_related,
        DEFAULT_KNOWLEDGE_BUDGET["business"]["max_raw_refs"],
    )
    experience_raw_refs = collect_raw_from_summaries(
        "experience",
        _dedupe_keep_order(experience_summary_refs + guideline_refs),
        experience_related,
        DEFAULT_KNOWLEDGE_BUDGET["experience"]["max_raw_refs"],
    )

    plan = {
        "mode": "wiki_routed_raw_precision",
        "facts": {
            "required_wiki_refs": facts_required_wiki_refs,
            "raw_refs_from_source_refs": [],
            "policy": STAGE_POLICIES["facts"],
        },
        "business": {
            "summary_refs": business_summary_refs,
            "related_summary_refs": business_related,
            "raw_refs_from_source_refs": business_raw_refs,
            "policy": STAGE_POLICIES["business"],
        },
        "experience": {
            "guideline_entry_refs": guideline_entry_refs,
            "summary_refs": experience_summary_refs,
            "guideline_refs": guideline_refs,
            "related_summary_refs": experience_related,
            "raw_refs_from_source_refs": experience_raw_refs,
            "policy": STAGE_POLICIES["experience"],
        },
    }
    return plan, source_ref_chains
