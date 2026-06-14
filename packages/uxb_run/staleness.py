from __future__ import annotations

from pathlib import Path


def is_context_stale(
    manifest_path: Path,
    context_bundle_dir: Path,
    source_requirement_path: Path,
    source_background_path: Path,
    route_decision_path: Path,
) -> bool:
    if not manifest_path.exists() or not context_bundle_dir.exists():
        return True
    manifest_mtime = manifest_path.stat().st_mtime
    inputs = [source_requirement_path, source_background_path, route_decision_path]
    for path in inputs:
        if path.exists() and path.stat().st_mtime > manifest_mtime:
            return True
    return False


def is_gate_stale(artifact_path: Path, gate_status_path: Path) -> bool:
    if not artifact_path.exists() or not gate_status_path.exists():
        return True
    return artifact_path.stat().st_mtime > gate_status_path.stat().st_mtime


def is_final_check_stale(output_paths: list[Path], check_status_path: Path) -> bool:
    if not check_status_path.exists():
        return True
    status_mtime = check_status_path.stat().st_mtime
    for path in output_paths:
        if path.exists() and path.stat().st_mtime > status_mtime:
            return True
    return False
