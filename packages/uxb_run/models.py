from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class PhaseState:
    schema_version: str = "uxb_phase_state@2.0"
    project_id: str = ""
    phase: str = ""
    execution_mode: str = "unknown"
    status: str = "in_progress"
    target_artifact: str = ""
    target_artifacts: list[str] = field(default_factory=list)
    required_inputs: list[str] = field(default_factory=list)
    template_refs: list[str] = field(default_factory=list)
    rule_refs: list[str] = field(default_factory=list)
    preflight_errors: list[str] = field(default_factory=list)
    repair_mode: bool = False
    repair_refs: list[str] = field(default_factory=list)
    gate_status_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class StageContext:
    schema_version: str = "uxb_stage_context@2.0"
    project_id: str = ""
    context: dict[str, object] = field(default_factory=dict)
    knowledge_trace: dict[str, object] = field(default_factory=dict)
    execution_trace: dict[str, object] = field(default_factory=dict)
    accumulated_warnings: list[dict[str, object]] = field(default_factory=list)
    updated_at: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class CurrentAction:
    schema_version: str = "uxb_current_action@1.0"
    project_id: str = ""
    action_id: str = ""
    phase: str = ""
    action_type: str = ""
    owner: str = ""
    execution_mode: str = "unknown"
    stage: str = ""
    status: str = ""
    target_artifacts: list[str] = field(default_factory=list)
    required_inputs: list[str] = field(default_factory=list)
    status_sources: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class UXBRunHistoryItem:
    timestamp: str = ""
    project_id: str = ""
    command: str = ""
    phase_before: str = ""
    phase_after: str = ""
    action_type: str = ""
    owner: str = ""
    auto_commands_run: list[str] = field(default_factory=list)
    result: str = ""
    next_phase: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class ProjectRunState:
    project_id: str
    project_dir: Path
    source_dir: Path
    runtime_dir: Path
    workspace_dir: Path
    preview_dir: Path
    project_exists: bool
    source_ready: bool
    source_errors: list[str] = field(default_factory=list)
    route_decision: dict[str, object] = field(default_factory=dict)
    phase_state: dict[str, object] = field(default_factory=dict)
    stage_context: dict[str, object] = field(default_factory=dict)
    context_manifest: dict[str, object] = field(default_factory=dict)
    context_manifest_exists: bool = False
    context_bundle_exists: bool = False
    context_is_stale: bool = False
    remediation_plan: dict[str, object] = field(default_factory=dict)
    retry_scope: dict[str, object] = field(default_factory=dict)
    gate_statuses: dict[str, dict[str, object]] = field(default_factory=dict)
    check_status: dict[str, object] = field(default_factory=dict)
    preview_exists: bool = False

    def gate_status(self, stage: str) -> dict[str, object]:
        payload = self.gate_statuses.get(stage, {})
        return payload if isinstance(payload, dict) else {}
