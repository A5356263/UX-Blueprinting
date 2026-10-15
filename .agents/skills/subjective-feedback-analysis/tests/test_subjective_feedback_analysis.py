from __future__ import annotations

import copy
import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, RefResolver
except ImportError:
    Draft202012Validator = None
    RefResolver = None


ROOT = Path(__file__).resolve().parents[4]
SKILL = ROOT / ".agents/skills/subjective-feedback-analysis"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_validator():
    path = SKILL / "scripts/validate_subjective_output.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


def valid_package() -> dict:
    return json.loads((FIXTURES / "valid_output.json").read_text(encoding="utf-8"))


class SubjectiveFeedbackAnalysisAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def test_runtime_structure_is_minimal(self):
        self.assertFalse((SKILL / "subskills").exists())
        self.assertFalse((SKILL / "requirements.txt").exists())
        self.assertTrue((SKILL / "tests").exists())
        self.assertEqual({path.name for path in (SKILL / "schemas").glob("*.json")}, {"input.schema.json", "output.schema.json"})
        self.assertEqual({path.name for path in (SKILL / "scripts").glob("*.py")}, {"validate_subjective_output.py"})
        self.assertEqual(
            {path.name for path in (SKILL / "references").glob("*.md")},
            {
                "input-processing-rules.md",
                "analysis-rules.md",
                "evidence-contract-rules.md",
                "knowledge-candidate-rules.md",
                "comparative-analysis-rules.md",
                "ticket-experience-classification-rules.md",
            },
        )

    def test_skill_uses_uxb_structure_without_forced_phase_pauses(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for heading in (
            "Step 0 · 运行入口",
            "角色定义",
            "总原则",
            "固定状态顺序",
            "上下文承接分支",
            "Knowledge Wiki 消费协议",
            "Step 1 · 输入理解与分析范围",
            "Step 6 · 标准交接",
            "自检",
        ):
            self.assertIn(heading, text)
        self.assertNotIn("Phase 1 结束后", text)
        self.assertNotIn("A. 全量发现", text)
        self.assertIn("最多三个问题", text)

    @unittest.skipIf(Draft202012Validator is None, "jsonschema shared test tool is not installed")
    def test_schemas_and_fixtures_are_valid(self):
        for path in (SKILL / "schemas").glob("*.json"):
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
        request_schema = json.loads((SKILL / "schemas/input.schema.json").read_text(encoding="utf-8"))
        request = json.loads((SKILL / "examples/request.example.json").read_text(encoding="utf-8"))
        request_resolver = RefResolver(
            base_uri=(SKILL / "schemas/input.schema.json").resolve().as_uri(),
            referrer=request_schema,
        )
        Draft202012Validator(request_schema, resolver=request_resolver).validate(request)
        output_schema = json.loads((SKILL / "schemas/output.schema.json").read_text(encoding="utf-8"))
        output_resolver = RefResolver(
            base_uri=(SKILL / "schemas/output.schema.json").resolve().as_uri(),
            referrer=output_schema,
        )
        Draft202012Validator(output_schema, resolver=output_resolver).validate(valid_package())
        context_schema = json.loads((ROOT / "shared-workflow/data-analysis/schemas/context_handoff.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(context_schema).validate(valid_package())

    def test_graph_and_registry_use_conditional_context_and_versioned_contract(self):
        graph = json.loads((ROOT / "shared-workflow/skill-graph.json").read_text(encoding="utf-8"))
        skill = next(item for item in graph["skills"] if item["id"] == "subjective-feedback-analysis")
        self.assertEqual(skill["reads"], [])
        self.assertEqual(set(skill["conditional_reads"]), {"uxb", "experience-blueprint", "journey-metrics", "knowledge-wiki"})
        self.assertEqual(skill["context_policy"]["independent"], "user_inputs_only")
        registry = json.loads((ROOT / "shared-workflow/data-analysis/artifact-registry.json").read_text(encoding="utf-8"))
        artifact = next(item for item in registry["artifacts"] if item["artifact_id"] == "subjective")
        self.assertEqual(artifact["current_version"], "4.0.0")
        self.assertEqual(artifact["legacy_read_versions"], [])
        self.assertEqual(next(item for item in registry["external_contexts"] if item["context_id"] == "knowledge-wiki")["path"], ".agents/skills/knowledge-wiki/knowledge/wiki/index.md")

    def test_valid_package_passes_core_gate(self):
        self.validator.validate_output(valid_package())

    def test_prepare_input_deduplicates_and_redacts_before_agent_analysis(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feedback.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["反馈内容"])
                writer.writeheader()
                writer.writerow({"反馈内容": "联系 13800138000，提交时报错"})
                writer.writerow({"反馈内容": "联系 13800138000，提交时报错"})
            request = {
                "artifact_type": "subjective_analysis_request",
                "artifact_version": "4.0.0",
                "project_name": "测试",
                "source_mode": "independent",
                "analysis_mode": "discovery",
                "input_sources": [{
                    "source_id": "feedback",
                    "source_type": "ticket",
                    "format": "csv",
                    "path_ref": str(path),
                }],
            }
            prepared = self.validator.prepare_input(request)
            self.assertEqual(prepared["status"], "ready")
            self.assertEqual(prepared["deduplicated_item_count"], 1)
            self.assertFalse(prepared["raw_text_persisted"])
            self.assertIn("[PHONE]", prepared["prepared_items"][0]["redacted_text"])
            self.assertNotIn("13800138000", json.dumps(prepared, ensure_ascii=False))

    def test_service_log_requires_explicit_usable_text_binding(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "service.csv"
            path.write_text("企业名称,处理记录,状态\n示例企业,内部排障记录,处理中\n", encoding="utf-8")
            request = {
                "artifact_type": "subjective_analysis_request",
                "artifact_version": "4.0.0",
                "project_name": "测试",
                "source_mode": "independent",
                "analysis_mode": "discovery",
                "input_sources": [{
                    "source_id": "service",
                    "source_type": "service_log",
                    "format": "csv",
                    "path_ref": str(path),
                }],
            }
            prepared = self.validator.prepare_input(request)
            self.assertEqual(prepared["status"], "not_evaluable")
            self.assertEqual(prepared["source_manifest"][0]["read_status"], "loaded")
            self.assertEqual(prepared["source_manifest"][0]["analysis_status"], "unavailable")
            self.assertEqual(prepared["source_manifest"][0]["unavailable_reason"], "service_log_requires_explicit_text_field_binding")
            self.assertEqual(prepared["prepared_items"], [])

            request["input_sources"][0].update({
                "content_role": "internal_context",
                "field_bindings": {
                    "internal_context": "处理记录",
                    "enterprise_name": "企业名称",
                },
            })
            usable = self.validator.prepare_input(request)
            self.assertEqual(usable["status"], "not_evaluable")
            self.assertEqual(usable["source_manifest"][0]["analysis_status"], "context_only")
            self.assertEqual(usable["prepared_items"][0]["segment_fields"]["enterprise_name"], "示例企业")

    def test_privacy_risk_sets_manual_review_from_detection(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feedback.csv"
            path.write_text("反馈内容\n请联系13800138000\n", encoding="utf-8")
            request = {
                "artifact_type": "subjective_analysis_request",
                "artifact_version": "4.0.0",
                "project_name": "测试",
                "source_mode": "independent",
                "analysis_mode": "discovery",
                "input_sources": [{
                    "source_id": "feedback",
                    "source_type": "ticket",
                    "format": "csv",
                    "path_ref": str(path),
                }],
            }
            prepared = self.validator.prepare_input(request)
            self.assertTrue(prepared["prepared_items"][0]["manual_review_required"])

    def test_enterprise_identifiers_remain_available_for_segmentation(self):
        text, risks = self.validator._redact(
            "enterprise_id=ent-001 enterprise_name=示例企业 user_id=u-001"
        )
        self.assertIn("enterprise_id=ent-001", text)
        self.assertIn("enterprise_name=示例企业", text)
        self.assertNotIn("u-001", text)
        self.assertEqual([], risks)

    def test_markdown_is_a_complete_user_report_not_an_empty_placeholder(self):
        report = self.validator.render_markdown(valid_package())
        for section in (
            "执行摘要",
            "反馈主题与样本边界",
            "数据质量与隐私边界",
            "下一步",
        ):
            self.assertIn(section, report)
        self.assertGreater(len(report), 300)

    def test_unredacted_phone_is_rejected(self):
        package = valid_package()
        package["analysis_results"]["normalized_feedback_items"][0]["redacted_text"] = "请联系13800138000"
        with self.assertRaisesRegex(ValueError, "unredacted phone"):
            self.validator.validate_output(package)

    def test_hypothesis_cannot_be_formal_evidence(self):
        package = valid_package()
        package["evidence_items"][0]["claim_type"] = "hypothesis"
        with self.assertRaisesRegex(ValueError, "unsupported evidence claim type"):
            self.validator.validate_output(package)

    def test_hypothesis_finding_cannot_be_evidence_eligible(self):
        package = valid_package()
        package["findings"][0]["claim_type"] = "hypothesis"
        with self.assertRaisesRegex(ValueError, "cannot be evidence-eligible"):
            self.validator.validate_output(package)

    def test_ineligible_finding_cannot_enter_evidence(self):
        package = valid_package()
        package["findings"][0]["evidence_eligible"] = False
        with self.assertRaisesRegex(ValueError, "evidence-eligible finding"):
            self.validator.validate_output(package)

    def test_every_eligible_finding_requires_exactly_one_evidence(self):
        package = valid_package()
        extra = copy.deepcopy(package["findings"][0])
        extra["finding_id"] = "sff_002"
        extra["statement"] = "第二条合格发现没有对应 Evidence。"
        package["findings"].append(extra)
        with self.assertRaisesRegex(ValueError, "exactly one evidence item; actual=0"):
            self.validator.validate_output(package)

        package = valid_package()
        extra = copy.deepcopy(package["evidence_items"][0])
        extra["evidence_id"] = "sfe_002"
        package["evidence_items"].append(extra)
        package["handoff"]["evidence_refs"].append("sfe_002")
        package["handoff"]["payload_refs"].append("#/evidence_items/1")
        with self.assertRaisesRegex(ValueError, "exactly one evidence item; actual=2"):
            self.validator.validate_output(package)

    def test_handoff_payload_refs_cover_every_evidence_in_order(self):
        package = valid_package()
        package["handoff"]["payload_refs"] = []
        with self.assertRaisesRegex(ValueError, "exactly match every evidence_items index"):
            self.validator.validate_output(package)

    def test_visualization_handoff_must_release_privacy_and_limitations(self):
        for pointer in ("#/privacy", "#/limitations"):
            with self.subTest(pointer=pointer):
                package = valid_package()
                package["handoff"]["visualization"]["payload_refs"].remove(pointer)
                with self.assertRaisesRegex(ValueError, "visualization handoff"):
                    self.validator.validate_output(package)

    def test_zero_finding_zero_evidence_is_a_legal_delivery(self):
        package = valid_package()
        package["findings"] = []
        package["evidence_items"] = []
        package["analysis_results"]["objective_validation_requests"] = []
        package["handoff"]["payload_refs"] = []
        package["handoff"]["evidence_refs"] = []
        package["handoff"]["input_gate_status"] = "blocked"
        package["handoff"]["handoff_status"] = "blocked"
        package["handoff"]["blocked_reasons"] = ["no_evidence_eligible_findings"]
        self.validator.validate_output(package)
        report = self.validator.render_markdown(package)
        self.assertIn("当前样本未形成可发布的反馈发现", report)

    def test_inferred_business_rule_cannot_be_marked_confirmed(self):
        package = valid_package()
        package["analysis_results"]["business_rule_signals"] = [
            {
                "basis_id": "sfbr_001",
                "source_type": "evidence_inferred",
                "source_detail": "evidence_inferred",
                "source_ref": "sfi_001",
                "source_version": None,
                "rule_type": "validation_rule",
                "applicable_scope": {},
                "confidence": "low",
                "confirmation_status": "confirmed",
                "description": "从一条工单推断的规则。",
                "allowed_uses": ["analysis_context"],
                "forbidden_uses": ["business_fact"],
            }
        ]
        with self.assertRaisesRegex(ValueError, "cannot be confirmed"):
            self.validator.validate_output(package)

    def test_knowledge_candidates_cannot_auto_publish(self):
        package = valid_package()
        package["handoff"]["knowledge_review_request"]["auto_publish_allowed"] = True
        with self.assertRaisesRegex(ValueError, "auto-publish"):
            self.validator.validate_output(package)

    def test_comparison_rejects_effectiveness_status(self):
        package = valid_package()
        package["run"]["analysis_mode"] = "comparative_analysis"
        package["analysis_results"]["comparison"] = {
            "baseline_window": {"label": "before"},
            "comparison_window": {"label": "after"},
            "baseline_type": "run_local_comparison",
            "reusable": False,
            "comparability_status": "comparable_with_caveats",
            "theme_changes": [{"item_ref": "sfc_001", "status": "effective", "baseline_sample_count": 2, "comparison_sample_count": 1}],
            "channel_changes": [],
            "limitations": [],
        }
        with self.assertRaisesRegex(ValueError, "unsupported comparison status"):
            self.validator.validate_output(package)

    def test_ticket_rules_define_six_multi_labels_and_reported_error_boundary(self):
        text = (SKILL / "references/ticket-experience-classification-rules.md").read_text(encoding="utf-8")
        for label in ("视觉动线", "交互流程", "信息传达", "负向体验信号", "界面或交互异常", "报错与失败反馈"):
            self.assertIn(label, text)
        self.assertIn("允许多标签", text)
        self.assertIn("reported_error", text)
        self.assertIn("heuristic_reference", text)

    def test_independent_mode_cannot_claim_upstream_refs(self):
        package = valid_package()
        package["run"]["upstream_refs"] = ["spark-output/context/uxb.json"]
        with self.assertRaisesRegex(ValueError, "independent mode"):
            self.validator.validate_output(package)

    def test_prevalence_and_effect_claims_are_rejected(self):
        for statement in ("该问题的真实发生率很高。", "方案已经有效。", "这是已验证根因。"):
            package = valid_package()
            package["findings"][0]["statement"] = statement
            with self.assertRaisesRegex(ValueError, "prohibited subjective claim"):
                self.validator.validate_output(package)

    def test_prepare_input_combines_structured_text_and_keeps_fine_grained_slices(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feedback.csv"
            path.write_text(
                "标题,问题描述,页面,功能,操作节点,渠道,企业编号,企业类型\n"
                "发票导入失败,上传文件后提示格式错误,发票管理页,发票导入,文件校验,工单,ent-1,深度月活企业\n",
                encoding="utf-8",
            )
            prepared = self.validator.prepare_input({
                "artifact_type": "subjective_analysis_request",
                "artifact_version": "4.0.0",
                "project_name": "细粒度切片",
                "source_mode": "independent",
                "analysis_mode": "discovery",
                "input_sources": [{
                    "source_id": "feedback",
                    "source_type": "ticket",
                    "format": "csv",
                    "path_ref": str(path),
                    "field_bindings": {
                        "customer_voice": ["标题", "问题描述"],
                        "page": "页面",
                        "function": "功能",
                        "operation_node": "操作节点",
                        "channel": "渠道",
                        "enterprise_id": "企业编号",
                        "segment_fields": {"enterprise_group": "企业类型"},
                    },
                }],
            })
            item = prepared["prepared_items"][0]
            self.assertIn("【标题】发票导入失败", item["redacted_text"])
            self.assertIn("【问题描述】上传文件后提示格式错误", item["redacted_text"])
            self.assertEqual("发票管理页", item["product_location"]["page"])
            self.assertEqual("发票导入", item["product_location"]["function"])
            self.assertEqual("文件校验", item["product_location"]["operation_node"])
            self.assertEqual("工单", item["channel"])
            self.assertEqual("ent-1", item["segment_fields"]["enterprise_id"])
            self.assertEqual("深度月活企业", item["segment_fields"]["enterprise_group"])

    def test_sample_slice_requires_sample_only_boundary_and_valid_theme_refs(self):
        package = valid_package()
        package["analysis_results"]["sample_slices"] = [{
            "slice_id": "sfsl_page_invoice",
            "dimensions": {"page": "发票管理页", "channel": "工单"},
            "sample_count": 1,
            "sample_share": 1.0,
            "sample_status": "low_sample_risk",
            "mapping_basis": "explicit_field",
            "mapping_confidence": "high",
            "theme_refs": [package["analysis_results"]["theme_clusters"][0]["cluster_id"]],
            "interpretation_boundary": "current_feedback_sample_only_not_objective_prevalence",
        }]
        self.validator.validate_output(package)
        package["analysis_results"]["sample_slices"][0]["interpretation_boundary"] = "population_prevalence"
        with self.assertRaisesRegex(ValueError, "sample-only"):
            self.validator.validate_output(package)

    def test_prepare_input_computes_nps_and_business_slices(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "survey.csv"
            path.write_text(
                "答卷ID,反馈,NPS,板块,企业状态\n"
                "r1,很好,10,薪税,深度月活\n"
                "r2,一般,7,薪税,月活\n"
                "r3,很差,2,费控,月活\n"
                "r3,重复答卷,2,费控,月活\n",
                encoding="utf-8",
            )
            prepared = self.validator.prepare_input({
                "artifact_type": "subjective_analysis_request",
                "artifact_version": "4.0.0",
                "project_name": "NPS 测试",
                "source_mode": "independent",
                "analysis_mode": "discovery",
                "input_sources": [{
                    "source_id": "survey",
                    "source_type": "survey",
                    "format": "csv",
                    "path_ref": str(path),
                    "invited_count": 6,
                    "field_bindings": {
                        "customer_voice": "反馈",
                        "nps_score": "NPS",
                        "response_id": "答卷ID",
                        "business_board": "板块",
                        "enterprise_state": "企业状态",
                    },
                }],
            })
        summary = prepared["nps_summary"]
        self.assertEqual("completed", summary["status"])
        self.assertEqual(3, summary["overall"]["response_count"])
        self.assertAlmostEqual(0.0, summary["overall"]["nps"])
        self.assertAlmostEqual(.5, summary["overall"]["response_rate"]["value"])
        self.assertEqual(1, summary["reliability"]["duplicate_response_count"])
        scopes = {
            tuple(sorted(item["measurement_scope"]["dimensions"].items()))
            for item in summary["slices"]
        }
        self.assertIn((("business_board", "薪税"),), scopes)
        self.assertIn(
            (("business_board", "薪税"), ("enterprise_state", "深度月活")),
            scopes,
        )

    def test_nps_contract_rejects_non_reconciling_counts(self):
        package = valid_package()
        package["analysis_results"]["nps_summary"] = {
            "status": "completed",
            "overall": {
                "measurement_scope": {
                    "grain": "survey_response",
                    "dimensions": {},
                },
                "response_count": 3,
                "promoter_count": 2,
                "passive_count": 1,
                "detractor_count": 1,
                "nps": 33.3333333333,
                "response_rate": {
                    "status": "not_evaluable",
                    "numerator": 3,
                    "denominator": None,
                    "value": None,
                },
            },
            "slices": [],
            "reliability": {},
            "limitations": [],
        }
        with self.assertRaisesRegex(ValueError, "does not reconcile"):
            self.validator.validate_output(package)


if __name__ == "__main__":
    unittest.main()
