from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


TAG_PATTERN = re.compile(r"^\s*(?:-\s+)?\[(GAP|CONFLICT|QUESTION)\]\s*(.+?)\s*$")


def list_raw_files(raw_root: Path) -> list[Path]:
    return sorted(
        p
        for p in raw_root.rglob("*.md")
        if p.is_file() and "manifests" not in p.parts
    )


def source_group_for(path: Path) -> str:
    if "business" in path.parts:
        return "business"
    if "guidelines" in path.parts:
        return "guidelines"
    return "inbox"


def summary_path_for(root: Path, raw_file: Path) -> Path:
    raw_root = root / "raw"
    rel = raw_file.relative_to(raw_root)
    return root / "wiki" / "summaries" / rel


def summary_ref_for(root: Path, raw_file: Path) -> str:
    return f"knowledge/{summary_path_for(root, raw_file).relative_to(root).as_posix()}"


def page_id_for(raw_file: Path, group: str) -> str:
    rel = raw_file.with_suffix("").parts
    suffix = "-".join(part.upper().replace("-", "_") for part in rel)
    return f"PG-SUMMARY-{group.upper()}-{suffix}"


def title_for(lines: list[str], raw_file: Path) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return raw_file.stem


def nonempty_content_lines(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        cleaned.append(stripped)
    return cleaned


def extract_intro(lines: list[str], fallback_title: str) -> str:
    content = nonempty_content_lines(lines)
    intro_parts: list[str] = []
    for line in content:
        if line.startswith(("-", "*")) or re.match(r"^\d+\.", line):
            continue
        intro_parts.append(line)
        if len(" ".join(intro_parts)) >= 140:
            break
    if intro_parts:
        return " ".join(intro_parts[:3])
    return f"本摘要对应原始资料《{fallback_title}》，用于提供快速理解入口。"


def extract_scope(lines: list[str], group: str) -> tuple[list[str], list[str]]:
    applies: list[str] = []
    not_applies: list[str] = []
    for line in nonempty_content_lines(lines):
        if "适用" in line and len(applies) < 3:
            applies.append(line)
        elif "不适用" in line and len(not_applies) < 3:
            not_applies.append(line)
    if not applies:
        applies.append("适用于快速判断该原始资料是否与当前任务相关。")
        applies.append(f"适用于构建 {group} 领域的背景理解与阅读入口。")
    if not not_applies:
        not_applies.append("不适用于替代原文证据、细节条款或最终业务裁决。")
    return applies[:3], not_applies[:3]


def extract_key_facts(lines: list[str]) -> list[str]:
    facts: list[str] = []
    for line in nonempty_content_lines(lines):
        if TAG_PATTERN.search(line):
            continue
        if line.startswith(("-", "*")):
            facts.append(line.lstrip("-* ").strip())
        elif "：" in line or ":" in line:
            facts.append(line)
        if len(facts) >= 6:
            break
    if not facts:
        facts.append("原文以结构化说明为主，建议回查 raw 获取完整事实细节。")
    return facts[:6]


def extract_terms(lines: list[str]) -> list[str]:
    terms: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            term = stripped[3:].strip()
            if term and term not in terms:
                terms.append(term)
        elif stripped.startswith("### "):
            term = stripped[4:].strip()
            if term and term not in terms:
                terms.append(term)
        if len(terms) >= 6:
            break
    if not terms:
        terms.append("建议回查原文章节标题与列表项，确认关键对象。")
    return terms[:6]


def extract_tagged_items(lines: list[str]) -> list[str]:
    items: list[str] = []
    for line in lines:
        match = TAG_PATTERN.match(line.strip())
        if match:
            items.append(f"[{match.group(1)}] {match.group(2).strip()}")
    if not items:
        items.append("none")
    return items[:10]


def related_summaries_for(root: Path, raw_file: Path, all_raw_files: list[Path], max_items: int = 5) -> list[str]:
    raw_root = root / "raw"
    current_rel = raw_file.relative_to(raw_root)
    siblings = [p for p in all_raw_files if p.parent == raw_file.parent and p != raw_file]
    ordered = sorted(siblings, key=lambda p: p.name)
    related = [summary_ref_for(root, p) for p in ordered[:max_items]]
    if len(related) < max_items:
        for candidate in all_raw_files:
            if candidate == raw_file or candidate.parent == raw_file.parent:
                continue
            if current_rel.parts and candidate.parts[-1].startswith(current_rel.parts[-1][:2]):
                rel = summary_ref_for(root, candidate)
                if rel not in related:
                    related.append(rel)
            if len(related) >= max_items:
                break
    return related[:max_items]


def build_summary_content(root: Path, raw_file: Path, all_raw_files: list[Path]) -> str:
    lines = raw_file.read_text(encoding="utf-8").splitlines()
    group = source_group_for(raw_file)
    title = title_for(lines, raw_file)
    applies, not_applies = extract_scope(lines, group)
    summary_path = summary_path_for(root, raw_file)
    rel_source = f"knowledge/{raw_file.relative_to(root).as_posix()}"
    related = related_summaries_for(root, raw_file, all_raw_files)
    tagged = extract_tagged_items(lines)
    facts = extract_key_facts(lines)
    terms = extract_terms(lines)
    intro = extract_intro(lines, title)
    related_lines = related if related else ["none"]
    content = [
        f"# {title}",
        "",
        f"- page_id: {page_id_for(raw_file.relative_to(root / 'raw'), group)}",
        "- page_type: summary",
        f"- source_path: {rel_source}",
        f"- source_group: {group}",
        "- status: active",
        "- confidence: medium",
        f"- updated_at: {date.today().isoformat()}",
        f"- source_refs: [{rel_source}]",
        "- related_summaries:",
        *([f"  - {item}" for item in related_lines]),
        "",
        "## 1. 这份原始资料讲什么",
        "",
        intro,
        "",
        "## 2. 适用范围 / 不适用范围",
        "",
        "### 适用范围",
        *([f"- {item}" for item in applies]),
        "",
        "### 不适用范围",
        *([f"- {item}" for item in not_applies]),
        "",
        "## 3. 关键事实",
        "",
        *([f"- {item}" for item in facts]),
        "",
        "## 4. 关键术语 / 关键对象",
        "",
        *([f"- {item}" for item in terms]),
        "",
        "## 5. 当前缺口 / 冲突 / 问题",
        "",
        *([f"- {item}" for item in tagged]),
        "",
        "## 6. 相关摘要 / 建议继续阅读",
        "",
        *([f"- {item}" for item in related_lines]),
        "",
        f"> summary_path: knowledge/{summary_path.relative_to(root).as_posix()}",
        "",
    ]
    return "\n".join(content)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--only")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    raw_root = root / "raw"
    raw_files = list_raw_files(raw_root)
    if args.only:
        only_path = Path(args.only)
        target = only_path if only_path.is_absolute() else (root.parent / only_path if only_path.parts[:1] == ("knowledge",) else root / only_path)
        raw_files = [p for p in raw_files if p.resolve() == target.resolve()]

    updated: list[str] = []
    created_dirs: set[Path] = set()
    for raw_file in raw_files:
        summary_file = summary_path_for(root, raw_file)
        content = build_summary_content(root, raw_file, list_raw_files(raw_root))
        if args.apply and not args.dry_run:
            summary_file.parent.mkdir(parents=True, exist_ok=True)
            created_dirs.add(summary_file.parent)
            summary_file.write_text(content, encoding="utf-8")
        updated.append(summary_file.relative_to(root).as_posix())

    mode = "dry-run" if args.dry_run or not args.apply else "apply"
    print(f"mode={mode}")
    print(f"summary_count={len(updated)}")
    for item in updated:
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
