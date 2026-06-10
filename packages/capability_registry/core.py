from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.common import get_repo_root, sanitize_json_text


def get_registry_dir() -> Path:
    external_dir = get_repo_root() / "packages" / "capability_registry"
    if external_dir.exists():
        return external_dir
    return Path(__file__).resolve().parent


def get_registry_file() -> Path:
    return get_registry_dir() / "registry.yaml"


def get_capabilities_dir() -> Path:
    return get_registry_dir() / "capabilities"


def _read_registry_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing capability registry file: {path}")
    try:
        payload = json.loads(sanitize_json_text(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid capability registry payload: {path}") from error
    if not isinstance(payload, dict):
        raise SystemExit(f"Capability registry payload must be an object: {path}")
    return payload


def load_registry() -> dict[str, Any]:
    return _read_registry_payload(get_registry_file())


def get_capability_file(capability_id: str) -> Path:
    return get_capabilities_dir() / f"{capability_id}.yaml"


def load_capability(capability_id: str) -> dict[str, Any]:
    capability = _read_registry_payload(get_capability_file(capability_id))
    if capability.get("capability_id") != capability_id:
        raise SystemExit(f"Capability id mismatch in registry file: {capability_id}")
    return capability


def list_capabilities() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    registry = load_registry()
    capability_ids = registry.get("capability_ids", [])
    if not isinstance(capability_ids, list):
        raise SystemExit("Capability registry field `capability_ids` must be a list.")
    capabilities = [load_capability(str(capability_id)) for capability_id in capability_ids]
    return registry, capabilities


def run_capabilities_list() -> int:
    registry, capabilities = list_capabilities()
    payload = {
        "registry_version": registry.get("registry_version"),
        "project": registry.get("project"),
        "description": registry.get("description"),
        "capability_count": len(capabilities),
        "capabilities": [
            {
                "capability_id": capability.get("capability_id"),
                "display_name": capability.get("display_name"),
                "type": capability.get("type"),
                "stage": capability.get("stage"),
                "status": capability.get("status"),
                "entrypoint": capability.get("entrypoint"),
            }
            for capability in capabilities
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def run_capability_show(capability_id: str) -> int:
    capability = load_capability(capability_id)
    print(json.dumps(capability, ensure_ascii=False, indent=2))
    return 0
