from __future__ import annotations

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


def run_step(root: Path, script_name: str) -> StepResult:
    script = root / "scripts" / script_name
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(root),
        capture_output=True,
        text=False,
    )
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
    changed: list[Path] = []
    for file in files:
        modified = datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc)
        if modified > last_dt:
            changed.append(file)
    return changed


def tokenize(path: Path) -> set[str]:
    text = path.stem.replace("-", "_")
    tokens = {x.strip().lower() for x in text.split("_") if x.strip()}
    tokens.update({part.lower() for part in path.parts if part})
    return {t for t in tokens if len(t) >= 3}


def suggest_wiki_pages(root: Path, changed_files: list[Path], max_items: int = 20) -> list[Path]:
    wiki_root = root / "wiki"
    wiki_pages = [p for p in wiki_root.rglob("*.md") if p.is_file() and p.name != "log.md"]
    keywords: set[str] = set()
    for file in changed_files:
        keywords |= tokenize(file.relative_to(root))
    scored: list[tuple[int, Path]] = []
    for page in wiki_pages:
        rel = page.relative_to(root).as_posix().lower()
        score = sum(1 for kw in keywords if kw in rel)
        if score == 0:
            try:
                body = page.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                body = ""
            score = sum(1 for kw in keywords if kw in body)
        if score > 0:
            scored.append((score, page))
    scored.sort(key=lambda item: (-item[0], item[1].as_posix()))
    return [x[1] for x in scored[:max_items]]


def build_pending_report(
    root: Path,
    run_time_utc: str,
    steps: list[StepResult],
    changed_files: list[Path],
    suggested_pages: list[Path],
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
    if changed_files:
        for file in changed_files:
            lines.append(f"- {file.relative_to(root).as_posix()}")
    else:
        lines.append("- none")
    lines.extend(["", "## Suggested Wiki Pages For AI Update", ""])
    if suggested_pages:
        for page in suggested_pages:
            lines.append(f"- {page.relative_to(root).as_posix()}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## AI Actions",
            "",
            "- 检查 Changed Raw Sources 是否包含新增事实或冲突。",
            "- 按建议页面逐个更新 `source_refs`、边界、缺口与关系描述。",
            "- 如存在无法裁决的冲突，写入 `knowledge/wiki/questions.md`。",
            "- 完成语义更新后，追加 `knowledge/wiki/log.md`。",
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
    root = Path(__file__).resolve().parents[1]
    outputs_reports = root / "outputs" / "reports"
    report_file = outputs_reports / "pending_wiki_updates.md"
    state_file = outputs_reports / "update_wiki_state.json"
    old_state = read_state(state_file)
    last_run = old_state.get("last_run_utc")

    steps_order = [
        "scan_raw.py",
        "build_manifest.py",
        "reindex_wiki.py",
        "refresh_overview.py",
        "lint_wiki.py",
    ]
    results: list[StepResult] = []
    for script_name in steps_order:
        result = run_step(root, script_name)
        results.append(result)
        if result.returncode != 0:
            break

    run_time = utc_now_iso()
    changed = changed_raw_files(root, last_run)
    suggested = suggest_wiki_pages(root, changed)
    build_pending_report(root, run_time, results, changed, suggested, report_file, state_file)

    if all(item.returncode == 0 for item in results) and len(results) == len(steps_order):
        write_state(state_file, {"last_run_utc": run_time})
        print(f"status=ok")
        print(f"pending_report={report_file}")
        return 0

    print("status=failed")
    print(f"pending_report={report_file}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
