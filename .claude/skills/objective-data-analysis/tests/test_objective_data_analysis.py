from __future__ import annotations

import importlib.util
import csv
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, RefResolver
except ImportError:  # optional test dependency
    Draft202012Validator = None
    RefResolver = None


ROOT = Path(__file__).resolve().parents[4]
SKILL = ROOT / ".claude/skills/objective-data-analysis"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_script(name: str):
    path = SKILL / "scripts" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


def pilot_request(source: Path, intent: str = "report") -> dict:
    return {
        "artifact_type": "objective_analysis_request",
        "artifact_version": "4.0.0",
        "project_name": "差旅报销验收",
        "source_mode": "independent",
        "invocation_context": "independent",
        "analysis_purpose": {
            "purpose_key": "pilot-journey",
            "purpose_label": "试点旅程分析"
        },
        "input_bindings": [],
        "requested_deliverables": [
            {"format": "json", "required": True},
            {"format": "markdown", "required": True}
        ],
        "publication_policy": {
            "level": "formal",
            "update_current_for_purpose": True
        },
        "retention_policy": "retain_result",
        "analysis_intent": intent,
        "input_data_sources": [{"source_id": "pilot-events", "path": str(source), "format": "csv", "role": "event_data"}],
        "requested_analyses": ["metrics", "funnel", "journey", "errors", "segments"],
        "analysis_scope": {"time_window": "2026-06-01", "grain": "task_instance", "scenario_key": "travel-expense"},
        "analysis_contract": {
            "field_mapping": {
                "user_id": "user_id", "enterprise_id": "enterprise_id", "task_instance_id": "task_instance_id",
                "session_id": "session_id", "event_time": "event_time", "event_name": "event_name",
                "journey_step": "journey_step", "error_message": "error_message", "error_code": "error_code"
            },
            "event_mapping": {
                "entry": ["enter"], "submit": ["submit"], "success": ["completed"], "error": ["error"],
                "exit": ["exit"], "draft": ["draft"], "backtrack": ["back"]
            },
            "funnel_steps": ["进入提单", "填写费用", "提交", "完成"],
            "completion_events": ["completed"], "submit_events": ["submit"], "draft_events": ["draft"], "exit_events": ["exit"],
            "minimum_segment_sample": 2,
            "segment_definitions": [
                {"segment_id": "travel", "label": "差旅", "conditions": [{"field": "scenario", "op": "eq", "value": "差旅"}], "basis": {"source": "user_confirmed"}},
                {"segment_id": "daily", "label": "日常", "conditions": [{"field": "scenario", "op": "eq", "value": "日常"}], "basis": {"source": "user_confirmed"}}
            ]
        }
    }


def add_envelope(request: dict, purpose_key: str) -> dict:
    request.update({
        "invocation_context": "independent",
        "analysis_purpose": {
            "purpose_key": purpose_key,
            "purpose_label": purpose_key,
        },
        "input_bindings": [],
        "requested_deliverables": [{"format": "json", "required": True}],
        "publication_policy": {
            "level": "working",
            "update_current_for_purpose": False,
        },
        "retention_policy": "retain_result",
    })
    return request


class ObjectiveDataAnalysisAcceptance(unittest.TestCase):
    def test_unknown_completion_is_not_converted_to_zero(self):
        task = load_script("task_analyzer.py")
        result = task.analyze_tasks(
            [
                {
                    "task_instance_id": "t1",
                    "event_name": "open",
                    "journey_step": "打开",
                    "event_time": "2026-06-01T00:00:00Z",
                }
            ],
            {"funnel_steps": ["打开"], "completion_events": []},
        )
        self.assertEqual(result["metrics"]["status"], "not_evaluable")
        self.assertIsNone(result["metrics"]["completion_count"])
        self.assertIsNone(result["metrics"]["completion_rate"])
        self.assertEqual(result["funnel"]["status"], "completed")

    def test_explicit_all_incomplete_can_report_zero(self):
        task = load_script("task_analyzer.py")
        result = task.analyze_tasks(
            [
                {
                    "task_instance_id": "t1",
                    "completion_flag": False,
                    "event_name": "open",
                    "journey_step": "打开",
                    "event_time": "2026-06-01T00:00:00Z",
                }
            ],
            {"funnel_steps": ["打开"], "completion_events": []},
        )
        self.assertEqual(result["metrics"]["status"], "completed")
        self.assertEqual(result["metrics"]["completion_count"], 0)
        self.assertEqual(result["metrics"]["completion_rate"], 0.0)

    def test_task_summary_requires_completion_for_every_task(self):
        task = load_script("task_analyzer.py")
        result = task.analyze_task_summaries(
            [
                {"task_instance_id": "t1", "completion_flag": True},
                {"task_instance_id": "t2", "completion_flag": ""},
            ],
            {},
        )
        self.assertEqual(result["metrics"]["status"], "not_evaluable")
        self.assertIsNone(result["metrics"]["completion_rate"])

    def test_timestamp_formats_are_equivalent(self):
        adapter = load_script("input_adapter.py")
        iso = adapter.parse_time("2026-06-29T08:31:39Z")
        seconds = adapter.parse_time(1782721899)
        milliseconds = adapter.parse_time(1782721899000)
        self.assertEqual(iso, seconds)
        self.assertEqual(seconds, milliseconds)
        for value in (None, "", 123456789, float("nan"), float("inf")):
            self.assertIsNone(adapter.parse_time(value))

    def test_confirmation_detection_uses_action_and_question_tone(self):
        analyzer = load_script("error_analyzer.py")
        self.assertEqual(analyzer.message_kind("删除该工资算税数据吗?"), "confirmation")
        self.assertEqual(analyzer.message_kind("是否确认删除？"), "confirmation")
        self.assertEqual(analyzer.message_kind("删除失败，请重试"), "actionable_error")
        self.assertEqual(analyzer.message_kind("该数据不存在？"), "unknown")

    def test_source_manifest_does_not_expose_absolute_workspace_path(self):
        adapter = load_script("input_adapter.py")
        source = FIXTURES / "pilot_events.csv"
        _, manifest = adapter.load_source(
            {"path": str(source), "format": "csv", "source_id": "pilot-events"}
        )
        self.assertFalse(Path(manifest["path_ref"]).is_absolute())
        self.assertEqual(
            manifest["path_ref"],
            ".claude/skills/objective-data-analysis/tests/fixtures/pilot_events.csv",
        )

    def test_task_summary_fields_are_consumed_without_event_reconstruction(self):
        runner = load_script("run_objective_analysis.py")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "summary.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "任务ID", "任务名称", "是否完成", "是否一次完成", "总耗时(min)", "报错次数", "旅程路径"
                ])
                writer.writeheader()
                writer.writerow({"任务ID": "t1", "任务名称": "报销提单", "是否完成": "1.0", "是否一次完成": "1.0", "总耗时(min)": "30", "报错次数": "0", "旅程路径": "进入>填写>完成"})
                writer.writerow({"任务ID": "t2", "任务名称": "报销提单", "是否完成": "0.0", "是否一次完成": "0.0", "总耗时(min)": "60", "报错次数": "2", "旅程路径": "进入>填写"})
            request = add_envelope({
                "artifact_type": "objective_analysis_request",
                "artifact_version": "4.0.0",
                "project_name": "任务汇总测试",
                "source_mode": "independent",
                "input_data_sources": [{"source_id": "summary", "path": str(path), "format": "csv"}],
                "requested_analyses": ["metrics", "journey", "errors"],
                "analysis_contract": {
                    "field_mapping": {
                        "task_instance_id": "任务ID",
                        "task_name": "任务名称",
                        "completion_flag": "是否完成",
                        "one_time_completion_flag": "是否一次完成",
                        "task_duration": "总耗时(min)",
                        "task_error_count": "报错次数",
                        "journey_path": "旅程路径"
                    },
                    "journey_path_delimiter": ">"
                }
            }, "task-summary-test")
            package = runner.build_package(request)
            self.assertEqual(package["data_quality"]["data_grain"], "task_summary")
            self.assertEqual(package["analysis_results"]["metrics"]["completion_rate"], 0.5)
            self.assertEqual(package["analysis_results"]["metrics"]["one_time_completion_rate"], 0.5)
            self.assertEqual(package["analysis_results"]["metrics"]["duration_seconds"]["p50"], 2700)
            self.assertEqual(package["analysis_results"]["metrics"]["task_duration_source_unit"], "minutes")
            self.assertEqual(package["analysis_results"]["errors"]["affected_task_count"], 1)
            self.assertEqual(package["analysis_results"]["journey"]["path_patterns"][0]["task_count"], 1)
            self.assertEqual(package["data_quality"]["field_mapping"]["completion_flag"]["confidence"], "explicit")

    def test_missing_error_signal_is_not_zero_error_evidence(self):
        runner = load_script("run_objective_analysis.py")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "summary.csv"
            path.write_text("任务ID,是否完成\nt1,是\n", encoding="utf-8")
            request = add_envelope({
                "artifact_type": "objective_analysis_request",
                "artifact_version": "4.0.0",
                "project_name": "无报错信号测试",
                "source_mode": "independent",
                "input_data_sources": [{"source_id": "summary", "path": str(path), "format": "csv"}],
                "requested_analyses": ["metrics", "errors"],
                "analysis_contract": {"field_mapping": {"task_instance_id": "任务ID", "completion_flag": "是否完成"}}
            }, "missing-error-signal-test")
            package = runner.build_package(request)
            self.assertEqual(package["analysis_results"]["errors"]["status"], "not_evaluable")
            self.assertNotIn("未识别到报错事件", json.dumps(package, ensure_ascii=False))

    def test_bounded_statistical_inference_is_opt_in(self):
        task_analyzer = load_script("task_analyzer.py")
        interval = task_analyzer.wilson_interval(60, 100)
        self.assertIsNotNone(interval)
        self.assertLess(interval["low"], interval["estimate"])
        self.assertGreater(interval["high"], interval["estimate"])
        difference = task_analyzer.proportion_difference_interval(60, 100, 40, 100)
        self.assertIsNotNone(difference)
        self.assertAlmostEqual(difference["estimate"], 0.2)

    def test_skill_has_only_confirmed_runtime_structure(self):
        self.assertFalse((SKILL / "subskills").exists())
        self.assertFalse((SKILL / "requirements.txt").exists())
        self.assertEqual(
            {path.name for path in (SKILL / "scripts").glob("*.py")},
            {"run_objective_analysis.py", "input_adapter.py", "task_analyzer.py", "journey_analyzer.py", "enterprise_state_analyzer.py", "error_analyzer.py", "baseline_analyzer.py", "report_renderer.py", "time_parsing.py"},
        )
        self.assertEqual({path.name for path in (SKILL / "schemas").glob("*.json")}, {"input.schema.json", "output.schema.json"})
        self.assertEqual({path.name for path in (SKILL / "references").glob("*.md")}, {"metric-rules.md", "preprocessing-and-privacy-rules.md", "analysis-rules.md"})

    @unittest.skipIf(Draft202012Validator is None, "jsonschema shared test tool is not installed")
    def test_parent_schemas_and_example_are_valid(self):
        for path in (SKILL / "schemas").glob("*.json"):
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(schema.get("$schema"), "https://json-schema.org/draft/2020-12/schema")
            Draft202012Validator.check_schema(schema)
        request_schema = json.loads((SKILL / "schemas/input.schema.json").read_text(encoding="utf-8"))
        example = json.loads((SKILL / "examples/request.example.json").read_text(encoding="utf-8"))
        resolver = RefResolver(
            base_uri=(SKILL / "schemas/input.schema.json").resolve().as_uri(),
            referrer=request_schema,
        )
        Draft202012Validator(request_schema, resolver=resolver).validate(example)

    def test_skill_doc_follows_uxb_style_and_declares_boundaries(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for heading in ("Step 0 · 运行入口", "角色定义", "总原则", "固定状态顺序", "上下文承接分支", "Knowledge Wiki 消费协议", "Step 1 · 输入理解与合同建立", "Step 6 · 标准交接"):
            self.assertIn(heading, text)
        self.assertIn("不要询问是否启用", text)
        self.assertIn("不要默认询问“字段映射情况”或“是否允许查看 schema/表头”", text)
        self.assertIn("先说出系统当前的理解和建议", text)
        self.assertIn("每张报销单算一次办理", text)
        self.assertIn("按你的建议先分析", text)
        self.assertNotIn("哪一列代表一次任务，哪个事件代表任务完成", text)
        self.assertIn("Independent", text)
        self.assertIn("只在用户明确要求时", text)

    def test_input_adapter_supports_minimal_formats_without_parquet(self):
        adapter = load_script("input_adapter.py")
        self.assertEqual(adapter.SUPPORTED_FORMATS, {"csv", "tsv", "xlsx", "json", "jsonl"})
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            jsonl = directory / "events.jsonl"
            jsonl.write_text('{"event_name":"a","task_instance_id":"1"}\n{"event_name":"b","task_instance_id":"2"}\n', encoding="utf-8")
            rows, manifest = adapter.load_source({"path": str(jsonl), "format": "jsonl", "source_id": "jsonl"})
            self.assertEqual(len(rows), 2)
            self.assertEqual(manifest["read_mode"], "iterative_read")
            try:
                from openpyxl import Workbook
            except ImportError:
                return
            xlsx = directory / "events.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "events"
            sheet.append(["event_name", "task_instance_id"])
            sheet.append(["a", "1"])
            sheet.append(["b", "2"])
            workbook.save(xlsx)
            rows, manifest = adapter.load_source({"path": str(xlsx), "format": "xlsx", "source_id": "xlsx", "sheets": ["events"]})
            self.assertEqual(len(rows), 2)
            self.assertEqual(manifest["read_mode"], "streaming_read_only")
            with self.assertRaisesRegex(ValueError, "unsupported input format"):
                adapter.load_source({"path": str(jsonl), "format": "parquet"})

    def test_preprocessing_deduplicates_and_derives_tasks(self):
        adapter = load_script("input_adapter.py")
        rows = [
            {"user_id": "u", "session_id": "s", "event_time": "2026-01-01T00:00:00Z", "event_name": "enter", "journey_step": "A", "task_instance_id": "", "error_code": "", "error_message": ""},
            {"user_id": "u", "session_id": "s", "event_time": "2026-01-01T00:00:00Z", "event_name": "enter", "journey_step": "A", "task_instance_id": "", "error_code": "", "error_message": ""},
            {"user_id": "u", "session_id": "s", "event_time": "2026-01-01T00:01:00Z", "event_name": "done", "journey_step": "B", "task_instance_id": "", "error_code": "", "error_message": ""}
        ]
        rows, duplicate_count = adapter.deduplicate_rows(rows)
        self.assertEqual(duplicate_count, 1)
        adapter.classify_events(rows, {"event_mapping": {"entry": ["enter"], "success": ["done"]}})
        derived, reliable, reasons = adapter.derive_task_instances(rows)
        self.assertEqual(derived, 2)
        self.assertTrue(reliable)
        self.assertEqual(reasons, [])
        self.assertEqual(len({row["task_instance_id"] for row in rows}), 1)

    def test_repeated_entry_does_not_split_active_task(self):
        adapter = load_script("input_adapter.py")
        rows = [
            {"session_id": "s", "event_time": "2026-01-01T00:00:00Z", "event_name": "enter", "event_class": "entry_event", "task_instance_id": ""},
            {"session_id": "s", "event_time": "2026-01-01T00:01:00Z", "event_name": "enter", "event_class": "entry_event", "task_instance_id": ""},
            {"session_id": "s", "event_time": "2026-01-01T00:02:00Z", "event_name": "done", "event_class": "success_event", "task_instance_id": ""},
        ]
        adapter.derive_task_instances(rows)
        self.assertEqual(len({row["task_instance_id"] for row in rows}), 1)

    def test_dedup_is_source_local_unless_explicitly_enabled(self):
        adapter = load_script("input_adapter.py")
        base = {"user_id": "u", "task_instance_id": "t", "event_time": "2026-01-01", "event_name": "x"}
        rows = [{**base, "_source_ref": "a"}, {**base, "_source_ref": "b"}]
        local, local_duplicates = adapter.deduplicate_rows(rows)
        cross, cross_duplicates = adapter.deduplicate_rows(rows, {"cross_source_deduplication": {"enabled": True, "event_key_fields": ["task_instance_id", "event_name"]}})
        self.assertEqual((len(local), local_duplicates), (2, 0))
        self.assertEqual((len(cross), cross_duplicates), (1, 1))

    def test_business_blueprint_dedup_uses_blueprint_identity(self):
        adapter = load_script("input_adapter.py")
        rows = [
            {
                "_source_ref": "blueprint",
                "_source_semantic_type": "business_blueprint",
                "business_scenario": "差旅报销",
                "journey_name": "提单",
                "registered_node_name": "填写费用",
            },
            {
                "_source_ref": "blueprint",
                "_source_semantic_type": "business_blueprint",
                "business_scenario": "差旅报销",
                "journey_name": "提单",
                "registered_node_name": "提交",
            },
        ]
        kept, duplicate_count = adapter.deduplicate_rows(rows)
        self.assertEqual((len(kept), duplicate_count), (2, 0))
        repeated, duplicate_count = adapter.deduplicate_rows(
            [rows[0], dict(rows[0])]
        )
        self.assertEqual((len(repeated), duplicate_count), (1, 1))
        cross_source_rows = [
            rows[0],
            {**rows[0], "_source_ref": "another-blueprint"},
        ]
        kept, duplicate_count = adapter.deduplicate_rows(
            cross_source_rows,
            {
                "cross_source_deduplication": {
                    "enabled": True,
                    "event_key_fields": ["task_instance_id", "event_name"],
                }
            },
        )
        self.assertEqual((len(kept), duplicate_count), (2, 0))

    def test_metric_contract_removes_targets_and_legacy_rules(self):
        runner = load_script("run_objective_analysis.py")
        raw = {"metric_id": "m1", "target_value": 95, "目标参考值": 90, "nested": {"health_value": 80, "formula": "a/b"}, "异动指标说明": "legacy"}
        clean = runner.sanitize_metric_definition(raw)
        encoded = json.dumps(clean, ensure_ascii=False)
        for forbidden in ("target_value", "目标参考值", "health_value", "异动指标说明"):
            self.assertNotIn(forbidden, encoded)
        self.assertEqual(clean["nested"]["formula"], "a/b")

    def test_controlled_segments_require_business_rules_and_reconcile(self):
        task = load_script("task_analyzer.py")
        self.assertEqual(task.analyze_segments([], [])["reason"], "confirmed_business_segment_definitions_missing")
        rows = [
            {"task_instance_id": "1", "role": "operator", "event_class": "success_event"},
            {"task_instance_id": "2", "role": "reviewer", "event_class": "exit_event"},
            {"task_instance_id": "3", "role": "", "event_class": "success_event"}
        ]
        definitions = [
            {"segment_id": "operator", "label": "操作员", "conditions": [{"field": "role", "op": "eq", "value": "operator"}], "basis": {"source": "user_confirmed"}},
            {"segment_id": "reviewer", "label": "审核员", "conditions": [{"field": "role", "op": "eq", "value": "reviewer"}], "basis": {"source": "user_confirmed"}}
        ]
        result = task.analyze_segments(rows, definitions, 2)
        self.assertTrue(result["reconciliation"]["balanced"])
        self.assertTrue(result["mutually_exclusive"])
        self.assertIn("UNKNOWN", {item["label"] for item in result["segments"]})

        overlapping = definitions + [{"segment_id": "all", "label": "全部", "conditions": [{"field": "role", "op": "not_empty"}], "basis": {"source": "user_confirmed"}}]
        blocked = task.analyze_segments(rows, overlapping, 2)
        self.assertEqual(blocked["status"], "not_evaluable")
        self.assertEqual(blocked["reason"], "segment_rules_not_mutually_exclusive")

    def test_step_errors_are_attributed_to_actual_error_step(self):
        task = load_script("task_analyzer.py")
        rows = [
            {"task_instance_id": "1", "event_time": "2026-01-01T00:00:00Z", "event_name": "a", "event_class": "step_event", "journey_step": "A"},
            {"task_instance_id": "1", "event_time": "2026-01-01T00:01:00Z", "event_name": "err", "event_class": "error_event", "journey_step": "B"},
            {"task_instance_id": "1", "event_time": "2026-01-01T00:02:00Z", "event_name": "done", "event_class": "success_event", "journey_step": "C"},
        ]
        result = task.analyze_tasks(rows, {"funnel_steps": ["A", "B", "C"], "completion_events": ["done"]})
        counts = {item["step"]: item["error_task_count"] for item in result["funnel"]["steps"]}
        self.assertEqual(counts, {"A": 0, "B": 1, "C": 0})

    def test_feature_eligibility_is_explicit_and_not_inferred(self):
        task = load_script("task_analyzer.py")
        rows = [
            {"user_id": "u1", "event_name": "eligible", "role": "operator"},
            {"user_id": "u1", "event_name": "enter", "role": "operator"},
            {"user_id": "u1", "event_name": "use", "role": "operator"},
            {"user_id": "u2", "event_name": "enter", "role": "viewer"},
        ]
        result = task.analyze_feature_usage(rows, {"subject_col": "user_id", "entry_event": "enter", "usage_event": "use", "eligibility": {"event": "eligible"}})
        eligible = next(item for item in result["usage_metrics"] if item["metric_id"] == "eligible_to_usage")
        self.assertEqual((eligible["numerator"], eligible["denominator"], eligible["value"]), (1, 1, 1.0))

    def test_baseline_excludes_current_and_refuses_insufficient_history(self):
        analyzer = load_script("baseline_analyzer.py")
        import csv
        with (FIXTURES / "baseline_series.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        result = analyzer.analyze_baseline(rows, {"period_col": "period", "metric_col": "metric", "task_identity": "fixture-task", "current_periods": 1, "minimum_history": 3, "method": "same_period", "season_col": "season"})
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["definition"]["current_window_strictly_excluded"])
        self.assertEqual(result["comparisons"][0]["current_value"], 60.0)
        candidate = result["candidate"]
        self.assertEqual("proposed", candidate["lifecycle_status"])
        self.assertEqual("pending", candidate["review_status"])
        self.assertEqual("metric", candidate["metric_contract_ref"])
        self.assertIn("baseline_values", candidate)
        self.assertNotIn("baseline_candidate_id", candidate)
        insufficient = analyzer.analyze_baseline(rows[:4], {"period_col": "period", "metric_col": "metric", "task_identity": "fixture-task", "current_periods": 1, "minimum_history": 8})
        self.assertEqual(insufficient["reason"], "insufficient_history")

    def test_baseline_groups_unique_periods_and_requires_explicit_aggregation(self):
        analyzer = load_script("baseline_analyzer.py")
        rows = [{"period": period, "metric": value} for period, value in [("2026-01", 10), ("2026-01", 20), ("2026-02", 30), ("2026-02", 40), ("2026-03", 50), ("2026-03", 60)]]
        blocked = analyzer.analyze_baseline(rows, {"period_col": "period", "metric_col": "metric", "task_identity": "fixture-task", "minimum_history": 2})
        self.assertTrue(blocked["reason"].startswith("period_aggregation_required"))
        result = analyzer.analyze_baseline(rows, {"period_col": "period", "metric_col": "metric", "task_identity": "fixture-task", "period_aggregation": "mean", "minimum_history": 2})
        self.assertEqual(result["definition"]["history_window"]["end"], "2026-02")
        self.assertEqual(result["definition"]["current_window"]["start"], "2026-03")
        self.assertEqual(result["comparisons"][0]["current_value"], 55.0)

    def test_error_redaction_covers_extended_sensitive_parameters(self):
        analyzer = load_script("error_analyzer.py")
        raw = "failed token=abc cookie=session123 user@example.com 13800138000 task_id=998877 https://x.test/a?q=secret /Users/name/private/file.txt"
        label = analyzer.canonical_safe_label(raw)
        for secret in ("abc", "session123", "user@example.com", "13800138000", "998877", "q=secret", "/Users/name/private/file.txt"):
            self.assertNotIn(secret, label)

        uncertain = analyzer.analyze_rows([{"task_instance_id": "t", "event_class": "error_event", "error_message": "opaque ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"}])
        self.assertEqual(uncertain["top_error_patterns"][0]["redaction_state"], "uncertain")
        self.assertEqual(uncertain["top_error_patterns"][0]["canonical_safe_label"], "unclassified_redacted_error")

    def test_real_business_error_formats_are_redacted_and_error_detail_role_is_kept(self):
        adapter = load_script("input_adapter.py")
        analyzer = load_script("error_analyzer.py")
        samples = {
            "发票号码I--26447000000343589628已被使用": "发票号码=<ID>已被使用",
            "预付款单ID=FY202607270001，金额=1234.56，发生日期=2026-07-27，地点=上海": None,
            "INFO1: 提交失败;INFO4: request_id=998877665544;INFO5: user=张三": None,
        }
        for raw, expected in samples.items():
            label = analyzer.canonical_safe_label(raw)
            if expected is not None:
                self.assertEqual(expected, label)
            for secret in ("26447000000343589628", "FY202607270001", "1234.56", "2026-07-27", "上海", "998877665544", "张三"):
                self.assertNotIn(secret, label)
        rows = [{"_source_role": "error_detail", "task_instance_id": "t1"}]
        adapter.classify_events(rows, {})
        self.assertEqual("error_event", rows[0]["event_class"])

    def test_zero_errors_is_a_completed_observation(self):
        analyzer = load_script("error_analyzer.py")
        result = analyzer.analyze_rows([{"task_instance_id": "t", "event_class": "success_event"}])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["error_event_count"], 0)

    def test_independent_mode_rejects_upstream_contract(self):
        runner = load_script("run_objective_analysis.py")
        request = pilot_request(FIXTURES / "pilot_events.csv")
        request["upstream_analysis_contract"] = {"completion_events": ["other"]}
        with self.assertRaisesRegex(ValueError, "independent mode"):
            runner.build_package(request)

    def test_end_to_end_unified_output_report_and_explicit_visualization(self):
        script = SKILL / "scripts/run_objective_analysis.py"
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            request_path = directory / "request.json"
            output_root = directory / "spark-output"
            request_path.write_text(json.dumps(pilot_request(FIXTURES / "pilot_events.csv"), ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run([sys.executable, str(script), "--request", str(request_path), "--output-root", str(output_root)], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            pointer = json.loads((output_root / "context/current/objective.json").read_text(encoding="utf-8"))
            ref = pointer["current_by_purpose"][0]["artifact_instance_ref"]
            package_path = directory / ref["artifact_path"]
            package = json.loads(package_path.read_text(encoding="utf-8"))
            if Draft202012Validator is not None:
                schema = json.loads((SKILL / "schemas/output.schema.json").read_text(encoding="utf-8"))
                resolver = RefResolver(
                    base_uri=(SKILL / "schemas/output.schema.json").resolve().as_uri(),
                    referrer=schema,
                )
                Draft202012Validator(schema, resolver=resolver).validate(package)
            self.assertEqual(set(package), {"run", "scope", "effective_analysis_contract", "data_quality", "analysis_results", "findings", "evidence_items", "limitations", "publication", "delivery", "handoff"})
            self.assertEqual(package["run"]["artifact_version"], "4.0.0")
            self.assertNotIn("baseline", package["handoff"])
            self.assertTrue(package["handoff"]["payload_refs"])
            for payload_ref in package["handoff"]["payload_refs"]:
                index = int(payload_ref.rsplit("/", 1)[1])
                self.assertIsInstance(package["evidence_items"][index], dict)
            self.assertEqual(package["handoff"]["analysis_result_refs"]["baseline"], "#/analysis_results/baseline")
            metrics = package["analysis_results"]["metrics"]
            self.assertEqual(metrics["task_instance_count"], 6)
            self.assertEqual(metrics["completion_count"], 3)
            self.assertAlmostEqual(metrics["completion_rate"], .5)
            self.assertEqual(metrics["one_time_completion_count"], 2)
            self.assertEqual(metrics["error_task_count"], 1)
            journey = package["analysis_results"]["journey"]
            self.assertTrue(journey["reconciliation"]["balanced"])
            self.assertEqual(sum(item["task_count"] for item in journey["terminal_outcomes"]), 6)
            errors = json.dumps(package["analysis_results"]["errors"], ensure_ascii=False)
            self.assertNotIn("secret123", errors)
            self.assertNotIn("user@example.com", errors)
            segments = {item["label"]: item for item in package["analysis_results"]["segments"]["segments"]}
            self.assertAlmostEqual(segments["差旅"]["completion_rate"], 2 / 3)
            self.assertAlmostEqual(segments["日常"]["completion_rate"], 1 / 3)
            report = package_path.with_suffix(".md").read_text(encoding="utf-8")
            self.assertNotIn(package["run"]["run_id"], report)
            self.assertIn("运行标识、对象 ID 和数据指纹保留在结构化结果中", report)
            for section in ("执行摘要", "预处理与数据质量", "阶段与固定漏斗", "终态、实际路径与桑基数据", "报错与报错后行为", "限制与下游交接"):
                self.assertIn(section, report)
            self.assertFalse((output_root / "data-visualization/objective-analysis-report.html").exists())
            self.assertFalse((output_root / "context/objective-analysis-profile-registry.json").exists())
            self.assertFalse((output_root / "context/analysis-run-log.jsonl").exists())
            self.assertFalse((output_root / "run").exists())
            self.assertEqual("published", package["publication"]["status"])
            self.assertEqual("completed", package["delivery"]["status"])

    def test_formal_publication_rejects_external_source_without_portable_reference(self):
        runner = load_script("run_objective_analysis.py")
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            directory = Path(directory)
            source = directory / "external.csv"
            source.write_text(
                "task_instance_id,event_name,completion_flag\nt-1,completed,true\n",
                encoding="utf-8",
            )
            request = pilot_request(source)
            request_path = directory / "request.json"
            request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "external_source_reference_unresolved") as caught:
                runner.run(request_path, directory / "workspace/spark-output")
            self.assertNotIn(str(source), str(caught.exception))
            self.assertFalse((directory / "workspace/spark-output/context/current/objective.json").exists())

    def test_formal_publication_accepts_workspace_relative_source_reference(self):
        runner = load_script("run_objective_analysis.py")
        request = pilot_request(FIXTURES / "pilot_events.csv")
        runner.validate_formal_source_references(request)

    def test_formal_publication_rejects_mixed_external_sources(self):
        runner = load_script("run_objective_analysis.py")
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            directory = Path(directory)
            external = directory / "optional-external.csv"
            external.write_text(
                "task_instance_id,event_name,completion_flag\nt-1,completed,true\n",
                encoding="utf-8",
            )
            request = pilot_request(FIXTURES / "pilot_events.csv")
            request["input_data_sources"].append({
                "source_id": "optional-external",
                "path": str(external),
                "format": "csv",
                "role": "event_data",
                "critical": False,
            })
            with self.assertRaisesRegex(ValueError, "复制到受控 workspace") as caught:
                runner.validate_formal_source_references(request)
            self.assertNotIn(str(external), str(caught.exception))

    def test_working_external_source_does_not_update_current(self):
        runner = load_script("run_objective_analysis.py")
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            directory = Path(directory)
            source = directory / "external.csv"
            source.write_text(
                "task_instance_id,event_name,completion_flag\nt-1,completed,true\n",
                encoding="utf-8",
            )
            request = pilot_request(source, intent="focused")
            request["requested_deliverables"] = [{"format": "json", "required": True}]
            request["publication_policy"] = {
                "level": "working",
                "update_current_for_purpose": False,
            }
            request_path = directory / "request.json"
            request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
            package = runner.run(request_path, directory / "workspace/spark-output")
            self.assertEqual("published", package["publication"]["status"])
            self.assertFalse((directory / "workspace/spark-output/context/current/objective.json").exists())

    def test_optional_source_failure_degrades_without_blocking_readable_sources(self):
        runner = load_script("run_objective_analysis.py")
        request = pilot_request(FIXTURES / "pilot_events.csv", intent="focused")
        request["input_data_sources"].append({"source_id": "optional-xlsx", "path": "/missing/optional.xlsx", "format": "xlsx", "critical": False})
        package = runner.build_package(request)
        self.assertEqual(package["run"]["status"], "completed_with_caveats")
        self.assertEqual(package["data_quality"]["source_failures"][0]["source_id"], "optional-xlsx")

    def test_pending_rules_block_formal_evidence(self):
        runner = load_script("run_objective_analysis.py")
        request = pilot_request(FIXTURES / "pilot_events.csv", intent="focused")
        request["business_rule_sources"] = [{"source": "analyst_proposed", "confirmation_status": "analyst_proposed_pending_confirmation"}]
        package = runner.build_package(request)
        self.assertTrue(package["findings"])
        self.assertFalse(package["evidence_items"])
        self.assertTrue(any("待确认" in value for value in package["limitations"]))

    def test_unrelated_mapping_issue_only_limits_affected_analysis(self):
        runner = load_script("run_objective_analysis.py")
        request = pilot_request(FIXTURES / "pilot_events.csv", intent="focused")
        request["analysis_contract"]["field_mapping"]["enterprise_id"] = "missing_enterprise_column"
        request["business_thresholds"] = [{"metric_id": "completion_rate", "value": 0.8}]
        package = runner.build_package(request)
        self.assertIn("pilot-events:enterprise_id", package["data_quality"]["invalid_explicit_mappings"])
        self.assertTrue(package["evidence_items"])
        self.assertTrue(any("业务阈值" in value for value in package["limitations"]))

        request["analysis_contract"]["field_mapping"]["event_name"] = "missing_event_column"
        blocked = runner.build_package(request)
        affected = {item["finding_id"] for item in blocked["findings"] if item["source_analysis"] in {"metrics", "funnel", "errors"}}
        self.assertFalse(any(item["finding_ref"] in affected for item in blocked["evidence_items"]))

    def test_blueprint_local_mapping_issue_does_not_block_event_evidence(self):
        runner = load_script("run_objective_analysis.py")
        with tempfile.TemporaryDirectory() as directory:
            blueprint = Path(directory) / "blueprint.csv"
            blueprint.write_text(
                "业务场景,旅程名称,节点名称\n差旅报销,提单,填写费用\n差旅报销,提单,提交\n",
                encoding="utf-8",
            )
            request = pilot_request(FIXTURES / "pilot_events.csv", intent="focused")
            event_mapping = request["analysis_contract"].pop("field_mapping")
            request["input_data_sources"][0]["semantic_type"] = "general_event_log"
            request["input_data_sources"][0]["field_mapping"] = event_mapping
            request["input_data_sources"].append({
                "source_id": "business-blueprint",
                "path": str(blueprint),
                "format": "csv",
                "semantic_type": "business_blueprint",
                "blueprint_authority": "reference_only",
                "field_mapping": {
                    "business_scenario": "业务场景",
                    "journey_name": "旅程名称",
                    "registered_node_name": "节点名称",
                },
            })
            control = runner.build_package(request)
            request["input_data_sources"][1]["field_mapping"][
                "task_instance_id"
            ] = "不存在的任务字段"
            affected = runner.build_package(request)
        self.assertTrue(control["evidence_items"])
        self.assertEqual(
            len(affected["evidence_items"]), len(control["evidence_items"])
        )
        self.assertNotEqual(affected["handoff"]["handoff_status"], "blocked")
        self.assertIn(
            "business-blueprint:task_instance_id",
            affected["data_quality"]["invalid_explicit_mappings"],
        )

    def test_analysis_scope_does_not_delete_reports_or_replace_other_purpose(self):
        runner = load_script("run_objective_analysis.py")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            output_root = directory / "spark-output"
            request_path = directory / "request.json"
            request = pilot_request(FIXTURES / "pilot_events.csv")
            request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
            runner.run(request_path, output_root)
            pointer_path = output_root / "context/current/objective.json"
            before = pointer_path.read_text(encoding="utf-8")
            request["analysis_intent"] = "focused"
            request["analysis_purpose"] = {
                "purpose_key": "focused-errors",
                "purpose_label": "聚焦报错分析"
            }
            request["requested_analyses"] = ["errors"]
            request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
            runner.run(request_path, output_root)
            successful = pointer_path.read_text(encoding="utf-8")
            pointer = json.loads(successful)
            self.assertEqual(
                {"pilot-journey", "focused-errors"},
                {item["purpose_key"] for item in pointer["current_by_purpose"]},
            )
            for item in pointer["current_by_purpose"]:
                result = directory / item["artifact_instance_ref"]["artifact_path"]
                self.assertTrue(result.is_file())
                self.assertTrue(result.with_suffix(".md").is_file())
            request["input_data_sources"][0]["path"] = str(FIXTURES / "missing.csv")
            request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "no readable input data sources"):
                runner.run(request_path, output_root)
            self.assertEqual(pointer_path.read_text(encoding="utf-8"), successful)
            self.assertNotEqual(before, successful)
            self.assertFalse((output_root / "context/analysis-run-log.jsonl").exists())

    def test_generated_preview_keeps_internal_evidence_chain_hidden(self):
        subprocess.run(["node", str(ROOT / "shared-workflow/generate-progress-preview.js")], cwd=ROOT, check=True, capture_output=True, text=True)
        html = (ROOT / "spark-output/progress-preview.html").read_text(encoding="utf-8")
        match = re.search(r"window\.__PREVIEW_STATE__ = (.*?);</script>", html, re.S)
        self.assertIsNotNone(match)
        state = json.loads(match.group(1))
        ids = [skill["id"] for section in state["sections"] for skill in section["skills"]]
        self.assertNotIn("evidence-govern", ids)
        self.assertNotIn("evidence-normalize", json.dumps(state, ensure_ascii=False))
        self.assertNotIn("evidence-triangulate", json.dumps(state, ensure_ascii=False))

    def test_duration_column_alone_does_not_misclassify_event_data_as_task_summary(self):
        adapter = load_script("input_adapter.py")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            path.write_text(
                "xft_taskId,xft_time,xft_eventID,xft_duration\n"
                "t1,2026-06-01T10:00:00,start,100\n",
                encoding="utf-8",
            )
            _, quality, _ = adapter.preprocess(
                [{
                    "source_id": "events",
                    "path": str(path),
                    "format": "csv",
                    "field_mapping": {
                        "task_instance_id": "xft_taskId",
                        "event_time": "xft_time",
                        "event_name": "xft_eventID",
                        "task_duration": "xft_duration",
                    },
                }],
                {"_requested_analyses": ["metrics"]},
            )
            self.assertEqual("event", quality["data_grain"])

    def test_message_info_rule_controls_error_classification_and_signature(self):
        runner = load_script("run_objective_analysis.py")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            path.write_text(
                "xft_taskId,xft_time,xft_eventID,xft_type,xft_info,xft_info3,xft_info4\n"
                "t1,2026-06-01T10:00:00,click-a,messageInfo,提交失败,E100,toast\n"
                "t2,2026-06-01T10:01:00,click-b,messageInfo,提交失败,E100,toast\n"
                "t3,2026-06-01T10:02:00,click-c,requestTime,提交失败,E100,toast\n"
                "t4,2026-06-01T10:03:00,click-d,messageInfo,提交失败,E100,alert\n",
                encoding="utf-8",
            )
            request = add_envelope({
                "artifact_type": "objective_analysis_request",
                "artifact_version": "4.0.0",
                "project_name": "报错规则测试",
                "source_mode": "independent",
                "input_data_sources": [{
                    "source_id": "front-log",
                    "path": str(path),
                    "format": "csv",
                    "role": "event_log",
                    "data_grain": "event",
                    "field_mapping": {
                        "task_instance_id": "xft_taskId",
                        "event_time": "xft_time",
                        "event_name": "xft_eventID",
                        "error_message": "xft_info",
                        "error_code": "xft_info3",
                        "error_presentation": "xft_info4"
                    },
                    "event_classification_rules": [{
                        "event_class": "error_event",
                        "conditions": [{"field": "xft_type", "op": "eq", "value": "messageInfo"}]
                    }]
                }],
                "requested_analyses": ["errors"],
                "analysis_contract": {}
            }, "error-rule-test")
            package = runner.build_package(request)
            errors = package["analysis_results"]["errors"]
            self.assertEqual(3, errors["error_event_count"])
            self.assertEqual(2, errors["unique_error_pattern_count"])
            self.assertTrue(package["data_quality"]["error_classification_reliable"])

    def test_xft_header_candidates_and_journey_node_fallback_follow_confirmed_semantics(self):
        adapter = load_script("input_adapter.py")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "xft.csv"
            path.write_text(
                "xft_taskId,xft_time,Time,ServerTime,xft_login_id,LoginID,"
                "xft_prj_code,xft_prj_name,xft_eventID,xft_cust_id,xft_duration,"
                "xft_taskNodeName,xft_info,xft_info3,xft_info4\n"
                "t1,2026-06-01T10:00:00,wrong,wrong,u1,wrong,e1,企业甲,"
                "event-start,custom-a,250,,失败,E1,toast\n",
                encoding="utf-8",
            )
            rows, quality, _ = adapter.preprocess(
                [{"source_id": "xft", "path": str(path), "format": "csv", "data_grain": "event"}],
                {"_requested_analyses": ["journey"]},
            )
            mapping = quality["field_mapping"]
            self.assertEqual("xft_time", mapping["event_time"]["source_field"])
            self.assertEqual("xft_login_id", mapping["user_id"]["source_field"])
            self.assertEqual("xft_prj_code", mapping["enterprise_id"]["source_field"])
            self.assertEqual("xft_prj_name", mapping["enterprise_name"]["source_field"])
            self.assertEqual("xft_eventID", mapping["event_name"]["source_field"])
            self.assertEqual("xft_cust_id", mapping["event_custom_id"]["source_field"])
            self.assertEqual("xft_duration", mapping["event_duration_ms"]["source_field"])
            self.assertEqual("event-start", rows[0]["journey_step"])

    def test_enterprise_identifier_is_not_removed_from_safe_error_text(self):
        error = load_script("error_analyzer.py")
        label, state, _ = error.redact_message("enterprise_id=ent-001 提交失败")
        self.assertEqual("safe", state)
        self.assertIn("enterprise_id=ent-001", label)

    def test_source_semantics_keep_error_context_out_of_full_journey(self):
        adapter = load_script("input_adapter.py")
        runner = load_script("run_objective_analysis.py")
        with tempfile.TemporaryDirectory() as directory:
            summary = Path(directory) / "summary.csv"
            error = Path(directory) / "errors.csv"
            summary.write_text("任务ID,是否完成,旅程路径,总耗时(min)\nt1,是,A>B>C,10\nt2,否,A>B,20\n", encoding="utf-8")
            error.write_text("任务ID,报错信息,节点\nt2,提交失败,B\n", encoding="utf-8")
            rows, quality, _ = adapter.preprocess([
                {"source_id": "summary", "path": str(summary), "format": "csv"},
                {"source_id": "errors", "path": str(error), "format": "csv"},
            ], {"_requested_analyses": ["journey", "errors"]})
            self.assertEqual("task_summary", quality["source_semantic_types"]["summary"])
            self.assertEqual("error_context_detail", quality["source_semantic_types"]["errors"])
            self.assertEqual(
                {"task_summary", "error_context_detail"},
                {row["_source_semantic_type"] for row in rows},
            )
            request = add_envelope({
                "artifact_type": "objective_analysis_request",
                "artifact_version": "4.0.0",
                "project_name": "混合旅程来源",
                "source_mode": "independent",
                "input_data_sources": [
                    {"source_id": "summary", "path": str(summary), "format": "csv"},
                    {"source_id": "errors", "path": str(error), "format": "csv"},
                ],
                "requested_analyses": ["metrics", "journey", "errors"],
                "analysis_contract": {},
            }, "mixed-journey-source")
            package = runner.build_package(request)
            journey_result = package["analysis_results"]["journey"]
            self.assertEqual(2, journey_result["task_instance_count"])
            self.assertEqual("task_summary", journey_result["source_semantic_type"])
            self.assertEqual(
                "observed_structural_separator",
                package["effective_analysis_contract"]["journey_path_delimiter_basis"],
            )
            self.assertEqual(
                "mapped_source_field_unit",
                package["effective_analysis_contract"]["task_duration_unit_basis"],
            )
            self.assertEqual(
                600,
                journey_result["top_path_patterns"][0]["duration_seconds"]["p50"],
            )
            self.assertNotEqual(
                {"error_without_observed_followup"},
                {item["outcome"] for item in journey_result["terminal_outcomes"]},
            )
            self.assertEqual(1, journey_result["error_cohort_paths"]["with_error"][0]["task_count"])
            self.assertEqual(1, journey_result["error_cohort_paths"]["without_error"][0]["task_count"])

    def test_task_summary_journey_and_segment_completion_share_the_same_state(self):
        journey = load_script("journey_analyzer.py")
        task = load_script("task_analyzer.py")
        rows = [
            {"task_instance_id": "t1", "journey_path": "A>B>C", "completion_flag": "是", "group": "甲", "event_class": "noise_event"},
            {"task_instance_id": "t2", "journey_path": "A>B", "completion_flag": "否", "group": "乙", "event_class": "noise_event"},
        ]
        result = journey.analyze_task_summaries(rows, delimiter=">")
        self.assertTrue(result["reconciliation"]["balanced"])
        self.assertEqual("task_summary", result["source_semantic_type"])
        outcomes = {item["outcome"]: item["task_count"] for item in result["terminal_outcomes"]}
        self.assertEqual(1, outcomes["success"])
        self.assertEqual(1, outcomes["incomplete_or_tracking_ended"])
        segments = task.analyze_segments(rows, [
            {"segment_id": "a", "label": "甲", "conditions": [{"field": "group", "op": "eq", "value": "甲"}], "basis": {"source": "user_confirmed"}},
            {"segment_id": "b", "label": "乙", "conditions": [{"field": "group", "op": "eq", "value": "乙"}], "basis": {"source": "user_confirmed"}},
        ], minimum_sample=1)
        self.assertTrue(segments["reconciliation"]["balanced"])
        self.assertEqual(1, segments["reconciliation"]["segment_completion_count"])
        self.assertTrue(segments["comparison_evaluable"])

    def test_same_scope_metric_conflict_fails_closed_and_other_scope_does_not(self):
        runner = load_script("run_objective_analysis.py")
        calculated = {"status": "completed", "completion_rate": .75, "one_time_completion_rate": .63, "limitations": []}
        aggregate_rows = [{
            "_source_ref": "official",
            "task_name": "税前算税",
            "aggregate_completion_rate": .733,
            "aggregate_one_time_completion_rate": .608,
        }]
        manifests = [
            {"source_id": "detail", "semantic_type": "task_summary", "declared_scope": {"scope_fingerprint": "same"}},
            {"source_id": "official", "semantic_type": "aggregate_metric_summary", "metric_authority": "official", "declared_scope": {"scope_fingerprint": "same"}},
        ]
        conflict = runner._reconcile_metric_sources(dict(calculated), aggregate_rows, manifests, .0001)
        self.assertEqual("not_evaluable", conflict["status"])
        self.assertTrue(conflict["source_reconciliation"]["source_conflict"])
        manifests[1]["declared_scope"]["scope_fingerprint"] = "other"
        separate = runner._reconcile_metric_sources(dict(calculated), aggregate_rows, manifests, .0001)
        self.assertFalse(separate["source_reconciliation"]["source_conflict"])
        self.assertNotIn("headline_metrics", separate)
        self.assertEqual(.75, separate["completion_rate"])

    def test_error_analysis_excludes_confirmations_and_reports_repetition_density(self):
        error = load_script("error_analyzer.py")
        rows = [
            {"task_instance_id": "t1", "event_class": "error_event", "error_message": "账号格式不能少于8位", "journey_step": "提交", "event_time": f"2026-06-01T10:00:{index:02d}"}
            for index in range(5)
        ] + [
            {"task_instance_id": "t2", "event_class": "error_event", "error_message": "操作确认"},
            {"task_instance_id": "t3", "event_class": "error_event", "error_message": "恢复成功"},
        ]
        result = error.analyze_rows(rows)
        self.assertEqual(2, result["excluded_non_error_event_count"])
        self.assertEqual(5, result["error_event_count"])
        self.assertEqual(1, result["top_error_patterns"][0]["affected_task_count"])
        self.assertEqual(5, result["top_error_patterns"][0]["max_events_in_60_seconds_same_task"])
        self.assertEqual("提交", result["error_by_step"][0]["step"])
        self.assertEqual(
            [{"type": "form_validation", "event_count": 5}],
            result["error_by_step"][0]["error_types"],
        )

    def test_explicit_dimension_lookup_joins_by_enterprise_and_rejects_conflicts(self):
        adapter = load_script("input_adapter.py")
        rows = [
            {"_source_ref": "tasks", "_source_semantic_type": "task_summary", "enterprise_id": "e1"},
            {"_source_ref": "tasks", "_source_semantic_type": "task_summary", "enterprise_id": "e2"},
            {"_source_ref": "enterprise-types", "_source_semantic_type": "dimension_lookup", "enterprise_id": "e1", "企业类型": "深度月活"},
        ]
        result = adapter.apply_dimension_joins(rows, [{
            "lookup_source_id": "enterprise-types",
            "target_key": "enterprise_id",
            "lookup_key": "enterprise_id",
            "value_fields": {"enterprise_group": "企业类型"},
            "minimum_coverage": .5,
        }])
        self.assertEqual("深度月活", rows[0]["enterprise_group"])
        self.assertNotIn("enterprise_group", rows[1])
        self.assertEqual(.5, result[0]["coverage"])
        rows.append({"_source_ref": "enterprise-types", "_source_semantic_type": "dimension_lookup", "enterprise_id": "e1", "企业类型": "月活"})
        with self.assertRaisesRegex(ValueError, "conflicting duplicate keys"):
            adapter.apply_dimension_joins(rows, [{
                "lookup_source_id": "enterprise-types",
                "value_fields": {"enterprise_group": "企业类型"},
            }])

    def test_journey_node_duration_quantiles_are_preserved(self):
        journey = load_script("journey_analyzer.py")
        rows = [
            {"task_instance_id": "t1", "journey_step": "填写", "event_time": "2026-06-01T10:00:00", "journey_step_duration_seconds": 10, "event_class": "step_event"},
            {"task_instance_id": "t2", "journey_step": "填写", "event_time": "2026-06-01T10:01:00", "journey_step_duration_seconds": 30, "event_class": "step_event"},
        ]
        result = journey.analyze_rows(rows)
        node = result["stage_nodes"][0]
        self.assertEqual(20, node["duration_seconds"]["p50"])
        self.assertEqual(28, node["duration_seconds"]["p90"])

    def test_registered_nodes_without_order_are_not_promoted_to_formal_blueprint(self):
        journey = load_script("journey_analyzer.py")
        compiled = journey.compile_business_blueprints([
            {
                "business_scenario": "报销",
                "journey_name": "提单",
                "registered_node_name": "填写",
            },
            {
                "business_scenario": "报销",
                "journey_name": "提单",
                "registered_node_name": "提交",
            },
        ])
        self.assertEqual("registered_nodes_only", compiled["definition_status"])
        self.assertEqual([], compiled["formal_blueprints"])
        self.assertEqual("unavailable", compiled["definitions"][0]["order_status"])

    def test_formal_blueprint_requires_explicit_unique_order_and_authority(self):
        journey = load_script("journey_analyzer.py")
        compiled = journey.compile_business_blueprints([
            {
                "business_scenario": "报销",
                "journey_name": "提单",
                "registered_node_name": "提交",
                "registered_node_order": 2,
                "_blueprint_authority": "business_confirmed",
            },
            {
                "business_scenario": "报销",
                "journey_name": "提单",
                "registered_node_name": "填写",
                "registered_node_order": 1,
                "_blueprint_authority": "business_confirmed",
            },
        ])
        self.assertEqual("formal", compiled["definition_status"])
        self.assertEqual(
            ["填写", "提交"],
            compiled["formal_blueprints"][0]["required_steps"],
        )

    def test_journey_emits_full_paths_exits_and_multi_duration_facts(self):
        journey = load_script("journey_analyzer.py")
        rows = []
        for index in range(25):
            rows.extend([
                {
                    "task_instance_id": f"t{index}",
                    "journey_step": "进入",
                    "event_time": f"2026-06-01T10:{index:02d}:00",
                    "event_class": "step_event",
                },
                {
                    "task_instance_id": f"t{index}",
                    "journey_step": f"节点{index}",
                    "event_time": f"2026-06-01T10:{index:02d}:10",
                    "event_class": "exit_event",
                },
            ])
        result = journey.analyze_rows(rows)
        self.assertEqual(25, len(result["path_patterns"]))
        self.assertEqual(20, len(result["top_path_patterns"]))
        self.assertEqual(2, result["path_patterns"][0]["event_count"])
        self.assertEqual(25, sum(item["task_count"] for item in result["exit_points"]))
        transition = result["stage_transitions"][0]
        self.assertEqual(10, transition["duration_seconds"]["p50"])
        self.assertIn("p70", transition["duration_seconds"])
        self.assertIn("p90", transition["duration_seconds"])

    def test_enterprise_state_analyzer_emits_aggregates_without_enterprise_ids(self):
        analyzer = load_script("enterprise_state_analyzer.py")
        rows = [
            {
                "enterprise_id": "e1",
                "statistics_date": "2026-05-31",
                "business_board": "薪税",
                "_enterprise_state_type": "active",
            },
            {
                "enterprise_id": "e1",
                "statistics_date": "2026-06-30",
                "business_board": "薪税",
                "_enterprise_state_type": "active",
            },
            {
                "enterprise_id": "e2",
                "statistics_date": "2026-06-30",
                "business_board": "薪税",
                "_enterprise_state_type": "active",
            },
        ]
        result = analyzer.analyze(rows)
        self.assertEqual(2, result["reconciliation"]["period_count"])
        self.assertFalse(result["reconciliation"]["row_level_enterprise_ids_persisted"])
        self.assertEqual(
            1,
            next(
                item["enterprise_count"]
                for item in result["state_membership_changes"]
                if item["change_type"] == "entered"
            ),
        )
        self.assertNotIn("e1", json.dumps(result))

    def test_enterprise_wide_retained_flags_compile_as_board_memberships(self):
        analyzer = load_script("enterprise_state_analyzer.py")
        result = analyzer.analyze([
            {
                "enterprise_id": "e1",
                "statistics_date": "2026-05-31",
                "是否三级功能费用报销存续": 1,
                "是否三级功能差旅报销存续": 0,
            }
        ])
        board = result["enterprise_board_state_snapshots"][0]
        self.assertEqual("retained", board["state"])
        self.assertEqual("三级功能费用报销", board["business_board"])


if __name__ == "__main__":
    unittest.main()
