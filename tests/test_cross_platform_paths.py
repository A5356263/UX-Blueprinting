from __future__ import annotations

import unittest
from pathlib import Path

from packages.common import (
    extract_uxb_complexity_ref_suffix,
    normalize_repo_ref,
    repo_ref_to_path,
    to_repo_ref,
)


class CrossPlatformPathTests(unittest.TestCase):
    def test_normalize_repo_ref_unifies_slashes(self) -> None:
        self.assertEqual(
            normalize_repo_ref(r"\templates\facts.template.md"),
            "templates/facts.template.md",
        )

    def test_repo_ref_to_path_builds_path_parts(self) -> None:
        self.assertEqual(
            repo_ref_to_path("templates/facts.template.md"),
            Path("templates") / "facts.template.md",
        )

    def test_repo_ref_to_path_rejects_wildcards(self) -> None:
        with self.assertRaises(ValueError):
            repo_ref_to_path("templates/*.md")

    def test_to_repo_ref_always_returns_posix_style(self) -> None:
        repo_root = Path.cwd()
        target = repo_root / "templates" / "facts.template.md"
        self.assertEqual(to_repo_ref(target, repo_root), "templates/facts.template.md")

    def test_extract_complexity_suffix_accepts_codex_and_claude_hosts(self) -> None:
        codex_ref = ".codex/skills/uxb/references/complexity/00_core_complexity_judgment.md"
        claude_ref = ".claude/skills/uxb/references/complexity/00_core_complexity_judgment.md"
        expected = "00_core_complexity_judgment.md"
        self.assertEqual(extract_uxb_complexity_ref_suffix(codex_ref), expected)
        self.assertEqual(extract_uxb_complexity_ref_suffix(claude_ref), expected)


if __name__ == "__main__":
    unittest.main()
