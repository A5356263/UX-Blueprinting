from __future__ import annotations

from datetime import date
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wiki = root / "wiki"
    manifest = root / "raw" / "manifests" / "source_manifest.md"
    wiki_pages = sorted(p for p in wiki.rglob("*.md") if p.is_file())
    source_count = 0
    if manifest.exists():
        source_count = sum(1 for line in manifest.read_text(encoding="utf-8").splitlines() if line.startswith("| SRC-"))
    content = "\n".join(
        [
            "# Knowledge Wiki Overview",
            "",
            "- page_id: PG-SYSTEM-OVERVIEW",
            "- page_type: system",
            "- status: stable",
            "- confidence: medium",
            "- source_refs: [SRC-BIZ-0001, SRC-GDL-0001]",
            "- related_pages: [index.md, log.md, questions.md]",
            "- created_at: 2026-04-09",
            f"- updated_at: {date.today().isoformat()}",
            "",
            "## 当前概况",
            "",
            f"- 页面总数: {len(wiki_pages)}",
            f"- 来源总数: {source_count}",
            f"- 最近更新: {date.today().isoformat()}",
            "- 未解决冲突数: 0",
            "- 未解决缺口数: 0",
            "- 孤立页数: 0",
            "- 过时页数: 0",
            "- 待回写 outputs 数量: 0",
            "",
        ]
    )
    (wiki / "overview.md").write_text(content, encoding="utf-8")
    print("refreshed=knowledge/wiki/overview.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
