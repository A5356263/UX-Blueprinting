from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path


TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".py"}
SOURCE_SHARED = Path("_shared")
SOURCE_SKILLS = Path(".claude/skills")
DEFAULT_ZIP = Path("intranet-agent-package.zip")
KNOWLEDGE_SKILL_NAME = "knowledge-wiki"
INTRANET_KNOWLEDGE_SKILL_NAME = "knowledge-wiki_private"

TEXT_REPLACEMENTS = (
    (".claude/skills/knowledge-wiki/knowledge/", "knowledge-wiki_private/knowledge/"),
    (".claude\\skills\\knowledge-wiki\\knowledge\\", "knowledge-wiki_private/knowledge/"),
    ("skills/knowledge-wiki/knowledge/", "knowledge-wiki_private/knowledge/"),
    ("skills\\knowledge-wiki\\knowledge\\", "knowledge-wiki_private/knowledge/"),
    ("knowledge-wiki/knowledge/", "knowledge-wiki_private/knowledge/"),
    ("knowledge-wiki\\knowledge\\", "knowledge-wiki_private/knowledge/"),
    ("knowledge-root/", "knowledge-wiki_private/knowledge/"),
    ("knowledge-root\\", "knowledge-wiki_private/knowledge/"),
    (".claude/skills/knowledge-wiki", "knowledge-wiki_private"),
    (".claude\\skills\\knowledge-wiki", "knowledge-wiki_private"),
)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export an intranet-ready package from _shared and .claude/skills."
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_ZIP),
        help="Zip file path relative to repo root or absolute path.",
    )
    return parser


def copy_export_sources(repo_root: Path, temp_root: Path) -> Path:
    export_root = temp_root / "intranet-agent-package"
    shutil.copytree(repo_root / SOURCE_SHARED, export_root / "_shared")
    shutil.copytree(
        repo_root / SOURCE_SKILLS,
        export_root / "skills",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    return export_root


def rename_knowledge_skill(export_root: Path) -> None:
    source = export_root / "skills" / KNOWLEDGE_SKILL_NAME
    target = export_root / "skills" / INTRANET_KNOWLEDGE_SKILL_NAME
    if not source.exists():
        raise RuntimeError(f"Missing source knowledge skill: {source}")
    if target.exists():
        raise RuntimeError(f"Target knowledge skill already exists: {target}")
    source.rename(target)


def rewrite_text_files(export_root: Path) -> list[Path]:
    changed: list[Path] = []
    for path in export_root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        original = path.read_text(encoding="utf-8")
        updated = original
        for source, target in TEXT_REPLACEMENTS:
            updated = updated.replace(source, target)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(path)
    return changed


def ensure_required_paths(export_root: Path) -> None:
    required = (
        export_root / "_shared",
        export_root / "skills",
        export_root / "skills" / INTRANET_KNOWLEDGE_SKILL_NAME,
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError("Missing exported paths: " + ", ".join(missing))


def ensure_no_legacy_knowledge_paths(export_root: Path) -> None:
    legacy_markers = (
        ".claude/skills/knowledge-wiki",
        ".claude\\skills\\knowledge-wiki",
        "knowledge-wiki/knowledge/",
        "knowledge-wiki\\knowledge\\",
        "knowledge-root/",
        "knowledge-root\\",
    )
    offenders: list[str] = []
    for path in export_root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for marker in legacy_markers:
            if marker in text:
                offenders.append(f"{path.relative_to(export_root).as_posix()}: {marker}")
    if offenders:
        preview = "; ".join(offenders[:10])
        raise RuntimeError(f"Legacy knowledge path markers remain: {preview}")


def write_zip(export_root: Path, output_zip: Path) -> None:
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(export_root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(export_root).as_posix())


def resolve_output_path(repo_root: Path, output_arg: str) -> Path:
    output_path = Path(output_arg)
    if output_path.is_absolute():
        return output_path
    return repo_root / output_path


def main() -> int:
    args = build_parser().parse_args()
    repo_root = repo_root_from_script()
    output_zip = resolve_output_path(repo_root, args.output)

    with tempfile.TemporaryDirectory(prefix="intranet-agent-package-", dir=repo_root) as temp_dir:
        export_root = copy_export_sources(repo_root, Path(temp_dir))
        rename_knowledge_skill(export_root)
        changed_files = rewrite_text_files(export_root)
        ensure_required_paths(export_root)
        ensure_no_legacy_knowledge_paths(export_root)
        write_zip(export_root, output_zip)

    print(f"output_zip={output_zip}")
    print(f"changed_files={len(changed_files)}")
    print("knowledge_skill=knowledge-wiki_private")
    print("status=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
