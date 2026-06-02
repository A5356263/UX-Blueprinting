from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import PyInstaller.__main__


ALLOWED_CLAUDE_SKILLS = {"grill-me", "knowledge-ingestion", "uxb"}
ALLOWED_CODEX_SKILLS = {"grill-me", "knowledge-ingestion", "uxb", "scripts"}
ROOT_FILES = {
    ".gitignore",
    "README.md",
    "run_packages.ps1",
    "run_packages.sh",
}
ROOT_DIRS = {
    "knowledge",
    "specs",
    "templates",
}
PROJECTS_README = Path("projects/README.md")
INPUT_SOURCE = Path("input/自助权限申请/需求文档_员工自助申请权限.md")
INPUT_TARGET = Path("input/需求文档_员工自助申请权限.md")
RELEASE_INIT = '"""UXB release package thin entry."""\n'
RELEASE_MAIN = """from __future__ import annotations

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

    completed = subprocess.run([str(core), *sys.argv[1:]], env=env)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
"""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
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
    branch = branch_result.stdout.strip() or "<detached-head>"
    print(f"Packaging from branch: {branch}")

    status_result = run(["git", "status", "--short"], cwd=root)
    if status_result.returncode != 0:
        raise SystemExit(f"Failed to inspect git status:\n{status_result.stderr.strip()}")
    return [line.rstrip() for line in status_result.stdout.splitlines() if line.strip()]


def detect_platform_tag() -> str:
    import platform

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a strict-whitelist UXstrategy release package.")
    parser.add_argument("--package-name", default="UXstrategy")
    parser.add_argument("--output-dir", default=".")
    return parser.parse_args()


def create_build_root(source_root: Path) -> Path:
    build_root = source_root.parent / "_uxstrategy_release_build"
    if build_root.exists():
        shutil.rmtree(build_root)
    build_root.mkdir(parents=True, exist_ok=True)
    return build_root


def require_path(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Required packaging source is missing: {path}")


def copy_file(source_root: Path, stage_root: Path, rel_path: Path) -> None:
    source = source_root / rel_path
    require_path(source)
    target = stage_root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_dir(source_root: Path, stage_root: Path, rel_path: Path) -> None:
    source = source_root / rel_path
    require_path(source)
    target = stage_root / rel_path
    shutil.copytree(source, target, dirs_exist_ok=True)


def copy_selected_skill_dirs(source_root: Path, stage_root: Path, base_dir: Path, allowed_names: set[str]) -> None:
    skills_root = source_root / base_dir
    require_path(skills_root)
    for name in sorted(allowed_names):
        source = skills_root / name
        require_path(source)
        target = stage_root / base_dir / name
        shutil.copytree(source, target, dirs_exist_ok=True)


def write_release_packages_shell(stage_root: Path) -> None:
    packages_dir = stage_root / "packages"
    packages_dir.mkdir(parents=True, exist_ok=True)
    (packages_dir / "__init__.py").write_text(RELEASE_INIT, encoding="utf-8")
    (packages_dir / "__main__.py").write_text(RELEASE_MAIN, encoding="utf-8")


def build_core_executable(source_root: Path, stage_root: Path, build_root: Path) -> None:
    bin_dir = stage_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    work_dir = build_root / "pyinstaller-work"
    spec_dir = build_root / "pyinstaller-spec"
    dist_dir = bin_dir

    for path in (work_dir, spec_dir):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    entrypoint = source_root / "packages" / "__main__.py"
    require_path(entrypoint)

    data_sep = ";" if os.name == "nt" else ":"
    args = [
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "uxb-core",
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(spec_dir),
        "--add-data",
        f"{source_root / 'packages' / 'capability_registry'}{data_sep}packages/capability_registry",
        "--add-data",
        f"{source_root / 'packages' / 'route_decision' / 'rules.json'}{data_sep}packages/route_decision",
        str(entrypoint),
    ]
    old_cwd = Path.cwd()
    try:
        os.chdir(source_root)
        PyInstaller.__main__.run(args)
    finally:
        os.chdir(old_cwd)


def build_release_workspace(source_root: Path, stage_root: Path, build_root: Path) -> None:
    for name in sorted(ROOT_DIRS):
        copy_dir(source_root, stage_root, Path(name))

    for name in sorted(ROOT_FILES):
        copy_file(source_root, stage_root, Path(name))

    copy_selected_skill_dirs(source_root, stage_root, Path(".claude/skills"), ALLOWED_CLAUDE_SKILLS)
    copy_selected_skill_dirs(source_root, stage_root, Path(".codex/skills"), ALLOWED_CODEX_SKILLS)
    copy_file(source_root, stage_root, PROJECTS_README)

    input_source = source_root / INPUT_SOURCE
    require_path(input_source)
    input_target = stage_root / INPUT_TARGET
    input_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_source, input_target)

    write_release_packages_shell(stage_root)
    build_core_executable(source_root, stage_root, build_root)


def cleanup_validation_artifacts(stage_root: Path) -> None:
    shutil.rmtree(stage_root / ".tmp", ignore_errors=True)
    shutil.rmtree(stage_root / "projects" / "dist-smoke", ignore_errors=True)
    shutil.rmtree(stage_root / "packages" / "__pycache__", ignore_errors=True)


def validate_release(stage_root: Path) -> None:
    exe_name = "uxb-core.exe" if sys.platform.startswith("win") else "uxb-core"
    required_paths = [
        "bin",
        f"bin/{exe_name}",
        "packages/__init__.py",
        "packages/__main__.py",
        "specs",
        "templates",
        "knowledge",
        ".claude/skills/grill-me",
        ".claude/skills/knowledge-ingestion",
        ".claude/skills/uxb",
        ".codex/skills/grill-me",
        ".codex/skills/knowledge-ingestion",
        ".codex/skills/uxb",
        ".codex/skills/scripts",
        "projects/README.md",
        "input/需求文档_员工自助申请权限.md",
        "README.md",
        ".gitignore",
        "run_packages.ps1",
        "run_packages.sh",
    ]
    for rel_path in required_paths:
        if not (stage_root / rel_path).exists():
            raise SystemExit(f"Release validation failed: missing required asset `{rel_path}`.")

    forbidden_paths = [
        "tests",
        "test",
        "docs",
        "tools",
        "memory",
        "build",
        "dist",
        "release",
        ".mcp.json",
        "CLAUDE.md",
        "CODEX.md",
        "packages/examples",
        "packages/README.md",
        "packages/common.py",
        "packages/archive",
        "packages/generation",
        "packages/validate",
        "packages/repair_loop",
    ]
    for rel_path in forbidden_paths:
        if (stage_root / rel_path).exists():
            raise SystemExit(f"Release validation failed: excluded path still present `{rel_path}`.")

    projects_dir = stage_root / "projects"
    project_entries = sorted(path.name for path in projects_dir.iterdir())
    if project_entries != ["README.md"]:
        raise SystemExit(
            "Release validation failed: `projects/` must contain only README.md, "
            f"got: {project_entries}"
        )

    input_dir = stage_root / "input"
    input_entries = sorted(path.name for path in input_dir.iterdir())
    if input_entries != ["需求文档_员工自助申请权限.md"]:
        raise SystemExit(
            "Release validation failed: `input/` must contain only 需求文档_员工自助申请权限.md, "
            f"got: {input_entries}"
        )

    package_entries = sorted(path.name for path in (stage_root / "packages").iterdir())
    if package_entries != ["__init__.py", "__main__.py"]:
        raise SystemExit(
            "Release validation failed: `packages/` must contain only thin entry files, "
            f"got: {package_entries}"
        )

    init_text = (stage_root / "packages" / "__init__.py").read_text(encoding="utf-8").strip()
    if init_text != '"""UXB release package thin entry."""':
        raise SystemExit("Release validation failed: unexpected packages/__init__.py release marker.")

    claude_entries = sorted(path.name for path in (stage_root / ".claude" / "skills").iterdir())
    if claude_entries != sorted(ALLOWED_CLAUDE_SKILLS):
        raise SystemExit(f"Release validation failed: unexpected .claude skills {claude_entries}")

    codex_entries = sorted(path.name for path in (stage_root / ".codex" / "skills").iterdir())
    if codex_entries != sorted(ALLOWED_CODEX_SKILLS):
        raise SystemExit(f"Release validation failed: unexpected .codex skills {codex_entries}")

    validation_commands = [
        [sys.executable, "-m", "packages", "--help"],
        [sys.executable, "-m", "packages", "capabilities-list"],
        [sys.executable, "-m", "packages", "env-check"],
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
        [sys.executable, "-m", "packages", "project-structure-check", "dist-smoke"],
    ]
    for command in validation_commands:
        result = run(command, cwd=stage_root)
        if result.returncode != 0:
            raise SystemExit(
                "Release validation failed:\n"
                f"Command: {' '.join(command)}\n"
                f"{result.stdout.strip()}\n{result.stderr.strip()}".strip()
            )

    cleanup_validation_artifacts(stage_root)


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
    build_root = create_build_root(source_root)
    try:
        staging_parent = build_root / "staging"
        stage_root = staging_parent / package_name
        stage_root.mkdir(parents=True, exist_ok=True)

        build_release_workspace(source_root, stage_root, build_root)
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
