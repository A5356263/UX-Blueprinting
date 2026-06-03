from __future__ import annotations

import json
import re
from pathlib import Path

from packages.common import get_project_runtime_dir, get_repo_root, normalize_repo_ref, repo_ref_to_path
from packages.knowledge_consumption.summary_parser import parse_summary_metadata

from .schemas import KnowledgeNote


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def _first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def _parse_bullets(text: str) -> list[str]:
    results: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            results.append(line[2:].strip())
    return results


def _classify_note(path_text: str, text: str) -> str:
    metadata = parse_summary_metadata(text)
    source_group = str(metadata.get("source_group") or "")
    if str(metadata.get("summary_role") or "").strip() == "light_route_card" and source_group in {"business", "guideline", "inbox"}:
        return source_group
    lowered = path_text.lower()
    if "knowledge/wiki/summaries/设计准则/" in lowered:
        return "guideline"
    if "knowledge/wiki/summaries/" in lowered:
        return "business"
    if "knowledge/wiki" in lowered:
        return "wiki"
    if "knowledge/raw" in lowered:
        return "raw"
    return "knowledge"


def _load_reference_paths_from_manifest(project_id: str, stage: str) -> list[str]:
    manifest_path = get_project_runtime_dir(project_id) / "context_manifest.json"
    if not manifest_path.exists():
        return []

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    references = payload.get("references")
    if not isinstance(references, list):
        return []
    refs: list[str] = []
    for item in references:
        if not isinstance(item, dict):
            continue
        consumed_by = [str(value) for value in item.get("consumed_by", []) if isinstance(value, str)]
        if stage not in consumed_by:
            continue
        reference = str(item.get("reference") or "").strip()
        if reference:
            refs.append(reference)
    return refs


def _read_note(repo_root: Path, note_id: str, ref_path: str) -> KnowledgeNote | None:
    normalized_ref = normalize_repo_ref(ref_path)
    path = repo_root / repo_ref_to_path(normalized_ref)
    if not path.exists() or not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    title = _first_heading(text, path.stem)
    bullets = _parse_bullets(text)
    signal_lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    signals = bullets[:6] or signal_lines[:6]
    summary = "；".join(signals[:3]) if signals else f"引用于 {title}"
    return KnowledgeNote(
        note_id=note_id,
        path=ref_path,
        kind=_classify_note(ref_path, text),
        title=title,
        summary=summary,
        signals=signals[:6],
    )


def load_knowledge_notes(project_id: str, stage: str) -> list[KnowledgeNote]:
    repo_root = get_repo_root()
    raw_refs = _load_reference_paths_from_manifest(project_id, stage)

    deduped: list[str] = []
    seen: set[str] = set()
    for ref in raw_refs:
        normalized = normalize_repo_ref(ref)
        if not normalized or normalized in seen or "*" in normalized:
            continue
        seen.add(normalized)
        deduped.append(normalized)

    notes: list[KnowledgeNote] = []
    for index, ref in enumerate(deduped, start=1):
        note = _read_note(repo_root, f"KN-{index:02d}", ref)
        if note is None:
            continue
        if stage in {"facts", "business"} and note.kind == "guideline":
            continue
        notes.append(note)
    return notes
