from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


TAG_PATTERN = re.compile(r"^\s*(?:-\s+)?\[(GAP|CONFLICT|QUESTION)\]\s*(.+?)\s*$")
PLACEHOLDER_TEXT = "待 AI Code 读取 raw 后生成。"

# 需保护的语义节标题（脚本不覆盖）
SEMANTIC_SECTIONS = [
    "## 1. 知识定位",
    "## 2. 任务触发线索",
    "## 3. 覆盖内容",
    "## 4. 可直接使用的稳定结论",
]


def list_raw_files(raw_root: Path) -> list[Path]:
    return sorted(
        p
        for p in raw_root.rglob("*.md")
        if p.is_file() and "清单" not in p.parts
    )


def source_group_for(path: Path) -> str:
    if "业务" in path.parts:
        return "business"
    if "设计准则" in path.parts:
        return "设计准则"
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


def build_raw_lookup_rules() -> list[str]:
    """返回必须回查 raw 的通用规则（结构性内容，非语义）。"""
    return [
        "需要完整规则细节或精确条款时",
        "需要正式证据或原文引用时",
        "需要页面或流程的完整描述时",
        "涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时",
        "summary 无法覆盖当前判断点或信息量不足时",
    ]


# ---- 骨架与元数据保护 ----

def parse_existing_semantic_sections(text: str) -> dict[str, str]:
    """从已有 summary 中提取 sections 1-4 的现有语义内容。"""
    sections: dict[str, str] = {}
    lines = text.splitlines()
    current_key: str | None = None
    current_lines: list[str] = []

    section_starts = {
        "## 1. 知识定位": "s1_position",
        "## 2. 任务触发线索": "s2_triggers",
        "## 3. 覆盖内容": "s3_coverage",
        "## 4. 可直接使用的稳定结论": "s4_conclusions",
    }
    next_sections = {
        "s1_position": "## 2. 任务触发线索",
        "s2_triggers": "## 3. 覆盖内容",
        "s3_coverage": "## 4. 可直接使用的稳定结论",
        "s4_conclusions": "## 5. 必须回查 raw 的情况",
    }

    for line in lines:
        stripped = line.strip()
        if stripped in section_starts:
            # 先保存上一节内容，再切换
            if current_key and current_lines:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = section_starts[stripped]
            current_lines = []
            continue
        if current_key and stripped == next_sections.get(current_key, ""):
            sections[current_key] = "\n".join(current_lines).strip()
            current_key = None
            current_lines = []
            continue
        if current_key:
            current_lines.append(line)

    if current_key and current_lines:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections


def has_placeholder(text: str) -> bool:
    """检查文本中是否含占位符。"""
    return PLACEHOLDER_TEXT in text


def extract_status(text: str) -> str:
    """从 summary 元数据中提取 status。"""
    for line in text.splitlines():
        if line.strip().startswith("- status:"):
            return line.split(":", 1)[1].strip()
    return "draft"


def extract_confidence(text: str) -> str:
    """从 summary 元数据中提取 confidence。"""
    for line in text.splitlines():
        if line.strip().startswith("- confidence:"):
            return line.split(":", 1)[1].strip()
    return "low"


def extract_semantic_status(text: str) -> str:
    """从已有 summary 元数据中提取 semantic_status。"""
    for line in text.splitlines():
        if line.strip().startswith("- semantic_status:"):
            return line.split(":", 1)[1].strip()
    return "pending"


# ---- 核心生成函数 ----

def build_summary_content(root: Path, raw_file: Path, all_raw_files: list[Path], force_regenerate: bool = False) -> str:
    lines = raw_file.read_text(encoding="utf-8").splitlines()
    group = source_group_for(raw_file)
    title = title_for(lines, raw_file)
    summary_path = summary_path_for(root, raw_file)
    rel_source = f"knowledge/{raw_file.relative_to(root).as_posix()}"
    related = related_summaries_for(root, raw_file, all_raw_files)
    tagged = extract_tagged_items(lines)
    lookup_rules = build_raw_lookup_rules()
    related_lines = related if related else ["none"]
    today_str = date.today().isoformat()

    existing_summary = summary_path if summary_path.exists() else None
    existing_text = existing_summary.read_text(encoding="utf-8") if existing_summary else None

    # 判断模式
    if existing_text and not force_regenerate:
        # ---- 元数据保护模式：保留 AI 语义内容 ----
        existing_sections = parse_existing_semantic_sections(existing_text)
        s1 = existing_sections.get("s1_position", PLACEHOLDER_TEXT)
        s2 = existing_sections.get("s2_triggers", PLACEHOLDER_TEXT)
        s3 = existing_sections.get("s3_coverage", PLACEHOLDER_TEXT)
        s4 = existing_sections.get("s4_conclusions", PLACEHOLDER_TEXT)
        status = extract_status(existing_text)
        confidence = extract_confidence(existing_text)
        semantic_status = extract_semantic_status(existing_text)
    else:
        # ---- 骨架模式：占位符 ----
        s1 = PLACEHOLDER_TEXT
        s2 = PLACEHOLDER_TEXT
        s3 = PLACEHOLDER_TEXT
        s4 = PLACEHOLDER_TEXT
        status = "draft"
        confidence = "low"
        semantic_status = "pending"

    # 组装 summary
    s1_body = _format_section_body(s1)
    s2_body = _format_section_body(s2)
    s3_body = _format_section_body(s3)
    s4_body = _format_section_body(s4)

    content = [
        f"# {title}",
        "",
        f"- page_id: {page_id_for(raw_file.relative_to(root / 'raw'), group)}",
        "- page_type: summary",
        f"- source_path: {rel_source}",
        f"- source_group: {group}",
        f"- status: {status}",
        f"- confidence: {confidence}",
        "- summary_role: ai_route_card",
        f"- semantic_status: {semantic_status}",
        f"- semantic_updated_at: {today_str}",
        f"- updated_at: {today_str}",
        f"- source_refs: [{rel_source}]",
        "- related_summaries:",
        *([f"  - {item}" for item in related_lines]),
        "",
        "## 1. 知识定位",
        "",
        s1_body,
        "",
        "## 2. 任务触发线索",
        "",
        s2_body,
        "",
        "## 3. 覆盖内容",
        "",
        s3_body,
        "",
        "## 4. 可直接使用的稳定结论",
        "",
        s4_body,
        "",
        "## 5. 必须回查 raw 的情况",
        "",
        "以下情况不能只读 summary：",
        "",
        *([f"- {item}" for item in lookup_rules]),
        "",
        "## 6. 缺口 / 冲突 / 不确定项",
        "",
        *([f"- {item}" for item in tagged]),
        "",
        "## 7. 邻近阅读",
        "",
        "弱指向 3-5 个相关 summary。",
        "",
        *([f"- {item}" for item in related_lines]),
        "",
        f"> summary_path: knowledge/{summary_path.relative_to(root).as_posix()}",
        "",
    ]
    return "\n".join(content)


def _format_section_body(text: str) -> str:
    """格式化节正文：检查是否占位符，占位符不额外缩进。"""
    if text == PLACEHOLDER_TEXT:
        return text
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--only")
    parser.add_argument("--force-regenerate", action="store_true")
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
        content = build_summary_content(root, raw_file, list_raw_files(raw_root), force_regenerate=args.force_regenerate)
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
