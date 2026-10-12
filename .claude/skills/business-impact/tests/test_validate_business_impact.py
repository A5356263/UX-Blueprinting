from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "example_output.json"
SCRIPT = ROOT / "scripts" / "validate_business_impact.py"

spec = importlib.util.spec_from_file_location("business_impact_validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)

def shared_request(context="independent"):
    return {
        "invocation_context": context,
        "analysis_purpose": {"purpose_key": "business-value", "purpose_label": "业务价值"},
        "requested_analyses": ["solution_value"],
        "input_bindings": [],
        "requested_deliverables": [{"format": "json", "required": True}],
        "publication_policy": {"level": "formal", "update_current_for_purpose": True},
        "retention_policy": "retain_result",
    }


def blueprint_ref():
    return {
        "artifact_id": "experience-blueprint",
        "artifact_version": "4.0.0",
        "producer_skill": "experience-blueprint",
        "run_id": "bp-1",
        "artifact_path": "blueprint.json",
        "content_digest": "0" * 64,
        "project_name": "测试",
        "analysis_purpose_key": "solution-design",
        "publication_status": "published",
    }


class BusinessImpactValidatorTests(unittest.TestCase):
    def package(self):
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def assert_invalid(self, package, contains=None):
        with self.assertRaises(validator.PackageError) as context:
            validator.validate_package(package)
        if contains:
            self.assertIn(contains, str(context.exception))

    def test_example_is_valid(self):
        validator.validate_package(self.package())

    def test_markdown_renderer_produces_a_complete_user_report(self):
        report = validator.render_markdown(self.package())
        self.assertGreater(len(report), 300)
        self.assertIn("业务影响评估", report)
        self.assertIn("价值", report)

    def test_solution_value_input_requires_valuation_ready_blueprint(self):
        blueprint = {
            "run": {
                "run_id": "bp-1",
                "artifact_version": "4.0.0",
                "producer_skill": "experience-blueprint",
                "project_name": "测试",
            },
            "solution_designs": [{
                "solution_id": "solution-1",
                "readiness": "valuation_ready",
                "valuation_inputs_status": "complete",
                "open_questions": [],
                "allowed_uses": ["solution_value_input"],
            }],
            "handoff": {
                "handoff_id": "handoff-bp-bi-1",
                "target_skill": "business-impact",
                "handoff_type": "solution_value_input",
                "handoff_status": "ready",
                "payload_refs": ["#/solution_designs/0"],
                "allowed_uses": ["solution_value_assessment"],
                "forbidden_uses": ["effect_claim"],
                "required_review_request_ids": [],
                "caveats": [],
            },
        }
        request = {
            "project_name": "测试",
            "context_mode": "chain_context",
            "requested_modes": ["solution_value"],
            "sources": [{
                "source_id": "bp",
                "source_type": "artifact",
                "source_ref": "experience-blueprint",
                "source_version": "4.0.0",
                "project_name": "测试",
                "run_id": "bp-1",
                "explicitly_referenced": True,
            }],
            "source_artifact_refs": ["experience-blueprint"],
            "solution_refs": ["experience-blueprint#/solution_designs/0"],
            "blueprint_artifact_instance_ref": blueprint_ref(),
            "blueprint_handoff": copy.deepcopy(blueprint["handoff"]),
        }
        request.update(shared_request("chain_context"))
        request["input_bindings"] = [{
            "binding_type": "artifact_instance",
            "binding_ref": request["blueprint_artifact_instance_ref"],
            "allowed_use": "solution_value_assessment",
        }]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "blueprint.json").write_text(json.dumps(blueprint), encoding="utf-8")
            old_validate = validator.contract_runtime.validate_instance_ref
            try:
                validator.contract_runtime.validate_instance_ref = (
                    lambda *args, **kwargs: (blueprint, root / "blueprint.json")
                )
                validator.validate_input_request(request)
                blueprint["solution_designs"][0]["readiness"] = "review_required"
                with self.assertRaisesRegex(validator.PackageError, "not valuation_ready"):
                    validator.validate_input_request(request)
            finally:
                validator.contract_runtime.validate_instance_ref = old_validate

    def test_user_solution_can_be_valued_independently(self):
        request = {
            "project_name": "测试",
            "context_mode": "independent",
            "requested_modes": ["solution_value"],
            "sources": [{
                "source_id": "user-solution",
                "source_type": "user_input",
                "source_ref": "conversation://solution",
                "project_name": "测试",
                "explicitly_referenced": True,
            }],
            "user_solution_statement": "在提交前解释资格条件并提供修复入口",
        }
        request.update(shared_request())
        validator.validate_input_request(request)

    def test_formal_plan_can_be_valued_independently(self):
        request = {
            "project_name": "测试",
            "context_mode": "independent",
            "requested_modes": ["solution_value"],
            "sources": [{
                "source_id": "formal-plan",
                "source_type": "formal_plan",
                "source_ref": "plan://approved-v1",
                "project_name": "测试",
                "explicitly_referenced": True,
            }],
        }
        request.update(shared_request())
        validator.validate_input_request(request)

    def test_blueprint_solution_must_be_released_by_exact_handoff(self):
        blueprint = {
            "run": {
                "run_id": "bp-1",
                "artifact_version": "4.0.0",
                "producer_skill": "experience-blueprint",
                "project_name": "测试",
            },
            "solution_designs": [{
                "solution_id": "solution-1",
                "readiness": "valuation_ready",
                "valuation_inputs_status": "complete",
                "open_questions": [],
                "allowed_uses": ["solution_value_input"],
            }],
            "handoff": {
                "handoff_id": "handoff-bp-bi-1",
                "target_skill": "business-impact",
                "handoff_type": "solution_value_input",
                "handoff_status": "ready",
                "payload_refs": ["#/solution_designs/0"],
                "allowed_uses": ["solution_value_assessment"],
                "forbidden_uses": ["effect_claim"],
                "required_review_request_ids": [],
                "caveats": [],
            },
        }
        request = {
            "project_name": "测试",
            "context_mode": "chain_context",
            "requested_modes": ["solution_value"],
            "sources": [{
                "source_id": "bp",
                "source_type": "artifact",
                "source_ref": "experience-blueprint",
                "source_version": "4.0.0",
                "project_name": "测试",
                "run_id": "bp-1",
                "explicitly_referenced": True,
            }],
            "source_artifact_refs": ["experience-blueprint"],
            "solution_refs": ["experience-blueprint#/solution_designs/1"],
            "blueprint_artifact_instance_ref": blueprint_ref(),
            "blueprint_handoff": copy.deepcopy(blueprint["handoff"]),
        }
        request.update(shared_request("chain_context"))
        request["input_bindings"] = [{
            "binding_type": "artifact_instance",
            "binding_ref": request["blueprint_artifact_instance_ref"],
            "allowed_use": "solution_value_assessment",
        }]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "blueprint.json").write_text(json.dumps(blueprint), encoding="utf-8")
            old_validate = validator.contract_runtime.validate_instance_ref
            try:
                validator.contract_runtime.validate_instance_ref = (
                    lambda *args, **kwargs: (blueprint, root / "blueprint.json")
                )
                with self.assertRaisesRegex(validator.PackageError, "not released"):
                    validator.validate_input_request(request)
            finally:
                validator.contract_runtime.validate_instance_ref = old_validate

    def test_schema_files_are_json_and_draft_2020_12(self):
        for name in ("input.schema.json", "output.schema.json"):
            schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_output_schema_external_handoff_ref_resolves_from_schema_path(self):
        schema_path = ROOT / "schemas" / "output.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        ref = schema["allOf"][0]["$ref"]
        target = (schema_path.parent / ref).resolve()
        self.assertTrue(target.is_file())
        handoff_schema = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(handoff_schema["$id"], "context_handoff.schema.json")

    def test_removed_top_level_field_is_rejected(self):
        package = self.package()
        package["value_assessments"] = []
        self.assert_invalid(package, "top-level fields")

    def test_break_even_is_rejected_anywhere(self):
        package = self.package()
        package["portfolio_summary"]["break_even_analysis"] = {}
        self.assert_invalid(package, "removed fields")

    def test_duplicate_valuation_input_is_rejected(self):
        package = self.package()
        package["valuation_inputs"].append(copy.deepcopy(package["valuation_inputs"][0]))
        self.assert_invalid(package, "duplicate input_id")

    def test_valuation_input_must_resolve_to_registered_source(self):
        package = self.package()
        package["valuation_inputs"][0]["source_ref"] = "missing-source#/problem"
        self.assert_invalid(package, "does not resolve")

    def test_package_classification_cannot_be_lower_than_input(self):
        package = self.package()
        package["run"]["data_classification"] = "confidential"
        self.assert_invalid(package, "lower than input sensitivity")

    def test_preliminary_case_cannot_merge_analysis_skills(self):
        package = self.package()
        extra = copy.deepcopy(package["valuation_inputs"][0])
        extra.update({"input_id": "vi-subjective", "source_type": "analysis_artifact", "source_skill": "subjective-feedback-analysis"})
        package["valuation_inputs"].append(extra)
        problem = package["problem_impact_cases"][0]
        problem["maturity"] = "preliminary"
        problem["source_input_refs"] = ["vi-subjective", "vi-problem"]
        self.assert_invalid(package, "cannot merge multiple analysis skills")

    def test_root_cause_direction_cannot_be_solution_scope(self):
        package = self.package()
        solution_input = next(item for item in package["valuation_inputs"] if item["input_id"] == "vi-solution")
        solution_input["source_skill"] = "root-cause-synthesis"
        self.assert_invalid(package, "cannot use Root Cause")

    def test_transition_link_requires_business_rule(self):
        package = self.package()
        link = package["solution_value_cases"][0]["metric_value_links"][0]
        link["source_input_refs"].remove("vi-rule")
        self.assert_invalid(package, "requires business rule")

    def test_duplicate_included_dedup_group_is_rejected(self):
        package = self.package()
        solution = package["solution_value_cases"][0]
        duplicate = copy.deepcopy(solution["metric_value_links"][0])
        duplicate["link_id"] = "mvl-duplicate"
        solution["metric_value_links"].append(duplicate)
        normalized = validator.normalize_package(package)
        self.assert_invalid(normalized, "duplicate included dedup_group")

    def test_forecast_cannot_claim_validated_effect(self):
        package = self.package()
        package["solution_value_cases"][0]["metric_value_links"][0]["effect_status"] = "validated_result"
        self.assert_invalid(package, "forecast cannot claim")

    def test_validated_revaluation_requires_outcome_and_prior_snapshot(self):
        package = self.package()
        solution = package["solution_value_cases"][0]
        solution["valuation_timing"] = "validated_revaluation"
        solution["forecast_status"] = "not_applicable"
        solution["metric_value_links"][0]["effect_status"] = "validated_result"
        normalized = validator.normalize_package(package)
        self.assert_invalid(normalized, "needs Outcome input")

    def test_harmed_guardrail_requires_manual_risk_review(self):
        package = self.package()
        package["solution_value_cases"][0]["guardrail_impacts"][0]["status"] = "harmed"
        self.assert_invalid(package, "manual_risk_review")

    def test_evidence_archive_requires_pending_explicit_review(self):
        package = self.package()
        archive = next(item for item in package["downstream_handoffs"] if item["target_skill"] == "evidence-archive")
        archive["required_review_request_ids"] = []
        self.assert_invalid(package, "pending explicit review")

    def test_evidence_govern_is_not_an_allowed_reverse_handoff(self):
        package = self.package()
        package["downstream_handoffs"][0]["target_skill"] = "evidence-govern"
        self.assert_invalid(package, "outside the capability boundary")

    def test_affected_share_must_be_derived(self):
        package = self.package()
        package["problem_impact_cases"][0]["affected_population"]["affected_share_range"]["base"] = 0.46
        self.assert_invalid(package, "affected share is not derived")

    def test_financial_outputs_must_be_derived(self):
        package = self.package()
        package["solution_value_cases"][0]["roi_range"]["base"] = 0.9
        self.assert_invalid(package, "not programmatically derived")

    def test_value_vs_effort_normalization_removes_financial_claims(self):
        package = self.package()
        solution = package["solution_value_cases"][0]
        solution["valuation_level"] = "value_vs_effort"
        solution["metric_value_links"] = []
        solution["qualitative_value_links"] = [{
            "link_id": "qvl-completion-value",
            "metric_ref": "metric:task_completion_rate",
            "value_direction": "positive",
            "description": "减少任务失败预计有助于完成与后续活跃，但当前不货币化",
            "source_input_refs": ["vi-solution", "vi-population"],
        }]
        normalized = validator.normalize_package(package)
        solution = normalized["solution_value_cases"][0]
        self.assertIsNone(solution["expected_benefit_range"])
        self.assertIsNone(solution["roi_range"])
        self.assertEqual(solution["benefit_components"], [])
        validator.validate_package(normalized)

    def test_value_vs_effort_requires_qualitative_value_link(self):
        package = self.package()
        solution = package["solution_value_cases"][0]
        solution["valuation_level"] = "value_vs_effort"
        solution["metric_value_links"] = []
        normalized = validator.normalize_package(package)
        self.assert_invalid(normalized, "needs qualitative value links")

    def test_metric_value_link_requires_baseline_ref_in_sources(self):
        package = self.package()
        package["solution_value_cases"][0]["metric_value_links"][0]["source_input_refs"].remove("vi-population")
        self.assert_invalid(package, "baseline_input_ref")

    def test_run_valuation_state_must_match_cases(self):
        package = self.package()
        package["run"]["valuation_state"] = "decision_ready_forecast"
        self.assert_invalid(package, "valuation_state")

    def test_decision_ready_forecast_rejects_scenario_input(self):
        package = self.package()
        package["solution_value_cases"][0]["forecast_status"] = "decision_ready_forecast"
        self.assert_invalid(package, "decision-ready forecast")

    def test_expected_benefit_cannot_exceed_addressable_opportunity(self):
        package = self.package()
        package["problem_impact_cases"][0]["addressable_opportunity"]["value_range"] = {"low": 1, "base": 1, "high": 1}
        self.assert_invalid(package, "cannot exceed addressable opportunity")

    def test_population_projection_rejects_subjective_basis(self):
        package = self.package()
        population_input = next(item for item in package["valuation_inputs"] if item["input_id"] == "vi-population")
        population_input["source_skill"] = "subjective-feedback-analysis"
        self.assert_invalid(package, "cannot project population")

    def test_population_projection_rejects_zero_join_coverage(self):
        package = self.package()
        join = package["problem_impact_cases"][0]["affected_population"]["join_coverage"]
        join.update({
            "status": "no_overlap",
            "matched_count": 0,
            "left_match_rate": 0,
            "right_match_rate": 0,
        })
        self.assert_invalid(package, "requires positive join coverage")

    def test_affected_population_counts_cannot_invert(self):
        package = self.package()
        package["problem_impact_cases"][0]["affected_population"]["observed_affected_count"] = 10001
        self.assert_invalid(package, "cannot exceed observed sample")

    def test_cost_currency_must_match_contract(self):
        package = self.package()
        package["solution_value_cases"][0]["effort_profile"]["components"][0]["currency"] = "USD"
        self.assert_invalid(package, "currency must match contract")

    def test_valuation_input_window_must_match_measurement_scope(self):
        package = self.package()
        population_input = next(
            item for item in package["valuation_inputs"]
            if item["input_id"] == "vi-population"
        )
        population_input["measurement_scope"]["time_window"]["start"] = "2026-04-01"
        self.assert_invalid(package, "time_window must match measurement_scope")

    def test_affected_population_requires_matching_objective_aggregate_scope(self):
        package = self.package()
        package["problem_impact_cases"][0]["affected_population"][
            "measurement_scope"
        ]["dimensions"]["business_board"] = "薪税"
        self.assert_invalid(package, "matching measurement_scope")

    def test_metric_value_baseline_scope_must_match_link_scope(self):
        package = self.package()
        package["solution_value_cases"][0]["metric_value_links"][0][
            "measurement_scope"
        ]["dimensions"]["business_board"] = "薪税"
        self.assert_invalid(package, "baseline measurement_scope")

    def test_transition_value_requires_enterprise_scope(self):
        package = self.package()
        link = package["solution_value_cases"][0]["metric_value_links"][0]
        effect_input = next(
            item for item in package["valuation_inputs"]
            if item["input_id"] == "vi-effect"
        )
        link["baseline_input_ref"] = "vi-effect"
        link["measurement_scope"] = copy.deepcopy(
            effect_input["measurement_scope"]
        )
        self.assert_invalid(package, "transition value requires enterprise scope")

    def test_nps_points_are_scaled_to_fraction_in_value_formula(self):
        package = self.package()
        solution = package["solution_value_cases"][0]
        link = solution["metric_value_links"][0]
        effect = next(
            item for item in package["valuation_inputs"]
            if item["input_id"] == "vi-effect"
        )
        nps_scope = {
            "grain": "survey_response",
            "dimensions": {"business_board": "费控"},
            "time_window": copy.deepcopy(effect["time_window"]),
            "population_definition": "费控 NPS 有效响应",
        }
        effect["measurement_scope"] = copy.deepcopy(nps_scope)
        link.update({
            "metric_ref": "metric:nps",
            "measurement_scope": copy.deepcopy(nps_scope),
            "baseline_input_ref": "vi-effect",
            "formula_type": "nps_value",
            "metric_change": {"low": 5, "base": 10, "high": 15},
            "metric_change_unit": "nps_points",
        })
        normalized = validator.normalize_package(package)
        benefit = normalized["solution_value_cases"][0]["metric_value_links"][0][
            "benefit_range"
        ]
        self.assertEqual(158760, benefit["base"])

    def test_downstream_handoff_ids_are_unique(self):
        package = self.package()
        package["downstream_handoffs"][1]["handoff_id"] = package["downstream_handoffs"][0]["handoff_id"]
        self.assert_invalid(package, "duplicate downstream handoff")

    def test_normalize_recalculates_benefit(self):
        package = self.package()
        package["solution_value_cases"][0]["metric_value_links"][0]["metric_change"]["base"] = 0.035
        normalized = validator.normalize_package(package)
        self.assertNotEqual(normalized["solution_value_cases"][0]["expected_benefit_range"]["base"], 47628)
        validator.validate_package(normalized)

    def test_atomic_commit_writes_normalized_package(self):
        package = self.package()
        package["solution_value_cases"][0]["metric_value_links"][0]["metric_change"]["base"] = 0.035
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "business-impact-assessment.json"
            validator.atomic_commit(package, output)
            committed = json.loads(output.read_text(encoding="utf-8"))
            self.assertNotEqual(committed["solution_value_cases"][0]["expected_benefit_range"]["base"], 47628)
            validator.validate_package(committed)

    def test_failed_atomic_commit_preserves_previous_latest(self):
        package = self.package()
        package["portfolio_summary"]["break_even_analysis"] = {}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "business-impact-assessment.json"
            output.write_text('{"previous": true}\n', encoding="utf-8")
            with self.assertRaises(validator.PackageError):
                validator.atomic_commit(package, output)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"previous": True})


if __name__ == "__main__":
    unittest.main()
