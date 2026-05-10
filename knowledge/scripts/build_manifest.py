from __future__ import annotations

from datetime import date
from pathlib import Path


def classify(path: Path) -> tuple[str, str]:
    if "业务" in path.parts:
        return "business", "SRC-BIZ"
    if "设计准则" in path.parts:
        return "设计准则", "SRC-GDL"
    return "inbox", "SRC-INB"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    raw_root = root / "raw"
    out_generated = raw_root / "清单" / "source_manifest.generated.md"
    out_canonical = raw_root / "清单" / "source_manifest.md"
    rows: list[str] = []
    idx_map: dict[str, int] = {"SRC-BIZ": 0, "SRC-GDL": 0, "SRC-INB": 0}
    files = sorted(p for p in raw_root.rglob("*.md") if p.is_file() and "清单" not in p.parts)
    for file in files:
        group, prefix = classify(file)
        idx_map[prefix] += 1
        source_id = f"{prefix}-{idx_map[prefix]:04d}"
        rel = file.relative_to(root).as_posix()
        title = file.stem.replace("_", " ").replace("-", " ")
        rows.append(
            f"| {source_id} | {title} | {rel} | {group} | md | {date.today().isoformat()} | active | auto-generated |"
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
    manifest_text = "\n".join(content)
    out_generated.write_text(manifest_text, encoding="utf-8")
    out_canonical.write_text(manifest_text, encoding="utf-8")
    print(f"written={out_generated}")
    print(f"written={out_canonical}")
    print(f"record_count={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
