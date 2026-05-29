from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path


THIN_INIT = '"""UXB release package thin entry."""\n'

THIN_MAIN = """from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _release_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _core_path(root: Path) -> Path:
    name = "uxb-core.exe" if os.name == "nt" else "uxb-core"
    return root / "bin" / name


def main() -> int:
    root = _release_root()
    core = _core_path(root)

    if not core.exists():
        print(f"ERROR: UXB core executable not found: {core}", file=sys.stderr)
        return 127

    env = os.environ.copy()
    env.setdefault("UXB_ROOT", str(root))
    env.setdefault("UXB_PROJECTS_DIR", str(root / "projects"))
    env.setdefault("UXB_KNOWLEDGE_DIR", str(root / "knowledge"))
    env.setdefault("UXB_MEMORY_DIR", str(root / "memory"))

    completed = subprocess.run([str(core), *sys.argv[1:]], env=env)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
"""

RELEASE_README_TEMPLATE = """# {package_name} 使用说明

## 使用方式

继续使用原有命令：

```bash
python -m packages <command> <project-id>
```

也可以使用：

```bash
bash run_packages.sh <command> <project-id>
```

或 Windows：

```powershell
powershell -ExecutionPolicy Bypass -File .\\run_packages.ps1 <command> <project-id>
```

## 核心目录

- `.agent/skills/`：发行包内保留的一套技能说明与参考资料。
- `specs/`：规则真源。
- `templates/`：产物模板。
- `knowledge/`：知识资产。
- `projects/`：项目输入与输出目录。
- `memory/`：长期记忆与偏好配置。

## 不建议手动修改

- `.agent/skills/`
- `specs/`
- `templates/`
- `bin/`
- `packages/`

## 知识更新

知识入库请优先使用 `knowledge-ingestion` Skill。
稳定知识最终进入 `knowledge/raw/`，再刷新 `knowledge/wiki/`。
"""

SOURCE_REQUIRED_ITEMS = {
    ".claude",
    "specs",
    "templates",
    "knowledge",
    "projects",
    "CLAUDE.md",
    "CODEX.md",
    "README.md",
    "run_packages.ps1",
    "run_packages.sh",
}

EXCLUDED_RELATIVE_PATHS = {
    ".git",
    ".github",
    ".playwright-mcp",
    ".claude",
    ".codex",
    "build",
    "dist",
    "release",
    "_uxb_release_build",
    "_uxstrategy_release_build",
    "docs",
    "input",
    "memory",
    "test",
    "tools",
    "specs",
    "templates",
    "知识候选区",
    "PPT.MD",
    "CLAUDE.md",
    "CODEX.md",
    ".mcp.json",
    "skills-lock.json",
    ".gitignore",
}

EXCLUDED_NAME_PATTERNS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".DS_Store",
    "Thumbs.db",
    "*.pyc",
    "*.pyo",
    "*.pyd",
}

SOURCE_HIDDEN_PATHS = {
    "packages/common.py",
    "packages/mainline.py",
    "packages/context_assemble",
    "packages/generation",
    "packages/validate",
    "packages/capability_registry",
}

TEXT_EXTENSIONS = {
    ".json",
    ".jsonl",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".txt",
    ".yaml",
    ".yml",
}

ALLOWED_AGENT_SKILLS = {
    "knowledge-ingestion",
    "uxb",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def inspect_source_tree(root: Path) -> list[str]:
    branch_result = run(["git", "branch", "--show-current"], cwd=root)
    if branch_result.returncode != 0:
        raise SystemExit(f"Failed to detect current branch:\n{branch_result.stderr.strip()}")
    branch = branch_result.stdout.strip()
    if branch != "研发版模式":
        raise SystemExit(f"Packaging must run on branch `研发版模式`, current branch is `{branch}`.")

    status_result = run(["git", "status", "--short"], cwd=root)
    if status_result.returncode != 0:
        raise SystemExit(f"Failed to inspect git status:\n{status_result.stderr.strip()}")
    return [line.rstrip() for line in status_result.stdout.splitlines() if line.strip()]


def require_source_entrypoint(root: Path) -> None:
    result = run([sys.executable, "-m", "packages", "--help"], cwd=root)
    if result.returncode != 0:
        raise SystemExit(
            "Source entrypoint validation failed:\n"
            f"{result.stdout.strip()}\n{result.stderr.strip()}".strip()
        )


def require_pyinstaller(root: Path) -> None:
    result = run([sys.executable, "-m", "PyInstaller", "--version"], cwd=root)
    if result.returncode == 0:
        return
    install_result = run([sys.executable, "-m", "pip", "install", "pyinstaller"], cwd=root)
    if install_result.returncode != 0:
        raise SystemExit(
            "Failed to install PyInstaller:\n"
            f"{install_result.stdout.strip()}\n{install_result.stderr.strip()}".strip()
        )


def detect_platform_tag() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch_map = {
        "amd64": "x64",
        "x86_64": "x64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }
    arch = arch_map.get(machine, machine or "unknown")
    if system.startswith("win"):
        return f"win-{arch}"
    if system == "darwin":
        return f"macos-{arch}"
    if system == "linux":
        return f"linux-{arch}"
    return f"{system}-{arch}"


def is_excluded(rel_path: Path, package_name: str, zip_name: str) -> bool:
    rel_posix = rel_path.as_posix()
    if rel_posix in EXCLUDED_RELATIVE_PATHS:
        return True
    if rel_posix == package_name or rel_posix.startswith(f"{package_name}/"):
        return True
    if rel_posix == zip_name:
        return True
    name = rel_path.name
    return any(fnmatch(name, pattern) for pattern in EXCLUDED_NAME_PATTERNS)


def copy_release_workspace(source_root: Path, stage_root: Path, package_name: str, zip_name: str) -> None:
    for item in source_root.iterdir():
        rel_path = Path(item.name)
        if is_excluded(rel_path, package_name, zip_name):
            continue
        target = stage_root / item.name
        if item.is_dir():
            shutil.copytree(item, target, ignore=shutil.ignore_patterns(*EXCLUDED_NAME_PATTERNS))
        else:
            shutil.copy2(item, target)


def write_release_entrypoints(stage_root: Path) -> None:
    packages_dir = stage_root / "packages"
    if packages_dir.exists():
        shutil.rmtree(packages_dir)
    packages_dir.mkdir(parents=True, exist_ok=True)
    (packages_dir / "__init__.py").write_text(THIN_INIT, encoding="utf-8")
    (packages_dir / "__main__.py").write_text(THIN_MAIN, encoding="utf-8")


def build_core_binary(source_root: Path, build_root: Path) -> Path:
    dist_dir = build_root / "core_build" / "dist"
    work_dir = build_root / "core_build" / "work"
    spec_dir = build_root / "core_build" / "spec"
    specs_source = (source_root / "specs").resolve()
    templates_source = (source_root / "templates").resolve()
    dist_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "uxb-core",
        "--collect-submodules",
        "packages",
        "--collect-data",
        "packages",
        "--add-data",
        f"{specs_source}{os.pathsep}specs",
        "--add-data",
        f"{templates_source}{os.pathsep}templates",
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(spec_dir),
        "packages/__main__.py",
    ]
    result = run(command, cwd=source_root)
    if result.returncode != 0:
        raise SystemExit(
            "PyInstaller build failed:\n"
            f"{result.stdout.strip()}\n{result.stderr.strip()}".strip()
        )

    exe_name = "uxb-core.exe" if os.name == "nt" else "uxb-core"
    core_path = dist_dir / exe_name
    if not core_path.exists():
        raise SystemExit(f"Compiled core executable not found: {core_path}")
    return core_path


def copy_core_binary(core_path: Path, stage_root: Path) -> None:
    bin_dir = stage_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    target = bin_dir / core_path.name
    shutil.copy2(core_path, target)
    if os.name != "nt":
        target.chmod(target.stat().st_mode | 0o111)


def extract_section(markdown: str, heading: str) -> str:
    marker = f"## {heading}\n"
    start = markdown.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    next_index = markdown.find("\n## ", start)
    end = len(markdown) if next_index == -1 else next_index
    return markdown[start:end].strip()


def build_agent_markdown(source_root: Path) -> str:
    code_md = (source_root / "CODEX.md").read_text(encoding="utf-8")
    claude_md = (source_root / "CLAUDE.md").read_text(encoding="utf-8")

    sections: list[str] = ["# AGENT.md"]

    code_execution = extract_section(code_md, "编码执行约束")
    if code_execution:
        sections.append("## 编码执行约束\n\n" + code_execution)

    language_rules = extract_section(claude_md, "语言与沟通规则")
    if language_rules:
        sections.append("## 语言与沟通规则\n\n" + language_rules)

    path_rules = extract_section(code_md, "路径与目录规则")
    if path_rules:
        sections.append("## 路径与目录规则\n\n" + path_rules)

    capability_rules = extract_section(code_md, "能力模块边界规则")
    if capability_rules:
        sections.append("## 能力模块边界规则\n\n" + capability_rules)

    git_rules = extract_section(claude_md, "Git 提交规则")
    if git_rules:
        sections.append("## Git 提交规则\n\n" + git_rules)

    scope = extract_section(code_md, "适用范围") or extract_section(claude_md, "适用范围")
    if scope:
        sections.append("## 适用范围\n\n" + scope)

    return "\n\n".join(section.strip() for section in sections if section.strip()) + "\n"


def install_agent_assets(source_root: Path, stage_root: Path) -> None:
    source_agent = source_root / ".claude"
    target_agent = stage_root / ".agent"
    shutil.copytree(source_agent, target_agent)

    skills_dir = target_agent / "skills"
    for child in skills_dir.iterdir():
        if child.is_dir() and child.name not in ALLOWED_AGENT_SKILLS:
            shutil.rmtree(child)

    agent_md = build_agent_markdown(source_root)
    (stage_root / "AGENT.md").write_text(agent_md, encoding="utf-8")


def reset_projects_directory(source_root: Path, stage_root: Path) -> None:
    source_projects = source_root / "projects"
    target_projects = stage_root / "projects"
    if target_projects.exists():
        shutil.rmtree(target_projects)
    target_projects.mkdir(parents=True, exist_ok=True)

    readme_path = source_projects / "README.md"
    if readme_path.exists():
        shutil.copy2(readme_path, target_projects / "README.md")


def rewrite_agent_references(stage_root: Path) -> None:
    replacements = {
        ".claude/skills/": ".agent/skills/",
        ".codex/skills/": ".agent/skills/",
        ".claude\\skills\\": ".agent\\skills\\",
        ".codex\\skills\\": ".agent\\skills\\",
    }

    for path in stage_root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in {"AGENT.md", "README.md", "RELEASE_README.md"}:
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = original
        for source_text, target_text in replacements.items():
            updated = updated.replace(source_text, target_text)
        if updated != original:
            path.write_text(updated, encoding="utf-8")


def write_release_readme(stage_root: Path, package_name: str) -> None:
    readme_path = stage_root / "RELEASE_README.md"
    readme_path.write_text(RELEASE_README_TEMPLATE.format(package_name=package_name), encoding="utf-8")


def validate_release(stage_root: Path) -> None:
    validation_env = os.environ.copy()
    validation_env["PYTHONDONTWRITEBYTECODE"] = "1"
    for command in [
        [sys.executable, "-m", "packages", "--help"],
        [sys.executable, "-m", "packages", "capabilities-list"],
        [
            sys.executable,
            "-m",
            "packages",
            "bootstrap",
            "dist-smoke",
            "--task-name",
            "Dist Smoke",
            "--domain",
            "权限管理",
            "--force",
        ],
    ]:
        result = run(command, cwd=stage_root, env=validation_env)
        if result.returncode != 0:
            raise SystemExit(
                "Release validation failed:\n"
                f"Command: {' '.join(command)}\n"
                f"{result.stdout.strip()}\n{result.stderr.strip()}".strip()
            )

    required_paths = [
        ".agent/skills/uxb/SKILL.md",
        ".agent/skills/knowledge-ingestion/SKILL.md",
        "knowledge/raw",
        "knowledge/wiki",
        "run_packages.ps1",
        "run_packages.sh",
        "AGENT.md",
    ]
    for rel_path in required_paths:
        if not (stage_root / rel_path).exists():
            raise SystemExit(f"Release validation failed: missing required asset `{rel_path}`.")

    forbidden_paths = [
        ".claude",
        ".codex",
        "CLAUDE.md",
        "CODEX.md",
        ".mcp.json",
        "skills-lock.json",
        "tools",
        "docs",
        "memory",
        "specs",
        "templates",
        "知识候选区",
        ".gitignore",
        ".git",
        "input",
        "test",
        "PPT.MD",
    ]
    for rel_path in forbidden_paths:
        if (stage_root / rel_path).exists():
            raise SystemExit(f"Release validation failed: excluded path still present `{rel_path}`.")

    packages_dir = stage_root / "packages"
    pycache_dir = packages_dir / "__pycache__"
    if pycache_dir.exists():
        shutil.rmtree(pycache_dir)
    expected = {packages_dir / "__init__.py", packages_dir / "__main__.py"}
    actual = {path for path in packages_dir.iterdir()}
    if actual != expected:
        raise SystemExit("Release validation failed: packages/ must contain only __init__.py and __main__.py.")

    for rel_path in SOURCE_HIDDEN_PATHS:
        if (stage_root / rel_path).exists():
            raise SystemExit(f"Release validation failed: source path still present `{rel_path}`.")

    if not (stage_root / "projects" / "dist-smoke").exists():
        raise SystemExit("Release validation failed: bootstrap smoke project was not created.")
    shutil.rmtree(stage_root / "projects" / "dist-smoke", ignore_errors=True)


def ensure_expected_root_items(source_root: Path) -> None:
    missing = [item for item in sorted(SOURCE_REQUIRED_ITEMS) if not (source_root / item).exists()]
    if missing:
        raise SystemExit(f"Required source items are missing: {', '.join(missing)}")


def make_zip(staging_parent: Path, package_name: str, output_path: Path) -> None:
    if output_path.exists():
        output_path.unlink()
    shutil.make_archive(
        str(output_path.with_suffix("")),
        "zip",
        root_dir=str(staging_parent),
        base_dir=package_name,
    )


def ensure_source_tree_unchanged(root: Path, baseline: list[str], output_path: Path) -> None:
    status_result = run(["git", "status", "--short"], cwd=root)
    if status_result.returncode != 0:
        raise SystemExit(f"Failed to inspect post-build git status:\n{status_result.stderr.strip()}")

    current = [line.rstrip() for line in status_result.stdout.splitlines() if line.strip()]
    allowed_untracked = f"?? {output_path.name}"
    baseline_filtered = [line for line in baseline if line != allowed_untracked]
    current_filtered = [line for line in current if line != allowed_untracked]
    if current_filtered != baseline_filtered:
        baseline_text = "\n".join(baseline_filtered) or "<clean>"
        current_text = "\n".join(current_filtered) or "<clean>"
        raise SystemExit(
            "Packaging changed the source working tree unexpectedly.\n"
            f"Baseline:\n{baseline_text}\n"
            f"Current:\n{current_text}"
        )


def create_build_root(source_root: Path) -> Path:
    build_root = source_root.parent / "_uxstrategy_release_build"
    if build_root.exists():
        shutil.rmtree(build_root)
    build_root.mkdir(parents=True, exist_ok=True)
    return build_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the UXstrategy release package with only the core delivery assets.")
    parser.add_argument("--package-name", default="UXstrategy")
    parser.add_argument("--output-dir", default=".")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = repo_root()
    output_dir = (source_root / args.output_dir).resolve()
    package_name = args.package_name
    platform_tag = detect_platform_tag()
    stamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"{package_name}-{platform_tag}-{stamp}.zip"
    output_path = output_dir / zip_name

    baseline_status = inspect_source_tree(source_root)
    ensure_expected_root_items(source_root)
    require_source_entrypoint(source_root)
    require_pyinstaller(source_root)

    build_root = create_build_root(source_root)
    try:
        core_path = build_core_binary(source_root, build_root)
        staging_parent = build_root / "staging"
        stage_root = staging_parent / package_name
        stage_root.mkdir(parents=True, exist_ok=True)

        copy_release_workspace(source_root, stage_root, package_name, zip_name)
        install_agent_assets(source_root, stage_root)
        reset_projects_directory(source_root, stage_root)
        rewrite_agent_references(stage_root)
        write_release_entrypoints(stage_root)
        copy_core_binary(core_path, stage_root)
        write_release_readme(stage_root, package_name)
        validate_release(stage_root)

        output_dir.mkdir(parents=True, exist_ok=True)
        make_zip(staging_parent, package_name, output_path)
    finally:
        shutil.rmtree(build_root, ignore_errors=True)

    ensure_source_tree_unchanged(source_root, baseline_status, output_path)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
