from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import multiprocessing
import os
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts/archive_evidence.py"
GOVERN_EXAMPLE = (
    SKILL_ROOT.parent
    / "evidence-govern/examples/evidence-govern-result.example.json"
)
REQUEST_EXAMPLE = SKILL_ROOT / "examples/archive-request.example.json"
SUMMARY_EXAMPLE = SKILL_ROOT / "examples/archive-summary.example.json"
ROOT_CAUSE_EXAMPLE = (
    SKILL_ROOT.parent
    / "root-cause-synthesis/examples/candidate-synthesis.example.json"
)
OUTCOME_EXAMPLE = (
    SKILL_ROOT.parent
    / "outcome-validation-recheck/examples/effectiveness-validation.example.json"
)

SPEC = importlib.util.spec_from_file_location("archive_evidence", SCRIPT)
archive = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(archive)


def archive_worker(request: dict, root: str, registry: str, queue) -> None:
    try:
        summary = archive.archive_request(
            request,
            root=Path(root),
            registry_path=Path(registry),
        )
        queue.put(summary["archive_results"][0]["result"])
    except Exception as exc:  # pragma: no cover - surfaced through the parent assertion.
        queue.put(f"error:{exc}")


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


class EvidenceArchiveTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.registry_path = self.root / "shared-workflow/data-analysis/artifact-registry.json"
        self.registry = {
            "version": "test",
            "artifacts": [
                self.artifact(
                    "governed",
                    "evidence_govern_result",
                    "spark-output/context/current/governed.json",
                    "evidence-govern",
                    "6.0.0",
                ),
                self.artifact(
                    "objective",
                    "objective_evidence_package",
                    "spark-output/context/current/objective.json",
                    "objective-data-analysis",
                    "4.0.0",
                ),
                self.artifact(
                    "root-cause",
                    "root_cause_synthesis_package",
                    "spark-output/context/current/root-cause.json",
                    "root-cause-synthesis",
                    "5.0.0",
                ),
                self.artifact(
                    "outcome",
                    "outcome_validation_package",
                    "spark-output/context/current/outcome.json",
                    "outcome-validation-recheck",
                    "4.0.0",
                ),
                self.artifact(
                    "business-impact",
                    "business_impact_assessment",
                    "spark-output/context/current/business-impact.json",
                    "business-impact",
                    "4.0.0",
                ),
                self.artifact(
                    "archive-summary",
                    "evidence_archive_summary",
                    "spark-output/context/current/archive-summary.json",
                    "evidence-archive",
                    "3.0.0",
                ),
            ],
            "stores": [
                self.store(
                    "archived-evidence-store",
                    "spark-output/context/stores/archived-evidence-store.jsonl",
                    ".claude/skills/evidence-archive/schemas/archive_record.schema.json",
                ),
                self.store(
                    "baseline-store",
                    "spark-output/context/stores/baseline-store.jsonl",
                    "shared-workflow/data-analysis/schemas/baseline_item.schema.json",
                ),
            ],
        }
        write_json(self.registry_path, self.registry)
        self.govern = json.loads(GOVERN_EXAMPLE.read_text(encoding="utf-8"))
        write_json(self.source_path("governed"), self.govern)
        self.write_other_sources()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def artifact(
        artifact_id: str,
        artifact_type: str,
        path: str,
        producer: str,
        version: str,
    ) -> dict:
        return {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "results_root": f"spark-output/results/{artifact_id}",
            "current_pointer_path": f"spark-output/context/current/{artifact_id}.json",
            "producer_skill": producer,
            "current_version": version,
            "schema_ref": "unused",
            "write_policy": "immutable_result_with_purpose_pointer",
            "read_policy": "explicit_artifact_ref_only",
            "legacy_read_versions": [],
        }

    @staticmethod
    def store(artifact_id: str, path: str, schema_ref: str) -> dict:
        return {
            "artifact_id": artifact_id,
            "artifact_type": artifact_id.replace("-", "_"),
            "path": path,
            "producer_skill": "evidence-archive",
            "current_version": "3.0.0",
            "schema_ref": schema_ref,
            "write_policy": "approved_append_only_lazy_create",
            "read_policy": "explicit_record_ref_only",
            "legacy_read_versions": [],
        }

    def source_path(self, artifact_id: str) -> Path:
        entry = next(
            item
            for item in self.registry["artifacts"]
            if item["artifact_id"] == artifact_id
        )
        return self.root / entry["results_root"] / "test-artifact.json"

    def write_other_sources(self) -> None:
        self.govern["context_factor_assessments"] = [
            {
                "factor_id": "ctx-1",
                "factor_type": "product_change",
                "source_refs": ["release-note-1"],
                "time_window": {"start": "2026-07-01", "end": "2026-07-02"},
                "affected_scope": {"scenario_key": "submit"},
                "related_evidence_refs": ["ev_27fc5d01b5b080f1"],
                "time_overlap": "partial",
                "scope_overlap": "full",
                "possible_effect_direction": "mixed",
                "disposition": "add_caveat",
                "assessment_confidence": "medium",
                "rationale": "版本变化与观察窗口部分重叠",
            }
        ]
        baseline = {
            "baseline_id": "baseline-task-completion",
            "baseline_version": "1",
            "metric_contract_ref": "metric:task_completion_rate",
            "scenario_key": "submit",
            "grain": "overall",
            "segment_definition_ref": None,
            "baseline_window": {"start": "2026-01", "end": "2026-05"},
            "period_granularity": "month",
            "calculation_method": "median_quantile",
            "baseline_values": {
                "center_value": 0.8,
                "normal_band": {"low": 0.7, "high": 0.9},
                "wide_band": {"low": 0.6, "high": 0.95},
                "history_count": 5,
            },
            "comparability_contract": {
                "metric_contract_ref": "metric:task_completion_rate",
                "scenario_key": "submit",
                "grain": "overall",
                "comparison_fingerprint": "cmp_1",
                "current_window_excluded": True,
            },
            "comparison_fingerprint": "cmp_1",
            "confidence": "medium",
            "lifecycle_status": "proposed",
            "review_status": "pending",
            "lineage": {
                "source_artifact_refs": ["source-1"],
                "source_item_refs": ["source-1#series"],
                "input_fingerprint": "input-1",
            },
            "supersedes_ref": None,
        }
        objective = {
            "run": {
                "artifact_type": "objective_evidence_package",
                "artifact_version": "4.0.0",
                "producer_skill": "objective-data-analysis",
                "run_id": "oda-test",
                "project_name": "示例项目",
                "generated_at": "2026-07-24",
            },
            "analysis_results": {"baseline": {"candidate": baseline}},
        }
        write_json(self.source_path("objective"), objective)

        root_source = json.loads(ROOT_CAUSE_EXAMPLE.read_text(encoding="utf-8"))
        root_source["run"]["run_id"] = "root-test"
        root_source["analysis_results"]["root_cause_candidates"][0][
            "candidate_id"
        ] = "rc-1"
        write_json(self.source_path("root-cause"), root_source)

        outcome_source = json.loads(OUTCOME_EXAMPLE.read_text(encoding="utf-8"))
        outcome_source["run"]["run_id"] = "outcome-test"
        outcome_source["analysis_results"]["validation_assessment"][
            "assessment_id"
        ] = "vd-1"
        write_json(self.source_path("outcome"), outcome_source)

        business_source = {
            "run": {
                "artifact_type": "business_impact_assessment",
                "artifact_version": "4.0.0",
                "producer_skill": "business-impact",
                "run_id": "bi-test",
                "project_name": "示例项目",
                "generated_at": "2026-07-24",
                "valuation_state": "provisional_forecast",
            },
            "portfolio_summary": {
                "problem_case_count": 1,
                "solution_case_count": 1,
                "business_value_priority_view": [],
            },
            "limitations": ["预测不是效果事实"],
            "downstream_handoffs": [],
        }
        write_json(self.source_path("business-impact"), business_source)

        self.govern["baseline_patches"] = [
            {
                "patch_id": "bgp-1",
                "baseline_ref": "baseline-task-completion",
                "action": "activate",
                "from_status": "proposed",
                "to_status": "active",
                "decision_status": "approved",
                "review_id": "review-baseline-1",
                "source_refs": ["objective#baseline"],
                "rationale": "口径与历史窗口已审核",
                "can_persist": True,
                "applied": False,
            }
        ]
        self.govern["manual_review_queue"] = [
            {
                "review_id": "review-baseline-1",
                "review_type": "baseline",
                "target_refs": ["baseline-task-completion"],
                "risk_level": "medium",
                "reason": "baseline activation",
                "required_action": "review",
                "status": "closed",
            }
        ]
        self.govern["review_decisions"] = [
            {
                "review_id": "review-baseline-1",
                "decision": "approved",
                "reviewer_ref": "reviewer:test",
                "decided_at": "2026-07-24",
                "rationale": "approved",
                "approved_actions": ["persist_in_archive"],
            }
        ]
        self.govern["downstream_handoffs"].append(
            {
                "handoff_id": "egh-baseline-1",
                "target_skill": "evidence-archive",
                "handoff_type": "approved_archive_persistence",
                "handoff_status": "ready",
                "payload_refs": ["#/baseline_patches/0"],
                "allowed_uses": ["persist_in_archive"],
                "forbidden_uses": ["recalculate_baseline"],
                "required_review_request_ids": ["review-baseline-1"],
                "caveats": [],
            }
        )
        write_json(self.source_path("governed"), self.govern)

    def evidence_draft(self) -> dict:
        return {
            "artifact_type": "evidence_archive_request",
            "artifact_version": "3.0.0",
            "project_name": "示例项目",
            "authorization": {
                "mode": "explicit_user_request",
                "authorization_ref": "conversation://archive-evidence",
                "confirmed_at": "2026-07-24",
                "authorized_target_refs": [
                    "governed#evidence_id=ev_27fc5d01b5b080f1"
                ],
                "authorized_field_paths": ["evidence_items"],
                "approved_actions": ["persist_in_archive"],
                "review_decision_refs": [],
            },
            "targets": [
                {
                    "target_ref": "governed#evidence_id=ev_27fc5d01b5b080f1",
                    "record_kind": "evidence",
                    "projection": "canonical_evidence_item",
                    "logical_object_ref": "evidence:ev_27fc5d01b5b080f1",
                    "source_artifact_id": "governed",
                    "source_artifact_version": "",
                    "source_run_id": "",
                    "source_selector": {
                        "path": "evidence_items",
                        "id_field": "evidence_id",
                        "id_value": "ev_27fc5d01b5b080f1",
                    },
                    "source_content_digest": "0" * 64,
                    "authorized_field_paths": ["evidence_items"],
                    "record_action": "new",
                    "supersedes_ref": None,
                    "sensitivity": "internal",
                    "redaction_state": "not_required",
                    "allowed_uses": ["historical_trace"],
                    "forbidden_uses": ["claim_confirmed_root_cause"],
                    "governance": {
                        "artifact_id": "governed",
                        "source_run_id": None,
                        "content_digest": None,
                        "handoff_ref": "egh_example_archive",
                        "patch_ref": "egp_example_release",
                        "review_decision_refs": [],
                    },
                }
            ],
        }

    def prepare(self, request: dict) -> dict:
        request = copy.deepcopy(request)
        request.setdefault("invocation_context", "chain_context")
        request.setdefault(
            "analysis_purpose",
            {"purpose_key": "evidence-archive", "purpose_label": "证据归档"},
        )
        request.setdefault("requested_analyses", ["archive"])
        request.setdefault("input_bindings", [])
        request.setdefault(
            "requested_deliverables", [{"format": "json", "required": True}]
        )
        request.setdefault(
            "publication_policy",
            {"level": "formal", "update_current_for_purpose": True},
        )
        request.setdefault("retention_policy", "archive_requested")
        for target in request.get("targets", []):
            source_id = target["source_artifact_id"]
            target["source_artifact_instance_ref"] = self.instance_ref(source_id)
            governance = target.get("governance", {})
            if governance.get("artifact_id"):
                governance["artifact_instance_ref"] = self.instance_ref(
                    governance["artifact_id"]
                )
        return archive.prepare_request(
            request, root=self.root, registry_path=self.registry_path
        )

    def instance_ref(self, artifact_id: str) -> dict:
        entry = next(
            item for item in self.registry["artifacts"]
            if item["artifact_id"] == artifact_id
        )
        path = self.source_path(artifact_id)
        source = json.loads(path.read_text(encoding="utf-8"))
        return {
            "artifact_id": artifact_id,
            "artifact_version": entry["current_version"],
            "producer_skill": entry["producer_skill"],
            "run_id": source["run"]["run_id"],
            "artifact_path": str(path.relative_to(self.root)),
            "content_digest": hashlib.sha256(path.read_bytes()).hexdigest(),
            "project_name": source["run"]["project_name"],
            "analysis_purpose_key": "test",
            "publication_status": "published",
        }

    def archive(self, request: dict, **kwargs) -> dict:
        return archive.archive_request(
            request,
            root=self.root,
            registry_path=self.registry_path,
            **kwargs,
        )

    def test_examples_satisfy_local_schemas(self):
        request = json.loads(REQUEST_EXAMPLE.read_text(encoding="utf-8"))
        summary = json.loads(SUMMARY_EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual([], archive._request_errors(request))
        self.assertEqual(
            [], archive._validate_json_schema(request, archive.REQUEST_SCHEMA_PATH)
        )
        self.assertEqual(
            [], archive._validate_json_schema(summary, archive.SUMMARY_SCHEMA_PATH)
        )

    def test_evidence_archive_is_lazy_idempotent_and_exactly_readable(self):
        prepared = self.prepare(self.evidence_draft())
        store = self.root / self.registry["stores"][0]["path"]
        self.assertFalse(store.exists())
        summary = self.archive(prepared)
        self.assertEqual("archived", summary["archive_results"][0]["result"])
        record_ref = summary["archive_results"][0]["archive_record_ref"]
        record_id = record_ref.split("=", 1)[1]
        record = archive.get_record(
            "evidence",
            archive_record_id=record_id,
            root=self.root,
            registry_path=self.registry_path,
        )
        self.assertEqual("released", record["payload_snapshot"]["lifecycle_status"])
        self.assertNotIn("payload_ref", record)
        duplicate = self.archive(prepared)
        self.assertEqual("duplicate", duplicate["archive_results"][0]["result"])
        self.assertEqual(record_ref, duplicate["archive_results"][0]["archive_record_ref"])
        self.assertEqual(
            1,
            archive.verify_store(
                "evidence", root=self.root, registry_path=self.registry_path
            )["record_count"],
        )

    def test_external_review_decision_must_bind_exact_archive_handoff(self):
        handoff = next(
            item
            for item in self.govern["downstream_handoffs"]
            if item["handoff_id"] == "egh_example_archive"
        )
        handoff["required_review_request_ids"] = ["review-external-archive"]
        write_json(self.source_path("governed"), self.govern)
        request = self.evidence_draft()
        request["authorization"]["review_decision_refs"] = [
            "review-external-archive"
        ]
        request["targets"][0]["governance"]["review_decision_refs"] = [
            "review-external-archive"
        ]
        request["review_decisions"] = [
            {
                "review_id": "decision-external-archive",
                "review_request_id": "review-external-archive",
                "source_artifact_instance_ref": self.instance_ref("governed"),
                "handoff_id": handoff["handoff_id"],
                "payload_refs": handoff["payload_refs"],
                "decision": "approved",
                "approved_actions": ["persist_in_archive"],
                "reviewed_at": "2026-07-26T10:00:00+08:00",
                "reviewer_ref": "reviewer:test",
                "caveats": [],
            }
        ]
        prepared = self.prepare(request)
        summary = self.archive(prepared)
        self.assertEqual("archived", summary["archive_results"][0]["result"])

        mismatched = self.evidence_draft()
        mismatched["authorization"]["review_decision_refs"] = [
            "review-external-archive"
        ]
        mismatched["targets"][0]["governance"]["review_decision_refs"] = [
            "review-external-archive"
        ]
        mismatched["review_decisions"] = copy.deepcopy(request["review_decisions"])
        mismatched["review_decisions"][0]["payload_refs"] = ["#/limitations"]
        with self.assertRaisesRegex(archive.ArchiveError, "未覆盖当前 Handoff payload"):
            self.prepare(mismatched)

    def test_source_change_after_prepare_is_blocked(self):
        prepared = self.prepare(self.evidence_draft())
        changed = copy.deepcopy(self.govern)
        changed["evidence_items"][0]["claim_summary"] = "changed"
        write_json(self.source_path("governed"), changed)
        with self.assertRaisesRegex(archive.ArchiveError, "内容摘要不匹配"):
            self.archive(prepared)

    def test_same_lineage_with_new_lifecycle_is_superseding_not_duplicate(self):
        first_request = self.prepare(self.evidence_draft())
        first_summary = self.archive(first_request)
        first_ref = first_summary["archive_results"][0]["archive_record_ref"]

        governed = copy.deepcopy(self.govern)
        patch = governed["evidence_patches"][0]
        patch["action"] = "restrict"
        patch["to_status"] = "restricted"
        patch["rationale"] = "用途限制发生变化"
        write_json(self.source_path("governed"), governed)

        draft = self.evidence_draft()
        draft["targets"][0]["record_action"] = "superseding"
        draft["targets"][0]["supersedes_ref"] = first_ref
        second_request = self.prepare(draft)
        second_summary = self.archive(second_request)
        self.assertEqual("archived", second_summary["archive_results"][0]["result"])
        self.assertNotEqual(
            first_ref, second_summary["archive_results"][0]["archive_record_ref"]
        )
        self.assertEqual(
            2,
            archive.verify_store(
                "evidence", root=self.root, registry_path=self.registry_path
            )["record_count"],
        )

    def test_restricted_payload_and_unapproved_action_are_blocked(self):
        draft = self.evidence_draft()
        draft["targets"][0]["sensitivity"] = "restricted"
        with self.assertRaisesRegex(archive.ArchiveError, "restricted"):
            self.prepare(draft)
        draft = self.evidence_draft()
        draft["authorization"]["approved_actions"] = []
        with self.assertRaisesRegex(archive.ArchiveError, "persist_in_archive"):
            self.prepare(draft)

    def test_core_contract_rejects_unknown_fields_without_schema_help(self):
        draft = self.evidence_draft()
        draft["targets"][0]["unexpected"] = True
        errors = archive._request_errors(draft)
        self.assertTrue(any("未知字段" in value for value in errors))

    def test_approved_handoff_must_allow_persistence(self):
        draft = self.evidence_draft()
        draft["authorization"]["mode"] = "approved_handoff"
        governed = copy.deepcopy(self.govern)
        handoff = next(
            item
            for item in governed["downstream_handoffs"]
            if item["handoff_id"] == "egh_example_archive"
        )
        handoff["allowed_uses"] = ["historical_trace"]
        write_json(self.source_path("governed"), governed)
        with self.assertRaisesRegex(archive.ArchiveError, "persist_in_archive"):
            self.prepare(draft)

    def test_archive_handoff_can_restrict_but_never_trigger_write(self):
        governed = copy.deepcopy(self.govern)
        handoff = next(
            item
            for item in governed["downstream_handoffs"]
            if item["target_skill"] == "evidence-archive"
        )
        handoff["handoff_status"] = "blocked"
        write_json(self.source_path("governed"), governed)
        with self.assertRaisesRegex(archive.ArchiveError, "尚未 ready"):
            self.prepare(self.evidence_draft())

    def test_baseline_candidate_is_patched_and_read_by_exact_version(self):
        draft = {
            "project_name": "示例项目",
            "authorization": {
                "mode": "approved_handoff",
                "authorization_ref": "handoff://egh-baseline-1",
                "authorized_target_refs": ["objective#baseline-task-completion"],
                "authorized_field_paths": ["analysis_results.baseline.candidate"],
                "approved_actions": ["persist_in_archive"],
                "review_decision_refs": ["review-baseline-1"],
            },
            "targets": [
                {
                    "target_ref": "objective#baseline-task-completion",
                    "record_kind": "baseline",
                    "projection": "shared_baseline_item",
                    "logical_object_ref": "baseline:baseline-task-completion",
                    "source_artifact_id": "objective",
                    "source_artifact_version": "",
                    "source_run_id": "",
                    "source_selector": {
                        "path": "analysis_results.baseline.candidate",
                        "id_field": "baseline_id",
                        "id_value": "baseline-task-completion",
                    },
                    "source_content_digest": "0" * 64,
                    "authorized_field_paths": ["analysis_results.baseline.candidate"],
                    "record_action": "new",
                    "supersedes_ref": None,
                    "sensitivity": "internal",
                    "redaction_state": "not_required",
                    "allowed_uses": ["baseline_comparison"],
                    "forbidden_uses": ["recalculate"],
                    "governance": {
                        "artifact_id": "governed",
                        "source_run_id": None,
                        "content_digest": None,
                        "handoff_ref": "egh-baseline-1",
                        "patch_ref": "bgp-1",
                        "review_decision_refs": ["review-baseline-1"],
                    },
                }
            ],
        }
        prepared = self.prepare(draft)
        summary = self.archive(prepared)
        self.assertEqual("archived", summary["archive_results"][0]["result"])
        item = archive.get_record(
            "baseline",
            baseline_id="baseline-task-completion",
            baseline_version="1",
            root=self.root,
            registry_path=self.registry_path,
        )
        self.assertEqual("active", item["lifecycle_status"])
        self.assertEqual("approved", item["review_status"])

    def test_business_snapshot_requires_explicit_extra_approval_and_stays_minimal(self):
        draft = {
            "project_name": "示例项目",
            "authorization": {
                "mode": "explicit_user_request",
                "authorization_ref": "conversation://archive-bi",
                "authorized_target_refs": ["business-impact#portfolio_summary"],
                "authorized_field_paths": ["run", "portfolio_summary", "limitations"],
                "approved_actions": [
                    "persist_in_archive",
                    "approve_archive_decision_snapshot",
                ],
                "review_decision_refs": [],
            },
            "targets": [
                {
                    "target_ref": "business-impact#portfolio_summary",
                    "record_kind": "business_decision_snapshot",
                    "projection": "business_decision_minimum",
                    "logical_object_ref": "business-decision:portfolio",
                    "source_artifact_id": "business-impact",
                    "source_artifact_version": "",
                    "source_run_id": "",
                    "source_selector": {"path": "portfolio_summary"},
                    "source_content_digest": "0" * 64,
                    "authorized_field_paths": [
                        "run",
                        "portfolio_summary",
                        "limitations",
                    ],
                    "record_action": "new",
                    "supersedes_ref": None,
                    "sensitivity": "confidential",
                    "redaction_state": "archive_safe_projection",
                    "allowed_uses": ["business_decision_review"],
                    "forbidden_uses": ["evidence", "knowledge_publication"],
                    "governance": {
                        "artifact_id": None,
                        "source_run_id": None,
                        "content_digest": None,
                        "handoff_ref": None,
                        "patch_ref": None,
                        "review_decision_refs": [],
                    },
                }
            ],
        }
        prepared = self.prepare(draft)
        summary = self.archive(prepared)
        record_id = summary["archive_results"][0]["archive_record_ref"].split("=", 1)[1]
        record = archive.get_record(
            "evidence",
            archive_record_id=record_id,
            root=self.root,
            registry_path=self.registry_path,
        )
        snapshot = record["payload_snapshot"]
        self.assertEqual({"run", "portfolio_summary", "limitations"}, set(snapshot))
        self.assertNotIn("consumer_access", snapshot)

    def test_root_and_outcome_projection_do_not_upgrade_claims(self):
        root_source = json.loads(self.source_path("root-cause").read_text(encoding="utf-8"))
        candidate = root_source["analysis_results"]["root_cause_candidates"][0]
        root_target = {
            "record_kind": "root_cause",
            "authorized_field_paths": ["analysis_results.root_cause_candidates"]
        }
        root_snapshot = archive._project_snapshot(
            root_target, root_source, candidate, None
        )
        self.assertEqual("candidate_requires_review", root_snapshot["status"])
        self.assertNotIn("validated", root_snapshot)

        outcome_source = json.loads(self.source_path("outcome").read_text(encoding="utf-8"))
        outcome_snapshot = archive._project_snapshot(
            {
                "record_kind": "outcome",
                "authorized_field_paths": [
                    "analysis_contract",
                    "analysis_results.validation_assessment",
                    "limitations",
                ],
            },
            outcome_source,
            outcome_source["analysis_results"]["validation_assessment"],
            None,
        )
        self.assertEqual(
            "causal_suggestive",
            outcome_snapshot["validation_assessment"]["attribution"]["strength"],
        )
        self.assertEqual(
            outcome_source["limitations"], outcome_snapshot["limitations"]
        )

    def test_context_root_and_outcome_archive_as_typed_snapshots(self):
        targets = [
            {
                "target_ref": "governed#context=ctx-1",
                "record_kind": "context_factor",
                "projection": "governed_context_assessment",
                "logical_object_ref": "context:ctx-1",
                "source_artifact_id": "governed",
                "source_artifact_version": "",
                "source_run_id": "",
                "source_selector": {
                    "path": "context_factor_assessments",
                    "id_field": "factor_id",
                    "id_value": "ctx-1",
                },
                "source_content_digest": "0" * 64,
                "authorized_field_paths": ["context_factor_assessments"],
                "record_action": "new",
                "supersedes_ref": None,
                "sensitivity": "internal",
                "redaction_state": "not_required",
                "allowed_uses": ["historical_context"],
                "forbidden_uses": ["raw_log_reconstruction"],
                "governance": {
                    "artifact_id": None,
                    "source_run_id": None,
                    "content_digest": None,
                    "handoff_ref": None,
                    "patch_ref": None,
                    "review_decision_refs": [],
                },
            },
            {
                "target_ref": "root-cause#candidate=rc-1",
                "record_kind": "root_cause",
                "projection": "root_cause_minimum",
                "logical_object_ref": "root-cause:rc-1",
                "source_artifact_id": "root-cause",
                "source_artifact_version": "",
                "source_run_id": "",
                "source_selector": {
                    "path": "analysis_results.root_cause_candidates",
                    "id_field": "candidate_id",
                    "id_value": "rc-1",
                },
                "source_content_digest": "0" * 64,
                "authorized_field_paths": [
                    "analysis_results.root_cause_candidates"
                ],
                "record_action": "new",
                "supersedes_ref": None,
                "sensitivity": "internal",
                "redaction_state": "not_required",
                "allowed_uses": ["historical_trace"],
                "forbidden_uses": ["claim_confirmed_root_cause"],
                "governance": {
                    "artifact_id": None,
                    "source_run_id": None,
                    "content_digest": None,
                    "handoff_ref": None,
                    "patch_ref": None,
                    "review_decision_refs": [],
                },
            },
            {
                "target_ref": "outcome#decision=vd-1",
                "record_kind": "outcome",
                "projection": "outcome_minimum",
                "logical_object_ref": "outcome:vd-1",
                "source_artifact_id": "outcome",
                "source_artifact_version": "",
                "source_run_id": "",
                "source_selector": {
                    "path": "analysis_results.validation_assessment",
                    "id_field": "assessment_id",
                    "id_value": "vd-1",
                },
                "source_content_digest": "0" * 64,
                "authorized_field_paths": [
                    "analysis_contract",
                    "analysis_results.validation_assessment",
                    "limitations",
                ],
                "record_action": "new",
                "supersedes_ref": None,
                "sensitivity": "internal",
                "redaction_state": "not_required",
                "allowed_uses": ["historical_trace"],
                "forbidden_uses": ["cross_case_generalization"],
                "governance": {
                    "artifact_id": None,
                    "source_run_id": None,
                    "content_digest": None,
                    "handoff_ref": None,
                    "patch_ref": None,
                    "review_decision_refs": [],
                },
            },
        ]
        request = {
            "project_name": "示例项目",
            "authorization": {
                "mode": "explicit_user_request",
                "authorization_ref": "conversation://archive-three-types",
                "authorized_target_refs": [item["target_ref"] for item in targets],
                "authorized_field_paths": sorted(
                    {
                        field
                        for item in targets
                        for field in item["authorized_field_paths"]
                    }
                ),
                "approved_actions": ["persist_in_archive"],
                "review_decision_refs": [],
            },
            "targets": targets,
        }
        summary = self.archive(self.prepare(request))
        self.assertEqual(
            {"context_factor", "root_cause", "outcome"},
            {item["record_kind"] for item in summary["archive_results"]},
        )
        self.assertTrue(
            all(item["result"] == "archived" for item in summary["archive_results"])
        )

    def test_superseding_chain_rejects_missing_cross_object_and_branch(self):
        prepared = self.prepare(self.evidence_draft())
        self.archive(prepared)
        records = archive._read_jsonl(
            self.root / self.registry["stores"][0]["path"],
            archive._validate_archive_record,
        )
        bad = copy.deepcopy(records[0])
        bad["record"]["record_action"] = "superseding"
        bad["record"]["supersedes_ref"] = (
            "archived-evidence-store#archive_record_id=ar_missing"
        )
        bad["record"]["archive_record_id"] = "ar_" + "f" * 24
        with self.assertRaisesRegex(archive.ArchiveError, "不存在"):
            archive._validate_record_chains(records + [bad])

    def test_overbroad_store_permissions_block_write(self):
        prepared = self.prepare(self.evidence_draft())
        store = self.root / self.registry["stores"][0]["path"]
        store.parent.mkdir(parents=True, exist_ok=True)
        store.write_text("", encoding="utf-8")
        os.chmod(store, 0o644)
        with self.assertRaisesRegex(archive.ArchiveError, "没有记录成功归档"):
            self.archive(prepared)

    def test_summary_failure_keeps_store_and_retry_rebuilds_receipt(self):
        prepared = self.prepare(self.evidence_draft())

        def fail_summary(_path: Path, _value: dict) -> None:
            raise OSError("summary unavailable")

        with self.assertRaisesRegex(OSError, "summary unavailable"):
            self.archive(prepared, summary_writer=fail_summary)
        store = self.root / self.registry["stores"][0]["path"]
        self.assertEqual(1, len(store.read_text(encoding="utf-8").splitlines()))
        summary = self.archive(prepared)
        self.assertEqual("duplicate", summary["archive_results"][0]["result"])

    def test_concurrent_identical_writers_append_only_once(self):
        prepared = self.prepare(self.evidence_draft())
        context = multiprocessing.get_context("fork")
        queue = context.Queue()
        processes = [
            context.Process(
                target=archive_worker,
                args=(
                    prepared,
                    str(self.root),
                    str(self.registry_path),
                    queue,
                ),
            )
            for _ in range(2)
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join(10)
            self.assertEqual(0, process.exitcode)
        outcomes = sorted(queue.get(timeout=2) for _ in processes)
        self.assertEqual(["archived", "duplicate"], outcomes)
        store = self.root / self.registry["stores"][0]["path"]
        self.assertEqual(1, len(store.read_text(encoding="utf-8").splitlines()))


if __name__ == "__main__":
    unittest.main()
