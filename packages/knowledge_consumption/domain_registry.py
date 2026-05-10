from __future__ import annotations

from pathlib import Path

from packages.common import get_knowledge_root_dir, get_repo_root

from .summary_parser import parse_summary_metadata


def _to_repo_relative(repo_root: Path, path: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


def _domain_from_summary_path(summary_root: Path, path: Path) -> str:
    rel_parts = path.relative_to(summary_root).parts
    return rel_parts[1] if len(rel_parts) > 1 else ""


def _entry_rank(path: Path) -> tuple[int, str]:
    if path.name == "README.md":
        return (0, path.name)
    if path.stem.startswith("00_"):
        return (1, path.name)
    return (2, path.name)


def build_facts_required_wiki_by_domain() -> dict[str, list[str]]:
    repo_root = get_repo_root()
    summaries_root = get_knowledge_root_dir() / "wiki" / "summaries"
    result: dict[str, list[str]] = {}

    if not summaries_root.exists() or not summaries_root.is_dir():
        return {}

    candidates_by_domain: dict[str, list[Path]] = {}
    for summary in summaries_root.rglob("*.md"):
        metadata = parse_summary_metadata(summary.read_text(encoding="utf-8"))
        if metadata.get("page_type") != "summary" or metadata.get("source_group") != "business":
            continue
        domain = _domain_from_summary_path(summaries_root, summary)
        if not domain:
            continue
        candidates_by_domain.setdefault(domain, []).append(summary)

    for domain, candidates in candidates_by_domain.items():
        ranked = sorted(candidates, key=_entry_rank)
        result[domain] = [_to_repo_relative(repo_root, candidate) for candidate in ranked[:8]]

    return result
