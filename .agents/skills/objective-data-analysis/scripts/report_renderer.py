#!/usr/bin/env python3
"""Render Objective 4.0 user-facing report sections from the unified JSON."""

from __future__ import annotations

import json
from typing import Any


def _pct(value: Any) -> str:
    return "—" if value is None else f"{float(value) * 100:.1f}%"


def _table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    if not rows:
        return ["当前无可展示结果。"]
    return [
        "| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |",
        *["| " + " | ".join(str(value) if value is not None else "—" for value in row) + " |" for row in rows],
    ]


def _start(lines: list[str], number: int, title: str, result: dict[str, Any]) -> bool:
    lines += ["", f"## {number}. {title}", ""]
    if result.get("status") == "not_evaluable":
        lines.append(f"本次无法评估：{result.get('reason', 'insufficient_data')}。")
        return False
    return result.get("status") == "completed" or result.get("status") == "completed_with_caveats"


TERMINAL_LABELS = {
    "success": "已完成",
    "draft": "已保存待继续",
    "exit": "明确退出",
    "error_without_observed_followup": "报错后未观察到后续行为",
    "incomplete_or_tracking_ended": "未完成或埋点中断",
    "unknown": "无法判断",
    "error_terminal": "报错后未观察到后续行为",
    "abandoned_or_unknown": "未完成或无法判断",
}


def render_markdown(package: dict[str, Any]) -> str:
    run, results = package["run"], package["analysis_results"]
    selected = set(run.get("selected_analyses", []))
    metrics, funnel, journey = results["metrics"], results["funnel"], results["journey"]
    errors, segments, baseline, feature = results["errors"], results["segments"], results["baseline"], results["feature_usage"]
    enterprise_states = results["enterprise_states"]
    lines = [
        f"# {run['project_name']}客观行为与旅程分析报告", "",
        "> 本报告只陈述客观数据中发生了什么、影响规模及与可比历史的差异；不声明根因、策略或收益承诺。", "",
        "## 1. 执行摘要", "", f"- 分析时间：{run['generated_at']}",
        f"- 数据周期：{package.get('scope', {}).get('time_window', '未声明')}", f"- 分析状态：{'已完成，但有注意事项' if run['status'] == 'completed_with_caveats' else '已完成'}",
        f"- 数据行数：{package['data_quality'].get('analysis_row_count', 0)}；任务实例：{metrics.get('task_instance_count', '不可评估')}",
        "- 历史归档：否；重要运行需显式交给 Evidence Archive。", "",
    ]
    lines.extend(f"- {item['statement']}" for item in package.get("findings", [])[:7])
    lines += ["", "## 2. 范围与数据来源", ""]
    for item in run.get("sources", []):
        if item.get("status") == "loaded":
            observed = item.get("observed_time_window", {})
            window = (
                f"{observed.get('start')} 至 {observed.get('end')}"
                if observed.get("start") or observed.get("end")
                else "未提供可解析时间字段"
            )
            lines.append(f"- {item['source_id']}：{item['format']}，{item['row_count']} 行，语义 {item.get('semantic_type', '未声明')}，实际时间覆盖 {window}。")
        else:
            lines.append(f"- {item['source_id']}：不可读取（{item.get('failure_reason')}）。")
    quality = package["data_quality"]
    lines += ["", "## 3. 预处理与数据质量", "", f"- 输入/分析行数：{quality['input_row_count']} / {quality['analysis_row_count']}", f"- 排除/去重行数：{quality['excluded_row_count']} / {quality['duplicate_row_count']}", f"- 推导任务行数：{quality['derived_task_row_count']}", f"- 无效时间戳：{quality['invalid_timestamp_count']}", f"- 任务边界可靠：{quality['task_boundary_reliable']}", f"- 质量状态：{quality['status']}"]

    if "metrics" in selected and _start(lines, 4, "指标口径与核心 KPI", metrics):
        headline = metrics.get("headline_metrics", {})
        lines += _table(["指标", "分子", "分母", "结果", "口径来源"], [
            ["任务完成率", metrics.get("completion_count"), metrics.get("task_instance_count"), _pct(metrics.get("completion_rate")), "任务/事件明细计算"],
            ["一次完成率", metrics.get("one_time_completion_count"), metrics.get("task_instance_count"), _pct(metrics.get("one_time_completion_rate")), "任务/事件明细计算"],
            ["报错任务率", metrics.get("error_task_count"), metrics.get("task_instance_count"), _pct(metrics.get("error_task_rate")), "任务/事件明细计算"],
            ["正式汇总任务完成率", None, headline.get("task_instance_count"), _pct(headline.get("completion_rate")), headline.get("source_ref", "未提供")],
            ["正式汇总一次完成率", None, headline.get("task_instance_count"), _pct(headline.get("one_time_completion_rate")), headline.get("source_ref", "未提供")],
        ])
        reconciliation = metrics.get("source_reconciliation", {})
        if reconciliation.get("reported_metric_candidates"):
            lines.append(f"- 跨来源口径核对：{reconciliation.get('status')}；不同时间窗或总体不会被静默合并。")
        duration = metrics.get("task_duration_seconds") or metrics.get("duration_seconds") or {}
        lines.append(f"- 任务时长 P50/P70/P90：{duration.get('p50')} / {duration.get('p70')} / {duration.get('p90')} 秒。")
    if "funnel" in selected and _start(lines, 5, "阶段与固定漏斗", funnel):
        lines += _table(["步骤", "进入任务", "整体转化", "流失任务", "报错任务", "P50/P70/P90 秒"], [[item.get("step"), item.get("entered_count"), _pct(item.get("overall_conversion_rate")), item.get("absolute_dropoff_count"), item.get("error_task_count"), "/".join(str(item.get("duration_seconds", {}).get(key) or "—") for key in ("p50", "p70", "p90"))] for item in funnel.get("steps", [])])
    if "journey" in selected and _start(lines, 6, "终态、实际路径与桑基数据", journey):
        lines.append(f"- 终态分母：{journey.get('task_instance_count', 0)} 个任务；旅程来源：{journey.get('source_semantic_type', '未声明')}。")
        lines += _table(["终态", "任务数", "占比"], [[TERMINAL_LABELS.get(item["outcome"], item["outcome"]), item["task_count"], _pct(item["share"])] for item in journey.get("terminal_outcomes", [])])
        lines += ["", "### 主要实际路径", ""] + _table(["路径", "任务数", "占比"], [[" → ".join(item["path"]), item["task_count"], _pct(item["share"])] for item in journey.get("path_patterns", [])[:10]])
        timed_nodes = [item for item in journey.get("stage_nodes", []) if item.get("duration_seconds", {}).get("p50") is not None]
        if timed_nodes:
            lines += ["", "### 节点耗时", ""] + _table(["节点", "任务数", "P50/P70/P90 秒"], [[item["label"], item["task_count"], "/".join(str(round(item["duration_seconds"][key], 1)) if item["duration_seconds"].get(key) is not None else "—" for key in ("p50", "p70", "p90"))] for item in timed_nodes[:20]])
        lines += ["", "### 蓝图偏差", ""] + _table(["偏差类型", "任务数"], [[item["type"], item["task_count"]] for item in journey.get("blueprint_deviations", [])])
        lines += ["", "### 桑基流向数据", ""] + _table(["来源", "去向", "任务数"], [[item["source"], item["target"], item["task_count"]] for item in journey.get("stage_transitions", [])[:20]])
    if "errors" in selected and _start(lines, 7, "报错与报错后行为", errors):
        lines.append(f"- 报错候选 {errors.get('candidate_error_event_count', errors.get('error_event_count', 0))} 条；排除确认、信息和成功状态 {errors.get('excluded_non_error_event_count', 0)} 条。")
        lines += _table(["安全报错标签", "类型", "事件数", "影响任务", "单任务均次", "60 秒单任务峰值"], [[item["canonical_safe_label"], item.get("message_kind", item["category"]), item["event_count"], item["affected_task_count"], round(item.get("events_per_affected_task") or 0, 1), item.get("max_events_in_60_seconds_same_task")] for item in errors.get("top_error_patterns", [])])
        lines += ["", "### 报错后的下一事件类别", ""] + _table(["下一事件类别", "事件数"], [[item["next_event_class"], item["event_count"]] for item in journey.get("error_after_behavior_paths", [])])
    if "segments" in selected and _start(lines, 8, "有业务依据的有限分群", segments):
        lines += _table(["分群", "样本", "占比", "完成率", "样本状态"], [[item["label"], item["sample_size"], _pct(item["share"]), _pct(item["completion_rate"]), item["sample_status"]] for item in segments.get("segments", [])])
        lines.append(f"- 分群对账：{'通过' if segments.get('reconciliation', {}).get('balanced') else '未通过'}；群体比较：{'可评估' if segments.get('comparison_evaluable') else '不可评估（至少需要两个样本充足的业务群体）'}。")
    if "baseline" in selected and _start(lines, 9, "历史基线与当前差异", baseline):
        lines += _table(["周期", "当前值", "绝对差", "相对差", "状态"], [[item["period"], item["current_value"], item["absolute_delta"], _pct(item["relative_delta"]), item["anomaly_status"]] for item in baseline.get("comparisons", [])])
    if "feature_usage" in selected and _start(lines, 10, "功能使用", feature):
        lines += _table(["指标", "分子", "分母", "结果"], [[item["metric_id"], item["numerator"], item["denominator"], _pct(item["value"])] for item in feature.get("usage_metrics", [])])
    if "enterprise_states" in selected and _start(lines, 10, "企业状态与板块人口", enterprise_states):
        lines += _table(
            ["周期", "企业状态", "板块", "企业数", "统计粒度"],
            [
                [
                    item["period"],
                    item["state_label"],
                    item.get("business_board") or "全部板块",
                    item["enterprise_count"],
                    item["measurement_scope"]["grain"],
                ]
                for item in (
                    enterprise_states.get("enterprise_state_snapshots", [])
                    + enterprise_states.get("enterprise_board_state_snapshots", [])
                )[:50]
            ],
        )
        changes = enterprise_states.get("state_membership_changes", [])
        if changes:
            lines += ["", "### 多期状态变化", ""] + _table(
                ["起止周期", "企业状态", "板块", "变化", "企业数"],
                [
                    [
                        f"{item['period_start']} → {item['period_end']}",
                        item["state_label"],
                        item.get("business_board") or "全部板块",
                        item["change_type"],
                        item["enterprise_count"],
                    ]
                    for item in changes[:50]
                ],
            )
        lines.append("- 企业状态按成员关系汇总，不默认假设月活、深度月活与存续互斥或存在固定转化关系。")

    lines += ["", "## 11. 客观发现与证据", ""]
    evidence_findings = {item["finding_ref"] for item in package.get("evidence_items", [])}
    for item in package.get("findings", []):
        evidence = "可进入证据治理" if item["finding_id"] in evidence_findings else "当前仅作描述性观察"
        lines.append(f"- {item['statement']}（样本 {item['sample_size']}，影响 {item['impact_count']}；{evidence}）")
    lines += ["", "## 12. 限制与下游交接", ""]
    lines.extend(f"- {value}" for value in package.get("limitations", []))
    lines += ["- 下一站：证据治理。", "- HTML、图表或桑基图需显式调用数据可视化；不得重算。", "", "## 13. 方法与口径", "", f"- 指标体系：{package['effective_analysis_contract']['metric_framework']}", f"- 已请求分析：{', '.join(run['selected_analyses'])}", "- 运行标识、对象 ID 和数据指纹保留在结构化结果中，主报告不展示。"]
    return "\n".join(lines).rstrip() + "\n"
