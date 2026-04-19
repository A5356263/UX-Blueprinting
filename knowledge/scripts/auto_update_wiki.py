from __future__ import annotations

import argparse
import json
import locale
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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


def process_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def collect_raw_snapshot(raw_root: Path) -> dict[str, int]:
    snapshot: dict[str, int] = {}
    for file in sorted(raw_root.rglob("*.md")):
        if not file.is_file() or "manifests" in file.parts:
            continue
        snapshot[file.relative_to(raw_root).as_posix()] = file.stat().st_mtime_ns
    return snapshot


def diff_files(old: dict[str, int], new: dict[str, int]) -> list[str]:
    keys = set(old) | set(new)
    return sorted(key for key in keys if old.get(key) != new.get(key))


def append_log(log_file: Path, message: str) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as file:
        file.write(f"[{utc_now_iso()}] {message}\n")


def write_runtime(runtime_file: Path, payload: dict[str, object]) -> None:
    runtime_file.parent.mkdir(parents=True, exist_ok=True)
    runtime_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run_update(root: Path, changed: list[str], log_file: Path, runtime_file: Path) -> int:
    update_script = root / "scripts" / "update_wiki.py"
    append_log(log_file, f"trigger_summary_refresh changed_count={len(changed)}")
    proc = subprocess.run(
        [sys.executable, str(update_script), "--apply"],
        cwd=str(root),
        capture_output=True,
        text=False,
    )
    stdout = decode_output(proc.stdout).strip()
    stderr = decode_output(proc.stderr).strip()
    append_log(log_file, f"update_exit_code={proc.returncode}")
    if stdout:
        append_log(log_file, f"update_stdout={stdout}")
    if stderr:
        append_log(log_file, f"update_stderr={stderr}")
    write_runtime(
        runtime_file,
        {
            "pid": os.getpid(),
            "last_trigger_utc": utc_now_iso(),
            "last_status": "ok" if proc.returncode == 0 else "failed",
            "last_changed_files": changed,
        },
    )
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval-seconds", type=int, default=20)
    parser.add_argument("--single-pass", action="store_true")
    parser.add_argument("--run-on-start", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    raw_root = root / "raw"
    reports_root = root / "outputs" / "reports"
    lock_file = reports_root / "auto_update_wiki.lock.json"
    log_file = reports_root / "auto_update_wiki.log"
    runtime_file = reports_root / "auto_update_runtime.json"

    reports_root.mkdir(parents=True, exist_ok=True)
    if lock_file.exists():
        try:
            lock = json.loads(lock_file.read_text(encoding="utf-8"))
            old_pid = int(lock.get("pid", 0))
        except (json.JSONDecodeError, TypeError, ValueError):
            old_pid = 0
        if process_exists(old_pid):
            append_log(log_file, f"already_running pid={old_pid}")
            return 0

    lock_file.write_text(
        json.dumps({"pid": os.getpid(), "started_at_utc": utc_now_iso()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    append_log(log_file, f"daemon_started pid={os.getpid()} interval={args.interval_seconds}")

    snapshot = collect_raw_snapshot(raw_root)
    try:
        write_runtime(
            runtime_file,
            {
                "pid": os.getpid(),
                "started_at_utc": utc_now_iso(),
                "last_scan_utc": utc_now_iso(),
                "last_status": "idle",
                "watching_root": raw_root.as_posix(),
            },
        )

        if args.run_on_start:
            run_update(root, list(snapshot.keys()), log_file, runtime_file)

        if args.single_pass:
            return 0

        while True:
            time.sleep(max(5, args.interval_seconds))
            new_snapshot = collect_raw_snapshot(raw_root)
            changed = diff_files(snapshot, new_snapshot)
            write_runtime(
                runtime_file,
                {
                    "pid": os.getpid(),
                    "last_scan_utc": utc_now_iso(),
                    "last_status": "watching",
                    "last_change_count": len(changed),
                    "watching_root": raw_root.as_posix(),
                },
            )
            if changed:
                run_update(root, changed, log_file, runtime_file)
            snapshot = new_snapshot
    finally:
        lock_file.unlink(missing_ok=True)
        append_log(log_file, "daemon_stopped")


if __name__ == "__main__":
    raise SystemExit(main())
