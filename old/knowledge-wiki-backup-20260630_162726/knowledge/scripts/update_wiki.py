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
    encodings = ["utf-8", locale.getpreferredencoding(False), "gbk"]
    for enc in encodings:
        if not enc:
            continue
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def run_step(root: Path, script_name: str, extra_args: list[str] | None = None) -> StepResult:
    script = root / "scripts" / script_name
    command = [sys.executable, str(script)]
    if extra_args:
        command.extend(extra_args)
    proc = subprocess.run(command, cwd=str(root), capture_output=True, text=False)
    return StepResult(
        name=script_name,
        returncode=proc.returncode,
        stdout=decode_output(proc.stdout).strip(),
        stderr=decode_output(proc.stderr).strip(),
    )


def count_md_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*.md") if item.is_file())


def count_orphan_summaries(root: Path) -> int:
    report = root / "outputs" / "reports" / "orphan_summaries.md"
    if not report.exists():
        return 0
    for line in report.read_text(encoding="utf-8").splitlines():
        if line.startswith("- orphan_count:"):
            return int(line.split(":", 1)[1].strip())
    return 0


def count_pending_semantic(root: Path) -> int:
    report = root / "outputs" / "reports" / "pending_semantic_summaries.md"
    if not report.exists():
        return 0
    pending_generate = 0
    pending_review = 0
    for line in report.read_text(encoding="utf-8").splitlines():
        if line.startswith("- pending_generate:"):
            pending_generate = int(line.split(":", 1)[1].strip())
        if line.startswith("- pending_review:"):
            pending_review = int(line.split(":", 1)[1].strip())
    return pending_generate + pending_review


def count_questions(root: Path) -> tuple[int, int, int]:
    question_file = root / "wiki" / "questions.md"
    gap_count = 0
    question_count = 0
    conflict_count = 0
    if not question_file.exists():
        return gap_count, question_count, conflict_count
    for line in question_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("- question_type:"):
            value = line.split(":", 1)[1].strip()
            if value == "GAP":
                gap_count += 1
            elif value == "QUESTION":
                question_count += 1
            elif value == "CONFLICT":
                conflict_count += 1
    return gap_count, question_count, conflict_count


def count_broken_source_paths(root: Path) -> int:
    summaries_root = root / "wiki" / "summaries"
    repo_root = root.parent
    broken = 0
    for summary_file in summaries_root.rglob("*.md"):
        text = summary_file.read_text(encoding="utf-8")
        for line in text.splitlines():
            if not line.startswith("- source_path:"):
                continue
            source_path = line.split(":", 1)[1].strip()
            if not (repo_root / source_path).exists():
                broken += 1
            break
    return broken


def count_unimported_candidates(root: Path) -> int:
    candidates_root = root / "candidates" / "未入库"
    return count_md_files(candidates_root)


def count_raw_without_summary(root: Path) -> int:
    raw_root = root / "raw"
    summaries_root = root / "wiki" / "summaries"
    raw_set = {path.relative_to(raw_root).as_posix() for path in raw_root.rglob("*.md") if path.is_file()}
    summary_set = {path.relative_to(summaries_root).as_posix() for path in summaries_root.rglob("*.md") if path.is_file()}
    return len(raw_set - summary_set)


def summarize(root: Path) -> None:
    raw_total = count_md_files(root / "raw")
    summary_total = count_md_files(root / "wiki" / "summaries")
    raw_without_summary = count_raw_without_summary(root)
    orphan_summary_count = count_orphan_summaries(root)
    pending_semantic_summary_count = count_pending_semantic(root)
    unimported_candidate_count = count_unimported_candidates(root)
    broken_source_path_count = count_broken_source_paths(root)
    gap_count, question_count, conflict_count = count_questions(root)

    print("status=ok")
    print(f"raw_total={raw_total}")
    print(f"summary_total={summary_total}")
    print(f"raw_without_summary={raw_without_summary}")
    print(f"orphan_summary_count={orphan_summary_count}")
    print(f"pending_semantic_summary_count={pending_semantic_summary_count}")
    print(f"unimported_candidate_count={unimported_candidate_count}")
    print(f"broken_source_path_count={broken_source_path_count}")
    print(f"gap_count={gap_count}")
    print(f"question_count={question_count}")
    print(f"conflict_count={conflict_count}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--only")
    parser.add_argument("--prune-orphans", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]

    summary_args: list[str] = []
    if args.dry_run:
        summary_args.append("--dry-run")
    if args.apply:
        summary_args.append("--apply")
    if args.only:
        summary_args.extend(["--only", args.only])

    prune_args = ["--dry-run"]
    if args.apply and args.prune_orphans:
        prune_args = ["--apply", "--confirm-delete"]

    steps_order: list[tuple[str, list[str]]] = [
        ("scan_raw.py", []),
        ("build_summaries.py", summary_args),
        ("prune_orphan_summaries.py", prune_args),
        ("reindex_wiki.py", []),
        ("refresh_questions.py", []),
        ("refresh_overview.py", []),
        ("refresh_semantic_summary_report.py", []),
        ("check_candidates.py", []),
        ("lint_wiki.py", []),
    ]

    results: list[StepResult] = []
    for script_name, extra_args in steps_order:
        result = run_step(root, script_name, extra_args=extra_args)
        results.append(result)
        if result.returncode != 0:
            print("status=failed")
            print(f"failed_step={script_name}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return 1 if args.strict else 0

    summarize(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
