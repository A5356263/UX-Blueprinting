import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_ROOT / "scripts/evidence_govern_contract.py"
EXAMPLE_PATH = SKILL_ROOT / "examples/evidence-govern-result.example.json"

SPEC = importlib.util.spec_from_file_location("evidence_govern_contract", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def shared_request_fields():
    return {
        "invocation_context": "chain_context",
        "analysis_purpose": {
            "purpose_key": "heuristic-governance",
            "purpose_label": "启发式证据治理",
        },
        "requested_analyses": ["evidence_governance"],
        "input_bindings": [],
        "requested_deliverables": [{"format": "json", "required": True}],
        "publication_policy": {
            "level": "formal",
            "update_current_for_purpose": True,
        },
        "retention_policy": "retain_result",
    }


def source_binding(root, artifact_path, heuristic):
    return {
        "artifact_instance_ref": {
            "artifact_id": "heuristic",
            "artifact_version": "4.0.0",
            "producer_skill": "experience-heuristic-analysis",
            "run_id": heuristic["run"]["run_id"],
            "artifact_path": artifact_path.relative_to(root).as_posix(),
            "content_digest": hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
            "project_name": heuristic["run"]["project_name"],
            "analysis_purpose_key": "heuristic-review",
            "publication_status": "published",
        },
        "handoff_ref": "#/handoff/evidence_govern",
        "payload_refs": ["#/evidence_items/0"],
        "allowed_use": "evidence_governance",
    }


def second_released_evidence(first, *, time_window=None):
    item = copy.deepcopy(first)
    item["evidence_type"] = "subjective"
    item["claim_type"] = "feedback_observation"
    item["claim_summary"] = "用户反馈同一场景存在提交失败。"
    item["time_window"] = time_window or copy.deepcopy(first["time_window"])
    item["lineage"] = {
        "sources": [
            {
                "source_artifact_ref": "subjective",
                "source_artifact_version": "4.0.0",
                "source_run_id": "sfa_semantic_test",
                "payload_ref": "#/evidence_items/0",
                "source_object_id": "sfe_semantic_test",
            }
        ],
        "canonicalization_version": "6.0.0",
        "lineage_fingerprint": "b" * 64,
    }
    item["evidence_id"] = MODULE._evidence_id(item)
    return item


def relationship(first, second, relationship_type="corroborates"):
    return {
        "relationship_id": f"rel_{relationship_type}",
        "relationship_type": relationship_type,
        "evidence_refs": [first["evidence_id"], second["evidence_id"]],
        "matched_dimensions": ["scope", "time_window"],
        "mismatched_dimensions": [],
        "source_independence": "independent",
        "evidence_link_confidence": "high",
        "rationale": "两个独立来源在同一时间窗口描述同一现象。",
        "limitations": [],
    }


class EvidenceGovernContractTest(unittest.TestCase):
    def setUp(self):
        self.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_example_passes_core_contract(self):
        self.assertEqual([], MODULE._validate_core(self.example))

    def test_example_uses_deterministic_evidence_id(self):
        item = self.example["evidence_items"][0]
        self.assertEqual(item["evidence_id"], MODULE._evidence_id(item))

    def test_change_signal_cannot_mutate_lifecycle(self):
        candidate = copy.deepcopy(self.example)
        candidate["evidence_change_signals"] = [
            {
                "signal_id": "sig_1",
                "evidence_refs": ["ev_27fc5d01b5b080f1"],
                "signal_type": "weakened",
                "source_refs": ["outcome#/signals/0"],
                "observed_at": "2026-07-24",
                "rationale": "example",
                "lifecycle_status": "archived",
            }
        ]
        errors = MODULE._validate_core(candidate)
        self.assertTrue(any("不得直接修改生命周期" in value for value in errors))

    def test_pending_patch_cannot_persist(self):
        candidate = copy.deepcopy(self.example)
        patch = candidate["evidence_patches"][0]
        patch["decision_status"] = "pending"
        patch["can_persist"] = True
        errors = MODULE._validate_core(candidate)
        self.assertTrue(any("未获准却 can_persist=true" in value for value in errors))

    def test_knowledge_handoff_requires_approval(self):
        candidate = copy.deepcopy(self.example)
        candidate["downstream_handoffs"].append(
            {
                "handoff_id": "egh_wiki",
                "target_skill": "knowledge-wiki",
                "handoff_type": "knowledge_candidate_review_request",
                "handoff_status": "ready",
                "payload_refs": ["#/evidence_items/0"],
                "allowed_uses": ["candidate_review"],
                "forbidden_uses": ["direct_publish"],
                "required_review_request_ids": [],
                "caveats": [],
            }
        )
        errors = MODULE._validate_core(candidate)
        self.assertTrue(
            any("approve_for_knowledge_submission" in value for value in errors)
        )

    def test_archive_handoff_requires_explicit_persistence_use(self):
        candidate = copy.deepcopy(self.example)
        handoff = next(
            item
            for item in candidate["downstream_handoffs"]
            if item["target_skill"] == "evidence-archive"
        )
        handoff["allowed_uses"] = ["historical_trace"]
        errors = MODULE._validate_core(candidate)
        self.assertTrue(any("persist_in_archive" in value for value in errors))

    def test_archive_handoff_rejects_unpersistable_patch(self):
        candidate = copy.deepcopy(self.example)
        candidate["evidence_patches"][0]["can_persist"] = False
        errors = MODULE._validate_core(candidate)
        self.assertTrue(any("未获准 Patch" in value for value in errors))

    def test_atomic_write_keeps_a_valid_latest(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate_path = Path(directory) / "candidate.json"
            output_path = Path(directory) / "latest.json"
            candidate_path.write_text(
                json.dumps(self.example, ensure_ascii=False),
                encoding="utf-8",
            )
            MODULE.atomic_write(candidate_path, output_path)
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual("written", written["run"]["write_status"])
            self.assertEqual("6.0.0", written["run"]["artifact_version"])

    def test_prepare_preserves_heuristic_privacy_and_use_limits(self):
        heuristic_root = SKILL_ROOT.parent / "experience-heuristic-analysis"
        heuristic = json.loads(
            (heuristic_root / "examples/example_output.json").read_text(
                encoding="utf-8"
            )
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact_path = root / "spark-output/results/heuristic/test.json"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text(
                json.dumps(heuristic, ensure_ascii=False), encoding="utf-8"
            )
            registry_path = root / "registry.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "artifacts": [
                            {
                                "artifact_id": "heuristic",
                                "producer_skill": "experience-heuristic-analysis",
                                "current_version": "4.0.0",
                                "results_root": "spark-output/results/heuristic",
                                "current_pointer_path": "spark-output/context/current/heuristic.json",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            request = {
                **shared_request_fields(),
                "artifact_type": "evidence_govern_request",
                "artifact_version": "6.0.0",
                "source_mode": "explicit_input",
                "requested_mode": "evidence_governance",
                "project_name": heuristic["run"]["project_name"],
                "upstream_artifact_refs": [source_binding(root, artifact_path, heuristic)],
                "context_inputs": [{
                    "input_type": "user_statement",
                    "source_ref": "context:test",
                    "statement": "测试期间发生过版本变更",
                    "declared_scope": {"time_window": "2026-07"},
                    "sensitivity": "internal",
                }],
            }
            request_path = root / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            old_root, old_registry = MODULE.WORKSPACE_ROOT, MODULE.REGISTRY_PATH
            try:
                MODULE.WORKSPACE_ROOT = root
                MODULE.REGISTRY_PATH = registry_path
                result = MODULE.prepare(request_path)
            finally:
                MODULE.WORKSPACE_ROOT = old_root
                MODULE.REGISTRY_PATH = old_registry
            item = result["evidence_items"][0]
            self.assertEqual("safe", item["privacy_status"])
            self.assertTrue(item["manual_review_required"])
            self.assertIn("preliminary_problem_signal", item["allowed_uses"])
            self.assertIn("business_impact_scale", item["forbidden_uses"])
            self.assertEqual("candidate", item["lifecycle_status"])
            self.assertEqual(1, len(result["manual_review_queue"]))
            manifest = result["analysis_contract"]["context_input_manifest"]
            self.assertEqual(1, len(manifest))
            self.assertEqual("context:test", manifest[0]["source_ref"])
            self.assertEqual("internal", manifest[0]["sensitivity"])
            self.assertNotIn("测试期间", json.dumps(manifest, ensure_ascii=False))
            self.assertEqual([], MODULE._validate_json_schema(result))

    def test_prepare_inherits_time_window_from_scene_descriptor(self):
        heuristic_root = SKILL_ROOT.parent / "experience-heuristic-analysis"
        heuristic = json.loads(
            (heuristic_root / "examples/example_output.json").read_text(
                encoding="utf-8"
            )
        )
        heuristic["evidence_items"][0]["scene_descriptor"]["time_window"] = "2026-07"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact_path = root / "spark-output/results/heuristic/test.json"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text(
                json.dumps(heuristic, ensure_ascii=False), encoding="utf-8"
            )
            registry_path = root / "registry.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "artifacts": [
                            {
                                "artifact_id": "heuristic",
                                "producer_skill": "experience-heuristic-analysis",
                                "current_version": "4.0.0",
                                "results_root": "spark-output/results/heuristic",
                                "current_pointer_path": "spark-output/context/current/heuristic.json",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            request = {
                **shared_request_fields(),
                "artifact_type": "evidence_govern_request",
                "artifact_version": "6.0.0",
                "source_mode": "explicit_input",
                "requested_mode": "evidence_governance",
                "project_name": heuristic["run"]["project_name"],
                "upstream_artifact_refs": [source_binding(root, artifact_path, heuristic)],
                "context_inputs": [],
            }
            request_path = root / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            old_root, old_registry = MODULE.WORKSPACE_ROOT, MODULE.REGISTRY_PATH
            try:
                MODULE.WORKSPACE_ROOT = root
                MODULE.REGISTRY_PATH = registry_path
                result = MODULE.prepare(request_path)
            finally:
                MODULE.WORKSPACE_ROOT = old_root
                MODULE.REGISTRY_PATH = old_registry
            self.assertEqual("2026-07", result["evidence_items"][0]["time_window"])

    def test_manual_review_and_use_limits_cannot_be_bypassed(self):
        candidate = copy.deepcopy(self.example)
        evidence = candidate["evidence_items"][0]
        evidence["manual_review_required"] = True
        candidate["manual_review_queue"] = [
            {
                "review_id": "review_privacy_1",
                "target_refs": [evidence["evidence_id"]],
                "risk_level": "medium",
                "reason": "privacy review",
                "blocked_consumers": ["root-cause-synthesis"],
                "status": "open",
            }
        ]
        errors = MODULE._validate_core(candidate)
        self.assertTrue(any("人工复核尚未 approved" in item for item in errors))

        candidate = copy.deepcopy(self.example)
        handoff = candidate["downstream_handoffs"][0]
        handoff["allowed_uses"].append("publish_publicly")
        errors = MODULE._validate_core(candidate)
        self.assertTrue(any("publish_publicly" in item for item in errors))

    def test_govern_may_grant_causal_synthesis_after_release(self):
        candidate = copy.deepcopy(self.example)
        evidence = candidate["evidence_items"][0]
        evidence["allowed_uses"].remove("causal_synthesis")
        errors = MODULE._validate_core(candidate)
        self.assertFalse(any("causal_synthesis" in item for item in errors), errors)

    def test_govern_cannot_grant_causal_synthesis_to_insufficient_evidence(self):
        candidate = copy.deepcopy(self.example)
        evidence = candidate["evidence_items"][0]
        evidence["allowed_uses"].remove("causal_synthesis")
        evidence["evidence_strength"] = "insufficient"
        errors = MODULE._validate_core(candidate)
        self.assertTrue(
            any("证据强度不足" in item and "causal_synthesis" in item for item in errors),
            errors,
        )

    def test_govern_cannot_grant_causal_synthesis_to_restricted_evidence(self):
        candidate = copy.deepcopy(self.example)
        evidence = candidate["evidence_items"][0]
        evidence["allowed_uses"].remove("causal_synthesis")
        evidence["privacy_status"] = "restricted"
        evidence["lifecycle_status"] = "restricted"
        errors = MODULE._validate_core(candidate)
        self.assertTrue(
            any("隐私状态不是 safe" in item and "causal_synthesis" in item for item in errors),
            errors,
        )

    def test_resolve_pointer_rejects_null_with_contract_error(self):
        with self.assertRaisesRegex(MODULE.ContractError, "非空字符串"):
            MODULE._resolve_pointer(self.example, None)

    def test_single_source_cannot_claim_multi_source_basis(self):
        candidate = copy.deepcopy(self.example)
        candidate["handoff"]["evidence_basis"] = "multi_source_corroborated"
        candidate["handoff"]["root_cause_readiness"] = "ready"
        errors = MODULE._validate_core(candidate)
        self.assertTrue(
            any("应为 single_source" in item for item in errors),
            errors,
        )

    def test_cross_window_evidence_cannot_corroborate(self):
        candidate = copy.deepcopy(self.example)
        first = candidate["evidence_items"][0]
        second = second_released_evidence(
            first,
            time_window={"start": "2026-07-01", "end": "2026-07-31"},
        )
        candidate["evidence_items"].append(second)
        link = relationship(first, second)
        link["matched_dimensions"] = ["scope"]
        link["mismatched_dimensions"] = ["time_window"]
        candidate["evidence_relationships"] = [link]
        candidate["handoff"]["evidence_basis"] = "multi_source_corroborated"
        candidate["handoff"]["root_cause_readiness"] = "ready"
        errors = MODULE._validate_core(candidate)
        self.assertTrue(any("时间窗口不可比" in item for item in errors), errors)
        self.assertTrue(any("应为 single_source" in item for item in errors), errors)

    def test_contested_basis_requires_valid_contradiction(self):
        candidate = copy.deepcopy(self.example)
        candidate["handoff"]["evidence_basis"] = "contested"
        candidate["handoff"]["root_cause_readiness"] = "conflict_first"
        errors = MODULE._validate_core(candidate)
        self.assertTrue(any("应为 single_source" in item for item in errors), errors)

    def test_same_window_independent_sources_may_corroborate(self):
        candidate = copy.deepcopy(self.example)
        first = candidate["evidence_items"][0]
        second = second_released_evidence(first)
        candidate["evidence_items"].append(second)
        candidate["evidence_relationships"] = [relationship(first, second)]
        candidate["handoff"]["evidence_basis"] = "multi_source_corroborated"
        candidate["handoff"]["root_cause_readiness"] = "ready"
        self.assertEqual([], MODULE._validate_core(candidate))

    def test_same_window_independent_sources_may_be_contested(self):
        candidate = copy.deepcopy(self.example)
        first = candidate["evidence_items"][0]
        second = second_released_evidence(first)
        candidate["evidence_items"].append(second)
        candidate["evidence_relationships"] = [
            relationship(first, second, relationship_type="contradicts")
        ]
        candidate["handoff"]["evidence_basis"] = "contested"
        candidate["handoff"]["root_cause_readiness"] = "conflict_first"
        self.assertEqual([], MODULE._validate_core(candidate))


if __name__ == "__main__":
    unittest.main()
