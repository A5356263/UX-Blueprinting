#!/usr/bin/env python3
"""
UTF-8 aware quick validator for local Codex skills.

This mirrors the bundled skill validator but forces UTF-8 reads so
repository-local skills with Chinese content can be validated
reliably on Windows environments whose default text encoding is not UTF-8.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata"}


def validate_skill(skill_path: Path) -> tuple[bool, str]:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, f"{skill_path}: SKILL.md not found"

    try:
        content = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return False, f"{skill_path}: SKILL.md is not valid UTF-8: {exc}"

    if not content.startswith("---"):
        return False, f"{skill_path}: no YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, f"{skill_path}: invalid frontmatter format"

    frontmatter_text = match.group(1)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        return False, f"{skill_path}: invalid YAML in frontmatter: {exc}"

    if not isinstance(frontmatter, dict):
        return False, f"{skill_path}: frontmatter must be a YAML dictionary"

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        allowed = ", ".join(sorted(ALLOWED_PROPERTIES))
        unexpected = ", ".join(sorted(unexpected_keys))
        return (
            False,
            f"{skill_path}: unexpected frontmatter key(s): {unexpected}. Allowed: {allowed}",
        )

    name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not isinstance(name, str) or not name.strip():
        return False, f"{skill_path}: missing or invalid 'name'"
    if not re.match(r"^[a-z0-9-]+$", name):
        return False, f"{skill_path}: name '{name}' must use lowercase letters, digits, and hyphens only"
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return False, f"{skill_path}: name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > MAX_SKILL_NAME_LENGTH:
        return False, f"{skill_path}: name is too long ({len(name)}), max is {MAX_SKILL_NAME_LENGTH}"

    if not isinstance(description, str) or not description.strip():
        return False, f"{skill_path}: missing or invalid 'description'"
    if "<" in description or ">" in description:
        return False, f"{skill_path}: description cannot contain angle brackets"
    if len(description) > 1024:
        return False, f"{skill_path}: description is too long ({len(description)}), max is 1024"

    return True, f"{skill_path}: Skill is valid"


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python quick_validate_utf8.py <skill_directory> [<skill_directory> ...]")
        return 1

    failed = False
    for raw_path in argv[1:]:
        valid, message = validate_skill(Path(raw_path))
        print(message)
        if not valid:
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
