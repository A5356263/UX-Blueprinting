from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SECTION_HEADERS = {"## Skills", "## Knowledge", "## Wiki", "## Templates"}


def parse_references(task_card_text: str) -> list[str]:
    refs: list[str] = []
    current_section = ""
    for raw_line in task_card_text.splitlines():
        line = raw_line.strip()
        if line in SECTION_HEADERS:
            current_section = line
            continue
        if line.startswith("## "):
            current_section = ""
            continue
        if current_section and line.startswith("- "):
            value = line[2:].strip()
            if "/" in value:
                refs.append(value)
    return refs


def copy_reference(repo_root: Path, target_root: Path, reference: str) -> dict[str, str]:
    source = repo_root / Path(reference.replace("/", "\\"))
    destination = target_root / Path(reference.replace("/", "\\"))
    destination.parent.mkdir(parents=True, exist_ok=True)

    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
        ref_type = "directory"
    else:
        shutil.copy2(source, destination)
        ref_type = "file"

    return {
        "reference": reference,
        "type": ref_type,
        "source": str(source),
        "destination": str(destination),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    task_dir = repo_root / "tasks" / "active" / args.task_id
    task_card_path = task_dir / "task_card.md"
    context_bundle_dir = task_dir / "artifacts" / "context_bundle"
    context_bundle_dir.mkdir(parents=True, exist_ok=True)

    task_card_text = task_card_path.read_text(encoding="utf-8")
    references = parse_references(task_card_text)
    copied = [copy_reference(repo_root, context_bundle_dir, reference) for reference in references]

    manifest = {
        "task_id": args.task_id,
        "reference_count": len(copied),
        "references": copied,
    }
    manifest_path = context_bundle_dir / "context_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Context assembled: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
