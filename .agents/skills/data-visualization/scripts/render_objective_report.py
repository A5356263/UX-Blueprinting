#!/usr/bin/env python3
"""Build a Data Visualization 5.0 candidate and project Objective 4.0 into HTML."""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_visualization_package import (
    SOURCE_CONTRACTS_PATH,
    atomic_write,
    load_json,
    validate_package,
)


def pct(value: Any) -> str:
    return "—" if value is None else f"{float(value) * 100:.1f}%"


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else "—"))


DISPLAY_REPLACEMENTS = {
    "same_scope_metric_source_conflict": "同一分析范围内的指标来源结果不一致",
    "same-scope metric sources disagree beyond tolerance; formal metric evidence is blocked": "同一口径来源的差异超过容许范围，正式核心指标已阻断",
    "task_summary_has_no_step_level_funnel_contract": "任务汇总数据没有固定步骤漏斗定义",
    "baseline_config_incomplete": "未提供完整的历史基线配置",
    "feature_config_incomplete": "未提供完整的功能使用分析配置",
    "confirmation, informational, and success-status messages were excluded from actionable error rankings": "确认、信息和成功状态提示未计入可行动错误排行",
    "unknown message types remain in the analysis and require sampled review": "仍有无法分类的消息类型，需要抽样复核",
    "UNKNOWN": "未匹配企业规模",
}


def readable(value: Any) -> str:
    text = str(value if value is not None else "—")
    for source, target in DISPLAY_REPLACEMENTS.items():
        text = text.replace(source, target)
    return text


def table(headers: list[str], rows: list[list[Any]]) -> str:
    body = "".join(
        "<tr>" + "".join(f"<td>{esc(value)}</td>" for value in row) + "</tr>"
        for row in rows
    )
    return (
        "<div class='table-wrap'><table><thead><tr>"
        + "".join(f"<th>{esc(value)}</th>" for value in headers)
        + f"</tr></thead><tbody>{body}</tbody></table></div>"
    )


def bar_rows(
    items: list[dict[str, Any]], label_key: str, value_key: str, count_key: str
) -> str:
    maximum = max((float(item.get(value_key) or 0) for item in items), default=0) or 1
    rows = []
    for item in items:
        value = float(item.get(value_key) or 0)
        width = max(2, value / maximum * 100) if value else 0
        rows.append(
            "<div class='bar-row'>"
            f"<span>{esc(item.get(label_key))}</span>"
            f"<i><b style='width:{width:.2f}%'></b></i>"
            f"<strong>{esc(item.get(count_key))} · {pct(item.get(value_key))}</strong></div>"
        )
    return "".join(rows) or "<p class='empty'>本次无可展示数据。</p>"


def _source_ref(path: Path, explicit_ref: str | None) -> str:
    if explicit_ref:
        return explicit_ref
    return "objective"


def _source_contract() -> dict[str, Any]:
    payload = load_json(SOURCE_CONTRACTS_PATH)
    return next(
        item
        for item in payload["contracts"]
        if item["producer_skill"] == "objective-data-analysis"
    )


def _point(label: str, value: Any, source_ref: str) -> dict[str, Any]:
    return {
        "label": label,
        "category": label,
        "x": None,
        "y": None,
        "value": value,
        "epistemic_status": "observed",
        "source_ref": source_ref,
    }


def _visual(
    visual_id: str,
    title: str,
    intent: str,
    chart_type: str,
    data_ref: str,
    points: list[dict[str, Any]],
    rationale: str,
    unit: str | None = None,
    caveats: list[str] | None = None,
) -> dict[str, Any]:
    status = "formal" if points else "spec_only"
    value = {
        "visual_id": visual_id,
        "title": title,
        "intent": intent,
        "chart_type": chart_type,
        "render_status": status,
        "data_ref": data_ref,
        "source_refs": [data_ref],
        "rationale": rationale,
        "epistemic_status": "observed",
        "encoding": {
            "x": "label",
            "y": "value",
            "color": "series",
            "size": None,
            "label": "value",
            "unit": unit,
            "denominator": "task_instance" if unit in {"ratio", "count"} else None,
            "time_window": "继承 Objective scope",
        },
        "accessibility": {
            "summary": title,
            "data_table_available": True,
            "color_independent": True,
        },
        "responsive": {
            "strategy": "label_reduction_with_table",
            "mobile_note": "窄屏保留关键标签，完整数据通过表格提供。",
        },
        "caveats": caveats or [],
    }
    if points:
        value["chart_data"] = {
            "series": [
                {
                    "series_id": visual_id,
                    "label": title,
                    "points": points,
                }
            ]
        }
    return value


def _relationship_diagram(
    nodes: list[dict[str, Any]], links: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    if not nodes or not links:
        return []
    normalized_nodes = []
    known: set[str] = set()
    for node in nodes:
        node_id = str(node.get("node_id") or "")
        if not node_id or node_id in known:
            continue
        known.add(node_id)
        normalized_nodes.append(
            {
                "node_id": node_id,
                "label": str(node.get("label") or node_id),
                "node_type": str(node.get("node_type") or "journey_stage"),
                "epistemic_status": "observed",
                "source_refs": ["objective#/analysis_results/journey/stage_nodes"],
            }
        )
    normalized_edges = []
    for index, link in enumerate(links):
        source = str(link.get("source") or "")
        target = str(link.get("target") or "")
        weight = link.get("task_count")
        if source not in known or target not in known or not isinstance(weight, (int, float)):
            continue
        normalized_edges.append(
            {
                "edge_id": f"objective-flow-{index + 1}",
                "source": source,
                "target": target,
                "relation_type": "observed_task_flow",
                "weight": weight,
                "weight_unit": "task_count",
                "epistemic_status": "observed",
                "source_refs": [
                    f"objective#/analysis_results/journey/stage_transitions/{index}"
                ],
                "caveats": [],
            }
        )
    if not normalized_edges:
        return []
    return [
        {
            "diagram_id": "objective-stage-flow",
            "title": "任务节点定量流向",
            "producer": "objective-data-analysis",
            "relation_type": "observed_task_flow",
            "source_refs": [
                "objective#/analysis_results/journey/stage_transitions"
            ],
            "nodes": normalized_nodes,
            "edges": normalized_edges,
            "confidence": "not_applicable",
            "caveats": ["线宽只表达 Objective 已计算的 task_count，不表示因果强度。"],
        }
    ]


def _validate_journey_projection(journey: dict[str, Any]) -> None:
    """Reject path facts that cannot be projected from the declared node graph."""
    if journey.get("status") not in {"completed", "completed_with_caveats"}:
        return
    known_nodes = {
        str(item.get("node_id") or "")
        for item in journey.get("stage_nodes", [])
        if item.get("node_id")
    }
    known_edges = {
        (str(item.get("source") or ""), str(item.get("target") or ""))
        for item in journey.get("stage_transitions", [])
        if item.get("source") and item.get("target")
    }
    for collection in ("path_patterns", "top_path_patterns"):
        for index, item in enumerate(journey.get(collection, [])):
            path = [str(value) for value in item.get("path", []) if value]
            if any(value not in known_nodes for value in path):
                raise ValueError(
                    f"projection_consistency_error: {collection}[{index}] references missing node"
                )
            if any(
                (path[position], path[position + 1]) not in known_edges
                for position in range(len(path) - 1)
            ):
                raise ValueError(
                    f"projection_consistency_error: {collection}[{index}] references missing edge"
                )


def build_spec(
    package: dict[str, Any],
    source_artifact_ref: str,
) -> dict[str, Any]:
    run = package["run"]
    results = package["analysis_results"]
    metrics = results.get("metrics", {})
    funnel = results.get("funnel", {})
    journey = results.get("journey", {})
    _validate_journey_projection(journey)
    errors = results.get("errors", {})
    segments = results.get("segments", {})
    limitations = [
        {
            "limitation_id": f"objective-limit-{index + 1}",
            "type": "source",
            "description": str(item),
            "affects_outputs": [],
        }
        for index, item in enumerate(package.get("limitations", []))
    ]
    contract = _source_contract()
    metric_points = [
        _point(
            "任务实例",
            metrics.get("task_instance_count"),
            "objective#/analysis_results/metrics/task_instance_count",
        ),
        _point(
            "任务完成率",
            metrics.get("completion_rate"),
            "objective#/analysis_results/metrics/completion_rate",
        ),
        _point(
            "一次完成率",
            metrics.get("one_time_completion_rate"),
            "objective#/analysis_results/metrics/one_time_completion_rate",
        ),
        _point(
            "报错任务率",
            metrics.get("error_task_rate"),
            "objective#/analysis_results/metrics/error_task_rate",
        ),
    ]
    metric_points = [item for item in metric_points if item["value"] is not None]
    funnel_points = [
        _point(
            str(item.get("step") or ""),
            item.get("overall_conversion_rate"),
            f"objective#/analysis_results/funnel/steps/{index}",
        )
        for index, item in enumerate(funnel.get("steps", []))
        if item.get("overall_conversion_rate") is not None
    ]
    terminal_points = [
        _point(
            str(item.get("outcome") or ""),
            item.get("share"),
            f"objective#/analysis_results/journey/terminal_outcomes/{index}",
        )
        for index, item in enumerate(journey.get("terminal_outcomes", []))
        if item.get("share") is not None
    ]
    error_points = [
        _point(
            str(item.get("canonical_safe_label") or ""),
            item.get("affected_task_count"),
            f"objective#/analysis_results/errors/top_error_patterns/{index}",
        )
        for index, item in enumerate(errors.get("top_error_patterns", []))
        if item.get("affected_task_count") is not None
    ]
    segment_points = [
        _point(
            str(item.get("label") or ""),
            item.get("completion_rate"),
            f"objective#/analysis_results/segments/segments/{index}",
        )
        for index, item in enumerate(segments.get("segments", []))
        if item.get("completion_rate") is not None
    ]
    relationships = _relationship_diagram(
        journey.get("stage_nodes", []), journey.get("stage_transitions", [])
    )
    visual_outputs = [
        _visual(
            "objective-kpis",
            "核心客观指标",
            "single_value",
            "metric_card",
            "objective#/analysis_results/metrics",
            metric_points,
            "直接呈现 Objective 已计算的核心指标，不重新定义或计算指标。",
        ),
        _visual(
            "objective-funnel",
            "阶段转化",
            "stage_conversion",
            "funnel",
            "objective#/analysis_results/funnel",
            funnel_points,
            "阶段具有明确顺序和上游计算的整体转化率，适合漏斗表达。",
            "ratio",
        ),
        _visual(
            "objective-terminal-outcomes",
            "终态分布",
            "comparison",
            "bar",
            "objective#/analysis_results/journey/terminal_outcomes",
            terminal_points,
            "类别比较使用柱状图并保留数据表。",
            "ratio",
        ),
        _visual(
            "objective-errors",
            "安全报错模式",
            "comparison",
            "bar",
            "objective#/analysis_results/errors/top_error_patterns",
            error_points,
            "使用上游安全标签比较受影响任务数，不展示未授权原始报错。",
            "count",
        ),
        _visual(
            "objective-segments",
            "有限分群完成率",
            "comparison",
            "bar",
            "objective#/analysis_results/segments/segments",
            segment_points,
            "只比较 Objective 已输出的有限分群，并保留样本可靠性限制。",
            "ratio",
        ),
    ]
    status_by_visual = {
        "objective-kpis": metrics.get("status"),
        "objective-funnel": funnel.get("status"),
        "objective-terminal-outcomes": journey.get("status"),
        "objective-errors": errors.get("status"),
        "objective-segments": segments.get("status"),
    }
    visual_outputs = [
        item for item in visual_outputs
        if status_by_visual.get(item["visual_id"]) in {"completed", "completed_with_caveats"}
        and item.get("chart_data", {}).get("series", [{}])[0].get("points")
    ]
    if relationships:
        visual_outputs.append(
            {
                "visual_id": "objective-sankey",
                "title": "任务节点定量流向",
                "intent": "quantitative_flow",
                "chart_type": "sankey",
                "render_status": "formal",
                "data_ref": "objective#/analysis_results/journey/stage_transitions",
                "source_refs": [
                    "objective#/analysis_results/journey/stage_transitions"
                ],
                "rationale": "每条边包含统一单位 task_count，允许使用带权重桑基表达。",
                "epistemic_status": "observed",
                "encoding": {
                    "x": "source_target",
                    "y": None,
                    "color": "stage",
                    "size": "task_count",
                    "label": "task_count",
                    "unit": "task_count",
                    "denominator": "task_instance",
                    "time_window": "继承 Objective scope",
                },
                "chart_data": {
                    "table": {
                        "columns": ["source", "target", "task_count"],
                        "rows": [
                            [
                                edge["source"],
                                edge["target"],
                                edge["weight"],
                            ]
                            for edge in relationships[0]["edges"]
                        ],
                    }
                },
                "accessibility": {
                    "summary": "各任务节点之间按任务数加权的流向。",
                    "data_table_available": True,
                    "color_independent": True,
                },
                "responsive": {
                    "strategy": "horizontal_scroll",
                    "mobile_note": "移动端横向滚动，完整关系通过表格读取。",
                },
                "caveats": ["线宽表示任务数，不表示因果强度。"],
            }
        )
    source_run_id = run["run_id"]
    status = "degraded" if limitations else "pass"
    spec = {
        "run": {
            "artifact_type": "visualization_package",
            "artifact_version": "5.0.0",
            "producer_skill": "data-visualization",
            "run_id": f"dv_objective_{re.sub(r'[^A-Za-z0-9_-]+', '-', source_run_id)}",
            "project_name": run.get("project_name", ""),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_mode": "registered_upstream",
            "sources": [source_artifact_ref],
            "write_status": "not_requested",
        },
        "data_quality": {
            "status": "ready_with_caveats" if limitations else "ready",
            "source_contract_valid": True,
            "semantic_gate_status": "degraded" if limitations else "passed",
            "notes": ["只表达 Objective 已有结论，不重新计算指标或关系。"],
        },
        "limitations": limitations,
        "handoff": {
            "input_gate_status": "ready_with_caveats" if limitations else "ready",
            "handoff_status": "terminal",
            "allowed_uses": ["presentation", "human_review", "offline_delivery"],
            "forbidden_uses": [
                "recalculate_analysis",
                "create_metric",
                "create_relationship",
                "upgrade_causality",
                "claim_validated_effect",
                "publish_knowledge",
                "auto_archive",
                "auto_trigger_downstream",
            ],
            "blocked_reasons": [],
        },
        "analysis_results": {
            "visualization_package": {
                "source_contracts": [
                    {
                        "source_id": "objective",
                        "producer_skill": "objective-data-analysis",
                        "artifact_type": "objective_evidence_package",
                        "artifact_version": "4.0.0",
                        "source_run_id": source_run_id,
                        "artifact_ref": source_artifact_ref,
                        "allowed_paths": contract["allowed_paths"],
                        "consumed_paths": [
                            "#/analysis_results",
                            "#/findings",
                            "#/limitations",
                            "#/handoff/visualization",
                        ],
                        "sensitivity_status": "inherited",
                        "privacy_gate_status": "safe",
                        "contract_status": "valid",
                    }
                ],
                "visual_outputs": visual_outputs,
                "relationship_diagrams": relationships,
                "output_files": [],
                "recalculation_performed": False,
            }
        },
        "manual_review_requests": [],
        "quality": {
            "overall_status": status,
            "source_traceability": "pass",
            "semantic_fidelity": "pass",
            "label_clarity": "pass",
            "accessibility": "pass",
            "responsive": "pass",
            "sensitive_display": "pass",
        },
        "write_safety": {
            "output_root_checked": True,
            "relative_paths_only": True,
            "overwrite_policy": "immutable_result_with_purpose_pointer",
            "atomic_write": True,
            "sensitive_content_checked": True,
        },
    }
    validate_package(spec)
    return spec


def render(package: dict[str, Any]) -> str:
    run = package.get("run", {})
    if run.get("artifact_version") != "4.0.0":
        raise ValueError("Objective HTML renderer only accepts artifact_version=4.0.0")
    run_id = run.get("run_id")
    if not run_id:
        raise ValueError("objective run.run_id is required")
    results = package["analysis_results"]
    metrics = results.get("metrics", {})
    funnel = results.get("funnel", {})
    journey = results.get("journey", {})
    errors = results.get("errors", {})
    segments = results.get("segments", {})
    headline = metrics.get("headline_metrics", {})
    metrics_publishable = metrics.get("status") in {
        "completed",
        "completed_with_caveats",
    }
    cards = (
        [
            (
                "任务实例",
                (headline.get("task_instance_count") or "未提供")
                if headline
                else metrics.get("task_instance_count", "未提供"),
            ),
            (
                "任务完成率",
                pct(
                    headline.get("completion_rate")
                    if headline
                    else metrics.get("completion_rate")
                ),
            ),
            (
                "一次完成率",
                pct(
                    headline.get("one_time_completion_rate")
                    if headline
                    else metrics.get("one_time_completion_rate")
                ),
            ),
            ("报错任务率", pct(metrics.get("error_task_rate"))),
        ]
        if metrics_publishable
        else []
    )
    cards_html = "".join(
        f"<div class='card'><span>{esc(label)}</span><strong>{esc(value)}</strong></div>"
        for label, value in cards
    )
    metric_note = ""
    if metrics_publishable and headline:
        metric_note = (
            "<p class='definition'>核心比率采用正式汇总口径；"
            f"{'已提供任务分母。' if headline.get('denominator_available') else '未提供任务分母，不与明细任务数拼接。'}</p>"
        )
    source_table = table(
        ["数据源", "语义", "格式", "行数", "实际时间覆盖"],
        [
            [
                item.get("source_id"),
                item.get("semantic_type"),
                item.get("format"),
                item.get("row_count"),
                " ～ ".join(
                    str(item.get("observed_time_window", {}).get(key) or "未提供")
                    for key in ("start", "end")
                ),
            ]
            for item in run.get("sources", [])
        ],
    )
    funnel_table = table(
        ["步骤", "进入任务", "整体转化", "掉点", "P50/P70/P90 秒"],
        [
            [
                item.get("step"),
                item.get("entered_count"),
                pct(item.get("overall_conversion_rate")),
                item.get("absolute_dropoff_count"),
                "/".join(
                    str(item.get("duration_seconds", {}).get(key) or "—")
                    for key in ("p50", "p70", "p90")
                ),
            ]
            for item in funnel.get("steps", [])
        ],
    )
    transitions = journey.get("stage_transitions", [])
    primary_transitions = [
        item for item in transitions
        if (item.get("share_of_total_tasks") or 0) >= 0.01
    ][:30] or transitions[:30]
    flow_table = table(
        ["来源", "目标", "任务数", "事件次数", "总任务占比", "来源流出占比", "P50/P70/P90 秒"],
        [
            [
                item.get("source"),
                item.get("target"),
                item.get("task_count"),
                item.get("transition_event_count"),
                pct(item.get("share_of_total_tasks")),
                pct(item.get("share_of_source_outflow")),
                "/".join(
                    str(item.get("duration_seconds", {}).get(key) or "—")
                    for key in ("p50", "p70", "p90")
                ),
            ]
            for item in primary_transitions
        ],
    )
    message_kind_labels = {
        "error": "错误",
        "actionable_error": "可行动错误",
        "warning": "警告",
        "unknown": "待复核",
    }
    error_table = table(
        ["安全报错标签", "类型", "事件数", "影响任务", "单任务均次", "60 秒峰值"],
        [
            [
                item.get("canonical_safe_label"),
                message_kind_labels.get(
                    item.get("message_kind") or item.get("category"),
                    item.get("message_kind") or item.get("category"),
                ),
                item.get("event_count"),
                item.get("affected_task_count"),
                round(item.get("events_per_affected_task") or 0, 1),
                item.get("max_events_in_60_seconds_same_task"),
            ]
            for item in errors.get("top_error_patterns", [])[:10]
        ],
    )
    sample_status_labels = {
        "sufficient": "样本充足",
        "low_sample": "样本不足",
        "low_sample_risk": "样本不足，谨慎比较",
        "not_comparable": "不可比较",
        "unknown": "待确认",
    }
    segment_table = table(
        ["场景/分群", "样本", "完成率", "可靠性"],
        [
            [
                "未匹配企业规模"
                if item.get("label") == "UNKNOWN"
                else item.get("label"),
                item.get("sample_size"),
                pct(item.get("completion_rate")),
                sample_status_labels.get(
                    item.get("sample_status"), item.get("sample_status")
                ),
            ]
            for item in segments.get("segments", [])
        ],
    )
    readable_limitations: list[str] = []
    for value in package.get("limitations", []):
        text = readable(value)
        if any(text in existing for existing in readable_limitations):
            continue
        readable_limitations = [
            existing for existing in readable_limitations if existing not in text
        ]
        readable_limitations.append(text)
    caveats = "".join(
        f"<li>{esc(value)}</li>" for value in readable_limitations
    ) or "<li>本次没有额外限制。</li>"
    visible_node_ids = {
        value
        for link in primary_transitions
        for value in (link.get("source"), link.get("target"))
        if value
    }
    chart_data = {
        "run_id": run_id,
        "nodes": journey.get("stage_nodes", []),
        "links": transitions,
        "stage_order": [
            item.get("step")
            for item in funnel.get("steps", [])
            if item.get("step")
        ],
        "paths": journey.get("path_patterns", []),
        "top_paths": journey.get("top_path_patterns", []),
        "reference_path_candidate": journey.get("inferred_reference_path_candidate"),
        "business_blueprint": journey.get("business_blueprint"),
        "blueprint_deviations": journey.get("blueprint_deviations", []),
        "exit_points": journey.get("exit_points", []),
        "backtracks": journey.get("backtrack_and_loop_paths", []),
        "error_by_step": errors.get("error_by_step", []),
    }
    safe_payload = json.dumps(chart_data, ensure_ascii=False).replace("</", "<\\/")
    labels = {
        "success": "已完成",
        "draft": "已保存待继续",
        "exit": "明确退出",
        "error_without_observed_followup": "报错后未观察到后续行为",
        "incomplete_or_tracking_ended": "未完成或埋点中断",
        "unknown": "无法判断",
        "error_terminal": "报错后未观察到后续行为",
        "abandoned_or_unknown": "未完成或无法判断",
    }
    terminal_rows = [
        {**item, "display_outcome": labels.get(item.get("outcome"), item.get("outcome"))}
        for item in journey.get("terminal_outcomes", [])
    ]
    findings_by_analysis: dict[str, list[str]] = {}
    for item in package.get("findings", []):
        statement = item.get("statement")
        if statement:
            findings_by_analysis.setdefault(
                str(item.get("source_analysis") or "other"), []
            ).append(str(statement))

    def insight(kind: str) -> str:
        values = findings_by_analysis.get(kind, [])
        return (
            "<div class='insight'><strong>本节结论</strong><ul>"
            + "".join(f"<li>{esc(readable(value))}</li>" for value in values[:5])
            + "</ul></div>"
        ) if values else "<p class='empty'>本次结构化结果未形成该维度的可发布结论。</p>"

    def result_section(
        title: str, result: dict[str, Any], body: str, kind: str
    ) -> str:
        status = result.get("status")
        if status == "not_requested":
            return ""
        if status == "not_evaluable":
            return (
                f"<h2>{esc(title)}</h2><section class='panel blocked'>"
                f"<strong>本次暂不能形成正式结论</strong>"
                f"<p>{esc(readable(result.get('reason', '输入或口径不足')))}</p></section>"
            )
        return f"<h2>{esc(title)}</h2><section class='panel'>{insight(kind)}{body}</section>"

    if metrics.get("status") == "not_requested":
        metric_section = ""
    elif metrics_publishable:
        metric_section = (
            "<h2>整体表现如何</h2><section class='panel'>"
            f"{insight('metrics')}<div class='cards'>{cards_html}</div>{metric_note}"
            "</section>"
        )
    else:
        metric_reason = str(metrics.get("reason") or "")
        metric_has_conflict = "conflict" in metric_reason
        metric_message = (
            "核心指标存在口径或来源冲突，当前不展示单一正式值"
            if metric_has_conflict
            else "核心指标暂不能评估"
        )
        metric_section = (
            "<h2>整体表现如何</h2><section class='panel blocked'>"
            f"<strong>{metric_message}</strong>"
            f"<p>{esc(readable(metrics.get('reason', '输入或口径不足')))}</p>"
            "<p>路径、报错和耗时等输入充分的部分仍会继续展示。</p>"
            "</section>"
        )

    journey_parts: list[str] = []
    if journey.get("status") == "completed" or journey.get("status") == "completed_with_caveats":
        journey_parts.append(insight("journey"))
        journey_parts.append(
            "<h3>任务结果分布</h3>"
            f"<p class='definition'>分母为 {esc(journey.get('task_instance_count', 0))} 个任务。"
            + (
                "这是任务明细中的终态分布，不替代上方暂不可评估的核心指标。"
                if not metrics_publishable
                else ""
            )
            + "</p>"
            + bar_rows(terminal_rows, "display_outcome", "share", "task_count")
        )
        if transitions:
            has_business_stage_mapping = bool(
                journey.get("journey_definition", {}).get(
                    "business_stage_mapping_ref"
                )
            )
            flow_title = (
                "主要业务阶段流向"
                if has_business_stage_mapping
                else "主要任务节点流向"
            )
            flow_note = (
                "已继承明确的业务阶段映射。"
                if has_business_stage_mapping
                else "本次没有明确的业务阶段映射，因此按原始任务节点展示，不把节点解释为业务阶段。"
            )
            journey_parts.append(
                f"<h3>{flow_title}</h3><p class='definition'>{flow_note}"
                " 可按真实路径筛选并点击路径或连线查看任务数、事件次数、占比、耗时与节点异常；线宽表示上游已计算的任务数，不表示因果强度。</p>"
                "<div class='path-toolbar'><label>路径范围 <select id='path-filter'><option value='top'>高频真实路径</option><option value='all'>在全部真实路径中按显示条数筛选</option><option value='ideal'>正式理想路径</option></select></label>"
                "<label>显示路径数 <select id='path-limit'><option>10</option><option>20</option><option>50</option></select></label>"
                "<button type='button' id='path-reset'>清除高亮</button><span id='path-summary' class='definition'></span></div>"
                "<div class='path-layout'><div><div id='path-list' class='path-list'></div>"
                '<div class="flow-scroll flow-canvas"><svg id="sankey-flow" viewBox="0 0 1180 470" role="img" aria-label="可交互的真实任务路径与节点流向图"></svg></div></div>'
                "<aside id='flow-detail' class='flow-detail' aria-live=\"polite\"><strong>路径与节点详情</strong><p>点击左侧路径、连线或节点查看详情。</p></aside></div>"
                + "<details class='data-detail flow-data-detail'><summary>查看主要节点流向数据表</summary>"
                + flow_table
                + "</details>"
            )
    elif journey.get("status") == "not_evaluable":
        journey_parts.append(
            "<div class='blocked'><strong>旅程暂不能评估</strong>"
            f"<p>{esc(readable(journey.get('reason', '任务路径输入不足')))}</p></div>"
        )
    if funnel.get("status") in {"completed", "completed_with_caveats"}:
        journey_parts.append(f"<h3>固定漏斗</h3>{insight('funnel')}{funnel_table}")
    elif funnel.get("status") == "not_evaluable":
        journey_parts.append(
            "<h3>固定漏斗</h3><div class='blocked'>"
            f"<p>本次无法评估：{esc(readable(funnel.get('reason', '缺少正式漏斗定义或步骤数据')))}</p></div>"
        )
    journey_section = (
        "<h2>任务在哪里停止、流转或重复</h2><section class='panel'>"
        + "".join(journey_parts)
        + "</section>"
        if journey_parts
        else ""
    )
    error_section = result_section(
        "报错与待复核消息模式",
        errors,
        f"<p>报错候选 {esc(errors.get('candidate_error_event_count', errors.get('error_event_count', 0)))} 条；排除确认、信息和成功状态 {esc(errors.get('excluded_non_error_event_count', 0))} 条。主报告展示前 10 个模式，完整明细保留在结构化结果中。</p>{error_table}",
        "errors",
    )
    segment_section = result_section(
        "业务场景与有限分群",
        segments,
        segment_table + f"<p>分群对账：{'通过' if segments.get('reconciliation', {}).get('balanced') else '未通过'}；群体比较：{'可评估' if segments.get('comparison_evaluable') else '不可评估'}。</p>",
        "segments",
    )
    source_count = len(run.get("sources", []))
    metric_framework = package.get("effective_analysis_contract", {}).get(
        "metric_framework", "未声明"
    )
    scope = package.get("scope", {})
    scope_text = (
        scope.get("analysis_scope")
        or scope.get("task_name")
        or scope.get("scenario")
        or "以本次 Objective 正式输入声明为准"
    )
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(run['project_name'])}客观行为与旅程分析报告</title>
<style>
:root{{--ink:#142033;--ink-soft:#334155;--muted:#64748b;--line:#dbe3ef;--line-strong:#c8d3e2;--bg:#f2f6fb;--surface:#fff;--surface-elevated:#fff;--brand:#3454d1;--brand-deep:#172a67;--brand-soft:#eef2ff;--accent:#f59e0b;--danger:#c2413a;--shadow:0 18px 45px rgba(29,48,91,.08);--shadow-soft:0 8px 24px rgba(29,48,91,.06)}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;overflow-x:hidden;background:radial-gradient(circle at 85% 0,#e8edff 0,transparent 30rem),var(--bg);color:var(--ink);font:14px/1.68 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif;-webkit-font-smoothing:antialiased}}
.skip-link{{position:fixed;z-index:20;top:12px;left:12px;transform:translateY(-160%);padding:10px 14px;border-radius:10px;background:#fff;color:var(--brand-deep);box-shadow:var(--shadow)}}.skip-link:focus{{transform:none}}
main{{max-width:1240px;margin:auto;padding:32px 24px 80px}}.report-hero{{position:relative;overflow:hidden;background:linear-gradient(135deg,#152557 0%,#2946b8 58%,#4f6be5 100%);color:white;border-radius:26px;padding:38px 40px;box-shadow:0 24px 55px rgba(34,55,130,.22)}}.report-hero:after{{content:"";position:absolute;width:360px;height:360px;right:-130px;top:-220px;border:1px solid #ffffff28;border-radius:50%;box-shadow:0 0 0 54px #ffffff0b,0 0 0 108px #ffffff08}}
.report-kicker{{position:relative;z-index:1;margin-bottom:12px;font-size:12px;font-weight:750;letter-spacing:.12em;text-transform:uppercase;color:#cbd5ff}}h1{{position:relative;z-index:1;margin:0 0 12px;max-width:900px;font-size:clamp(27px,3vw,38px);line-height:1.18;letter-spacing:-.03em}}h2{{display:flex;align-items:center;gap:10px;margin:42px 0 16px;font-size:23px;line-height:1.3;letter-spacing:-.02em}}h2:before{{content:"";width:5px;height:22px;border-radius:9px;background:linear-gradient(var(--brand),#7890f2)}}h3{{margin:28px 0 12px;font-size:17px;color:var(--ink-soft)}}.meta{{position:relative;z-index:1;color:#e3e8ff}}.notice{{position:relative;z-index:1;margin-top:20px;max-width:920px;padding:12px 15px;background:#ffffff14;border:1px solid #ffffff38;border-radius:12px;color:#f8fafc;backdrop-filter:blur(8px)}}
.panel{{min-width:0;background:var(--surface-elevated);border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:var(--shadow-soft)}}.panel>p:first-child{{margin-top:0}}.panel>p:last-child{{margin-bottom:0}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0 2px}}.card{{position:relative;min-height:112px;padding:18px;background:linear-gradient(145deg,#fff,#f7f9ff);border:1px solid var(--line);border-radius:16px;overflow:hidden}}.card:after{{content:"";position:absolute;left:0;right:0;bottom:0;height:4px;background:linear-gradient(90deg,var(--brand),#8b9df4)}}.card span{{display:block;color:var(--muted);font-weight:650}}.card strong{{display:block;margin-top:9px;font-size:29px;line-height:1;color:var(--brand-deep);font-variant-numeric:tabular-nums}}
.table-wrap,.flow-scroll{{width:100%;max-width:100%;overflow:auto;border:1px solid var(--line);border-radius:14px}}table{{width:100%;border-collapse:separate;border-spacing:0}}th,td{{padding:11px 13px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}}th{{position:sticky;top:0;z-index:1;color:#475569;background:#f5f7fb;font-size:12px;letter-spacing:.02em}}tbody tr:nth-child(even){{background:#fafcff}}tbody tr:hover{{background:#f1f5ff}}tbody tr:last-child td{{border-bottom:0}}
.flow-canvas{{min-height:560px;background-color:#fbfcff;background-image:linear-gradient(#e8edf6 1px,transparent 1px),linear-gradient(90deg,#e8edf6 1px,transparent 1px);background-size:28px 28px}}#sankey-flow{{min-width:1060px;width:100%;height:auto;min-height:560px;display:block}}.flow-link{{fill:none;stroke:#6f86df;stroke-opacity:.32;cursor:pointer;transition:stroke-opacity .18s,stroke .18s}}.flow-link.is-secondary{{stroke-opacity:.1}}.flow-link.active{{stroke:var(--accent);stroke-opacity:.96}}.flow-link.muted{{stroke-opacity:.035}}.flow-node{{fill:var(--brand);stroke:#fff;stroke-width:2;cursor:pointer;filter:drop-shadow(0 4px 5px rgba(52,84,209,.18));transition:opacity .18s,fill .18s,stroke .18s}}.flow-node.active{{fill:var(--accent);stroke:var(--brand-deep);stroke-width:4}}.flow-node.muted{{opacity:.16}}.flow-node.has-error{{fill:var(--danger)}}.flow-node.is-exit{{stroke:var(--accent);stroke-width:4}}.flow-label{{font-size:11px;font-weight:650;fill:#26364f}}.path-toolbar{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:16px 0;padding:12px;background:#f7f9fd;border:1px solid var(--line);border-radius:13px}}.path-toolbar label{{display:flex;gap:8px;align-items:center;color:var(--muted);font-weight:650}}.path-toolbar select,.path-toolbar button{{min-height:38px;padding:8px 11px;border:1px solid var(--line-strong);border-radius:9px;background:white;color:var(--ink);font:inherit}}.path-toolbar button{{cursor:pointer}}.path-layout{{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:16px;min-width:0}}.path-layout>div{{min-width:0}}.path-list{{display:flex;max-width:100%;gap:8px;overflow:auto;padding:2px 2px 12px;scrollbar-width:thin}}.path-chip{{white-space:nowrap;border:1px solid var(--line-strong);border-radius:999px;background:#fff;padding:8px 12px;color:var(--ink-soft);cursor:pointer;transition:.16s}}.path-chip:hover{{border-color:#91a4eb;transform:translateY(-1px)}}.path-chip.active{{background:var(--brand-deep);border-color:var(--brand-deep);color:white;box-shadow:0 7px 16px rgba(23,42,103,.2)}}.path-chip.active small{{color:#d8e0ff}}.path-chip small{{color:var(--muted)}}.flow-detail{{position:sticky;top:16px;align-self:start;min-width:0;border:1px solid #cfd9fa;background:linear-gradient(145deg,#f8faff,#eef2ff);border-radius:14px;padding:16px;min-height:190px;box-shadow:var(--shadow-soft)}}.flow-detail>strong{{display:block;margin-bottom:10px;color:var(--brand-deep)}}.flow-detail dl{{display:grid;grid-template-columns:72px minmax(0,1fr);gap:7px 10px;margin-bottom:0}}.flow-detail dt{{color:var(--muted)}}.flow-detail dd{{margin:0;overflow-wrap:anywhere}}.data-detail{{margin-top:18px;border:1px solid var(--line);border-radius:13px;background:#fbfcfe}}.data-detail summary{{padding:13px 15px;color:var(--brand-deep);font-weight:750;cursor:pointer}}.data-detail[open] summary{{border-bottom:1px solid var(--line)}}.data-detail .table-wrap{{border:0;border-radius:0}}
.bar-row{{display:grid;grid-template-columns:150px 1fr 150px;gap:12px;align-items:center;margin:12px 0}}.bar-row i{{height:13px;background:#e7ecf5;border-radius:9px;overflow:hidden}}.bar-row b{{display:block;height:100%;border-radius:9px;background:linear-gradient(90deg,var(--brand),#7187ec)}}.bar-row strong{{font-size:12px;font-variant-numeric:tabular-nums}}.empty,.definition{{color:var(--muted)}}.insight{{margin-bottom:18px;padding:14px 16px;background:linear-gradient(120deg,#f2f5ff,#fafbff);border:1px solid #d9e1ff;border-left:5px solid var(--brand);border-radius:12px}}.insight strong{{color:var(--brand-deep)}}.insight ul{{margin:8px 0 0;padding-left:20px}}.blocked{{background:#fff9e9;border-color:#f1d08a}}details{{margin-top:14px}}summary{{cursor:pointer;font-weight:700}}
:focus-visible{{outline:3px solid #f59e0b;outline-offset:3px}}@media(max-width:900px){{.cards{{grid-template-columns:repeat(2,1fr)}}.path-layout{{grid-template-columns:1fr}}.flow-detail{{position:static}}}}@media(max-width:620px){{main{{padding:16px 12px 52px}}.report-hero{{padding:27px 22px;border-radius:20px}}h2{{margin-top:32px;font-size:20px}}.panel{{padding:16px;border-radius:15px}}.cards{{grid-template-columns:1fr 1fr;gap:9px}}.card{{min-height:96px;padding:14px}}.card strong{{font-size:23px}}.bar-row{{grid-template-columns:100px 1fr}}.bar-row strong{{grid-column:2}}.path-toolbar{{align-items:stretch}}.path-toolbar label{{width:100%;justify-content:space-between}}}}
@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}*,*:before,*:after{{animation-duration:.01ms!important;transition-duration:.01ms!important}}}}@media print{{body{{background:#fff}}main{{max-width:none;padding:0}}.skip-link,.path-toolbar{{display:none!important}}.report-hero,.panel,.card{{box-shadow:none;break-inside:avoid}}.report-hero{{background:#fff;color:#111;border:1px solid #bbb}}.meta,.notice{{color:#333}}details{{display:block}}details>*{{display:block!important}}}}
</style></head><body data-source-run-id="{esc(run_id)}"><a class="skip-link" href="#report-main">跳到报告正文</a><main id="report-main" class="report-shell">
<header class="report-hero"><div class="report-kicker">客观行为与旅程分析</div><h1>{esc(run['project_name'])}客观行为与旅程分析报告</h1>
<div class="meta">生成时间：{esc(run['generated_at'])} · 指标体系：{esc(metric_framework)}</div>
<div class="notice">仅表达 Objective 已计算的 analysis_results；本页面不重算指标，不声明根因、策略或 ROI。</div></header>
<h2>本次分析了什么</h2><section class="panel">
<p><strong>分析范围：</strong>{esc(scope_text)}</p>
<p><strong>数据来源：</strong>{source_count} 个已登记输入；具体口径、时间覆盖和行数见技术附录。</p>
<p><strong>数据质量：</strong>{'存在限制，需要结合下方说明阅读。' if package.get('limitations') else '未记录额外限制。'}</p>
</section>
{metric_section}
{journey_section}
{error_section}
{segment_section}
<h2>哪些内容仍需验证</h2><section class="panel"><ul>{caveats}</ul>
<p class="definition">本报告只提供客观描述。问题机制、优化策略和方案价值应进入后续 Root Cause、Problem Framing、Experience Blueprint 与 Business Impact 环节。</p>
</section>
<h2>技术附录</h2><section class="panel"><details><summary>查看来源、运行与口径追溯信息</summary>
<p>来源运行：{esc(run_id)}</p>{source_table}</details></section>
<script type="application/json" id="objective-chart-ready">{safe_payload}</script>
<script>(function(){{
const data=JSON.parse(document.getElementById('objective-chart-ready').textContent),svg=document.getElementById('sankey-flow'),NS='http://www.w3.org/2000/svg',detail=document.getElementById('flow-detail'),list=document.getElementById('path-list');
if(!svg)return;
const declared=(data.stage_order||[]).filter(Boolean),blueprint=(data.business_blueprint||{{}}),ideal=(blueprint.required_steps||[]),summary=document.getElementById('path-summary');
const fmt=v=>v==null?'—':typeof v==='number'?(Number.isInteger(v)?String(v):v.toFixed(1).replace(/\\.0$/,'')):String(v),pct=v=>v==null?'—':(Number(v)*100).toFixed(1)+'%',dur=d=>d?`P50 ${{fmt(d.p50)}} / P70 ${{fmt(d.p70)}} / P90 ${{fmt(d.p90)}} 秒`:'—';
const show=(title,rows)=>{{detail.innerHTML=`<strong>${{title}}</strong><dl>${{rows.map(x=>`<dt>${{x[0]}}</dt><dd>${{x[1]}}</dd>`).join('')}}</dl>`}};
const exits=new Map((data.exit_points||[]).map(x=>[x.node_id,x])),nodeById=new Map((data.nodes||[]).map(x=>[x.node_id,x]));
let edgeEls=[],nodeEls=[];
function visibleGraph(paths){{const nodeIds=new Set(),edgeKeys=new Set();for(const item of paths){{const values=item.path||[];for(const id of values)if(id)nodeIds.add(id);for(let i=0;i<values.length-1;i++)edgeKeys.add(values[i]+'|||'+values[i+1])}}const visibleLinks=(data.links||[]).filter(link=>edgeKeys.has(link.source+'|||'+link.target));for(const link of visibleLinks){{nodeIds.add(link.source);nodeIds.add(link.target)}}return{{nodeIds,visibleLinks}}}}
function redraw(paths){{svg.replaceChildren();edgeEls=[];nodeEls=[];const graph=visibleGraph(paths),seen=new Set(),order=[];for(const id of [...declared,...ideal])if(graph.nodeIds.has(id)&&!seen.has(id)){{seen.add(id);order.push(id)}}for(const item of paths)for(const id of item.path||[])if(graph.nodeIds.has(id)&&!seen.has(id)){{seen.add(id);order.push(id)}}for(const id of graph.nodeIds)if(!seen.has(id)){{seen.add(id);order.push(id)}}svg.dataset.renderedNodeCount=String(order.length);svg.dataset.renderedLinkCount=String(graph.visibleLinks.length);if(!order.length){{svg.setAttribute('viewBox','0 0 1180 180');const t=document.createElementNS(NS,'text');t.setAttribute('x','20');t.setAttribute('y','40');t.textContent='本次无可展示流向';svg.appendChild(t);return}}const pos=new Map(),cols=Math.min(6,Math.max(2,order.length)),rows=Math.ceil(order.length/cols),canvasHeight=Math.max(560,120+rows*116),xGap=990/Math.max(cols-1,1);svg.setAttribute('viewBox',`0 0 1180 ${{canvasHeight}}`);order.forEach((id,i)=>pos.set(id,{{x:45+(i%cols)*xGap,y:55+Math.floor(i/cols)*116}}));for(const link of graph.visibleLinks){{const a=pos.get(link.source),b=pos.get(link.target);if(!a||!b)continue;const p=document.createElementNS(NS,'path'),mid=(a.x+b.x)/2,w=Number(link.task_count)||0,secondary=Number(link.share_of_total_tasks||0)<.01;p.setAttribute('d',`M${{a.x+122}},${{a.y+18}} C${{mid}},${{a.y+18}} ${{mid}},${{b.y+18}} ${{b.x}},${{b.y+18}}`);p.setAttribute('class','flow-link'+(secondary?' is-secondary':''));p.dataset.edge=`${{link.source}}|||${{link.target}}`;p.setAttribute('stroke-width',String(Math.max(2,Math.min(18,Math.sqrt(w||1)*1.7))));p.onclick=()=>show(`${{link.source}} → ${{link.target}}`,[['任务数',fmt(link.task_count)],['事件次数',fmt(link.transition_event_count)],['总任务占比',pct(link.share_of_total_tasks)],['来源流出占比',pct(link.share_of_source_outflow)],['耗时',dur(link.duration_seconds)]]);const title=document.createElementNS(NS,'title');title.textContent=`${{link.source}} → ${{link.target}}：${{w}} 个任务，${{pct(link.share_of_total_tasks)}}`;p.appendChild(title);svg.appendChild(p);edgeEls.push(p)}}order.forEach(id=>{{const p=pos.get(id),n=nodeById.get(id)||{{}},r=document.createElementNS(NS,'rect'),t=document.createElementNS(NS,'text'),title=document.createElementNS(NS,'title');r.setAttribute('x',p.x);r.setAttribute('y',p.y);r.setAttribute('width','122');r.setAttribute('height','36');r.setAttribute('rx','9');r.dataset.node=id;r.setAttribute('class','flow-node'+((n.error_task_count||0)>0?' has-error':'')+(exits.has(id)?' is-exit':''));r.onclick=()=>show(id,[['任务数',fmt(n.task_count)],['事件次数',fmt(n.event_count)],['任务覆盖',pct(n.share_of_total_tasks)],['报错任务',`${{fmt(n.error_task_count)}}（${{pct(n.error_task_share)}}）`],['节点耗时',dur(n.duration_seconds)],['退出任务',fmt((exits.get(id)||{{}}).task_count)]]);title.textContent=id;r.appendChild(title);t.setAttribute('x',p.x+61);t.setAttribute('y',p.y+55);t.setAttribute('text-anchor','middle');t.setAttribute('class','flow-label');t.textContent=String(id).slice(0,18);svg.append(r,t);nodeEls.push(r)}})}}
function highlight(path,chip){{document.querySelectorAll('.path-chip').forEach(x=>x.classList.remove('active'));if(chip)chip.classList.add('active');const values=path.path||[],nodes=new Set(values),keys=new Set(values.slice(0,-1).map((x,i)=>x+'|||'+values[i+1]));edgeEls.forEach(e=>{{e.classList.toggle('active',keys.has(e.dataset.edge));e.classList.toggle('muted',keys.size&&!keys.has(e.dataset.edge))}});nodeEls.forEach(e=>{{e.classList.toggle('active',nodes.has(e.dataset.node));e.classList.toggle('muted',nodes.size&&!nodes.has(e.dataset.node))}});const exitFacts=(data.exit_points||[]).filter(x=>nodes.has(x.node_id)).map(x=>`${{x.node_id}}：${{fmt(x.task_count)}} 个任务（${{x.outcome||'终止'}}）`),loopFacts=(data.backtracks||[]).filter(x=>JSON.stringify(x.path||[])===JSON.stringify(values)).map(x=>`${{(x.path||[]).join(' → ')}}：${{fmt(x.task_count)}} 个任务`),errorFacts=(data.error_by_step||[]).filter(x=>nodes.has(x.step)),errorEventFacts=errorFacts.map(x=>`${{x.step}}：${{fmt(x.error_event_count)}} 次`),errorTypeFacts=errorFacts.flatMap(x=>(x.error_types||[]).map(t=>`${{x.step}} / ${{t.type}}：${{fmt(t.event_count)}} 次`));show(path.kind||'真实路径',[['路径',values.join(' → ')],['任务数',fmt(path.task_count)],['事件次数',fmt(path.event_count)],['占比',pct(path.share)],['全程耗时',dur(path.duration_seconds)],['路径内退出明细',exitFacts.join('；')||'未提供'],['该路径折返/循环明细',loopFacts.join('；')||'未提供'],['路径节点报错事件',errorEventFacts.join('；')||'未提供'],['路径节点报错类型',errorTypeFacts.join('；')||'未提供'],['标记',path.label||path.kind||'真实路径']])}}
function pathRows(){{const mode=document.getElementById('path-filter').value,limit=Number(document.getElementById('path-limit').value),all=data.paths||[],source=mode==='all'?all:mode==='ideal'?(ideal.length?[{{path:ideal,kind:'正式理想路径',label:'来自已登记业务蓝图'}}]:[]):(data.top_paths||all),visible=source.slice(0,limit);list.innerHTML='';redraw(visible);if(summary){{const limited=source.length>visible.length?'；为保证可读性未一次绘制全部候选路径':'';summary.textContent=`当前绘制 ${{visible.length}} / ${{source.length}} 条路径，${{svg.dataset.renderedNodeCount||0}} 个节点，${{svg.dataset.renderedLinkCount||0}} 条连线${{limited}}`}}visible.forEach((p,i)=>{{const b=document.createElement('button');b.type='button';b.className='path-chip';p.kind=p.kind||(i===0?'最多真实路径':'真实路径');b.innerHTML=`${{p.kind}} · ${{fmt(p.task_count)}} <small>${{pct(p.share)}}</small>`;b.onclick=()=>highlight(p,b);list.appendChild(b)}});if(!list.children.length){{list.innerHTML='<span class="empty">当前没有可展示的正式理想路径；观察到的高频路径不会冒充理想路径。</span>';highlight({{path:[],kind:'无可高亮路径'}},null)}}else{{list.querySelector('.path-chip').click()}}}}
document.getElementById('path-filter').onchange=pathRows;document.getElementById('path-limit').onchange=pathRows;document.getElementById('path-reset').onclick=()=>highlight({{path:[],kind:'已清除高亮'}},null);pathRows();
}})();</script>
</main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--objective", required=True, type=Path)
    parser.add_argument("--package-output", required=True, type=Path)
    parser.add_argument("--source-ref")
    args = parser.parse_args()
    objective_path = args.objective.expanduser().resolve()
    package = load_json(objective_path)
    source_run_id = package["run"]["run_id"]
    spec_path = args.package_output.expanduser().resolve()
    spec = build_spec(package, _source_ref(objective_path, args.source_ref))
    atomic_write(spec_path, json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "status": "candidate_built",
                "source_run_id": source_run_id,
                "package": str(spec_path),
                "next_step": "publish_with_visualization_request",
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
