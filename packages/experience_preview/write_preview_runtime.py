from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from packages.common import get_project_preview_dir


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_preview_runtime(
    project_id: str,
    model: dict[str, Any],
    host: str,
    port: int | None,
    ready_state: str,
    preview_url: str,
) -> Path:
    preview_dir = get_project_preview_dir(project_id)
    preview_dir.mkdir(parents=True, exist_ok=True)

    model_path = preview_dir / "preview_model.json"
    model_path.write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    runtime_payload = {
        "project_id": project_id,
        "generated_at": now_iso(),
        "output_dir": str(preview_dir),
        "output_path": str(preview_dir / "index.html"),
        "server_host": host,
        "server_port": port,
        "preview_url": preview_url,
        "ready_state": ready_state,
        "page_count": len(model.get("page_views", [])),
        "global_note_count": len(model.get("global_context", {}).get("notes", [])),
        "unresolved_count": len(model.get("unresolved_items", [])),
        "source_business_blueprint": model.get("meta", {}).get("context", {}).get("source_business_blueprint", ""),
        "source_experience_blueprint": model.get("meta", {}).get("context", {}).get("source_experience_blueprint", ""),
    }
    runtime_path = preview_dir / "preview_runtime.json"
    runtime_path.write_text(json.dumps(runtime_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    build_log = [
        "# 体验蓝图预览构建日志",
        "",
        f"- project_id: `{project_id}`",
        f"- generated_at: `{runtime_payload['generated_at']}`",
        f"- source_business_blueprint: `{runtime_payload['source_business_blueprint']}`",
        f"- source_experience_blueprint: `{runtime_payload['source_experience_blueprint']}`",
        f"- ready_state: `{ready_state}`",
        f"- preview_url: `{preview_url or 'N/A'}`",
        f"- page_count: `{runtime_payload['page_count']}`",
        f"- global_note_count: `{runtime_payload['global_note_count']}`",
        f"- unresolved_count: `{runtime_payload['unresolved_count']}`",
    ]
    (preview_dir / "preview_build_log.md").write_text("\n".join(build_log) + "\n", encoding="utf-8")
    return runtime_path
