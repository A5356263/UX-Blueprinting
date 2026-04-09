from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "raw"
    files = sorted(p for p in root.rglob("*") if p.is_file())
    print(f"raw_root={root}")
    print(f"file_count={len(files)}")
    for file in files:
        print(file.relative_to(root).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
