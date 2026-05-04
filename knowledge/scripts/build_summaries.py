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


# ---- 新增：轻量路由生成函数 ----

def build_knowledge_position(lines: list[str], title: str, group: str) -> str:
    """基于标题、首段内容、领域归属，说明这份 raw 主要解决什么判断问题。"""
    content = nonempty_content_lines(lines)
    first_text = ""
    for line in content:
        if not line.startswith(("-", "*")) and not re.match(r"^\d+\.", line):
            first_text = line
            break
    if first_text:
        return first_text

    # 回退：使用第一个 ## 标题来描述定位
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip()
            if group == "guidelines":
                return f"定义并阐述「{heading}」相关的设计原则、触发条件、推导输出与自检标准。"
            return f"本文件围绕「{heading}」组织内容，具体知识定位待从 raw 中进一步确认。"

    group_label = "业务" if group == "business" else "设计指南" if group == "guidelines" else "待分类"
    return f"本文件属于 {group_label} 领域，具体知识定位待从 raw 中进一步确认。"


def build_task_triggers(lines: list[str], title: str, group: str) -> list[str]:
    """基于文件名、章节标题、领域上下文，列出哪些任务问题会触发本 raw。"""
    triggers: list[str] = []
    headings: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            headings.append(stripped[3:].strip())

    title_lower = title.lower()
    all_text = " ".join(headings).lower() + " " + title_lower

    if any(kw in all_text for kw in ["能力", "capability", "承载", "页面"]):
        triggers.append("判断某个能力由哪个页面承载")
        triggers.append("判断页面承担配置、查询、解释还是治理职责")
    if any(kw in all_text for kw in ["规则", "rule", "决策", "decision", "合同", "contract"]):
        triggers.append("需要理解或引用正式规则、判定链路或决策合同")
        triggers.append("判断权限、配置或状态裁决的生效逻辑与优先级")
    if any(kw in all_text for kw in ["对象", "object", "关系", "relation"]):
        triggers.append("需要明确业务对象定义及其关系边界")
    if any(kw in all_text for kw in ["流程", "flow", "场景", "scenario", "任务"]):
        triggers.append("需要理解业务流程或任务场景的完整路径")
    if any(kw in all_text for kw in ["治理", "governance", "审计", "audit"]):
        triggers.append("涉及治理模式、审批链路或审计追溯")
    if any(kw in all_text for kw in ["可用", "usability", "交互", "效率"]):
        triggers.append("评估交互方案的可用性、效率或操作合理性")
        triggers.append("将设计原则转化为具体的设计决策或自检标准")
    if any(kw in all_text for kw in ["信息架构", "ia", "导航", "可发现"]):
        triggers.append("评估信息架构、导航结构或内容可发现性")
    if any(kw in all_text for kw in ["视觉", "visual", "可读", "readability"]):
        triggers.append("评估视觉呈现或文本可读性")
    if any(kw in all_text for kw in ["认知", "cognition"]):
        triggers.append("评估认知负担或理解成本")
    if any(kw in all_text for kw in ["权限", "permission"]):
        triggers.append("涉及权限域的方案设计、配置、查询或排障")
    if any(kw in all_text for kw in ["边界", "范围", "scope", "boundary"]):
        triggers.append("需要明确领域、能力或对象的边界与不适用范围")
    if any(kw in all_text for kw in ["体验", "experience", "蓝图", "blueprint"]):
        triggers.append("涉及体验蓝图的构建或业务到体验的转译")
    if any(kw in all_text for kw in ["语义", "semantic", "解释"]):
        triggers.append("需要理解页面、对象或规则的语义定义与解释方式")

    if group == "business" and len(triggers) == 0:
        triggers.append("需要理解或使用本业务域的知识进行方案设计或判断时")
    elif group == "guidelines" and len(triggers) == 0:
        triggers.append("需要引用设计原则对方案进行自检或评审时")

    if not triggers:
        triggers.append("待从 raw 中进一步确认更精确的任务触发线索")

    return triggers[:8]


def build_coverage(lines: list[str]) -> tuple[list[str], list[str]]:
    """解析章节标题结构，列出覆盖内容和不涉及内容。"""
    headings: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            headings.append(stripped[3:].strip())

    objects: list[str] = []
    capabilities: list[str] = []
    pages: list[str] = []
    rules: list[str] = []
    states: list[str] = []
    risks: list[str] = []
    principles: list[str] = []
    uncategorized: list[str] = []

    for heading in headings:
        h_lower = heading.lower()
        if any(kw in h_lower for kw in ["对象", "object", "术语", "glossary", "实体", "entity"]):
            objects.append(heading)
        elif any(kw in h_lower for kw in ["能力", "capability", "功能", "feature", "承载"]):
            capabilities.append(heading)
        elif any(kw in h_lower for kw in ["页面", "page", "入口"]):
            pages.append(heading)
        elif any(kw in h_lower for kw in ["规则", "rule", "合同", "contract", "决策", "decision", "治理", "governance", "边界"]):
            rules.append(heading)
        elif any(kw in h_lower for kw in ["状态", "state", "生效", "生命周期"]):
            states.append(heading)
        elif any(kw in h_lower for kw in ["风险", "risk", "冲突", "conflict", "反模式", "缺口", "gap"]):
            risks.append(heading)
        elif any(kw in h_lower for kw in ["系列", "原则", "principle", "启发式", "标准", "ia-", "u-", "iso-", "i-"]):
            principles.append(heading)
        else:
            uncategorized.append(heading)

    covered: list[str] = []
    if objects:
        covered.append(f"对象：{', '.join(objects[:5])}")
    if capabilities:
        covered.append(f"能力：{', '.join(capabilities[:5])}")
    if pages:
        covered.append(f"页面：{', '.join(pages[:5])}")
    if principles:
        covered.append(f"原则：{', '.join(principles[:5])}")
    if rules:
        covered.append(f"规则：{', '.join(rules[:5])}")
    if states:
        covered.append(f"状态：{', '.join(states[:5])}")
    if risks:
        covered.append(f"风险：{', '.join(risks[:5])}")
    if uncategorized:
        covered.append(f"章节：{', '.join(uncategorized[:5])}")

    if not covered:
        covered.append("待从 raw 中进一步确认覆盖内容的具体分类")

    not_covered = ["本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源"]

    return covered, not_covered


def build_stable_conclusions(lines: list[str]) -> list[str]:
    """提取 raw 中结构化的确定性陈述作为可直接使用的稳定结论。"""
    conclusions: list[str] = []
    content = nonempty_content_lines(lines)

    for line in content:
        if TAG_PATTERN.search(line):
            continue
        # 跳过孤立标题/标签行（如 "页面承载：" 后面没有实质内容）
        stripped = line.lstrip("-* ").strip()
        if len(stripped) <= 12 and ("：" in stripped or ":" in stripped):
            continue
        if ("：" in line or ":" in line) and not line.startswith(("-", "*")):
            conclusions.append(line)
        elif line.startswith(("-", "*")) and ("：" in line or ":" in line or "是" in line):
            candidate = line.lstrip("-* ").strip()
            if len(candidate) > 12:
                conclusions.append(candidate)
        if len(conclusions) >= 6:
            break

    if not conclusions:
        conclusions.append("待从 raw 中进一步确认可直接使用的稳定结论。")

    return conclusions[:6]


def build_raw_lookup_rules() -> list[str]:
    """返回必须回查 raw 的通用规则。"""
    return [
        "需要完整规则细节或精确条款时",
        "需要正式证据或原文引用时",
        "需要页面或流程的完整描述时",
        "涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时",
        "summary 无法覆盖当前判断点或信息量不足时",
    ]


# ---- 核心生成函数 ----

def build_summary_content(root: Path, raw_file: Path, all_raw_files: list[Path]) -> str:
    lines = raw_file.read_text(encoding="utf-8").splitlines()
    group = source_group_for(raw_file)
    title = title_for(lines, raw_file)
    summary_path = summary_path_for(root, raw_file)
    rel_source = f"knowledge/{raw_file.relative_to(root).as_posix()}"
    related = related_summaries_for(root, raw_file, all_raw_files)
    tagged = extract_tagged_items(lines)
    position = build_knowledge_position(lines, title, group)
    triggers = build_task_triggers(lines, title, group)
    covered, not_covered = build_coverage(lines)
    conclusions = build_stable_conclusions(lines)
    lookup_rules = build_raw_lookup_rules()
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
        "## 1. 知识定位",
        "",
        position,
        "",
        "## 2. 任务触发线索",
        "",
        "当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：",
        "",
        *([f"- {item}" for item in triggers]),
        "",
        "## 3. 覆盖内容",
        "",
        "本 raw 覆盖：",
        "",
        *([f"- {item}" for item in covered]),
        "",
        "不涉及：",
        "",
        *([f"- {item}" for item in not_covered]),
        "",
        "## 4. 可直接使用的稳定结论",
        "",
        *([f"- {item}" for item in conclusions]),
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
