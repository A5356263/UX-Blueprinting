from __future__ import annotations

from pathlib import Path


RAW_MARKER = "页面结构语义（仅代表该页面基本结构语义，不代表所有状态）"
REQUIRED_WIKI_MARKERS = ["结构语义摘要", "原始区块关系图"]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    raw_path = root / "raw" / "business" / "permission" / "15_page_carrier_semantics.md"
    targets = [
        root / "wiki" / "topics" / "page-carrier-semantics-map.md",
        root / "wiki" / "topics" / "permission-domain-index.md",
        root / "wiki" / "entities" / "permission-detail-view.md",
    ]
    if not raw_path.exists():
        raise SystemExit(f"missing_raw={raw_path}")

    raw_text = raw_path.read_text(encoding="utf-8")
    if RAW_MARKER not in raw_text:
        raise SystemExit("raw_page_structure_semantics_marker_missing")

    checked = 0
    for target in targets:
        if not target.exists():
            raise SystemExit(f"missing_wiki_target={target}")
        text = target.read_text(encoding="utf-8")
        missing = [marker for marker in REQUIRED_WIKI_MARKERS if marker not in text]
        if missing:
            raise SystemExit(f"wiki_structure_semantics_missing={target.relative_to(root).as_posix()}::{','.join(missing)}")
        checked += 1

    print(f"raw_source={raw_path.relative_to(root).as_posix()}")
    print(f"checked_targets={checked}")
    for target in targets:
        print(f"synced_target={target.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
