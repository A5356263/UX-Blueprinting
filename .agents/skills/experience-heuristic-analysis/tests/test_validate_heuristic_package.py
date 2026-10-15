from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
WORKSPACE = SKILL_DIR.parents[2]
SCRIPT = SKILL_DIR / "scripts" / "validate_heuristic_package.py"
SPEC = importlib.util.spec_from_file_location("validate_heuristic_package", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


class HeuristicPackageValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request_example = json.loads(
            (SKILL_DIR / "examples/request.example.json").read_text(encoding="utf-8")
        )
        cls.output_example = json.loads(
            (SKILL_DIR / "examples/example_output.json").read_text(encoding="utf-8")
        )

    def request(self) -> dict:
        return copy.deepcopy(self.request_example)

    def package(self) -> dict:
        return copy.deepcopy(self.output_example)

    def assert_invalid(self, request: dict, package: dict, contains: str) -> None:
        with self.assertRaises(validator.PackageError) as context:
            validator.validate_package(request, package)
        self.assertIn(contains, str(context.exception))

    def test_examples_are_valid(self):
        validator.validate_input(self.request())
        validator.validate_package(self.request(), self.package())

    def test_publish_envelope_is_accepted_by_semantic_and_json_schema_gates(self):
        request = self.request()
        package = validator.contract_runtime.apply_request_envelope(self.package(), request)
        validator.validate_package(request, package)
        self.assertEqual(package["run"]["invocation_context"], request["invocation_context"])
        self.assertEqual(package["run"]["analysis_purpose"], request["analysis_purpose"])
        self.assertIn("publication", package)
        self.assertIn("delivery", package)

    def test_schema_documents_are_draft_2020_12(self):
        for name in ("input.schema.json", "output.schema.json"):
            schema = json.loads(
                (SKILL_DIR / "schemas" / name).read_text(encoding="utf-8")
            )
            self.assertEqual(
                "https://json-schema.org/draft/2020-12/schema", schema["$schema"]
            )

    def test_independent_mode_rejects_upstream_locator(self):
        request = self.request()
        request["sources"][0]["acquisition"] = "explicit_upstream"
        request["sources"][0]["upstream_locator"] = {
            "artifact_instance_ref": {
                "artifact_id": "uxb",
                "artifact_version": "1.0.0",
                "producer_skill": "uxb",
                "run_id": "uxb_1",
                "artifact_path": "spark-output/results/uxb/demo.json",
                "content_digest": "0" * 64,
                "project_name": "demo",
                "analysis_purpose_key": "uxb",
                "publication_status": "published",
            },
            "payload_ref": "#/scope",
        }
        with self.assertRaisesRegex(validator.PackageError, "independent mode"):
            validator.validate_input(request)

    def test_source_capability_whitelist_fails_closed(self):
        package = self.package()
        package["run"]["sources"][0]["observable_capabilities"].append(
            "runtime_interaction"
        )
        self.assert_invalid(
            self.request(), package, "unsupported observable capabilities"
        )

    def test_unknown_nested_fields_fail_without_jsonschema(self):
        package = self.package()
        package["findings"][0]["discussion_note"] = "internal history"
        self.assert_invalid(self.request(), package, "unsupported fields")

    def test_input_output_binding_is_exact(self):
        package = self.package()
        package["analysis_contract"]["focus_areas"] = ["另一个重点"]
        self.assert_invalid(self.request(), package, "focus_areas does not match")

    def test_duplicate_finding_key_is_rejected(self):
        package = self.package()
        duplicate = copy.deepcopy(package["findings"][0])
        duplicate["finding_id"] = "ehf_002"
        duplicate["evidence_status"] = "not_promoted"
        duplicate["not_promoted_reasons"] = ["duplicate candidate"]
        duplicate["validation_request_refs"] = []
        package["findings"].append(duplicate)
        package["analysis_results"]["summary"] = validator.derive_summary(package)
        self.assert_invalid(self.request(), package, "duplicate finding_key")

    def test_prohibited_claim_language_is_rejected(self):
        package = self.package()
        package["findings"][0]["risk_hypothesis"] = "用户一定看不到主行动"
        package["evidence_items"][0]["risk_hypothesis"] = "用户一定看不到主行动"
        self.assert_invalid(self.request(), package, "prohibited claim language")

    def test_strong_or_causal_evidence_is_rejected(self):
        package = self.package()
        package["evidence_items"][0]["can_be_used_as_strong_evidence"] = True
        self.assert_invalid(self.request(), package, "cannot be strong evidence")
        package = self.package()
        package["evidence_items"][0]["causal_claim_allowed"] = True
        self.assert_invalid(self.request(), package, "cannot allow causal claims")

    def test_blocked_privacy_prevents_promotion(self):
        package = self.package()
        package["findings"][0]["privacy_status"] = "blocked"
        package["evidence_items"][0]["privacy_status"] = "blocked"
        self.assert_invalid(self.request(), package, "blocked and cannot be promoted")

    def test_blocking_validation_request_prevents_promotion(self):
        package = self.package()
        package["validation_requests"][0]["blocks_evidence_promotion"] = True
        self.assert_invalid(self.request(), package, "cannot be promoted")

    def test_summary_and_handoff_are_derived_exactly(self):
        package = self.package()
        package["analysis_results"]["summary"]["major"] = 99
        self.assert_invalid(self.request(), package, "not programmatically derived")
        package = self.package()
        package["handoff"]["evidence_govern"]["payload_refs"] = ["#/findings/0"]
        self.assert_invalid(self.request(), package, "point exactly")

    def test_recheck_requires_structured_comparison(self):
        request = self.request()
        request["analysis_mode"] = "intervention_recheck"
        request["baseline_ref"] = {
            "ref_type": "source",
            "source_id": "src_screenshot_001",
            "fingerprint": "before",
        }
        request["current_ref"] = {
            "ref_type": "source",
            "source_id": "src_screenshot_001",
            "fingerprint": "after",
        }
        package = self.package()
        package["run"]["analysis_mode"] = "intervention_recheck"
        package["run"]["combined_input_fingerprint"] = validator.input_fingerprint(
            request
        )
        self.assert_invalid(request, package, "requires comparison")

    def test_real_screenshot_sources_are_treated_as_restricted(self):
        paths = [
            WORKSPACE / "input/数据分析loop测试数据/费控流程页面/报销单1.png",
            WORKSPACE / "input/数据分析loop测试数据/费控流程页面/报销单2-编辑费用.png",
            WORKSPACE / "input/数据分析loop测试数据/费控流程页面/申请单.png",
        ]
        if not all(path.is_file() for path in paths):
            self.skipTest("workspace screenshot fixtures are not present")
        package = self.package()
        source = package["run"]["sources"][0]
        self.assertEqual("restricted", source["privacy_status"])
        self.assertFalse(source["redaction_applied"])
        self.assertTrue(source["disclosure_limitations"])

    def test_report_hides_non_safe_finding_text(self):
        package = self.package()
        secret = "企业甲-用户13800000000-单据INV-9988"
        package["findings"][0]["privacy_status"] = "restricted"
        package["findings"][0]["observation"] = secret
        package["evidence_items"] = []
        package["findings"][0]["evidence_status"] = "not_promoted"
        package["findings"][0]["not_promoted_reasons"] = ["privacy_review_pending"]
        package["handoff"]["evidence_refs"] = []
        package["handoff"]["handoff_status"] = "blocked"
        package["handoff"]["evidence_govern"]["status"] = "blocked"
        package["handoff"]["evidence_govern"]["payload_refs"] = []
        package["analysis_results"]["summary"] = validator.derive_summary(package)
        report = validator.render_report(package)
        self.assertNotIn(secret, report)
        self.assertIn("内容受限", report)
        self.assertNotIn("visual-hierarchy", report)
        self.assertNotIn("restricted", report)

    def test_not_evaluable_cannot_replace_latest(self):
        package = self.package()
        package["run"]["status"] = "not_evaluable"
        package["findings"] = []
        package["evidence_items"] = []
        package["validation_requests"] = []
        package["analysis_results"]["coverage"][0]["status"] = "not_evaluable"
        package["analysis_results"]["summary"] = validator.derive_summary(package)
        package["handoff"]["analysis_status"] = "not_evaluable"
        package["handoff"]["handoff_status"] = "blocked"
        package["handoff"]["evidence_refs"] = []
        package["handoff"]["evidence_govern"]["status"] = "blocked"
        package["handoff"]["evidence_govern"]["payload_refs"] = []
        validator.validate_package(self.request(), package)
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "latest.json"
            with self.assertRaisesRegex(
                validator.PackageError, "only completed packages"
            ):
                validator.require(
                    package["run"]["status"]
                    in {"completed", "completed_with_caveats"},
                    "only completed packages may replace latest",
                )
            self.assertFalse(out.exists())

    def test_json_serialization_preserves_quotes_backslashes_and_newlines(self):
        package = self.package()
        special = '输入框显示“邮箱”与 "账号"；路径 C:\\\\temp\\\\file\\n下一行'
        package["findings"][0]["observation"] = special
        package["evidence_items"][0]["observation"] = special
        normalized = validator.normalize_package(self.request(), package)
        validator.validate_package(self.request(), normalized)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "heuristic.json"
            validator.atomic_write(
                json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
                output,
            )
            loaded = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(special, loaded["findings"][0]["observation"])
        self.assertEqual(special, loaded["evidence_items"][0]["observation"])


if __name__ == "__main__":
    unittest.main()
