from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import unquote

from _write_if_changed import write_text_if_changed


LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
NUMBERED_PATTERN = re.compile(r"^(\d+)_")
ALLOWED_BUSINESS_FILES = {
    "README.md",
    "业务对象与术语.md",
    "功能与操作清单.md",
    "任务与路径.md",
    "规则与权限.md",
    "状态与异常.md",
    "页面与字段.md",
    "问答与差异.md",
}
FORBIDDEN_SUMMARY_MARKERS = ("wiki/summaries", "summary-first", "先读 summary", "优先命中 `summary`")
STABLE_DESIGN_DIRS = {"设计准则", "交互模式"}
REQUIRED_ROUTE_HEADINGS = ("## 任务触发索引", "## 停止条件", "## 正式知识清单")
CONTRACT_HEADINGS = ("## 领域契约", "## 知识集合契约")


def markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def relative_link(source_dir: Path, target: Path) -> str:
    return Path(os.path.relpath(target, source_dir)).as_posix()


def canonical_anchor(value: str) -> str:
    value = unquote(value).lower().replace("-", "").replace(" ", "")
    return "".join(char for char in value if char.isalnum() or "\u4e00" <= char <= "\u9fff")


def discover_index_targets(raw_root: Path) -> list[Path]:
    targets: list[Path] = []
    for collection in sorted(path for path in raw_root.iterdir() if path.is_dir() and path.name not in STABLE_DESIGN_DIRS):
        collection_readme = collection / "README.md"
        if collection_readme.exists():
            targets.append(collection_readme)
            continue
        for child in sorted(collection.iterdir()):
            if child.is_dir():
                child_readme = child / "README.md"
                if child_readme.exists():
                    targets.append(child_readme)
                    continue
                direct_files = sorted(path for path in child.glob("*.md") if path.is_file())
                if len(direct_files) == 1:
                    targets.append(direct_files[0])
            elif child.suffix.lower() == ".md" and child.name != "README.md":
                targets.append(child)

    design = raw_root / "设计准则" / "设计准则.md"
    interaction = raw_root / "交互模式" / "README.md"
    if design.exists():
        targets.append(design)
    if interaction.exists():
        targets.append(interaction)
    return targets


def check_links(files: list[Path]) -> tuple[int, int, list[str]]:
    broken_paths = 0
    broken_anchors = 0
    issues: list[str] = []
    for file in files:
        text = file.read_text(encoding="utf-8")
        headings = [line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")]
        heading_keys = {canonical_anchor(heading) for heading in headings}
        for target in LINK_PATTERN.findall(text):
            target = target.strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path_part, separator, anchor = target.partition("#")
            if path_part:
                resolved = (file.parent / unquote(path_part)).resolve()
                if not resolved.exists():
                    broken_paths += 1
                    issues.append(f"broken_raw_path:{file.as_posix()}:{target}")
                    continue
            if separator and not path_part and canonical_anchor(anchor) not in heading_keys:
                broken_anchors += 1
                issues.append(f"broken_section_anchor:{file.as_posix()}:{target}")
    return broken_paths, broken_anchors, issues


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    repo_root = root.parent.parent.parent.parent
    raw_root = root / "raw"
    index_file = root / "wiki" / "index.md"
    raw_files = markdown_files(raw_root)
    route_readmes = [path for path in raw_files if path.name == "README.md"]
    contract_readmes = [path for path in route_readmes if path.parent.name != "交互模式"]
    issues: list[str] = []

    domain_readme_missing = 0
    for collection in sorted(path for path in raw_root.iterdir() if path.is_dir() and path.name not in STABLE_DESIGN_DIRS):
        for directory in sorted(path for path in collection.rglob("*") if path.is_dir()):
            markdown = [path for path in directory.glob("*.md") if path.is_file() and path.name != "README.md"]
            subdirectories = [path for path in directory.iterdir() if path.is_dir()]
            needs_route = len(markdown) > 1 or bool(subdirectories)
            if needs_route and not (directory / "README.md").exists():
                domain_readme_missing += 1
                issues.append(f"domain_readme_missing:{directory.relative_to(root).as_posix()}")

    for readme in contract_readmes:
        text = readme.read_text(encoding="utf-8")
        if not any(heading in text for heading in CONTRACT_HEADINGS):
            issues.append(f"missing_domain_contract:{readme.relative_to(root).as_posix()}:契约")
        for heading in REQUIRED_ROUTE_HEADINGS:
            if heading not in text:
                issues.append(f"missing_domain_contract:{readme.relative_to(root).as_posix()}:{heading}")

    index_text = index_file.read_text(encoding="utf-8") if index_file.exists() else ""
    index_targets = discover_index_targets(raw_root)
    unindexed_domains = 0
    for target in index_targets:
        expected = relative_link(index_file.parent, target)
        if expected not in index_text:
            unindexed_domains += 1
            issues.append(f"unindexed_domain:{target.relative_to(root).as_posix()}")

    target_set = {path.resolve() for path in index_targets}
    unrouted_raw = 0
    for raw_file in raw_files:
        if raw_file.name == "README.md":
            continue
        if raw_file.resolve() in target_set:
            routed = relative_link(index_file.parent, raw_file) in index_text
        else:
            readme = raw_file.parent / "README.md"
            routed = readme.exists() and raw_file.name in readme.read_text(encoding="utf-8")
        if not routed:
            unrouted_raw += 1
            issues.append(f"unrouted_raw:{raw_file.relative_to(root).as_posix()}")

    route_files = [*route_readmes, index_file]
    route_files = [path for path in route_files if path.exists()]
    broken_paths, _, link_issues = check_links(route_files)
    _, broken_anchors, anchor_issues = check_links(raw_files)
    issues.extend(link_issues)
    issues.extend(anchor_issues)

    duplicate_route_targets = 0
    for file in route_files:
        targets = [target for target in LINK_PATTERN.findall(file.read_text(encoding="utf-8")) if not target.startswith("#")]
        duplicates = len(targets) - len(set(targets))
        if duplicates:
            duplicate_route_targets += duplicates
            issues.append(f"duplicate_route_target:{file.relative_to(root).as_posix()}:{duplicates}")

    long_without_navigation = 0
    for file in raw_files:
        if file.name == "README.md":
            continue
        text = file.read_text(encoding="utf-8")
        if len(text.splitlines()) >= 400 and "## 快速导航" not in text:
            long_without_navigation += 1
            issues.append(f"long_raw_without_navigation:{file.relative_to(root).as_posix()}")

    business_root = raw_root / "业务"
    numbered_business_files = [
        file for file in raw_files
        if business_root in file.parents and NUMBERED_PATTERN.match(file.name)
    ]
    for file in numbered_business_files:
        issues.append(f"numbered_business_file:{file.relative_to(root).as_posix()}")

    nonstandard_business_files = [
        file for file in raw_files
        if business_root in file.parents and file.name not in ALLOWED_BUSINESS_FILES
    ]
    for file in nonstandard_business_files:
        issues.append(f"nonstandard_business_file:{file.relative_to(root).as_posix()}")

    forbidden_summary_references = 0
    for scan_root in [repo_root / ".claude" / "skills"]:
        for file in markdown_files(scan_root):
            if "knowledge-wiki/knowledge/outputs" in file.as_posix():
                continue
            text = file.read_text(encoding="utf-8")
            for line_number, line in enumerate(text.splitlines(), start=1):
                if any(marker in line for marker in FORBIDDEN_SUMMARY_MARKERS):
                    forbidden_summary_references += 1
                    issues.append(f"forbidden_summary_reference:{file.relative_to(repo_root).as_posix()}:{line_number}")

    encoding_issues = 0
    for file in markdown_files(root):
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            encoding_issues += 1
            issues.append(f"invalid_utf8:{file.relative_to(root).as_posix()}")
            continue
        if "\ufffd" in text:
            encoding_issues += 1
            issues.append(f"replacement_character:{file.relative_to(root).as_posix()}")

    metrics = {
        "raw_total": len(raw_files),
        "domain_readme_total": len(contract_readmes),
        "domain_readme_missing_count": domain_readme_missing,
        "unindexed_domain_count": unindexed_domains,
        "unrouted_raw_count": unrouted_raw,
        "broken_raw_path_count": broken_paths,
        "broken_section_anchor_count": broken_anchors,
        "duplicate_route_target_count": duplicate_route_targets,
        "long_raw_without_navigation_count": long_without_navigation,
        "forbidden_summary_reference_count": forbidden_summary_references,
        "numbered_business_file_count": len(numbered_business_files),
        "nonstandard_business_file_count": len(nonstandard_business_files),
        "encoding_issue_count": encoding_issues,
        "issue_total": len(issues),
    }
    report = root / "outputs" / "lint" / "latest_lint_report.md"
    lines = ["# Wiki Lint Report", "", *[f"- {key}: {value}" for key, value in metrics.items()], "", "## Issues", ""]
    lines.extend([f"- {issue}" for issue in issues] if issues else ["- none"])
    lines.append("")
    changed = write_text_if_changed(report, "\n".join(lines), encoding="utf-8")
    for key, value in metrics.items():
        print(f"{key}={value}")
    print(f"changed={str(changed).lower()}")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
