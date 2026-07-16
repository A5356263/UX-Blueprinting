from __future__ import annotations

import argparse
import locale
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StepResult:
    name: str
    returncode: int
    stdout: str
    stderr: str


def decode_output(raw: bytes) -> str:
    for encoding in ("utf-8", locale.getpreferredencoding(False), "gbk"):
        if not encoding:
            continue
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def run_step(root: Path, script_name: str) -> StepResult:
    process = subprocess.run(
        [sys.executable, str(root / "scripts" / script_name)],
        cwd=str(root),
        capture_output=True,
        text=False,
    )
    return StepResult(
        script_name,
        process.returncode,
        decode_output(process.stdout).strip(),
        decode_output(process.stderr).strip(),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    failed: list[StepResult] = []

    for script_name in (
        "scan_raw.py",
        "reindex_wiki.py",
        "refresh_questions.py",
        "check_candidates.py",
        "lint_wiki.py",
        "refresh_overview.py",
    ):
        result = run_step(root, script_name)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        if result.returncode != 0:
            failed.append(result)

    if failed:
        print("status=failed")
        print("failed_steps=" + ",".join(result.name for result in failed))
        return 1 if args.strict else 0

    print("status=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
