from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "root_contract", ROOT / "scripts/validate_and_write.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def load_example(name: str):
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


def make_input(mode: str):
    cases = []
    handoff_type = "governed_evidence_for_root_cause"
    if mode == "outcome_feedback_refresh":
        handoff_type = "governed_outcome_feedback_for_root_cause"
        cases = [
            {
                "outcome_ref": "outcome:a",
                "review_status": "approved",
                "govern_absorption_ref": "govern:a",
                "comparability_key": "scene-a"
            }
        ]
    if mode == "pattern_candidate_learning":
        handoff_type = "governed_pattern_cases_for_root_cause"
        cases = [
            {
                "outcome_ref": f"outcome:{suffix}",
                "review_status": "approved",
                "govern_absorption_ref": f"govern:{suffix}",
                "comparability_key": "scene-a"
            }
            for suffix in ("a", "b")
        ]
    return {
        "run": {
            "run_id": f"input-{mode}",
            "project_name": "demo",
            "run_mode": mode,
            "source_mode": "chain_context",
            "requested_at": "2026-07-25T00:00:00+08:00"
        },
        "invocation_context": "chain_context",
        "analysis_purpose": {"purpose_key": "root-cause", "purpose_label": "根因综合"},
        "requested_analyses": ["root_cause_synthesis"],
        "input_bindings": [],
        "requested_deliverables": [{"format": "json", "required": True}],
        "publication_policy": {"level": "formal", "update_current_for_purpose": True},
        "retention_policy": "retain_result",
        "govern_artifact_instance_ref": {
            "artifact_id": "governed",
            "artifact_version": "6.0.0",
            "producer_skill": "evidence-govern",
            "run_id": "eg-1",
            "artifact_path": "spark-output/results/governed/demo.json",
            "content_digest": "a" * 64,
            "project_name": "demo",
            "analysis_purpose_key": "evidence-governance",
            "publication_status": "published",
        },
        "govern_handoff": {
            "handoff_id": f"handoff-{mode}",
            "target_skill": "root-cause-synthesis",
            "handoff_type": handoff_type,
            "handoff_status": "ready",
            "payload_refs": ["#/evidence_items/0"],
            "allowed_uses": ["causal_synthesis"],
            "forbidden_uses": [],
            "required_review_request_ids": [],
            "caveats": []
        },
        "governed_context": {
            "evidence_basis": "multi_source_corroborated",
            "root_cause_readiness": "ready",
            "evidence_item_refs": ["evidence:1"],
            "evidence_relationship_refs": [],
            "context_factor_assessment_refs": [],
            "business_rule_basis_refs": [],
            "reviewed_outcome_case_refs": cases
        },
        "review_decisions": []
    }


class RootCauseContractTest(unittest.TestCase):
    def test_markdown_renderer_produces_a_complete_user_report(self):
        report = MODULE.render_markdown(load_example("candidate-synthesis.example.json"))
        self.assertGreater(len(report), 200)
        self.assertIn("根因综合报告", report)
        self.assertIn("候选", report)

    def test_examples_pass(self):
        pairs = [
            ("candidate_synthesis", "candidate-synthesis.example.json"),
            ("outcome_feedback_refresh", "outcome-feedback-refresh.example.json"),
            ("pattern_candidate_learning", "pattern-candidate-learning.example.json"),
        ]
        for mode, filename in pairs:
            with self.subTest(filename=filename):
                source = make_input(mode)
                output = load_example(filename)
                MODULE.validate_input(source)
                MODULE.validate_output(output, source)

    def test_direct_non_govern_input_is_rejected(self):
        source = make_input("candidate_synthesis")
        source["govern_artifact_instance_ref"]["producer_skill"] = "objective-data-analysis"
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_input(source)

    def test_unreleased_handoff_is_rejected(self):
        source = make_input("candidate_synthesis")
        source["govern_handoff"]["handoff_status"] = "pending_review"
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_input(source)

    def test_pending_review_can_be_closed_by_bound_decision(self):
        source = make_input("candidate_synthesis")
        handoff = source["govern_handoff"]
        handoff["handoff_status"] = "pending_review"
        handoff["required_review_request_ids"] = ["review-root-1"]
        source["review_decisions"] = [
            {
                "review_id": "decision-root-1",
                "review_request_id": "review-root-1",
                "source_artifact_instance_ref": source["govern_artifact_instance_ref"],
                "handoff_id": handoff["handoff_id"],
                "payload_refs": list(handoff["payload_refs"]),
                "decision": "approved",
                "approved_actions": ["causal_synthesis"],
                "reviewed_at": "2026-07-26T00:00:00+08:00",
                "reviewer_ref": "user-confirmed",
                "caveats": [],
            }
        ]
        MODULE.validate_input(source)

    def test_pattern_requires_two_reviewed_cases(self):
        source = make_input("pattern_candidate_learning")
        source["governed_context"]["reviewed_outcome_case_refs"] = source[
            "governed_context"
        ]["reviewed_outcome_case_refs"][:1]
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_input(source)

    def test_official_chain_resolves_exact_registered_govern_handoff(self):
        source = make_input("candidate_synthesis")
        handoff = source["govern_handoff"]
        governed = {
            "run": {
                "artifact_version": "6.0.0",
                "producer_skill": "evidence-govern",
                "project_name": "demo",
                "run_id": source["govern_artifact_instance_ref"]["run_id"],
            },
            "evidence_items": [{"evidence_id": "evidence:1"}],
            "downstream_handoffs": [copy.deepcopy(handoff)],
        }
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            governed_path = project / "governed.json"
            governed_path.write_text(
                json.dumps(governed, ensure_ascii=False), encoding="utf-8"
            )
            source["govern_artifact_instance_ref"].update({
                "artifact_path": "governed.json",
                "content_digest": hashlib.sha256(governed_path.read_bytes()).hexdigest(),
                "run_id": governed["run"]["run_id"],
            })
            (project / "registry.json").write_text(
                json.dumps({"artifacts": [{
                    "artifact_id": "governed",
                    "current_version": "6.0.0",
                    "producer_skill": "evidence-govern",
                    "results_root": ".",
                    "current_pointer_path": "pointer.json",
                }]}),
                encoding="utf-8",
            )
            old_project, old_registry = MODULE.PROJECT_ROOT, MODULE.REGISTRY
            try:
                MODULE.PROJECT_ROOT = project
                MODULE.REGISTRY = project / "registry.json"
                MODULE.validate_registered_govern_handoff(source)
                source["govern_artifact_instance_ref"]["run_id"] = "wrong-run"
                with self.assertRaisesRegex(MODULE.ContractError, "run_id"):
                    MODULE.validate_registered_govern_handoff(source)
            finally:
                MODULE.PROJECT_ROOT, MODULE.REGISTRY = old_project, old_registry

    def test_removed_fields_are_rejected(self):
        output = load_example("candidate-synthesis.example.json")
        output["validation_plans"] = []
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_output(output, make_input("candidate_synthesis"))

    def test_single_source_confidence_ceiling(self):
        output = load_example("candidate-synthesis.example.json")
        output["analysis_contract"]["evidence_basis"] = "single_source"
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_output(output, make_input("candidate_synthesis"))

    def test_stronger_alternative_cannot_remain_primary(self):
        output = load_example("candidate-synthesis.example.json")
        output["analysis_results"]["root_cause_candidates"][0][
            "alternative_explanations"
        ][0]["status"] = "stronger_than_primary"
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_output(output, make_input("candidate_synthesis"))

    def test_every_active_candidate_requires_mechanism_chain(self):
        output = load_example("candidate-synthesis.example.json")
        output["analysis_results"]["candidate_mechanism_chains"] = []
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_output(output, make_input("candidate_synthesis"))

    def test_low_confidence_direction_cannot_be_design_ready(self):
        output = load_example("candidate-synthesis.example.json")
        output["analysis_results"]["root_cause_candidates"][0][
            "causal_confidence"
        ]["level"] = "low"
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_output(output, make_input("candidate_synthesis"))

    def test_concrete_solution_is_rejected(self):
        output = load_example("candidate-synthesis.example.json")
        output["analysis_results"]["intervention_direction_candidates"][0][
            "objective"
        ] = "在页面增加按钮和弹窗"
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_output(output, make_input("candidate_synthesis"))

    def test_numeric_uplift_is_rejected(self):
        output = load_example("candidate-synthesis.example.json")
        output["analysis_results"]["validation_hypotheses"][0][
            "mechanism_statement"
        ] = "预计完成率提升 20%"
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_output(output, make_input("candidate_synthesis"))

    def test_lifecycle_patch_requires_feedback_mode(self):
        output = load_example("outcome-feedback-refresh.example.json")
        output["analysis_contract"]["run_mode"] = "candidate_synthesis"
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_output(output)

    def test_wiki_handoff_requires_pattern_mode(self):
        output = load_example("pattern-candidate-learning.example.json")
        output["analysis_contract"]["run_mode"] = "candidate_synthesis"
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_output(output)

    def test_archive_handoff_requires_persist_authorization(self):
        output = load_example("candidate-synthesis.example.json")
        handoff = copy.deepcopy(output["downstream_handoffs"][0])
        handoff["handoff_id"] = "archive-1"
        handoff["target_skill"] = "evidence-archive"
        handoff["allowed_uses"] = ["read"]
        output["downstream_handoffs"] = [handoff]
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_output(output, make_input("candidate_synthesis"))

    def test_blueprint_handoff_requires_candidate(self):
        output = load_example("candidate-synthesis.example.json")
        handoff = next(
            item
            for item in output["downstream_handoffs"]
            if item["target_skill"] == "problem-framing"
        )
        handoff["payload_refs"] = [
            ref
            for ref in handoff["payload_refs"]
            if "intervention_direction_candidates" in ref
        ]
        with self.assertRaisesRegex(
            MODULE.ContractError, "requires a Root Cause candidate"
        ):
            MODULE.validate_output(output, make_input("candidate_synthesis"))

    def test_atomic_write_requires_an_explicit_candidate_path(self):
        output = load_example("candidate-synthesis.example.json")
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = Path(temp_dir) / "candidate.json"
            written = MODULE.atomic_write(output, candidate)
            self.assertEqual(candidate, written)
            self.assertEqual("5.0.0", json.loads(written.read_text())["run"]["artifact_version"])


if __name__ == "__main__":
    unittest.main()
