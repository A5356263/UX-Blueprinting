from __future__ import annotations

import argparse
import json
import locale
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class StepResult:
    name: str
    returncode: int
    stdout: str
    stderr: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_state(state_file: Path) -> dict[str, str]:
    if not state_file.exists():
        return {}
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_state(state_file: Path, state: dict[str, str]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


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


def changed_raw_files(root: Path, last_run_utc: str | None) -> list[Path]:
    raw_root = root / "raw"
    files = sorted(p for p in raw_root.rglob("*.md") if p.is_file() and "manifests" not in p.parts)
    if not last_run_utc:
        return files
    try:
        last_dt = datetime.fromisoformat(last_run_utc.replace("Z", "+00:00"))
    except ValueError:
        return files
    return [file for file in files if datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc) > last_dt]


def suggest_summaries(root: Path, changed_files: list[Path]) -> list[Path]:
    suggestions: list[Path] = []
    for raw in changed_files:
        rel = raw.relative_to(root / "raw")
        suggestions.append(root / "wiki" / "summaries" / rel)
    return suggestions


def build_pending_report(
    root: Path,
    run_time_utc: str,
    steps: list[StepResult],
    changed_files: list[Path],
    suggested_summaries: list[Path],
    report_file: Path,
    state_file: Path,
) -> None:
    lines: list[str] = [
        "# Pending Wiki Updates",
        "",
        f"- generated_at_utc: {run_time_utc}",
        f"- orchestrator: knowledge/scripts/update_wiki.py",
        f"- state_file: {state_file.relative_to(root).as_posix()}",
        "",
        "## Mechanical Pipeline",
        "",
    ]
    for step in steps:
        status = "ok" if step.returncode == 0 else "failed"
        lines.append(f"- {step.name}: {status}")

    lines.extend(["", "## Changed Raw Sources", ""])
    lines.extend([f"- {file.relative_to(root).as_posix()}" for file in changed_files] or ["- none"])

    lines.extend(["", "## Updated Summaries", ""])
    lines.extend([f"- {item.relative_to(root).as_posix()}" for item in suggested_summaries] or ["- none"])

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- 当前链路采用 summary-first 轻量 Wiki 机制。",
            "- 默认产物为 raw 对应 summary、index、overview、questions 与 lint 报告。",
            "- 不再使用 registry、AUTO-SYNC block 或 heavy-sync 写回。",
            "",
            "## Step Outputs",
            "",
        ]
    )
    for step in steps:
        lines.append(f"### {step.name}")
        lines.append("")
        lines.append("```text")
        lines.append(step.stdout if step.stdout else "(empty)")
        if step.stderr:
            lines.append("--- stderr ---")
            lines.append(step.stderr)
        lines.append("```")
        lines.append("")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--only")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    outputs_reports = root / "outputs" / "reports"
    report_file = outputs_reports / "pending_wiki_updates.md"
    state_file = outputs_reports / "update_wiki_state.json"
    old_state = read_state(state_file)
    last_run = old_state.get("last_run_utc")

    summary_args: list[str] = []
    if args.dry_run:
        summary_args.append("--dry-run")
    if args.apply:
        summary_args.append("--apply")
    if args.only:
        summary_args.extend(["--only", args.only])

    steps_order: list[tuple[str, list[str]]] = [
        ("scan_raw.py", []),
        ("build_manifest.py", []),
        ("build_summaries.py", summary_args),
        ("reindex_wiki.py", []),
        ("refresh_questions.py", []),
        ("refresh_overview.py", []),
        ("refresh_semantic_summary_report.py", []),
        ("lint_wiki.py", []),
    ]
    results: list[StepResult] = []
    for script_name, extra_args in steps_order:
        result = run_step(root, script_name, extra_args=extra_args)
        results.append(result)
        if result.returncode != 0:
            break

    run_time = utc_now_iso()
    changed = changed_raw_files(root, last_run)
    suggested = suggest_summaries(root, changed)
    build_pending_report(root, run_time, results, changed, suggested, report_file, state_file)

    success = all(item.returncode == 0 for item in results) and len(results) == len(steps_order)
    if success:
        write_state(state_file, {"last_run_utc": run_time})
        print("status=ok")
        print(f"pending_report={report_file}")
        return 0

    print("status=failed")
    print(f"pending_report={report_file}")
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
