"""
Build UXB distributable Skill package.

This is a reserved entry for future packaging.

Current project remains development-mode:
- packages/ stays at repository root
- knowledge/ stays at repository root
- .claude/skills/uxb/ may be added later as a thin Skill entry

Future distribution-mode may package selected specs, templates,
knowledge packs, scripts, and runtime adapters into dist/uxb-skill/.
"""

from __future__ import annotations


def main() -> int:
    print("build_skill_package is reserved for future distribution packaging.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
