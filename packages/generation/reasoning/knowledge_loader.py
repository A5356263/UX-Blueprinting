from __future__ import annotations

import re
from pathlib import Path

from packages.common import get_project_runtime_dir, get_project_source_dir, get_repo_root

from .schemas import KnowledgeNote


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def _split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip()] = text[start:end].strip()
    return sections


def _parse_bullets(text: str) -> list[str]:
    results: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            results.append(line[2:].strip())
    return results


def _first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def _classify_ref(path_text: str) -> str:
    lowered = path_text.lower()
    if "guideline" in lowered or "principle" in lowered:
        return "guideline"
    if "knowledge/wiki" in lowered:
        return "wiki"
    if "/business/" in lowered:
        return "business"
    if "knowledge/raw" in lowered:
        return "raw"
    return "knowledge"


def _load_reference_paths_from_task_card(project_id: str) -> list[str]:
    task_card_path = get_project_source_dir(project_id) / "task_card.md"
    if not task_card_path.exists():
        return []
    sections = _split_sections(task_card_path.read_text(encoding="utf-8"))
    refs: list[str] = []
    for section_name in ("Knowledge", "Wiki", "Knowledge Consumption Policy"):
        section = sections.get(section_name, "")
        refs.extend([item for item in _parse_bullets(section) if "/" in item and not item.startswith("mode:")])
    return refs


def _load_reference_paths_from_manifest(project_id: str, stage: str) -> list[str]:
    manifest_path = get_project_runtime_dir(project_id) / "context_manifest.json"
    if not manifest_path.exists():
        return []
    import json

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    refs: list[str] = []
    for item in payload.get("references", []):
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
    path = repo_root / Path(ref_path.replace("/", "\\"))
    if not path.exists() or not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    title = _first_heading(text, path.stem)
    bullets = _parse_bullets(text)
    signal_lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    signals = bullets[:6] or signal_lines[:6]
    summary = "；".join(signals[:3]) if signals else f"引用了 {title}"
    return KnowledgeNote(
        note_id=note_id,
        path=ref_path,
        kind=_classify_ref(ref_path),
        title=title,
        summary=summary,
        signals=signals[:6],
    )


def load_knowledge_notes(project_id: str, stage: str) -> list[KnowledgeNote]:
    repo_root = get_repo_root()
    raw_refs = _load_reference_paths_from_manifest(project_id, stage) or _load_reference_paths_from_task_card(project_id)
    deduped: list[str] = []
    seen: set[str] = set()
    for ref in raw_refs:
        normalized = ref.replace("\\", "/").strip()
        if not normalized or normalized in seen or "*" in normalized:
            continue
        seen.add(normalized)
        deduped.append(normalized)

    notes: list[KnowledgeNote] = []
    for index, ref in enumerate(deduped, start=1):
        note = _read_note(repo_root, f"KN-{index:02d}", ref)
        if note is None:
            continue
        if stage == "facts" and note.kind == "guideline":
            continue
        if stage == "business" and note.kind == "guideline":
            continue
        notes.append(note)
    return notes
