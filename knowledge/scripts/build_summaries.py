from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from _write_if_changed import parse_metadata_value, replace_metadata_value, write_text_if_changed

TAG_PATTERN = re.compile(r"^\s*(?:-\s+)?\[(GAP|CONFLICT|QUESTION)\]\s*(.+?)\s*$")
PLACEHOLDER_POSITION = "待 AI Code 读取 raw 后补充这份知识的定位。"
PLACEHOLDER_TRIGGERS = ["待 AI Code 读取 raw 后补充触发信号。"]
PLACEHOLDER_CONCLUSIONS = ["待 AI Code 读取 raw 后补充稳定结论。"]
PLACEHOLDER_GAPS = ["暂无"]

SECTION_KEYS = {
    "## 定位": "positioning",
    "## 触发信号": "signals",
    "## 稳定结论": "conclusions",
    "## 已知缺口": "gaps",
}


def list_raw_files(raw_root: Path) -> list[Path]:
    return sorted(path for path in raw_root.rglob("*.md") if path.is_file())


def domain_for(path: Path) -> str:
    parts = path.parts
    if "设计准则" in parts:
        return "设计准则"
    if "业务" not in parts:
        return ""
    business_index = parts.index("业务")
    domain_parts = parts[business_index + 1 : -1]
    if not domain_parts:
        return "业务总览"
    return domain_parts[-1]


def summary_path_for(root: Path, raw_file: Path) -> Path:
    rel = raw_file.relative_to(root / "raw")
    return root / "wiki" / "summaries" / rel


def title_for(lines: list[str], raw_file: Path) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return raw_file.stem


def extract_tagged_items(lines: list[str]) -> list[str]:
    items: list[str] = []
    for line in lines:
        match = TAG_PATTERN.match(line.strip())
        if match:
            items.append(f"[{match.group(1)}] {match.group(2).strip()}")
    return items[:10]


def parse_existing_sections(text: str) -> dict[str, list[str] | str]:
    lines = text.splitlines()
    current_key = ""
    buffer: list[str] = []
    sections: dict[str, list[str] | str] = {}

    def _flush() -> None:
        if not current_key:
            return
        if current_key == "positioning":
            sections[current_key] = "\n".join(buffer).strip()
        else:
            values: list[str] = []
            for item in buffer:
                stripped = item.strip()
                if stripped.startswith("- "):
                    value = stripped[2:].strip()
                    if value:
                        values.append(value)
            sections[current_key] = values

    for line in lines:
        heading = line.strip()
        if heading in SECTION_KEYS:
            _flush()
            current_key = SECTION_KEYS[heading]
            buffer = []
            continue
        if current_key:
            buffer.append(line)
    _flush()
    return sections


def with_stable_timestamps(content: str, existing_text: str | None) -> str:
    if not existing_text:
        return content
    updated = parse_metadata_value(existing_text, "updated_at")
    stable = content
    if updated:
        stable = replace_metadata_value(stable, "updated_at", updated)
    return stable


def _positioning_body(value: str) -> list[str]:
    text = value.strip() if value.strip() else PLACEHOLDER_POSITION
    return [text]


def _bullet_body(values: list[str], placeholder: list[str]) -> list[str]:
    items = [value.strip() for value in values if value.strip()]
    if not items:
        items = placeholder
    return [f"- {item}" for item in items]


def build_summary_content(
    root: Path,
    raw_file: Path,
    force_regenerate: bool = False,
) -> str:
    lines = raw_file.read_text(encoding="utf-8").splitlines()
    title = title_for(lines, raw_file)
    summary_path = summary_path_for(root, raw_file)
    rel_source = f"knowledge/{raw_file.relative_to(root).as_posix()}"
    today_str = date.today().isoformat()
    domain = domain_for(raw_file)
    tagged_items = extract_tagged_items(lines)

    existing_text = summary_path.read_text(encoding="utf-8") if summary_path.exists() else None
    existing_sections = parse_existing_sections(existing_text) if (existing_text and not force_regenerate) else {}

    positioning = str(existing_sections.get("positioning") or "").strip()
    trigger_signals = list(existing_sections.get("signals") or [])
    stable_conclusions = list(existing_sections.get("conclusions") or [])
    gaps = list(existing_sections.get("gaps") or [])

    if force_regenerate:
        positioning = ""
        trigger_signals = []
        stable_conclusions = []
        gaps = []

    if not gaps:
        gaps = tagged_items or PLACEHOLDER_GAPS

    content = [
        f"# {title}",
        "",
        f"- source_path: {rel_source}",
        f"- domain: {domain}",
        "- summary_role: light_route_card",
        f"- updated_at: {today_str}",
        "",
        "## 定位",
        *_positioning_body(positioning),
        "",
        "## 触发信号",
        *_bullet_body(trigger_signals, PLACEHOLDER_TRIGGERS),
        "",
        "## 稳定结论",
        *_bullet_body(stable_conclusions, PLACEHOLDER_CONCLUSIONS),
        "",
        "## 已知缺口",
        *_bullet_body(gaps, PLACEHOLDER_GAPS),
        "",
    ]
    return "\n".join(content)


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
        raw_files = [path for path in raw_files if path.resolve() == target.resolve()]

    updated: list[str] = []
    written: list[str] = []
    for raw_file in raw_files:
        summary_file = summary_path_for(root, raw_file)
        content = build_summary_content(root, raw_file, force_regenerate=args.force_regenerate)
        existing_text = summary_file.read_text(encoding="utf-8") if summary_file.exists() else None
        content = with_stable_timestamps(content, existing_text)
        if args.apply and not args.dry_run:
            if write_text_if_changed(summary_file, content, encoding="utf-8"):
                written.append(summary_file.relative_to(root).as_posix())
        updated.append(summary_file.relative_to(root).as_posix())

    mode = "dry-run" if args.dry_run or not args.apply else "apply"
    print(f"mode={mode}")
    print(f"summary_count={len(updated)}")
    if args.apply and not args.dry_run:
        print(f"written_count={len(written)}")
    for item in updated:
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
