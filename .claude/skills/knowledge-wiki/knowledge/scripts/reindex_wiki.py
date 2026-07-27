from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from _write_if_changed import write_text_if_changed


STABLE_DESIGN_DIRS = {"设计准则", "交互模式"}


@dataclass(frozen=True)
class RouteEntry:
    group: str
    title: str
    signal: str
    target: Path


def relative_link(source_dir: Path, target: Path) -> str:
    return Path(os.path.relpath(target, source_dir)).as_posix()


def first_heading(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def first_section_line(path: Path, headings: tuple[str, ...]) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.strip() not in headings:
            continue
        level = len(line) - len(line.lstrip("#"))
        for candidate in lines[index + 1 :]:
            stripped = candidate.strip()
            if candidate.startswith("#"):
                candidate_level = len(candidate) - len(candidate.lstrip("#"))
                if candidate_level <= level:
                    break
            if not stripped or stripped.startswith(("- ", "|", ">", "```")):
                continue
            return stripped
    return "按该入口内的定位、覆盖边界和任务路由判断。"


def entry_for(group: str, target: Path) -> RouteEntry:
    return RouteEntry(
        group=group,
        title=first_heading(target),
        signal=first_section_line(
            target,
            (
                "### 领域定义",
                "### 知识集合定义",
                "## 使用定位",
                "## 这是什么",
                "## 文档定位",
            ),
        ),
        target=target,
    )


def collection_entries(raw: Path) -> list[RouteEntry]:
    entries: list[RouteEntry] = []
    for collection in sorted(path for path in raw.iterdir() if path.is_dir() and path.name not in STABLE_DESIGN_DIRS):
        collection_readme = collection / "README.md"
        if collection_readme.exists():
            entries.append(entry_for(collection.name, collection_readme))
            continue

        for child in sorted(collection.iterdir()):
            if child.is_dir():
                child_readme = child / "README.md"
                if child_readme.exists():
                    entries.append(entry_for(collection.name, child_readme))
                    continue
                direct_files = sorted(path for path in child.glob("*.md") if path.is_file())
                if len(direct_files) == 1:
                    entries.append(entry_for(collection.name, direct_files[0]))
            elif child.suffix.lower() == ".md" and child.name != "README.md":
                entries.append(entry_for(collection.name, child))
    return entries


def render_group(lines: list[str], group: str, entries: list[RouteEntry], wiki: Path) -> None:
    lines.extend([f"## {group}", ""])
    for entry in entries:
        lines.extend(
            [
                f"### {entry.title}",
                "",
                f"- 命中：{entry.signal}",
                "- 排除：只出现相近词但最终结果不由该入口解释时，按入口内的覆盖边界与条件依赖处理。",
                f"- 入口：[{entry.title}]({relative_link(wiki, entry.target)})",
                "",
            ]
        )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wiki = root / "wiki"
    raw = root / "raw"
    lines = [
        "# Knowledge Wiki Index",
        "",
        "本页只负责选择知识类型、业务集合或领域。业务知识进入领域 README 学习文件路由，再按目标文件顶部导航定位章节；index 明确直达的单一设计知识直接进入。不得遍历 raw。",
        "",
        "## 系统页",
        "",
        "- [当前健康状态](overview.md)",
        "- [显式未决项](questions.md)",
        "",
    ]

    entries = collection_entries(raw)
    groups: dict[str, list[RouteEntry]] = {}
    for entry in entries:
        groups.setdefault(entry.group, []).append(entry)
    for group, group_entries in groups.items():
        render_group(lines, group, group_entries, wiki)

    design = raw / "设计准则" / "设计准则.md"
    interaction = raw / "交互模式" / "README.md"
    lines.extend(["## 设计知识", ""])
    if design.exists():
        lines.extend(
            [
                "### 设计准则",
                "",
                "- 命中：需要判断交互行为应遵循的原则、红线、风险与例外。",
                "- 排除：需要具体交互组织方式时进入交互模式；业务事实仍进入业务知识。",
                f"- 入口：[设计准则章节地图]({relative_link(wiki, design)})",
                "",
            ]
        )
    if interaction.exists():
        lines.extend(
            [
                "### 交互模式",
                "",
                "- 命中：需要选择入口、承载、行为、状态反馈、恢复与回流的具体交互模式。",
                "- 排除：只需原则判断时读取设计准则；不得用模式替代业务事实。",
                f"- 入口：[交互模式全局地图]({relative_link(wiki, interaction)})",
                "",
            ]
        )

    changed = write_text_if_changed(wiki / "index.md", "\n".join(lines), encoding="utf-8")
    print("index_updated=knowledge/wiki/index.md")
    print(f"knowledge_collection_count={len(groups)}")
    print(f"domain_entry_count={len(entries)}")
    print(f"changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
