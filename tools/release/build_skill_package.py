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

    completed = subprocess.run([str(core), *sys.argv[1:]], env=env)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
"""

SOURCE_REQUIRED_ITEMS = {
    ".claude",
    "specs",
    "templates",
    "knowledge",
    "projects",
    "README.md",
    "run_packages.ps1",
    "run_packages.sh",
    ".gitignore",
}

EXCLUDED_RELATIVE_PATHS = {
    ".git",
    ".github",
    ".playwright-mcp",
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
    ".mcp.json",
    "CLAUDE.md",
    "CODEX.md",
    "skills-lock.json",
    "知识候选区",
    "PPT.MD",
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

ALLOWED_CLAUDE_SKILLS = {
    "uxb",
    "knowledge-ingestion",
    "grill-me",
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
    branch = branch_result.stdout.strip() or "<detached-head>"
    print(f"Packaging from branch: {branch}")

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


def require_supported_build_environment(root: Path) -> None:
    if platform.system().lower() != "darwin":
        return

    result = run([sys.executable, "-m", "pip", "show", "pathlib"], cwd=root)
    if result.returncode != 0:
        return

    raise SystemExit(
        "macOS build environment check failed:\n"
        "Detected the obsolete `pathlib` backport in the current Python environment. "
        "This package conflicts with PyInstaller on modern Python.\n\n"
        "Recommended fix:\n"
        "1. Use a clean virtual environment for packaging\n"
        "2. Remove the backport package: `pip uninstall pathlib -y`\n"
        "3. Re-run: `python ./tools/release/build_skill_package.py`"
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
    return any(fnmatch(rel_path.name, pattern) for pattern in EXCLUDED_NAME_PATTERNS)


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


def trim_claude_skills(stage_root: Path) -> None:
    claude_root = stage_root / ".claude"
    skills_dir = claude_root / "skills"

    if not skills_dir.exists():
        raise SystemExit("Release validation failed: `.claude/skills` is missing.")

    for child in skills_dir.iterdir():
        if child.name not in ALLOWED_CLAUDE_SKILLS:
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    for skill_name in sorted(ALLOWED_CLAUDE_SKILLS):
        if not (skills_dir / skill_name).exists():
            raise SystemExit(f"Release validation failed: missing `.claude/skills/{skill_name}`.")


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
        ".claude",
        ".claude/skills/uxb",
        ".claude/skills/knowledge-ingestion",
        ".claude/skills/grill-me",
        "specs",
        "templates",
        "knowledge/raw",
        "knowledge/wiki",
        "projects",
        "run_packages.ps1",
        "run_packages.sh",
        "README.md",
        ".gitignore",
    ]
    for rel_path in required_paths:
        if not (stage_root / rel_path).exists():
            raise SystemExit(f"Release validation failed: missing required asset `{rel_path}`.")

    forbidden_paths = [
        ".codex",
        "memory",
        ".mcp.json",
        "CLAUDE.md",
        "CODEX.md",
        "skills-lock.json",
        "tools",
        "docs",
        "知识候选区",
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
    parser = argparse.ArgumentParser(description="Build the UXstrategy release package while only processing packages/.")
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
    require_supported_build_environment(source_root)
    require_pyinstaller(source_root)

    build_root = create_build_root(source_root)
    try:
        core_path = build_core_binary(source_root, build_root)
        staging_parent = build_root / "staging"
        stage_root = staging_parent / package_name
        stage_root.mkdir(parents=True, exist_ok=True)

        copy_release_workspace(source_root, stage_root, package_name, zip_name)
        trim_claude_skills(stage_root)
        write_release_entrypoints(stage_root)
        copy_core_binary(core_path, stage_root)
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
