from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wiki = root / "wiki"
    files = sorted(p for p in wiki.rglob("*.md") if p.is_file())
    missing_source_refs: list[str] = []
    for file in files:
        text = file.read_text(encoding="utf-8")
        if "source_refs" not in text and file.name not in {"README.md", "log.md"}:
            missing_source_refs.append(file.relative_to(wiki).as_posix())
    report = root / "outputs" / "lint" / "latest_lint_report.md"
    lines = [
        "# Wiki Lint Report",
        "",
        f"- total_pages: {len(files)}",
        f"- missing_source_refs: {len(missing_source_refs)}",
        "",
        "## missing_source_refs_pages",
        "",
        *([f"- {x}" for x in missing_source_refs] if missing_source_refs else ["- none"]),
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"report={report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
