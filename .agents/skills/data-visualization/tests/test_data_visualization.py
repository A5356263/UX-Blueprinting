from __future__ import annotations

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
SKILL = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class DataVisualizationAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_module(
            SKILL / "scripts/validate_visualization_package.py"
        )
        cls.objective_renderer = load_module(
            SKILL / "scripts/render_objective_report.py"
        )

    def test_runtime_structure_is_minimal(self):
        self.assertFalse((SKILL / "examples").exists())
        self.assertFalse((SKILL / "templates").exists())
        self.assertEqual(
            {path.name for path in (SKILL / "references").glob("*.md")},
            {
                "chart-selection-and-visual-encoding-rules.md",
                "relationship-and-value-expression-rules.md",
                "report-responsive-accessibility-rules.md",
                "source-contract-risk-and-quality-rules.md",
            },
        )
        self.assertEqual(
            {path.name for path in (SKILL / "schemas").glob("*.json")},
            {
                "input.schema.json",
                "output.schema.json",
                "source-contracts.json",
            },
        )
        self.assertEqual(
            {path.name for path in (SKILL / "scripts").glob("*.py")},
            {
                "render_objective_report.py",
                "validate_visualization_package.py",
            },
        )

    def test_objective_path_limit_redraws_visible_graph(self):
        source = (
            SKILL / "scripts/render_objective_report.py"
        ).read_text(encoding="utf-8")
        self.assertIn("function visibleGraph(paths)", source)
        self.assertIn("function redraw(paths)", source)
        self.assertIn("redraw(visible)", source)
        self.assertIn("dataset.renderedNodeCount", source)
        self.assertIn("dataset.renderedLinkCount", source)
        self.assertNotIn("for(const link of data.links||[])", source)

    def test_skill_uses_light_uxb_structure_and_plain_language_gate(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for heading in (
            "Step 0 · 运行入口",
            "角色定义",
            "总原则",
            "固定状态顺序",
            "来源契约与门禁",
            "执行流程",
            "输出契约",
            "标准交接",
            "自检",
        ):
            self.assertIn(heading, text)
        self.assertIn("你希望读者通过这张图看懂什么", text)
        self.assertNotIn("chart-design-legacy-rules", text)
        self.assertNotIn("value-chain-legacy-skill", text)
        self.assertNotIn("UCATS", text)
        self.assertNotIn("扫描 `package.json`", text.split("本技能不负责：", 1)[0])
        self.assertIn("单一正式发布", text)
        self.assertNotIn(" render --package", text)
        self.assertNotIn("--output-root spark-output", text)

    def test_all_json_resources_parse(self):
        for path in [*(SKILL / "schemas").glob("*.json"), *FIXTURES.glob("*.json")]:
            self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)

    @unittest.skipIf(Draft202012Validator is None, "jsonschema shared test tool is not installed")
    def test_output_schema_and_mode_fixtures_are_valid(self):
        schema_path = SKILL / "schemas/output.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        resolver = RefResolver(base_uri=schema_path.resolve().as_uri(), referrer=schema)
        validator = Draft202012Validator(schema, resolver=resolver)
        for name in (
            "registered_upstream.example.json",
            "chart_ready.example.json",
            "visualization_brief.example.json",
        ):
            with self.subTest(name=name):
                validator.validate(fixture(name))

    def test_three_mode_fixtures_pass(self):
        for name in (
            "registered_upstream.example.json",
            "chart_ready.example.json",
            "visualization_brief.example.json",
        ):
            with self.subTest(name=name):
                self.validator.validate_package(fixture(name))

    def test_input_gate_validates_three_modes(self):
        shared = {
            "invocation_context": "independent",
            "analysis_purpose": {
                "purpose_key": "visual-summary",
                "purpose_label": "可视化摘要",
            },
            "requested_analyses": ["visualization"],
            "input_bindings": [],
            "requested_deliverables": [
                {"format": "json", "required": True},
                {"format": "html", "required": True},
            ],
            "publication_policy": {
                "level": "formal",
                "update_current_for_purpose": True,
            },
            "retention_policy": "retain_result",
        }
        registered = {
            "artifact_type": "visualization_package_input",
            "schema_version": "5.0.0",
            "source_mode": "registered_upstream",
            "project_name": "demo",
            "visualization_intent": {"reader_goal": "查看完成率"},
            "upstream_sources": [
                {
                    "artifact_instance_ref": {
                        "artifact_id": "objective",
                        "artifact_version": "4.0.0",
                        "producer_skill": "objective-data-analysis",
                        "run_id": "oda_demo",
                        "artifact_path": "spark-output/results/objective/demo.json",
                        "content_digest": "0" * 64,
                        "project_name": "demo",
                        "analysis_purpose_key": "overall",
                        "publication_status": "published",
                    },
                    "handoff": {
                        "handoff_id": "handoff-objective-viz",
                        "target_skill": "data-visualization",
                        "handoff_type": "visualization_input",
                        "handoff_status": "ready",
                        "payload_refs": ["#/analysis_results"],
                        "allowed_uses": ["visualization"],
                        "forbidden_uses": ["recalculate_analysis"],
                        "required_review_request_ids": [],
                        "caveats": [],
                    },
                    "allowed_use": "visualization",
                    "producer_skill": "objective-data-analysis",
                    "artifact_type": "objective_evidence_package",
                    "artifact_version": "4.0.0",
                    "requested_paths": ["#/analysis_results"],
                }
            ],
            "artifact_bundle": {
                "bundle_id": "bundle-objective-demo",
                "report_profile": "objective_journey",
                "source_run_ids": ["oda_demo"],
            },
        }
        chart_ready = {
            "artifact_type": "visualization_package_input",
            "schema_version": "5.0.0",
            "source_mode": "chart_ready",
            "project_name": "demo",
            "visualization_intent": {"reader_goal": "比较完成率"},
            "chart_ready_data": {
                "metrics": [
                    {
                        "metric_id": "completion",
                        "label": "完成率",
                        "value": 0.8,
                        "unit": "ratio",
                        "time_window": "2026-06",
                        "epistemic_status": "observed",
                    }
                ]
            },
        }
        brief = {
            "artifact_type": "visualization_package_input",
            "schema_version": "5.0.0",
            "source_mode": "visualization_brief",
            "project_name": "demo",
            "visualization_intent": {"reader_goal": "比较企业分群"},
            "visualization_brief": {
                "reader_goal": "比较企业分群",
                "available_information": [],
            },
        }
        registered.update(shared)
        chart_ready.update(shared)
        brief.update(shared)
        old_instance = self.validator.contract_runtime.validate_instance_ref
        old_handoff = self.validator.contract_runtime.validate_handoff
        try:
            self.validator.contract_runtime.validate_instance_ref = (
                lambda *args, **kwargs: (
                    {
                        "run": {"run_id": "oda_demo"},
                        "analysis_results": {},
                        "handoff": {
                            "visualization": registered["upstream_sources"][0][
                                "handoff"
                            ]
                        },
                    },
                    Path("objective.json"),
                )
            )
            self.validator.contract_runtime.validate_handoff = (
                lambda *args, **kwargs: None
            )
            for value in (registered, chart_ready, brief):
                self.validator.validate_input(value)
        finally:
            self.validator.contract_runtime.validate_instance_ref = old_instance
            self.validator.contract_runtime.validate_handoff = old_handoff

    def test_registered_source_rejects_old_version_and_stale_path(self):
        package = fixture("registered_upstream.example.json")
        source = package["analysis_results"]["visualization_package"][
            "source_contracts"
        ][0]
        source["artifact_version"] = "2.1.0"
        with self.assertRaisesRegex(self.validator.ContractError, "未登记或版本不匹配"):
            self.validator.validate_package(package)

        package = fixture("registered_upstream.example.json")
        source = package["analysis_results"]["visualization_package"][
            "source_contracts"
        ][0]
        source["consumed_paths"].append("#/blockage_candidates")
        with self.assertRaisesRegex(self.validator.ContractError, "allowed_paths 之外"):
            self.validator.validate_package(package)

    def test_brief_cannot_render_formal_values(self):
        package = fixture("visualization_brief.example.json")
        output = package["analysis_results"]["visualization_package"][
            "visual_outputs"
        ][0]
        output["render_status"] = "formal"
        output["chart_data"] = {
            "series": [
                {
                    "series_id": "fabricated",
                    "label": "fabricated",
                    "points": [],
                }
            ]
        }
        with self.assertRaisesRegex(self.validator.ContractError, "visualization_brief"):
            self.validator.validate_package(package)

    def test_explicit_bundle_builds_and_renders_without_scanning_or_recalculation(self):
        request = {
            "source_mode": "registered_upstream",
            "project_name": "完整诊断",
            "artifact_bundle": {
                "bundle_id": "diagnostic-demo",
                "report_profile": "full_diagnostic",
                "source_run_ids": ["oda_demo"],
            },
            "upstream_sources": [{
                "producer_skill": "objective-data-analysis",
                "artifact_type": "objective_evidence_package",
                "artifact_version": "4.0.0",
                "artifact_instance_ref": {
                    "artifact_id": "objective",
                    "run_id": "oda_demo",
                },
                "requested_paths": ["#/analysis_results", "#/limitations"],
            }],
        }
        objective = {
            "run": {"run_id": "oda_demo"},
            "analysis_results": {
                "metrics": {"completion_rate": .8},
                "journey": {"top_path_patterns": [], "stage_nodes": []},
            },
            "findings": [{"statement": "完成率为 80%。"}],
            "limitations": [],
        }
        old_validate = self.validator.validate_input
        old_payloads = self.validator._payloads_for_report
        try:
            self.validator.validate_input = lambda value: None
            self.validator._payloads_for_report = lambda value: {
                "objective-data-analysis": objective
            }
            package = self.validator.build_bundle_package(request)
        finally:
            self.validator.validate_input = old_validate
            self.validator._payloads_for_report = old_payloads
        source = package["analysis_results"]["visualization_package"][
            "source_contracts"
        ][0]
        self.assertIn("#/handoff/visualization", source["consumed_paths"])
        self.assertFalse(
            package["analysis_results"]["visualization_package"][
                "recalculation_performed"
            ]
        )
        html = self.validator.render_diagnostic_html(
            package, {"objective-data-analysis": objective}, "full_diagnostic"
        )
        self.assertIn("完成率为 80%", html)
        self.assertIn("不扫描 current/latest", html)
        for marker in (
            'class="skip-link"',
            'id="report-main"',
            ":focus-visible",
            "prefers-reduced-motion",
            "@media print",
            "--surface-elevated",
        ):
            self.assertIn(marker, html)

    def test_registered_upstream_rejects_projection_drift(self):
        authoritative = fixture("registered_upstream.example.json")
        candidate = json.loads(json.dumps(authoritative))
        candidate["analysis_results"]["visualization_package"]["visual_outputs"][0][
            "title"
        ] = "候选包自行改写的标题"
        request = {"source_mode": "registered_upstream"}
        original = self.validator._authoritative_projection_for_request
        try:
            self.validator._authoritative_projection_for_request = (
                lambda value: authoritative
            )
            with self.assertRaisesRegex(
                self.validator.ContractError, "权威确定性投影不一致"
            ):
                self.validator.validate_authoritative_projection(candidate, request)
        finally:
            self.validator._authoritative_projection_for_request = original

    def test_registered_upstream_accepts_exact_authoritative_projection(self):
        authoritative = fixture("registered_upstream.example.json")
        request = {"source_mode": "registered_upstream"}
        original = self.validator._authoritative_projection_for_request
        try:
            self.validator._authoritative_projection_for_request = (
                lambda value: authoritative
            )
            self.validator.validate_authoritative_projection(
                json.loads(json.dumps(authoritative)), request
            )
        finally:
            self.validator._authoritative_projection_for_request = original

    def test_nps_projection_preserves_survey_response_scope(self):
        html = self.validator._nps_diagnostic_section({
            "status": "completed",
            "overall": {
                "measurement_scope": {
                    "grain": "survey_response",
                    "dimensions": {},
                },
                "response_count": 100,
                "promoter_count": 50,
                "passive_count": 20,
                "detractor_count": 30,
                "nps": 20,
                "response_rate": {
                    "status": "available",
                    "value": .5,
                },
            },
            "slices": [],
        })
        self.assertIn("NPS", html)
        self.assertIn("50.0%", html)
        self.assertIn("survey_response", html)

    def test_sankey_requires_weighted_relationships(self):
        package = fixture("registered_upstream.example.json")
        output = package["analysis_results"]["visualization_package"][
            "visual_outputs"
        ][0]
        output["chart_type"] = "sankey"
        output["intent"] = "quantitative_flow"
        with self.assertRaisesRegex(self.validator.ContractError, "正式 sankey"):
            self.validator.validate_package(package)

    def test_relationship_producer_must_match_source_contract(self):
        package = fixture("registered_upstream.example.json")
        package["analysis_results"]["visualization_package"][
            "relationship_diagrams"
        ] = [
            {
                "diagram_id": "bad-producer",
                "title": "错误来源",
                "producer": "root-cause-synthesis",
                "relation_type": "candidate_mechanism",
                "source_refs": ["objective#/analysis_results"],
                "nodes": [],
                "edges": [],
                "confidence": "low",
                "caveats": [],
            }
        ]
        with self.assertRaisesRegex(self.validator.ContractError, "producer 未出现在"):
            self.validator.validate_package(package)

    def test_absolute_paths_are_rejected(self):
        package = fixture("chart_ready.example.json")
        package["analysis_results"]["visualization_package"]["output_files"] = [
            {
                "path": "/tmp/report.html",
                "format": "html",
                "purpose": "generic_visualization_page",
                "source_run_ids": ["user_chart_001"],
                "write_status": "written",
            }
        ]
        with self.assertRaisesRegex(self.validator.ContractError, "安全相对引用"):
            self.validator.validate_package(package)

    def test_generic_renderer_is_offline_and_does_not_write_a_second_result(self):
        package = fixture("chart_ready.example.json")
        before = json.dumps(package, ensure_ascii=False, sort_keys=True)
        html = self.validator.render_generic_html(package)
        self.assertIn("<!doctype html>", html.lower())
        self.assertNotIn("cdn.", html.lower())
        self.assertNotIn("http://", html.lower())
        for marker in (
            'class="skip-link"',
            'id="report-main"',
            ":focus-visible",
            "prefers-reduced-motion",
            "@media print",
            "--surface-elevated",
        ):
            self.assertIn(marker, html)
        self.assertEqual(before, json.dumps(package, ensure_ascii=False, sort_keys=True))
        self.assertEqual(
            [],
            package["analysis_results"]["visualization_package"]["output_files"],
        )

    def _semantic_package(self, chart_type, series, **changes):
        package = fixture("chart_ready.example.json")
        output = package["analysis_results"]["visualization_package"][
            "visual_outputs"
        ][0]
        output["visual_id"] = f"semantic-{chart_type}"
        output["chart_type"] = chart_type
        output["chart_data"] = {"series": series}
        output["encoding"].update({
            "unit": "ratio",
            "denominator": "task_instance",
            "time_window": "2026-06",
        })
        output.update(changes)
        return package

    @staticmethod
    def _points(*values):
        return [
            {
                "label": str(label),
                "category": str(label),
                "x": x,
                "y": y,
                "value": value,
                "epistemic_status": "observed",
                "source_ref": f"user-chart#/chart_ready_data/{index}",
            }
            for index, (label, x, y, value) in enumerate(values)
        ]

    def test_scatter_uses_numeric_xy_without_connecting_points(self):
        package = self._semantic_package(
            "scatter",
            [{"series_id": "segments", "label": "分群", "points": self._points(
                ("A", 100, .72, None), ("B", 10, .91, None)
            )}],
        )
        before = json.dumps(package, ensure_ascii=False, sort_keys=True)
        self.validator.validate_package(package)
        html = self.validator.render_generic_html(package)
        self.assertIn("class='scatter-point'", html)
        self.assertIn("data-x='100'", html)
        self.assertIn(">segment</text>", html)
        self.assertIn(">completion_rate</text>", html)
        self.assertNotIn("<polyline", html)
        self.assertEqual(before, json.dumps(package, ensure_ascii=False, sort_keys=True))

    def test_scatter_missing_xy_fails_closed(self):
        package = self._semantic_package(
            "scatter",
            [{"series_id": "segments", "label": "分群", "points": self._points(
                ("A", None, .72, None)
            )}],
        )
        with self.assertRaisesRegex(self.validator.ContractError, "散点图.*X 和 Y"):
            self.validator.validate_package(package)

    def test_distribution_is_not_rendered_as_a_line(self):
        package = self._semantic_package(
            "distribution",
            [{"series_id": "bins", "label": "耗时分布", "points": self._points(
                ("0–10 秒", None, None, 12), ("10–30 秒", None, None, 5)
            )}],
        )
        self.validator.validate_package(package)
        html = self.validator.render_generic_html(package)
        self.assertIn("distribution-bin", html)
        self.assertNotIn("<polyline", html)

        samples = self._semantic_package(
            "distribution",
            [{"series_id": "samples", "label": "原始样本", "points": self._points(
                ("样本一", 8, None, None), ("样本二", 21, None, None)
            )}],
        )
        with self.assertRaisesRegex(
            self.validator.ContractError, "原始样本.*已登记的分箱"
        ):
            self.validator.validate_package(samples)
        sample_output = samples["analysis_results"]["visualization_package"]["visual_outputs"][0]
        sample_output["render_status"] = "degraded"
        sample_output["caveats"] = ["只有原始样本，未提供正式分箱"]
        sample_output["chart_data"]["table"] = {
            "columns": ["样本", "耗时"],
            "rows": [["样本一", 8], ["样本二", 21]],
        }
        self.validator.validate_package(samples)
        sample_html = self.validator.render_generic_html(samples)
        self.assertIn("仅交付数据表", sample_html)
        self.assertNotIn("<circle class='distribution-sample'", sample_html)

    def test_line_series_are_not_connected_to_each_other(self):
        package = self._semantic_package(
            "line",
            [
                {"series_id": "current", "label": "当前", "points": self._points(
                    ("5 月", 1, None, .7), ("6 月", 2, None, .8)
                )},
                {"series_id": "baseline", "label": "基线", "points": self._points(
                    ("5 月", 1, None, .75), ("6 月", 2, None, .77)
                )},
            ],
        )
        self.validator.validate_package(package)
        html = self.validator._render_visual(
            package["analysis_results"]["visualization_package"]["visual_outputs"][0]
        )
        self.assertEqual(2, html.count("<polyline"))
        self.assertEqual(2, html.count("class='line-series "))

    def test_grouped_stacked_funnel_and_metric_semantic_gates(self):
        one_series = [{"series_id": "a", "label": "A", "points": self._points(
            ("企业一", None, None, .8)
        )}]
        grouped = self._semantic_package("grouped_bar", one_series)
        with self.assertRaisesRegex(self.validator.ContractError, "至少需要两个非空系列"):
            self.validator.validate_package(grouped)

        stacked = self._semantic_package(
            "stacked_bar",
            one_series + [{"series_id": "b", "label": "B", "points": self._points(
                ("企业一", None, None, .2)
            )}],
        )
        stacked["analysis_results"]["visualization_package"]["visual_outputs"][0]["encoding"]["unit"] = None
        with self.assertRaisesRegex(self.validator.ContractError, "缺少统一单位"):
            self.validator.validate_package(stacked)

        funnel = self._semantic_package(
            "funnel",
            [{"series_id": "tasks", "label": "任务", "points": self._points(
                ("进入", None, None, 100), ("完成", 2, None, 80)
            )}],
        )
        with self.assertRaisesRegex(self.validator.ContractError, "缺少明确的 X/顺序字段"):
            self.validator.validate_package(funnel)

        metric = self._semantic_package(
            "metric_card",
            [{"series_id": "metric", "label": "指标", "points": self._points(
                ("完成率", None, None, .8), ("报错率", None, None, .1)
            )}],
        )
        with self.assertRaisesRegex(self.validator.ContractError, "只能包含一个"):
            self.validator.validate_package(metric)

    def test_eight_supported_generic_types_use_dedicated_renderers(self):
        common = self._points(("A", 1, .7, .7), ("B", 2, .9, .9))
        second = self._points(("A", 1, .3, .3), ("B", 2, .1, .1))
        cases = {
            "metric_card": (
                [{"series_id": "metric", "label": "指标", "points": [common[0]]}],
                "metric-card",
            ),
            "bar": ([{"series_id": "bar", "label": "柱", "points": common}], "bar-row"),
            "grouped_bar": ([
                {"series_id": "g1", "label": "系列一", "points": common},
                {"series_id": "g2", "label": "系列二", "points": second},
            ], "grouped-chart"),
            "stacked_bar": ([
                {"series_id": "s1", "label": "系列一", "points": common},
                {"series_id": "s2", "label": "系列二", "points": second},
            ], "stacked-chart"),
            "line": ([{"series_id": "line", "label": "趋势", "points": common}], "series-svg"),
            "distribution": ([{"series_id": "bins", "label": "分布", "points": [
                {**common[0], "x": None}, {**common[1], "x": None}
            ]}], "distribution-chart"),
            "scatter": ([{"series_id": "scatter", "label": "关系", "points": common}], "scatter-svg"),
            "funnel": ([{"series_id": "funnel", "label": "漏斗", "points": common}], "funnel-chart"),
        }
        for chart_type, (series, marker) in cases.items():
            with self.subTest(chart_type=chart_type):
                package = self._semantic_package(chart_type, series)
                self.validator.validate_package(package)
                output = package["analysis_results"]["visualization_package"]["visual_outputs"][0]
                self.assertIn(marker, self.validator._render_visual(output))

    def test_eight_renderers_do_not_mutate_candidate_packages(self):
        common = self._points(("A", 1, .7, .7), ("B", 2, .9, .9))
        second = self._points(("A", 1, .3, .3), ("B", 2, .1, .1))
        cases = {
            "metric_card": [{"series_id": "metric", "label": "指标", "points": [common[0]]}],
            "bar": [{"series_id": "bar", "label": "柱", "points": common}],
            "grouped_bar": [
                {"series_id": "g1", "label": "系列一", "points": common},
                {"series_id": "g2", "label": "系列二", "points": second},
            ],
            "stacked_bar": [
                {"series_id": "s1", "label": "系列一", "points": common},
                {"series_id": "s2", "label": "系列二", "points": second},
            ],
            "line": [{"series_id": "line", "label": "趋势", "points": common}],
            "distribution": [{"series_id": "bins", "label": "分布", "points": [
                {**common[0], "x": None}, {**common[1], "x": None}
            ]}],
            "scatter": [{"series_id": "scatter", "label": "关系", "points": common}],
            "funnel": [{"series_id": "funnel", "label": "漏斗", "points": common}],
        }
        for chart_type, series in cases.items():
            with self.subTest(chart_type=chart_type):
                package = self._semantic_package(chart_type, series)
                before = json.dumps(package, ensure_ascii=False, sort_keys=True)
                self.validator.validate_package(package)
                output = package["analysis_results"]["visualization_package"]["visual_outputs"][0]
                self.validator._render_visual(output)
                self.assertEqual(before, json.dumps(package, ensure_ascii=False, sort_keys=True))
                self.assertEqual([], package["analysis_results"]["visualization_package"]["output_files"])

    def test_negative_bar_families_and_funnel_fail_closed_but_degraded_table_is_allowed(self):
        positive = self._points(("A", 1, None, 10), ("B", 2, None, -2))
        positive_second = self._points(("A", 1, None, 3), ("B", 2, None, 1))
        cases = {
            "bar": [{"series_id": "bar", "label": "柱", "points": positive}],
            "grouped_bar": [
                {"series_id": "one", "label": "一", "points": positive},
                {"series_id": "two", "label": "二", "points": positive_second},
            ],
            "stacked_bar": [
                {"series_id": "one", "label": "一", "points": positive},
                {"series_id": "two", "label": "二", "points": positive_second},
            ],
            "funnel": [{"series_id": "funnel", "label": "漏斗", "points": positive}],
        }
        for chart_type, series in cases.items():
            with self.subTest(chart_type=chart_type):
                package = self._semantic_package(chart_type, series)
                before = json.dumps(package, ensure_ascii=False, sort_keys=True)
                with self.assertRaises(self.validator.ContractError):
                    self.validator.validate_package(package)
                self.assertEqual(before, json.dumps(package, ensure_ascii=False, sort_keys=True))
                output = package["analysis_results"]["visualization_package"]["visual_outputs"][0]
                output["render_status"] = "degraded"
                output["caveats"] = ["当前版本不支持正负方向柱形"]
                output["chart_data"]["table"] = {
                    "columns": ["类别", "变化"], "rows": [["A", 10], ["B", -2]]
                }
                self.validator.validate_package(package)
                self.assertIn("仅交付数据表", self.validator.render_generic_html(package))

    def test_degraded_output_requires_table_and_never_draws_chart(self):
        package = self._semantic_package(
            "scatter",
            [{"series_id": "partial", "label": "不完整", "points": []}],
            render_status="degraded",
            caveats=["X 字段未提供"],
        )
        output = package["analysis_results"]["visualization_package"]["visual_outputs"][0]
        with self.assertRaisesRegex(self.validator.ContractError, "必须提供非空数据表"):
            self.validator.validate_package(package)
        output["chart_data"]["table"] = {"columns": ["企业", "完成率"], "rows": [["A", .8]]}
        self.validator.validate_package(package)
        html = self.validator.render_generic_html(package)
        self.assertIn("仅交付数据表", html)
        self.assertNotIn("<circle class='scatter-point'", html)

    def test_relationship_diagram_has_independent_node_and_edge_tables(self):
        package = fixture("chart_ready.example.json")
        package["analysis_results"]["visualization_package"]["relationship_diagrams"] = [{
            "diagram_id": "relation-table",
            "title": "问题与影响关系",
            "producer": "user",
            "relation_type": "observed_relationship",
            "source_refs": ["user-chart#/chart_ready_data"],
            "nodes": [
                {"node_id": "p", "label": "提交阻断", "node_type": "problem", "epistemic_status": "observed", "source_refs": ["user-chart#/chart_ready_data/0"]},
                {"node_id": "i", "label": "任务退出", "node_type": "impact", "epistemic_status": "observed", "source_refs": ["user-chart#/chart_ready_data/1"]},
            ],
            "edges": [{
                "edge_id": "e", "source": "p", "target": "i",
                "relation_type": "associated_with", "weight": None,
                "weight_unit": None, "epistemic_status": "observed",
                "source_refs": ["user-chart#/chart_ready_data"],
                "caveats": ["未提供可比较规模"],
            }],
            "confidence": "medium",
            "caveats": ["关系不表示因果"],
        }]
        before = json.dumps(package, ensure_ascii=False, sort_keys=True)
        self.validator.validate_package(package)
        html = self.validator.render_generic_html(package)
        for marker in ("关系数据表", "节点类型", "权重单位", "未提供可比较规模"):
            self.assertIn(marker, html)
        self.assertEqual(before, json.dumps(package, ensure_ascii=False, sort_keys=True))

    def test_skill_and_reference_require_explicit_degradation(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        rules = (SKILL / "references/chart-selection-and-visual-encoding-rules.md").read_text(encoding="utf-8")
        self.assertNotIn("不支持的类型降级为", skill)
        self.assertIn("不支持的类型在正式发布时失败关闭", skill)
        self.assertIn("原始样本", skill)
        self.assertIn("明确分箱标签", rules)

    def test_source_matrix_matches_registry_and_has_no_legacy_versions(self):
        matrix = json.loads(
            (SKILL / "schemas/source-contracts.json").read_text(encoding="utf-8")
        )
        registry = json.loads(
            (
                ROOT / "shared-workflow/data-analysis/artifact-registry.json"
            ).read_text(encoding="utf-8")
        )
        by_skill = {
            item["producer_skill"]: item
            for item in registry["artifacts"]
            if item["producer_skill"]
            in {
                "objective-data-analysis",
                "subjective-feedback-analysis",
                "experience-heuristic-analysis",
                "evidence-govern",
                "root-cause-synthesis",
                "outcome-validation-recheck",
                "business-impact",
                "problem-framing",
                "experience-blueprint",
            }
            and item["artifact_type"] != "human_readable_report"
        }
        external_skills = {
            item["producer_skill"] for item in registry["external_contexts"]
        }
        for contract in matrix["contracts"]:
            if contract["producer_skill"] in external_skills:
                continue
            artifact = by_skill[contract["producer_skill"]]
            self.assertEqual(contract["artifact_type"], artifact["artifact_type"])
            self.assertEqual(
                contract["artifact_version"], artifact["current_version"]
            )
            self.assertEqual([], artifact["legacy_read_versions"])

    def test_objective_renderer_rejects_2_1(self):
        with self.assertRaisesRegex(ValueError, "only accepts artifact_version=4.0.0"):
            self.objective_renderer.render({"run": {"artifact_version": "2.1.0"}})

    def test_objective_candidate_has_no_second_delivery_and_declares_findings(self):
        block = {"status": "not_requested"}
        objective = {
            "run": {
                "artifact_version": "4.0.0",
                "run_id": "oda_candidate",
                "project_name": "测试",
                "generated_at": "2026-07-29T00:00:00Z",
            },
            "analysis_results": {
                "metrics": block,
                "funnel": block,
                "journey": block,
                "errors": block,
                "segments": block,
            },
            "findings": [],
            "limitations": [],
        }
        candidate = self.objective_renderer.build_spec(objective, "objective")
        visualization = candidate["analysis_results"]["visualization_package"]
        self.assertEqual([], visualization["output_files"])
        self.assertIn(
            "#/findings", visualization["source_contracts"][0]["consumed_paths"]
        )
        self.assertEqual("not_requested", candidate["run"]["write_status"])

    def test_request_package_alignment_rejects_undeclared_findings_consumption(self):
        package = fixture("registered_upstream.example.json")
        source = package["analysis_results"]["visualization_package"][
            "source_contracts"
        ][0]
        source["consumed_paths"].append("#/findings")
        request_source = {
            "producer_skill": "objective-data-analysis",
            "artifact_type": "objective_evidence_package",
            "artifact_version": "4.0.0",
            "artifact_instance_ref": {"run_id": "oda_demo"},
            "requested_paths": ["#/analysis_results", "#/limitations"],
        }
        request = {
            "source_mode": "registered_upstream",
            "artifact_bundle": {
                "bundle_id": "bundle-objective-report",
                "report_profile": "objective_journey",
                "source_run_ids": ["oda_demo"],
            },
            "upstream_sources": [request_source],
        }
        with self.assertRaisesRegex(
            self.validator.ContractError, "未申请的路径"
        ):
            self.validator.validate_request_package_alignment(package, request)
        request_source["requested_paths"].append("#/findings")
        self.validator.validate_request_package_alignment(package, request)

    def test_formal_output_files_are_the_actual_immutable_pair(self):
        package = fixture("registered_upstream.example.json")
        request = {
            "source_mode": "registered_upstream",
            "analysis_purpose": {
                "purpose_key": "objective-report",
                "purpose_label": "客观分析报告",
            },
            "requested_deliverables": [
                {"format": "json", "required": True},
                {"format": "html", "required": True},
            ],
            "upstream_sources": [{"producer_skill": "objective-data-analysis"}],
            "artifact_bundle": {
                "bundle_id": "bundle-objective-output-files",
                "report_profile": "objective_journey",
                "source_run_ids": ["oda_demo"],
            },
        }
        files = self.validator._formal_output_files(package, request)
        self.assertEqual(["json", "html"], [item["format"] for item in files])
        self.assertEqual("contract", files[0]["purpose"])
        self.assertEqual("objective_report", files[1]["purpose"])
        self.assertEqual(
            files[0]["path"].removesuffix(".json"),
            files[1]["path"].removesuffix(".html"),
        )
        self.assertTrue(
            all(
                item["path"].startswith("spark-output/results/visualization/")
                for item in files
            )
        )

    def test_objective_publish_writes_one_matching_formal_json_html_pair(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_relative = "spark-output/results/objective/source.json"
            source_path = root / source_relative
            source_path.parent.mkdir(parents=True)
            block = {"status": "not_requested"}
            objective = {
                "run": {
                    "artifact_type": "objective_evidence_package",
                    "artifact_version": "4.0.0",
                    "producer_skill": "objective-data-analysis",
                    "run_id": "oda_publish",
                    "project_name": "测试",
                    "generated_at": "2026-07-29T00:00:00Z",
                    "sources": [],
                },
                "scope": {"analysis_scope": "任务完成情况"},
                "effective_analysis_contract": {"metric_framework": "指标-2026"},
                "analysis_results": {
                    "metrics": {
                        "status": "completed",
                        "task_instance_count": 10,
                        "completion_rate": .8,
                        "one_time_completion_rate": .7,
                        "error_task_rate": .1,
                    },
                    "funnel": block,
                    "journey": block,
                    "errors": block,
                    "segments": block,
                },
                "findings": [
                    {
                        "source_analysis": "metrics",
                        "statement": "10 个任务中有 8 个完成。",
                    }
                ],
                "limitations": [],
                "handoff": {
                    "visualization": {
                        "handoff_id": "handoff-objective-visualization-oda_publish",
                        "target_skill": "data-visualization",
                        "handoff_type": "analysis_for_visualization",
                        "handoff_status": "ready",
                        "payload_refs": [
                            "#/analysis_results",
                            "#/findings",
                            "#/limitations",
                        ],
                        "allowed_uses": ["visualization"],
                        "forbidden_uses": ["recalculate_analysis"],
                        "required_review_request_ids": [],
                        "caveats": [],
                    }
                },
            }
            source_path.write_text(
                json.dumps(objective, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            registry_path = root / "registry.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "version": "test",
                        "artifacts": [
                            {
                                "artifact_id": "objective",
                                "current_version": "4.0.0",
                                "producer_skill": "objective-data-analysis",
                                "results_root": "spark-output/results/objective",
                                "current_pointer_path": "spark-output/context/current/objective.json",
                            },
                            {
                                "artifact_id": "visualization",
                                "current_version": "5.0.0",
                                "producer_skill": "data-visualization",
                                "results_root": "spark-output/results/visualization",
                                "current_pointer_path": "spark-output/context/current/visualization.json",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            digest = self.validator.contract_runtime.content_digest_bytes(
                source_path.read_bytes()
            )
            instance_ref = {
                "artifact_id": "objective",
                "artifact_version": "4.0.0",
                "producer_skill": "objective-data-analysis",
                "run_id": "oda_publish",
                "artifact_path": source_relative,
                "content_digest": digest,
                "project_name": "测试",
                "analysis_purpose_key": "objective",
                "publication_status": "published",
            }
            request = {
                "artifact_type": "visualization_package_input",
                "schema_version": "5.0.0",
                "source_mode": "registered_upstream",
                "project_name": "测试",
                "visualization_intent": {"reader_goal": "理解任务完成情况"},
                "upstream_sources": [
                    {
                        "artifact_instance_ref": instance_ref,
                        "handoff": objective["handoff"]["visualization"],
                        "allowed_use": "visualization",
                        "producer_skill": "objective-data-analysis",
                        "artifact_type": "objective_evidence_package",
                        "artifact_version": "4.0.0",
                        "requested_paths": [
                            "#/analysis_results",
                            "#/findings",
                            "#/limitations",
                        ],
                    }
                ],
                "invocation_context": "independent",
                "analysis_purpose": {
                    "purpose_key": "objective-report",
                    "purpose_label": "客观分析报告",
                },
                "requested_analyses": ["visualization"],
                "input_bindings": [],
                "requested_deliverables": [
                    {"format": "json", "required": True},
                    {"format": "html", "required": True},
                ],
                "publication_policy": {
                    "level": "formal",
                    "update_current_for_purpose": True,
                },
                "retention_policy": "retain_result",
                "artifact_bundle": {
                    "bundle_id": "bundle-objective-publish",
                    "report_profile": "objective_journey",
                    "source_run_ids": ["oda_publish"],
                },
            }
            candidate = self.objective_renderer.build_spec(objective, "objective")
            old_root = self.validator.PROJECT_ROOT
            old_registry = self.validator.REGISTRY_PATH
            try:
                self.validator.PROJECT_ROOT = root
                self.validator.REGISTRY_PATH = registry_path
                reference = self.validator.publish_package(candidate, request)
            finally:
                self.validator.PROJECT_ROOT = old_root
                self.validator.REGISTRY_PATH = old_registry
            formal_json = root / reference["artifact_path"]
            published = json.loads(formal_json.read_text(encoding="utf-8"))
            files = published["analysis_results"]["visualization_package"][
                "output_files"
            ]
            self.assertEqual(
                published["delivery"]["files"],
                [
                    {
                        "format": item["format"],
                        "path": item["path"],
                        "required": True,
                        "status": "completed",
                    }
                    for item in files
                ],
            )
            html_path = root / files[1]["path"]
            self.assertTrue(html_path.is_file())
            html = html_path.read_text(encoding="utf-8")
            self.assertIn("本次分析了什么", html)
            self.assertIn("10 个任务中有 8 个完成", html)
            self.assertFalse((root / "spark-output/data-visualization").exists())
            self.assertFalse(
                (root / "spark-output/context/data-visualization.json").exists()
            )

    def test_objective_report_fails_closed_when_metrics_conflict(self):
        block = {"status": "not_requested"}
        package = {
            "run": {
                "artifact_version": "4.0.0",
                "run_id": "oda_conflict",
                "project_name": "测试",
                "generated_at": "2026-07-29T00:00:00Z",
                "sources": [],
            },
            "scope": {"analysis_scope": "税前算税导入任务"},
            "effective_analysis_contract": {"metric_framework": "指标-2026"},
            "analysis_results": {
                "metrics": {
                    "status": "not_evaluable",
                    "reason": "same_scope_metric_source_conflict",
                    "completion_rate": .751,
                },
                "funnel": block,
                "journey": block,
                "errors": block,
                "segments": block,
            },
            "findings": [],
            "limitations": ["同口径指标来源冲突"],
        }
        html = self.objective_renderer.render(package)
        self.assertIn("当前不展示单一正式值", html)
        self.assertNotIn("75.1%", html)
        self.assertNotIn("<section class=\"cards\">", html)

    def test_objective_html_omits_unrequested_funnel_and_uses_readable_terminal_labels(self):
        block = {"status": "not_requested"}
        package = {
            "run": {
                "artifact_version": "4.0.0",
                "run_id": "oda_test",
                "project_name": "测试",
                "generated_at": "2026-07-29T00:00:00Z",
            },
            "effective_analysis_contract": {"metric_framework": "指标-2026"},
            "analysis_results": {
                "metrics": {"status": "completed", "task_instance_count": 2, "completion_rate": .5, "one_time_completion_rate": .5, "error_task_rate": 0},
                "funnel": block,
                "journey": {
                    "status": "completed",
                    "task_instance_count": 2,
                    "source_semantic_type": "task_summary",
                    "terminal_outcomes": [
                        {"outcome": "success", "task_count": 1, "share": .5},
                        {"outcome": "incomplete_or_tracking_ended", "task_count": 1, "share": .5},
                    ],
                    "stage_nodes": [],
                    "stage_transitions": [],
                },
                "errors": block,
                "segments": block,
            },
            "findings": [{"source_analysis": "journey", "statement": "两类终态各占一半。"}],
            "limitations": [],
            "handoff": {"visualization": {}},
        }
        html = self.objective_renderer.render(package)
        self.assertNotIn("阶段与固定漏斗</h2>", html)
        self.assertIn("未完成或埋点中断", html)
        self.assertIn("两类终态各占一半", html)

    def test_raw_journey_nodes_are_not_named_business_stages(self):
        block = {"status": "not_requested"}
        package = {
            "run": {
                "artifact_version": "4.0.0",
                "run_id": "oda_nodes",
                "project_name": "测试",
                "generated_at": "2026-07-29T00:00:00Z",
                "sources": [],
            },
            "scope": {},
            "effective_analysis_contract": {"metric_framework": "指标-2026"},
            "analysis_results": {
                "metrics": block,
                "funnel": block,
                "journey": {
                    "status": "completed",
                    "task_instance_count": 10,
                    "journey_definition": {"grain": "task_instance"},
                    "terminal_outcomes": [],
                    "stage_nodes": [
                        {"node_id": "打开页面", "label": "打开页面"},
                        {"node_id": "提交", "label": "提交"},
                    ],
                    "stage_transitions": [
                        {
                            "source": "打开页面",
                            "target": "提交",
                            "task_count": 8,
                            "share_of_total_tasks": .8,
                            "share_of_source_outflow": .8,
                        }
                    ],
                },
                "errors": block,
                "segments": block,
            },
            "findings": [],
            "limitations": [],
        }
        html = self.objective_renderer.render(package)
        self.assertIn("主要任务节点流向", html)
        self.assertIn("不把节点解释为业务阶段", html)
        self.assertNotIn("主要业务阶段流向", html)

    def test_objective_journey_report_exposes_interactive_path_facts_without_recalculation(self):
        block = {"status": "not_requested"}
        package = {
            "run": {
                "artifact_version": "4.0.0",
                "run_id": "oda_interactive",
                "project_name": "交互旅程",
                "generated_at": "2026-07-30T00:00:00Z",
                "sources": [],
            },
            "scope": {},
            "effective_analysis_contract": {"metric_framework": "指标-2026"},
            "analysis_results": {
                "metrics": block,
                "funnel": block,
                "journey": {
                    "status": "completed",
                    "task_instance_count": 10,
                    "journey_definition": {"grain": "task_instance"},
                    "terminal_outcomes": [],
                    "stage_nodes": [
                        {"node_id": "填写", "label": "填写", "task_count": 10},
                        {
                            "node_id": "提交", "label": "提交", "task_count": 8,
                            "event_count": 10, "error_task_count": 2,
                            "error_task_share": .25,
                            "duration_seconds": {"p50": 2, "p70": 3, "p90": 6},
                        },
                    ],
                    "stage_transitions": [{
                        "source": "填写", "target": "提交", "task_count": 8,
                        "transition_event_count": 9,
                        "share_of_total_tasks": .8,
                        "share_of_source_outflow": .9,
                        "duration_seconds": {"p50": 3, "p70": 5, "p90": 9},
                    }],
                    "path_patterns": [{
                        "path": ["填写", "提交"], "task_count": 8, "event_count": 18, "share": .8,
                        "duration_seconds": {"p50": 8, "p70": 10, "p90": 15},
                    }],
                    "top_path_patterns": [{
                        "path": ["填写", "提交"], "task_count": 8, "event_count": 18, "share": .8,
                        "duration_seconds": {"p50": 8, "p70": 10, "p90": 15},
                    }],
                    "exit_points": [{"node_id": "提交", "outcome": "exit", "task_count": 2}],
                    "backtrack_and_loop_paths": [{"path": ["填写", "提交"], "task_count": 1}],
                },
                "errors": {
                    "status": "completed",
                    "error_by_step": [{
                        "step": "提交",
                        "error_event_count": 3,
                        "error_types": [{"type": "business_rule", "event_count": 3}],
                    }],
                },
                "segments": block,
            },
            "findings": [],
            "limitations": [],
        }
        html = self.objective_renderer.render(package)
        for marker in (
            "path-filter",
            "最多真实路径",
            "transition_event_count",
            "P50",
            "error_task_count",
            'aria-live="polite"',
            "flow-data-detail",
            "flow-canvas",
            "is-secondary",
            'class="skip-link"',
            "prefers-reduced-motion",
            "@media print",
            ".flow-node.active",
            "nodeEls.forEach",
            "为保证可读性未一次绘制全部候选路径",
            "在全部真实路径中按显示条数筛选",
            "path.event_count",
            "路径节点报错类型",
            "errorTypeFacts",
        ):
            self.assertIn(marker, html)

    def test_objective_journey_rejects_dangling_path_nodes_and_edges(self):
        block = {"status": "not_requested"}
        package = {
            "run": {"artifact_version": "4.0.0", "run_id": "oda_bad_path", "project_name": "fixture", "sources": []},
            "scope": {},
            "effective_analysis_contract": {},
            "analysis_results": {
                "metrics": block,
                "funnel": block,
                "journey": {
                    "status": "completed",
                    "stage_nodes": [{"node_id": "A"}],
                    "stage_transitions": [],
                    "path_patterns": [{"path": ["A", "B"], "task_count": 1, "share": 1.0}],
                    "top_path_patterns": [{"path": ["A", "B"], "task_count": 1, "share": 1.0}],
                },
                "errors": block,
                "segments": block,
            },
            "findings": [],
            "limitations": [],
        }
        with self.assertRaisesRegex(ValueError, "projection_consistency_error"):
            self.objective_renderer.build_spec(package, "objective")

    def test_no_generated_cache_is_part_of_runtime_contract(self):
        runtime_files = {
            path.relative_to(SKILL).as_posix()
            for path in SKILL.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        self.assertFalse(any(path.endswith(".pyc") for path in runtime_files))
        self.assertNotIn(".pytest_cache", runtime_files)

    def test_suite_targets_its_own_skill_directory(self):
        self.assertEqual(SKILL, Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    unittest.main()
