from __future__ import annotations

import argparse
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from export_knowledge_wiki_portable import (
    SOURCE_SKILL,
    assert_mapping_complete,
    collect_path_replacements,
    ensure_ascii_paths,
    ensure_counts_match,
    ensure_no_chinese_knowledge_paths,
    ensure_reference_paths_exist,
    rename_tree,
    rewrite_text_files,
)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def copy_source_tree(source_skill: Path, temp_root: Path) -> Path:
    temp_skill = temp_root / "knowledge-wiki"
    shutil.copytree(source_skill, temp_skill)
    return temp_skill


def backup_source_tree(source_skill: Path, backup_root: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / f"knowledge-wiki-backup-{timestamp}"
    shutil.copytree(source_skill, backup_dir)
    return backup_dir


def replace_source_tree(source_skill: Path, temp_skill: Path) -> None:
    source_skill.parent.mkdir(parents=True, exist_ok=True)
    if source_skill.exists():
        shutil.rmtree(source_skill)
    shutil.copytree(temp_skill, source_skill)


def validate_temp_skill(source_skill: Path, temp_skill: Path) -> None:
    ensure_counts_match(source_skill, temp_skill)
    ensure_ascii_paths(temp_skill)
    ensure_no_chinese_knowledge_paths(temp_skill)
    ensure_reference_paths_exist(temp_skill)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Migrate .claude/skills/knowledge-wiki source names to the reviewed ASCII naming scheme."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write the migrated temporary copy back to the source skill after validation.",
    )
    parser.add_argument(
        "--backup-dir",
        default="old",
        help="Directory under repo root where the original source tree backup will be stored when --apply is used.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = repo_root_from_script()
    source_skill = repo_root / SOURCE_SKILL
    backup_root = repo_root / args.backup_dir

    if not source_skill.exists():
        raise RuntimeError(f"未找到真源 knowledge-wiki: {source_skill}")

    assert_mapping_complete(source_skill)
    replacements = collect_path_replacements(source_skill)

    with tempfile.TemporaryDirectory(prefix="knowledge-wiki-source-migrate-", dir=repo_root) as temp_dir:
        temp_root = Path(temp_dir)
        temp_skill = copy_source_tree(source_skill, temp_root)

        rename_tree(temp_skill)
        rewrite_text_files(temp_skill, replacements)
        validate_temp_skill(source_skill, temp_skill)

        if not args.apply:
            print(f"source_skill={source_skill}")
            print(f"temp_skill={temp_skill}")
            print("mode=dry-run")
            print("status=ok")
            return 0

        backup_root.mkdir(parents=True, exist_ok=True)
        backup_dir = backup_source_tree(source_skill, backup_root)
        replace_source_tree(source_skill, temp_skill)

    print(f"source_skill={source_skill}")
    print(f"backup_dir={backup_dir}")
    print("mode=apply")
    print("status=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
