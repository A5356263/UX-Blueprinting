from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    candidates_root = root / "candidates" / "未入库"
    files = sorted(path for path in candidates_root.rglob("*.md") if path.is_file())

    print(f"unimported_candidate_count={len(files)}")
    for file in files:
        print(f"- knowledge/{file.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
