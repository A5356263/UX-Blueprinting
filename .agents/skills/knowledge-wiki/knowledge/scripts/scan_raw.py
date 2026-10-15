from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1] / "raw"
    files = sorted(p for p in root.rglob("*.md") if p.is_file())
    print(f"raw_total={len(files)}")
    if args.list:
        for file in files:
            print(file.relative_to(root).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
