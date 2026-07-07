#!/usr/bin/env python3
"""验证并归一化 UCATS 界面证据评估报告。

本脚本故意只使用 Python 标准库，便于在轻量 skill、CI 与批量评估环境中运行。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DIMENSIONS = ("usability", "clarity", "task_completion", "acceptance", "stability")
REQUIRED_DIMENSIONS = ("clarity",)
WEIGHTS = {
    "usability": 0.20,
    "clarity": 0.20,
    "task_completion": 0.25,
    "acceptance": 0.15,
    "stability": 0.20,
}
CONFIDENCE = {"high", "medium", "low"}
SEVERITY = {"Critical", "High", "Medium", "Low"}
INPUT_TYPES = {"browser", "screenshot", "mixed"}
UI_SOURCE_FIELDS = ("screenshots", "dom_snapshots", "accessibility_snapshots", "runtime_events")
SUPPLEMENTAL_SOURCE_FIELDS = ("behavior_metrics",)
SOURCE_FIELDS = UI_SOURCE_FIELDS + SUPPLEMENTAL_SOURCE_FIELDS
GENERATION_METHODS = {
    "browser": "auto_from_browser_and_prompt",
    "screenshot": "auto_from_screenshot_and_prompt",
    "mixed": "auto_from_mixed_and_prompt",
}
WALKTHROUGH_PRIMARY_FIELDS = ("information_presentation", "operation_experience")
WALKTHROUGH_STATUS = {"applicable", "not_applicable", "evidence_insufficient"}
EVIDENCE_ROOTS = {"input", "dsl"}
PROHIBITED_DSL_EVIDENCE_PARTS = (".task_context", ".generation", ".source")
DSL_EVIDENCE_PREFIXES = ("dsl.pages[", "dsl.flow", "dsl.interactions[", "dsl.uncertain[")
SCALE_LEVEL_POINTS = {level: 1 / (2 ** (level - 1)) for level in range(1, 7)}
VALID_CRITERION_IDS = {
    "E1-01", "E1-02", "E1-03", "E1-04",
    "E2-01", "E2-02",
    "E3-01", "E3-02", "E3-03",
    "E4-01", "E4-02", "E4-03",
    "E5-01", "E5-02", "E5-03",
    "E6-01", "E6-02", "E6-03",
    "E7-01", "E7-02",
    "E8-01", "E8-02", "E8-03",
    "E9-01", "E9-02", "E9-03",
    "E10-01", "E10-02", "E10-03", "E10-04",
    "E11-01", "E11-02", "E11-03",
}
PAGE_SOURCE_REF_FIELDS = {
    "dom_ref": "dom_snapshots",
    "accessibility_ref": "accessibility_snapshots",
    "runtime_ref": "runtime_events",
    "screenshot_ref": "screenshots",
}


class ReportError(Exception):
    """报告数据无效时抛出。"""


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ReportError(f"文件不存在：{path}") from exc
    except json.JSONDecodeError as exc:
        raise ReportError(f"JSON 无效：{exc}") from exc
    if not isinstance(data, dict):
        raise ReportError("报告根节点必须是对象。")
    return data


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def clamp_score(value: float) -> int:
    bounded = max(0.0, min(100.0, float(value)))
    return int(bounded + 0.5)


def path_exists(data: Any, path: str) -> bool:
    if not isinstance(path, str) or not path:
        return False
    current = data
    for part in path.split("."):
        if not part:
            return False
        name_end = part.find("[")
        if name_end == -1:
            name = part
            indexes: list[int] = []
        else:
            name = part[:name_end]
            indexes = []
            rest = part[name_end:]
            while rest:
                if not rest.startswith("["):
                    return False
                close = rest.find("]")
                if close == -1:
                    return False
                raw_index = rest[1:close]
                if not raw_index.isdigit():
                    return False
                indexes.append(int(raw_index))
                rest = rest[close + 1 :]
        if not name:
            return False
        if isinstance(current, dict):
            if name not in current:
                return False
            current = current[name]
        else:
            return False
        for index in indexes:
            if not isinstance(current, list) or index >= len(current):
                return False
            current = current[index]
    return True


def validate_paths(report: dict[str, Any], paths: Any, label: str, errors: list[str], *, min_items: bool = False) -> None:
    require(isinstance(paths, list), f"{label} 必须是列表。", errors)
    if not isinstance(paths, list):
        return
    if min_items:
        require(len(paths) > 0, f"{label} 必须至少包含一个 evidence 路径。", errors)
    for idx, path in enumerate(paths):
        require(isinstance(path, str) and bool(path), f"{label}[{idx}] 必须是非空路径。", errors)
        if not isinstance(path, str) or not path:
            continue
        root = path.split(".", 1)[0].split("[", 1)[0]
        require(root in EVIDENCE_ROOTS, f"{label}[{idx}] 必须以 input 或 dsl 开头：{path}。", errors)
        if root == "input":
            require(path.startswith("input.behavior_metrics["), f"{label}[{idx}] 只有具体的 input.behavior_metrics[n] 可作为 input 证据，任务上下文不能直接当界面证据：{path}。", errors)
        if root == "dsl":
            require(path.startswith(DSL_EVIDENCE_PREFIXES), f"{label}[{idx}] 必须指向具体 DSL 页面、流程、交互或 uncertain 项：{path}。", errors)
            for part in PROHIBITED_DSL_EVIDENCE_PARTS:
                require(part not in path, f"{label}[{idx}] 不能把 DSL 上下文或元数据当界面证据：{path}。", errors)
        require(path_exists(report, path), f"{label}[{idx}] 指向的 evidence 路径不存在：{path}。", errors)


def validate_adjustment(report: dict[str, Any], container: dict[str, Any], label: str, errors: list[str]) -> float:
    adjustment = container.get("adjustment", 0)
    require(isinstance(adjustment, (int, float)), f"{label}.adjustment 必须是数字。", errors)
    if isinstance(adjustment, (int, float)) and abs(adjustment) > 0:
        require(bool(container.get("adjustment_reason")), f"{label}.adjustment 非 0 时必须填写 adjustment_reason。", errors)
        validate_paths(report, container.get("adjustment_evidence"), f"{label}.adjustment_evidence", errors, min_items=True)
        return float(adjustment)
    return 0.0


def validate_table_deduction(deduction: dict[str, Any], label: str, points: Any, errors: list[str], warnings: list[str]) -> None:
    table_fields = ("problem_count", "scale_level", "points_per_problem")
    if not any(field in deduction for field in table_fields):
        return

    problem_count = deduction.get("problem_count")
    scale_level = deduction.get("scale_level")
    points_per_problem = deduction.get("points_per_problem")

    valid_problem_count = isinstance(problem_count, int) and not isinstance(problem_count, bool) and problem_count >= 0
    valid_scale_level = isinstance(scale_level, int) and not isinstance(scale_level, bool) and scale_level in SCALE_LEVEL_POINTS

    require(valid_problem_count, f"{label}.problem_count 必须是大于等于 0 的整数。", errors)
    require(valid_scale_level, f"{label}.scale_level 必须是 1 到 6 的整数。", errors)

    for field in ("criterion_id", "unit_scope", "state_scope", "expected", "actual", "evidence_test"):
        require(isinstance(deduction.get(field), str) and bool(deduction.get(field).strip()), f"{label}.{field} 是表格法扣分必填项，必须用于证明问题单元颗粒度和客观失败条件。", errors)
    criterion_id = deduction.get("criterion_id")
    if isinstance(criterion_id, str) and criterion_id:
        require(criterion_id in VALID_CRITERION_IDS, f"{label}.criterion_id 不在已定义客观检查标准中：{criterion_id}。", errors)

    if not valid_scale_level or not valid_problem_count:
        return

    expected_points_per_problem = SCALE_LEVEL_POINTS[scale_level]
    if points_per_problem is not None:
        require(isinstance(points_per_problem, (int, float)) and points_per_problem >= 0, f"{label}.points_per_problem 必须是大于等于 0 的数字。", errors)
        if isinstance(points_per_problem, (int, float)):
            require(
                abs(float(points_per_problem) - expected_points_per_problem) <= 0.0001,
                f"{label}.points_per_problem 应由 scale_level={scale_level} 自动得到 {expected_points_per_problem:g}。",
                errors,
            )

    if isinstance(points, (int, float)):
        expected_points = problem_count * expected_points_per_problem
        require(
            abs(float(points) - expected_points) <= 0.01,
            f"{label}.points 应等于 problem_count * points_per_problem，即 {problem_count} * {expected_points_per_problem:g} = {expected_points:g}。",
            errors,
        )
    if scale_level >= 4 and not deduction.get("scale_rationale"):
        warnings.append(f"{label}.scale_level 为 {scale_level}，高档位会显著稀释扣分；建议填写 scale_rationale。")


def contains_behavior_metric_evidence(paths: Any) -> bool:
    return isinstance(paths, list) and any(isinstance(path, str) and path.startswith("input.behavior_metrics[") for path in paths)


def collect_issue_ids(report: dict[str, Any]) -> set[str]:
    issue_ids: set[str] = set()
    issues = report.get("issues")
    if isinstance(issues, list):
        for issue in issues:
            if isinstance(issue, dict) and isinstance(issue.get("id"), str):
                issue_ids.add(issue["id"])
    return issue_ids


def collect_issue_dimensions(report: dict[str, Any]) -> dict[str, str]:
    issue_dimensions: dict[str, str] = {}
    issues = report.get("issues")
    if isinstance(issues, list):
        for issue in issues:
            if isinstance(issue, dict) and isinstance(issue.get("id"), str) and isinstance(issue.get("dimension"), str):
                issue_dimensions[issue["id"]] = issue["dimension"]
    return issue_dimensions


def validate_walkthrough_primary(
    report: dict[str, Any],
    field: str,
    primary: dict[str, Any],
    issue_ids: set[str],
    issue_dimensions: dict[str, str],
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any] | None:
    weight = primary.get("weight")
    score = primary.get("score")
    require(isinstance(weight, (int, float)) and 0 <= weight <= 1, f"ucats.walkthrough.{field}.weight 必须是 0 到 1 的数字。", errors)
    require(isinstance(score, int) and 0 <= score <= 100, f"ucats.walkthrough.{field}.score 必须是 0 到 100 的整数。", errors)
    status = primary.get("status", "applicable")
    require(status in WALKTHROUGH_STATUS, f"ucats.walkthrough.{field}.status 无效。", errors)
    involved_elements = primary.get("involved_elements")
    require(isinstance(involved_elements, list), f"ucats.walkthrough.{field}.involved_elements 必须是列表。", errors)
    validate_paths(report, primary.get("evidence"), f"ucats.walkthrough.{field}.evidence", errors, min_items=status != "not_applicable")

    elements = primary.get("elements")
    require(isinstance(elements, list) and len(elements) > 0, f"ucats.walkthrough.{field}.elements 必须至少包含一个检查元素。", errors)
    if not isinstance(elements, list):
        return None

    active_weight_total = 0.0
    weighted_score = 0.0
    active_ids: list[str] = []
    active_weights: list[tuple[str, float]] = []
    seen_element_ids: set[str] = set()
    has_evidence_insufficient_element = False
    for idx, element in enumerate(elements):
        label = f"ucats.walkthrough.{field}.elements[{idx}]"
        require(isinstance(element, dict), f"{label} 必须是对象。", errors)
        if not isinstance(element, dict):
            continue
        element_id = element.get("id")
        require(isinstance(element_id, str) and bool(element_id), f"{label}.id 是必填项。", errors)
        if isinstance(element_id, str):
            require(element_id not in seen_element_ids, f"ucats.walkthrough.{field}.elements 中 id 不能重复：{element_id}。", errors)
            seen_element_ids.add(element_id)
        element_status = element.get("status")
        require(element_status in WALKTHROUGH_STATUS, f"{label}.status 无效。", errors)
        if element_status == "evidence_insufficient":
            has_evidence_insufficient_element = True
        element_weight = element.get("weight")
        require(isinstance(element_weight, (int, float)) and 0 <= element_weight <= 1, f"{label}.weight 必须是 0 到 1 的数字。", errors)
        element_score = element.get("score")
        require(isinstance(element_score, int) and 0 <= element_score <= 100, f"{label}.score 必须是 0 到 100 的整数。", errors)
        validate_paths(report, element.get("evidence"), f"{label}.evidence", errors, min_items=element_status != "not_applicable")

        deductions = element.get("deductions")
        require(isinstance(deductions, list), f"{label}.deductions 必须是列表。", errors)
        deduction_points = 0.0
        seen_deduction_issue_ids: set[str] = set()
        if isinstance(deductions, list):
            for deduction_idx, deduction in enumerate(deductions):
                deduction_label = f"{label}.deductions[{deduction_idx}]"
                require(isinstance(deduction, dict), f"{deduction_label} 必须是对象。", errors)
                if not isinstance(deduction, dict):
                    continue
                issue_id = deduction.get("issue_id")
                require(isinstance(issue_id, str) and bool(issue_id), f"{deduction_label}.issue_id 是必填项。", errors)
                if isinstance(issue_id, str):
                    require(issue_id in issue_ids, f"{deduction_label}.issue_id 未在 issues 中定义：{issue_id}。", errors)
                    if issue_id in issue_dimensions:
                        require(issue_dimensions[issue_id] == "clarity", f"{deduction_label}.issue_id 引用的是界面走查问题，issues[].dimension 必须为 clarity：{issue_id}。", errors)
                    require(issue_id not in seen_deduction_issue_ids, f"{label}.deductions 不应重复引用同一个 issue_id：{issue_id}。", errors)
                    seen_deduction_issue_ids.add(issue_id)
                points = deduction.get("points")
                require(isinstance(points, (int, float)) and 0 <= points <= 100, f"{deduction_label}.points 必须是 0 到 100 的数字。", errors)
                if isinstance(points, (int, float)):
                    deduction_points += points
                validate_table_deduction(deduction, deduction_label, points, errors, warnings)
                require(bool(deduction.get("reason")), f"{deduction_label}.reason 是必填项。", errors)
                if "evidence" in deduction:
                    validate_paths(report, deduction.get("evidence"), f"{deduction_label}.evidence", errors)

        adjustment = validate_adjustment(report, element, label, errors)
        raw_element_score = 100 - deduction_points + adjustment
        expected_element_score = clamp_score(raw_element_score)
        if raw_element_score < 0:
            warnings.append(f"{label}.score 原始分为 {raw_element_score:g}，已按下限截断为 0；请复核 problem_count、scale_level 和重复计数。")
        if isinstance(element_score, int):
            require(element_score == expected_element_score, f"{label}.score 应由 deductions 和 adjustment 自动重算为 {expected_element_score}。", errors)

        if element_status == "not_applicable":
            require(element_weight == 0, f"{label}.status 为 not_applicable 时 weight 必须为 0。", errors)
            require(deductions == [], f"{label}.status 为 not_applicable 时 deductions 必须为空。", errors)
            require(element_score == 100, f"{label}.status 为 not_applicable 时 score 必须为 100。", errors)
            require(adjustment == 0, f"{label}.status 为 not_applicable 时 adjustment 必须为 0。", errors)
        elif isinstance(element_weight, (int, float)):
            active_weight_total += element_weight
            active_weights.append((label, float(element_weight)))
            if isinstance(element_score, int):
                weighted_score += element_score * element_weight
            if isinstance(element_id, str):
                active_ids.append(element_id)

    if active_ids:
        require(status != "not_applicable", f"ucats.walkthrough.{field}.status 为 not_applicable 时不能包含涉及元素。", errors)
        if has_evidence_insufficient_element:
            require(status == "evidence_insufficient", f"ucats.walkthrough.{field} 包含证据不足元素时 status 必须为 evidence_insufficient。", errors)
        else:
            require(status == "applicable", f"ucats.walkthrough.{field} 所有涉及元素证据充分时 status 必须为 applicable。", errors)
        require(abs(active_weight_total - 1.0) <= 0.01, f"ucats.walkthrough.{field}.elements 中涉及元素的 weight 之和必须为 1。", errors)
        expected_element_weight = 1 / len(active_ids)
        for label, element_weight in active_weights:
            require(abs(element_weight - expected_element_weight) <= 0.01, f"{label}.weight 必须在涉及元素之间均分，期望为 {expected_element_weight:.4f}。", errors)
    else:
        require(status == "not_applicable", f"ucats.walkthrough.{field} 没有涉及元素时 status 必须为 not_applicable。", errors)
        require(primary.get("weight") == 0, f"ucats.walkthrough.{field} 没有涉及元素时一级维度 weight 必须为 0。", errors)
        require(score == 100, f"ucats.walkthrough.{field} 没有涉及元素时 score 必须为 100。", errors)

    if isinstance(involved_elements, list):
        require(len(involved_elements) == len(set(involved_elements)), f"ucats.walkthrough.{field}.involved_elements 不应包含重复 id。", errors)
        require(set(involved_elements) == set(active_ids), f"ucats.walkthrough.{field}.involved_elements 必须等于非 not_applicable 元素 id 集合。", errors)

    primary_adjustment = validate_adjustment(report, primary, f"ucats.walkthrough.{field}", errors)
    if not active_ids:
        require(primary_adjustment == 0, f"ucats.walkthrough.{field} 没有涉及元素时 adjustment 必须为 0。", errors)
    expected_primary_score = clamp_score(weighted_score + primary_adjustment)
    if isinstance(score, int):
        require(score == expected_primary_score, f"ucats.walkthrough.{field}.score 应由 elements 自动重算为 {expected_primary_score}。", errors)
    return {"score": expected_primary_score, "active_count": len(active_ids)}


def validate(report: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    issue_ids = collect_issue_ids(report)
    issue_dimensions = collect_issue_dimensions(report)

    require(report.get("report_version") is not None, "缺少 report_version。", errors)

    input_data = report.get("input")
    require(isinstance(input_data, dict), "缺少 input 对象。", errors)
    input_type = None
    input_source_refs: set[str] = set()
    ui_source_refs: set[str] = set()
    source_types_by_ref: dict[str, str] = {}
    has_behavior_metrics = False
    if isinstance(input_data, dict):
        input_type = input_data.get("type")
        require(input_type in INPUT_TYPES, "input.type 必须是 browser、screenshot 或 mixed。", errors)

        source_counts: dict[str, int] = {}
        for field in SOURCE_FIELDS:
            sources = input_data.get(field, [])
            require(isinstance(sources, list), f"input.{field} 必须是列表。", errors)
            if not isinstance(sources, list):
                continue
            source_counts[field] = len(sources)
            for idx, source in enumerate(sources):
                require(isinstance(source, dict), f"input.{field}[{idx}] 必须是对象。", errors)
                if isinstance(source, dict):
                    source_ref = source.get("ref")
                    require(bool(source_ref), f"input.{field}[{idx}].ref 是必填项。", errors)
                    if isinstance(source_ref, str):
                        require(source_ref not in input_source_refs, f"input source ref 不能重复：{source_ref}。", errors)
                        input_source_refs.add(source_ref)
                        source_types_by_ref[source_ref] = field
                        if field in UI_SOURCE_FIELDS:
                            ui_source_refs.add(source_ref)

        has_screenshot = source_counts.get("screenshots", 0) > 0
        has_browser_source = any(source_counts.get(field, 0) > 0 for field in ("dom_snapshots", "accessibility_snapshots", "runtime_events"))
        has_behavior_metrics = source_counts.get("behavior_metrics", 0) > 0
        has_ui_source = has_screenshot or has_browser_source
        require(has_ui_source, "input 必须至少包含截图或浏览器结构化证据；行为数据只能作为补充来源。", errors)
        if input_type == "screenshot":
            require(has_screenshot, "input.type 为 screenshot 时，input.screenshots 必须至少包含一张截图。", errors)
        if input_type == "browser":
            require(has_browser_source, "input.type 为 browser 时，必须包含 DOM、Accessibility 或 runtime 来源。", errors)
        if input_type == "mixed":
            require(has_screenshot and has_browser_source, "input.type 为 mixed 时，必须同时包含截图和浏览器结构化来源。", errors)

    dsl = report.get("dsl")
    require(isinstance(dsl, dict), "缺少 dsl 对象。", errors)
    if isinstance(dsl, dict):
        pages = dsl.get("pages")
        require(isinstance(pages, list) and len(pages) > 0, "dsl.pages 必须至少包含一个页面。", errors)
        seen_page_ids: set[str] = set()
        if isinstance(pages, list):
            for idx, page in enumerate(pages):
                require(isinstance(page, dict), f"dsl.pages[{idx}] 必须是对象。", errors)
                if not isinstance(page, dict):
                    continue
                page_id = page.get("page_id")
                require(bool(page_id), f"dsl.pages[{idx}].page_id 是必填项。", errors)
                if isinstance(page_id, str):
                    require(page_id not in seen_page_ids, f"dsl.pages[].page_id 不能重复：{page_id}。", errors)
                    seen_page_ids.add(page_id)
                generation = page.get("generation")
                require(isinstance(generation, dict), f"dsl.pages[{idx}].generation 是必填对象。", errors)
                if isinstance(generation, dict):
                    method = generation.get("method")
                    require(method in GENERATION_METHODS.values(), f"dsl.pages[{idx}].generation.method 无效。", errors)
                    if input_type in GENERATION_METHODS:
                        require(method == GENERATION_METHODS[input_type], f"dsl.pages[{idx}].generation.method 必须匹配 input.type。", errors)
                    evidence_sources = generation.get("evidence_sources")
                    require(isinstance(evidence_sources, list) and len(evidence_sources) > 0, f"dsl.pages[{idx}].generation.evidence_sources 必须至少包含一个来源。", errors)
                    if isinstance(evidence_sources, list):
                        require(len(evidence_sources) == len(set(evidence_sources)), f"dsl.pages[{idx}].generation.evidence_sources 不应包含重复来源。", errors)
                        for source_ref in evidence_sources:
                            require(source_ref in input_source_refs, f"dsl.pages[{idx}].generation.evidence_sources 包含未知来源：{source_ref}。", errors)
                            require(source_ref in ui_source_refs, f"dsl.pages[{idx}].generation.evidence_sources 只能包含截图、DOM、Accessibility 或 runtime 主证据，不能用行为数据生成页面 DSL：{source_ref}。", errors)
                        require(
                            any(source_ref in ui_source_refs for source_ref in evidence_sources),
                            f"dsl.pages[{idx}].generation.evidence_sources 必须至少包含一个截图、DOM、Accessibility 或 runtime 主证据。",
                            errors,
                        )
                    context_fields_used = generation.get("context_fields_used")
                    require(isinstance(context_fields_used, list), f"dsl.pages[{idx}].generation.context_fields_used 必须是列表。", errors)
                    context_only_claims = generation.get("context_only_claims", [])
                    require(isinstance(context_only_claims, list), f"dsl.pages[{idx}].generation.context_only_claims 必须是列表。", errors)
                    conflicts = generation.get("conflicts", [])
                    require(isinstance(conflicts, list), f"dsl.pages[{idx}].generation.conflicts 必须是列表。", errors)
                source = page.get("source")
                require(isinstance(source, dict), f"dsl.pages[{idx}].source 是必填对象。", errors)
                if isinstance(source, dict):
                    source_mode = source.get("mode")
                    require(source_mode in INPUT_TYPES, f"dsl.pages[{idx}].source.mode 必须是 browser、screenshot 或 mixed。", errors)
                    if input_type in INPUT_TYPES:
                        require(source_mode == input_type, f"dsl.pages[{idx}].source.mode 必须匹配 input.type。", errors)
                    page_ref_values: dict[str, str] = {}
                    for ref_field, expected_source_type in PAGE_SOURCE_REF_FIELDS.items():
                        ref_value = source.get(ref_field)
                        if ref_value is None:
                            continue
                        require(isinstance(ref_value, str) and bool(ref_value), f"dsl.pages[{idx}].source.{ref_field} 必须是字符串或 null。", errors)
                        if isinstance(ref_value, str) and ref_value:
                            page_ref_values[ref_field] = ref_value
                            require(ref_value in input_source_refs, f"dsl.pages[{idx}].source.{ref_field} 包含未知来源：{ref_value}。", errors)
                            require(source_types_by_ref.get(ref_value) == expected_source_type, f"dsl.pages[{idx}].source.{ref_field} 来源类型不匹配：{ref_value}。", errors)
                    has_page_browser_ref = any(field in page_ref_values for field in ("dom_ref", "accessibility_ref", "runtime_ref"))
                    has_page_screenshot_ref = "screenshot_ref" in page_ref_values
                    if source_mode == "browser":
                        require(has_page_browser_ref, f"dsl.pages[{idx}].source.mode 为 browser 时必须包含 DOM、Accessibility 或 runtime ref。", errors)
                    if source_mode == "screenshot":
                        require(has_page_screenshot_ref, f"dsl.pages[{idx}].source.mode 为 screenshot 时必须包含 screenshot_ref。", errors)
                    if source_mode == "mixed":
                        require(has_page_browser_ref and has_page_screenshot_ref, f"dsl.pages[{idx}].source.mode 为 mixed 时必须同时包含浏览器 ref 和 screenshot_ref。", errors)
        uncertain = dsl.get("uncertain", [])
        if isinstance(uncertain, list) and len(uncertain) >= 5:
            warnings.append("DSL 中 uncertain 项较多；建议人工复核。")

    ucats = report.get("ucats")
    require(isinstance(ucats, dict), "缺少 ucats 对象。", errors)
    dimensions = ucats.get("dimensions") if isinstance(ucats, dict) else None
    walkthrough = ucats.get("walkthrough") if isinstance(ucats, dict) else None
    require(isinstance(walkthrough, dict), "缺少 ucats.walkthrough 对象。", errors)
    walkthrough_overall = None
    if isinstance(walkthrough, dict):
        primary_scores: dict[str, int] = {}
        primary_weights: dict[str, float] = {}
        primary_active: dict[str, bool] = {}
        for field in WALKTHROUGH_PRIMARY_FIELDS:
            primary = walkthrough.get(field)
            require(isinstance(primary, dict), f"ucats.walkthrough.{field} 必须是对象。", errors)
            if not isinstance(primary, dict):
                continue
            primary_result = validate_walkthrough_primary(report, field, primary, issue_ids, issue_dimensions, errors, warnings)
            if isinstance(primary_result, dict) and isinstance(primary_result.get("score"), int):
                primary_scores[field] = primary_result["score"]
                primary_active[field] = primary_result.get("active_count", 0) > 0
            weight = primary.get("weight")
            if isinstance(weight, (int, float)):
                primary_weights[field] = float(weight)
        walkthrough_overall = walkthrough.get("overall_score")
        require(isinstance(walkthrough_overall, int) and 0 <= walkthrough_overall <= 100, "ucats.walkthrough.overall_score 必须是 0 到 100 的整数。", errors)
        if len(primary_scores) == len(WALKTHROUGH_PRIMARY_FIELDS):
            require(any(primary_active.get(field, False) for field in WALKTHROUGH_PRIMARY_FIELDS), "ucats.walkthrough 至少要有一个一级维度涉及当前任务。", errors)
            if primary_active.get("information_presentation") and primary_active.get("operation_experience"):
                require(abs(primary_weights.get("information_presentation", 0) - 0.35) <= 0.01, "信息呈现和操作体验都涉及时，information_presentation.weight 必须为 0.35。", errors)
                require(abs(primary_weights.get("operation_experience", 0) - 0.65) <= 0.01, "信息呈现和操作体验都涉及时，operation_experience.weight 必须为 0.65。", errors)
            elif primary_active.get("information_presentation"):
                require(abs(primary_weights.get("information_presentation", 0) - 1.0) <= 0.01, "只有信息呈现涉及时，information_presentation.weight 必须为 1。", errors)
                require(abs(primary_weights.get("operation_experience", 0)) <= 0.01, "只有信息呈现涉及时，operation_experience.weight 必须为 0。", errors)
            elif primary_active.get("operation_experience"):
                require(abs(primary_weights.get("operation_experience", 0) - 1.0) <= 0.01, "只有操作体验涉及时，operation_experience.weight 必须为 1。", errors)
                require(abs(primary_weights.get("information_presentation", 0)) <= 0.01, "只有操作体验涉及时，information_presentation.weight 必须为 0。", errors)

            total_weight = sum(primary_weights.get(field, 0) for field in WALKTHROUGH_PRIMARY_FIELDS)
            require(abs(total_weight - 1.0) <= 0.01, "ucats.walkthrough 一级维度 weight 之和必须为 1。", errors)
            if total_weight > 0:
                expected_walkthrough_overall = clamp_score(
                    sum(primary_scores[field] * primary_weights.get(field, 0) for field in WALKTHROUGH_PRIMARY_FIELDS) / total_weight
                )
                if isinstance(walkthrough_overall, int):
                    require(walkthrough_overall == expected_walkthrough_overall, f"ucats.walkthrough.overall_score 应自动重算为 {expected_walkthrough_overall}。", errors)
    require(isinstance(dimensions, dict), "缺少 ucats.dimensions 对象。", errors)
    if isinstance(dimensions, dict):
        for name in REQUIRED_DIMENSIONS:
            require(isinstance(dimensions.get(name), dict), f"缺少必需维度：{name}。", errors)
        assessed_dimensions: set[str] = set()
        for name in DIMENSIONS:
            dim = dimensions.get(name)
            if dim is None:
                continue
            require(isinstance(dim, dict), f"ucats.dimensions.{name} 必须是对象。", errors)
            if not isinstance(dim, dict):
                continue
            assessed_dimensions.add(name)
            score = dim.get("score")
            require(isinstance(score, int) and 0 <= score <= 100, f"{name}.score 必须是 0 到 100 的整数。", errors)
            require(dim.get("confidence") in CONFIDENCE, f"{name}.confidence 必须是 high、medium 或 low。", errors)
            evidence = dim.get("evidence")
            require(isinstance(evidence, list) and len(evidence) > 0, f"{name}.evidence 必须至少包含一个路径。", errors)
            validate_paths(report, evidence, f"ucats.dimensions.{name}.evidence", errors, min_items=True)
            if name != "clarity":
                require(contains_behavior_metric_evidence(evidence), f"{name} 不能使用界面走查检查项评分；若评估该 UCATS 维度，必须引用 input.behavior_metrics[n] 等独立产品/行为证据。", errors)
            require(bool(dim.get("rationale")), f"{name}.rationale 是必填项。", errors)
        clarity = dimensions.get("clarity")
        if isinstance(clarity, dict) and isinstance(walkthrough_overall, int):
            require(clarity.get("score") == walkthrough_overall, "界面走查分只对应 UCATS clarity，ucats.dimensions.clarity.score 必须等于 ucats.walkthrough.overall_score。", errors)
        task_completion = dimensions.get("task_completion")
        if isinstance(task_completion, dict) and task_completion.get("confidence") == "low":
            warnings.append("Task Completion 置信度为 low；请转人工复核。")
        dimensions_have_scores = all(
            isinstance(dimensions.get(name), dict) and isinstance(dimensions[name].get("score"), int)
            for name in DIMENSIONS
        )
        if dimensions_have_scores:
            dimensions_overall = compute_overall(report)
            reported_overall = ucats.get("overall_score") if isinstance(ucats, dict) else None
            if reported_overall is not None:
                require(reported_overall == dimensions_overall, f"ucats.overall_score 应由五维分数自动重算为 {dimensions_overall}。", errors)
            reported_gate = ucats.get("gate") if isinstance(ucats, dict) else None
            if reported_gate is not None:
                expected_gate = compute_gate(report, dimensions_overall)
                require(reported_gate == expected_gate, f"ucats.gate 应由总分、严重度和置信度自动重算为 {expected_gate}。", errors)
        else:
            reported_overall = ucats.get("overall_score") if isinstance(ucats, dict) else None
            require(reported_overall in (None, ), "未提供五个 UCATS 维度的独立证据时，不能输出 ucats.overall_score；界面走查分只作为 clarity.score。", errors)
            reported_gate = ucats.get("gate") if isinstance(ucats, dict) else None
            if reported_gate is not None:
                expected_gate = compute_gate(report, None)
                require(reported_gate == expected_gate, f"ucats.gate 应由 clarity 分、严重度和置信度自动重算为 {expected_gate}。", errors)

    issues = report.get("issues")
    require(isinstance(issues, list), "issues 必须是列表。", errors)
    if isinstance(issues, list):
        seen_issue_ids: set[str] = set()
        for idx, issue in enumerate(issues):
            require(isinstance(issue, dict), f"issues[{idx}] 必须是对象。", errors)
            if not isinstance(issue, dict):
                continue
            for field in ("id", "dimension", "title", "observation", "impact"):
                require(bool(issue.get(field)), f"issues[{idx}].{field} 是必填项。", errors)
            issue_id = issue.get("id")
            if isinstance(issue_id, str):
                require(issue_id not in seen_issue_ids, f"issues[].id 不能重复：{issue_id}。", errors)
                seen_issue_ids.add(issue_id)
            require(issue.get("severity") in SEVERITY, f"issues[{idx}].severity 无效。", errors)
            evidence = issue.get("evidence")
            require(isinstance(evidence, list) and len(evidence) > 0, f"issues[{idx}].evidence 必须至少包含一个路径。", errors)
            validate_paths(report, evidence, f"issues[{idx}].evidence", errors, min_items=True)
            source_refs = issue.get("source_refs")
            has_source_refs = isinstance(source_refs, list) and len(source_refs) > 0
            require(has_source_refs, f"issues[{idx}].source_refs 必须是非空列表。", errors)
            if has_source_refs:
                require(len(source_refs) == len(set(source_refs)), f"issues[{idx}].source_refs 不应包含重复来源。", errors)
                for source_ref in source_refs:
                    require(source_ref in input_source_refs, f"issues[{idx}].source_refs 包含未知来源：{source_ref}。", errors)

    recommendations = report.get("recommendations")
    require(isinstance(recommendations, list), "recommendations 必须是列表。", errors)
    covered_issue_ids: set[str] = set()
    if isinstance(recommendations, list):
        seen_recommendation_ids: set[str] = set()
        for idx, recommendation in enumerate(recommendations):
            require(isinstance(recommendation, dict), f"recommendations[{idx}] 必须是对象。", errors)
            if not isinstance(recommendation, dict):
                continue
            for field in ("id", "priority", "title", "expected_impact", "effort"):
                require(bool(recommendation.get(field)), f"recommendations[{idx}].{field} 是必填项。", errors)
            recommendation_id = recommendation.get("id")
            if isinstance(recommendation_id, str):
                require(recommendation_id not in seen_recommendation_ids, f"recommendations[].id 不能重复：{recommendation_id}。", errors)
                seen_recommendation_ids.add(recommendation_id)
            steps = recommendation.get("steps")
            require(isinstance(steps, list) and len(steps) > 0, f"recommendations[{idx}].steps 必须至少包含一个步骤。", errors)
            target_issue_ids = recommendation.get("target_issue_ids", [])
            require(isinstance(target_issue_ids, list) and len(target_issue_ids) > 0, f"recommendations[{idx}].target_issue_ids 必须是非空列表。", errors)
            if isinstance(target_issue_ids, list):
                require(len(target_issue_ids) == len(set(target_issue_ids)), f"recommendations[{idx}].target_issue_ids 不应包含重复 issue。", errors)
                for issue_id in target_issue_ids:
                    require(issue_id in issue_ids, f"recommendations[{idx}].target_issue_ids 包含未知 issue：{issue_id}。", errors)
                    if isinstance(issue_id, str):
                        covered_issue_ids.add(issue_id)
        uncovered_issue_ids = sorted(issue_ids - covered_issue_ids)
        require(not uncovered_issue_ids, f"每个 issue 都必须至少被一个 recommendation.target_issue_ids 覆盖，未覆盖：{', '.join(uncovered_issue_ids)}。", errors)

    return errors, warnings


def compute_overall(report: dict[str, Any]) -> int | None:
    dimensions = report["ucats"]["dimensions"]
    if not all(isinstance(dimensions.get(name), dict) and isinstance(dimensions[name].get("score"), int) for name in DIMENSIONS):
        return None
    total = 0.0
    for name, weight in WEIGHTS.items():
        total += dimensions[name]["score"] * weight
    return int(round(total))


def compute_clarity_score(report: dict[str, Any]) -> int | None:
    clarity = report.get("ucats", {}).get("dimensions", {}).get("clarity")
    if isinstance(clarity, dict) and isinstance(clarity.get("score"), int):
        return clarity["score"]
    walkthrough_score = report.get("ucats", {}).get("walkthrough", {}).get("overall_score")
    if isinstance(walkthrough_score, int):
        return walkthrough_score
    return None


def compute_gate(report: dict[str, Any], overall: int | None = None) -> str:
    if overall is None:
        overall = compute_overall(report)
    score_basis = overall if overall is not None else compute_clarity_score(report)
    if score_basis is None:
        score_basis = 0

    dimensions = report.get("ucats", {}).get("dimensions", {})
    task_completion = dimensions.get("task_completion", {})
    issues = report.get("issues", [])
    critical_count = sum(1 for issue in issues if issue.get("severity") == "Critical")
    high_count = sum(1 for issue in issues if issue.get("severity") == "High")

    if score_basis < 65 or critical_count > 0 or task_completion.get("confidence") == "low":
        return "fail"
    if score_basis < 80 or high_count >= 1 or any(dim.get("confidence") == "medium" for dim in dimensions.values()):
        return "review"
    return "pass"


def normalize(report: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    overall = compute_overall(report)
    gate = compute_gate(report, overall)
    ucats = report.setdefault("ucats", {})
    clarity_score = compute_clarity_score(report)
    if clarity_score is not None:
        ucats["clarity_score"] = clarity_score
    ucats["overall_score"] = overall
    ucats["gate"] = gate
    automation = report.setdefault("automation", {})
    automation["validation_status"] = "valid"
    automation["warnings"] = warnings
    return report


def cmd_validate(path: Path) -> int:
    report = load_json(path)
    errors, warnings = validate(report)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    print("valid")
    return 0


def cmd_score(path: Path) -> int:
    report = load_json(path)
    errors, warnings = validate(report)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    overall = compute_overall(report)
    gate = compute_gate(report, overall)
    clarity_score = compute_clarity_score(report)
    gate_basis = "ucats_overall" if overall is not None else "clarity"
    print(json.dumps({"clarity_score": clarity_score, "overall_score": overall, "gate": gate, "gate_basis": gate_basis, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0


def cmd_normalize(path: Path, output: Path | None) -> int:
    report = load_json(path)
    errors, warnings = validate(report)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    normalized = normalize(report, warnings)
    text = json.dumps(normalized, ensure_ascii=False, indent=2) + "\n"
    if output is None:
        print(text, end="")
    else:
        output.write_text(text, encoding="utf-8")
        print(f"已写入 {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="验证并评分 UCATS 界面证据报告。")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="验证报告。")
    validate_parser.add_argument("report", type=Path)

    score_parser = subparsers.add_parser("score", help="打印加权总分与门禁结果。")
    score_parser.add_argument("report", type=Path)

    normalize_parser = subparsers.add_parser("normalize", help="写入重算分数和门禁后的报告。")
    normalize_parser.add_argument("report", type=Path)
    normalize_parser.add_argument("--output", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            return cmd_validate(args.report)
        if args.command == "score":
            return cmd_score(args.report)
        if args.command == "normalize":
            return cmd_normalize(args.report, args.output)
    except ReportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    parser.error(f"未知命令：{args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
