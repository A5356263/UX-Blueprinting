from __future__ import annotations

import json
from pathlib import Path

from packages.common import get_project_runtime_dir
from packages.uxb_run.models import UXBRunHistoryItem


def append_run_history(project_id: str, item: UXBRunHistoryItem) -> Path:
    runtime_dir = get_project_runtime_dir(project_id)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    path = runtime_dir / "uxb_run_history.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")
    return path
