from __future__ import annotations

from .domain_registry import build_facts_required_wiki_by_domain


FACTS_REQUIRED_WIKI_BY_DOMAIN = build_facts_required_wiki_by_domain()

DEFAULT_KNOWLEDGE_BUDGET = {
    "facts": {"max_summary_refs": 8, "max_raw_refs": 0, "max_related_summaries": 2},
    "business": {"max_summary_refs": 12, "max_raw_refs": 10, "max_related_summaries": 5},
    "experience": {"max_summary_refs": 12, "max_raw_refs": 10, "max_related_summaries": 5},
}

STAGE_POLICIES = {
    "facts": "wiki_for_boundary_only",
    "business": "summary_refs_route_to_raw",
    "experience": "business_first_translation_with_raw_support",
}
