from __future__ import annotations

from datetime import date
from pathlib import Path


def classify(path: Path) -> tuple[str, str]:
    if "business" in path.parts:
        return "business", "SRC-BIZ"
    if "guidelines" in path.parts:
        return "guidelines", "SRC-GDL"
    return "inbox", "SRC-INB"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    raw_root = root / "raw"
    out = raw_root / "manifests" / "source_manifest.generated.md"
    rows: list[str] = []
    idx_map: dict[str, int] = {"SRC-BIZ": 0, "SRC-GDL": 0, "SRC-INB": 0}
    for file in sorted(p for p in raw_root.rglob("*.md") if p.is_file() and "manifests" not in p.parts):
        group, prefix = classify(file)
        idx_map[prefix] += 1
        source_id = f"{prefix}-{idx_map[prefix]:04d}"
        rel = file.relative_to(root).as_posix()
        title = file.stem.replace("_", " ").replace("-", " ")
        rows.append(
            f"| {source_id} | {title} | {rel} | {group} | md | {date.today().isoformat()} | 完整 | auto-generated |"
        )
    content = [
        "# Source Manifest Generated",
        "",
        f"- updated_at: {date.today().isoformat()}",
        "",
        "| source_id | title | path | source_group | source_type | date | status | notes |",
        "|---|---|---|---|---|---|---|---|",
        *rows,
        "",
    ]
    out.write_text("\n".join(content), encoding="utf-8")
    print(f"written={out}")
    print(f"record_count={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
