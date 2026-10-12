from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "outcome_validator", ROOT / "scripts/validate_and_write.py"
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(VALIDATOR)


def load_example(name: str) -> dict:
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


def handoff(source: str, target: str, handoff_id: str) -> dict:
    handoff_type = {
        "root-cause-synthesis": "root_cause_hypothesis_for_outcome",
        "evidence-govern": "governed_evidence_for_outcome",
    }[source]
    return {
        "handoff_id": handoff_id,
        "target_skill": target,
        "handoff_type": handoff_type,
        "handoff_status": "ready",
        "payload_refs": ["#/analysis_results"],
        "allowed_uses": ["outcome_validation"],
        "forbidden_uses": [],
        "required_review_request_ids": [],
        "caveats": [],
    }


def make_input(mode: str, stage: str) -> dict:
    return {
        "run": {
            "run_id": "outcome-input-001",
            "project_name": "报销提单优化",
            "validation_mode": mode,
            "validation_stage": stage,
            "source_mode": "explicit_input",
            "requested_at": "2026-07-25T10:00:00+08:00",
        },
        "invocation_context": "chain_context",
        "analysis_purpose": {"purpose_key": "outcome-validation", "purpose_label": "效果验证"},
        "requested_analyses": ["outcome_validation"],
        "input_bindings": [],
        "requested_deliverables": [{"format": "json", "required": True}],
        "publication_policy": {"level": "formal", "update_current_for_purpose": True},
        "retention_policy": "retain_result",
        "root_artifact_instance_ref": {
            "artifact_id": "root-cause",
            "artifact_version": "4.0.0",
            "producer_skill": "root-cause-synthesis",
            "run_id": "run:root-cause-synthesis",
            "artifact_path": "spark-output/results/root-cause/demo.json",
            "content_digest": "a" * 64,
            "project_name": "报销提单优化",
            "analysis_purpose_key": "root-cause",
            "publication_status": "published",
        },
        "root_cause_handoff": handoff(
            "root-cause-synthesis", "outcome-validation-recheck", "root-outcome-001"
        ),
        "root_cause_context": {
            "candidate_refs": ["root-cause:rc-001"],
            "validation_hypothesis_refs": ["validation-hypothesis:vh-001"],
            "causal_caveats": [],
        },
        "intervention_contract": {
            "intervention_id": "int-001",
            "source_ref": "experience-blueprint:solution-001",
            "version": "1.0",
            "solution_source_type": "experience_blueprint",
            "linked_root_cause_candidate_refs": ["root-cause:rc-001"],
            "intended_mechanism": "降低规则理解负担并减少中断。",
            "change_scope": {"journey": "submit"},
            "target_population": {"segment": "all"},
            "validation_stage": stage,
            "exposure_definition": {"event": "full_solution_exposed"},
            "implementation_fidelity_definition": {"status": "complete"},
            "target_metric_refs": ["metric:completion-rate"],
            "guardrail_metric_refs": ["metric:error-rate"],
            "approval_status": "approved",
            "caveats": [],
        },
        "govern_artifact_instance_ref": None
        if mode == "readiness_validation"
        else {
            "artifact_id": "governed",
            "artifact_version": "5.0.0",
            "producer_skill": "evidence-govern",
            "run_id": "run:evidence-govern",
            "artifact_path": "spark-output/results/governed/demo.json",
            "content_digest": "b" * 64,
            "project_name": "报销提单优化",
            "analysis_purpose_key": "validation-evidence",
            "publication_status": "published",
        },
        "govern_handoff": None
        if mode == "readiness_validation"
        else handoff(
            "evidence-govern", "outcome-validation-recheck", "govern-outcome-001"
        ),
        "governed_validation_evidence": {
            "evidence_refs": []
            if mode == "readiness_validation"
            else ["evidence:objective-001"],
            "baseline_refs": ["baseline:001"],
            "observation_window_ref": "window:001",
            "core_metric_refs": ["metric:completion-rate"],
            "guardrail_metric_refs": ["metric:error-rate"],
            "segment_refs": ["segment:all"],
            "context_factor_refs": [],
            "business_rule_basis_refs": ["business-rule:completion"],
            "data_quality_status": "ready",
        },
        "business_impact_refs": [],
        "review_decisions": [],
    }


class OutcomeContractTests(unittest.TestCase):
    def test_markdown_renderer_produces_a_complete_user_report(self):
        report = VALIDATOR.render_markdown(
            load_example("effectiveness-validation.example.json")
        )
        self.assertGreater(len(report), 300)
        self.assertIn("效果验证报告", report)
        self.assertIn("验证", report)

    def test_all_three_examples_validate(self):
        for name in (
            "readiness-validation.example.json",
            "effectiveness-validation.example.json",
            "durability-monitoring.example.json",
        ):
            VALIDATOR.validate_output(load_example(name))

    def test_all_three_input_modes_validate(self):
        for mode, stage in (
            ("readiness_validation", "pre_launch"),
            ("effectiveness_validation", "pilot"),
            ("durability_monitoring", "long_term"),
        ):
            VALIDATOR.validate_input(make_input(mode, stage))

    def test_mode_stage_mismatch_is_rejected(self):
        payload = make_input("readiness_validation", "pre_launch")
        payload["run"]["validation_stage"] = "pilot"
        payload["intervention_contract"]["validation_stage"] = "pilot"
        with self.assertRaises(Exception):
            VALIDATOR.validate_input(payload)

    def test_non_root_handoff_is_rejected(self):
        payload = make_input("readiness_validation", "pre_launch")
        payload["root_artifact_instance_ref"]["producer_skill"] = "objective-data-analysis"
        with self.assertRaises(Exception):
            VALIDATOR.validate_input(payload)

    def test_unapproved_intervention_is_rejected(self):
        payload = make_input("readiness_validation", "pre_launch")
        payload["intervention_contract"]["approval_status"] = "pending"
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_input(payload)

    def test_effectiveness_requires_govern_handoff(self):
        payload = make_input("effectiveness_validation", "pilot")
        payload["govern_handoff"] = None
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_input(payload)

    def test_effectiveness_requires_governed_evidence(self):
        payload = make_input("effectiveness_validation", "pilot")
        payload["governed_validation_evidence"]["evidence_refs"] = []
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_input(payload)

    def test_pending_review_can_be_closed_by_bound_decision(self):
        payload = make_input("readiness_validation", "pre_launch")
        handoff_value = payload["root_cause_handoff"]
        handoff_value["handoff_status"] = "pending_review"
        handoff_value["required_review_request_ids"] = ["review-outcome-1"]
        payload["review_decisions"] = [
            {
                "review_id": "decision-outcome-1",
                "review_request_id": "review-outcome-1",
                "source_artifact_instance_ref": payload["root_artifact_instance_ref"],
                "handoff_id": handoff_value["handoff_id"],
                "payload_refs": list(handoff_value["payload_refs"]),
                "decision": "approved",
                "approved_actions": ["outcome_validation"],
                "reviewed_at": "2026-07-26T00:00:00+08:00",
                "reviewer_ref": "user-confirmed",
                "caveats": [],
            }
        ]
        VALIDATOR.validate_input(payload)

    def test_prelaunch_cannot_claim_effect(self):
        payload = load_example("readiness-validation.example.json")
        payload["analysis_results"]["validation_assessment"][
            "intervention_effectiveness"
        ] = "effective"
        payload["analysis_summary"]["effectiveness"] = "effective"
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_output(payload)

    def test_prelaunch_cannot_claim_attribution(self):
        payload = load_example("readiness-validation.example.json")
        payload["analysis_results"]["validation_assessment"]["attribution"].update(
            {"strength": "causal_supported", "confounding_risk": "low"}
        )
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_output(payload)

    def test_missing_exposure_requires_not_evaluable(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["validation_assessment"]["readiness"][
            "exposure"
        ] = "not_ready"
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_output(payload)

    def test_critical_harm_prevents_effective(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["validation_assessment"][
            "intervention_effectiveness"
        ] = "effective"
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_output(payload)

    def test_high_confounding_prevents_causal_claim(self):
        payload = load_example("durability-monitoring.example.json")
        payload["analysis_results"]["validation_assessment"]["attribution"][
            "strength"
        ] = "causal_suggestive"
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_output(payload)

    def test_causal_supported_requires_low_confounding(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["validation_assessment"]["attribution"].update(
            {"strength": "causal_supported", "confounding_risk": "medium"}
        )
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_output(payload)

    def test_validated_relationship_requires_causal_supported(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["outcome_relationships"][0][
            "relation_type"
        ] = "validated_effect"
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_output(payload)

    def test_patch_target_is_govern_only(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["outcome_evidence_patch_requests"][0][
            "target_processor"
        ] = "root-cause-synthesis"
        with self.assertRaises(Exception):
            VALIDATOR.validate_output(payload)

    def test_root_feedback_requires_govern_absorption(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["root_cause_feedback_signals"][0][
            "govern_absorption_required"
        ] = False
        with self.assertRaises(Exception):
            VALIDATOR.validate_output(payload)

    def test_pattern_observation_cannot_form_pattern(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["pattern_observation_signals"][0][
            "can_form_pattern"
        ] = True
        with self.assertRaises(Exception):
            VALIDATOR.validate_output(payload)

    def test_monitoring_cannot_schedule(self):
        payload = load_example("durability-monitoring.example.json")
        payload["analysis_results"]["monitoring_requirements"][0][
            "can_schedule"
        ] = True
        with self.assertRaises(Exception):
            VALIDATOR.validate_output(payload)

    def test_automation_ready_requires_all_policy_refs(self):
        payload = load_example("durability-monitoring.example.json")
        payload["analysis_results"]["monitoring_requirements"][0][
            "status"
        ] = "ready_for_automation_controller"
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_output(payload)

    def test_business_impact_rejected_before_effect_measurement(self):
        payload = load_example("readiness-validation.example.json")
        payload["downstream_handoffs"][0]["target_skill"] = "business-impact"
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_output(payload)

    def test_archive_requires_review_and_persist_use(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["downstream_handoffs"][0]["target_skill"] = "evidence-archive"
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_output(payload)

    def test_unknown_review_ref_is_rejected(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["downstream_handoffs"][0]["required_review_request_ids"] = ["missing"]
        with self.assertRaises(VALIDATOR.ContractError):
            VALIDATOR.validate_output(payload)

    def test_write_safety_must_remain_false(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["write_safety"]["can_auto_rollback"] = True
        with self.assertRaises(Exception):
            VALIDATOR.validate_output(payload)

    def test_old_parallel_results_are_rejected(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["validation_results"] = []
        with self.assertRaises(Exception):
            VALIDATOR.validate_output(payload)

    def test_nps_measurement_requires_survey_response_scope(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["effect_measurements"][0][
            "measurement_scope"
        ]["grain"] = "enterprise"
        with self.assertRaisesRegex(VALIDATOR.ContractError, "survey_response"):
            VALIDATOR.validate_output(payload)

    def test_enterprise_transition_measurement_requires_enterprise_scope(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["effect_measurements"][1][
            "measurement_scope"
        ]["grain"] = "survey_response"
        with self.assertRaisesRegex(VALIDATOR.ContractError, "enterprise grain"):
            VALIDATOR.validate_output(payload)

    def test_effect_measurement_change_must_reconcile(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["effect_measurements"][0][
            "absolute_change"
        ] = 99
        with self.assertRaisesRegex(VALIDATOR.ContractError, "does not reconcile"):
            VALIDATOR.validate_output(payload)

    def test_measurement_attribution_cannot_exceed_overall_assessment(self):
        payload = load_example("effectiveness-validation.example.json")
        payload["analysis_results"]["effect_measurements"][1][
            "attribution_strength"
        ] = "causal_supported"
        with self.assertRaisesRegex(VALIDATOR.ContractError, "exceeds"):
            VALIDATOR.validate_output(payload)

    def test_atomic_write_requires_an_explicit_candidate_path(self):
        payload = load_example("readiness-validation.example.json")
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "outcome-candidate.json"
            written = VALIDATOR.atomic_write(payload, candidate)
            self.assertEqual(written, candidate)
            expected = copy.deepcopy(payload)
            expected["run"]["write_status"] = "written"
            self.assertEqual(json.loads(written.read_text(encoding="utf-8")), expected)


if __name__ == "__main__":
    unittest.main()
