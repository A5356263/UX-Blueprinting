from __future__ import annotations

from pathlib import Path

from packages.common import get_repo_root


FACTS_REQUIRED_WIKI_CANDIDATES = [
    "00_domain_overview.md",
    "01_scope_and_boundary.md",
    "02_glossary.md",
    "03_business_objects.md",
    "04_object_relations.md",
    "README.md",
]

STATIC_FACTS_REQUIRED_WIKI_FALLBACK = {
    "permission": [
        "knowledge/wiki/summaries/business/permission/00_domain_overview.md",
        "knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md",
        "knowledge/wiki/summaries/business/permission/02_glossary.md",
        "knowledge/wiki/summaries/business/permission/03_business_objects.md",
        "knowledge/wiki/summaries/business/permission/04_object_relations.md",
    ]
}


def _to_repo_relative(repo_root: Path, path: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


def build_facts_required_wiki_by_domain() -> dict[str, list[str]]:
    repo_root = get_repo_root()
    business_root = repo_root / "knowledge" / "wiki" / "summaries" / "business"
    result: dict[str, list[str]] = {}

    if not business_root.exists() or not business_root.is_dir():
        return STATIC_FACTS_REQUIRED_WIKI_FALLBACK.copy()

    for domain_dir in sorted(item for item in business_root.iterdir() if item.is_dir()):
        refs: list[str] = []
        for file_name in FACTS_REQUIRED_WIKI_CANDIDATES:
            candidate = domain_dir / file_name
            if candidate.exists() and candidate.is_file():
                refs.append(_to_repo_relative(repo_root, candidate))
        if refs:
            result[domain_dir.name] = refs

    return result or STATIC_FACTS_REQUIRED_WIKI_FALLBACK.copy()
