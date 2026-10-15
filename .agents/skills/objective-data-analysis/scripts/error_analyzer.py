#!/usr/bin/env python3
"""Deterministic, privacy-safe error analysis for objective event data."""

from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from typing import Any

from time_parsing import parse_time


SENSITIVE_PATTERNS = [
    (re.compile(r"(?i)(access_token|refresh_token|token|secret|password|pwd|authorization|api[_-]?key|cookie|set-cookie)\s*[:=]\s*[^\s&;,]+"), r"\1=<REDACTED>"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "<EMAIL>"),
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "<PHONE>"),
    (re.compile(r"(?<!\d)\d{17}[0-9Xx](?!\d)"), "<IDENTITY_NUMBER>"),
    (re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"), "<PAYMENT_CARD>"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "<IP>"),
    (re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,36}\b"), "<UUID>"),
    (re.compile(r"(?i)(user_?id|task_?id|session_?id|trace_?id|order_?id|employee_?id|account_?id|invoice_?id|expense_?id|reimbursement_?id|prepayment_?id|bill_?id)\s*[:=|：]\s*[^\s&;,|]+"), r"\1=<ID>"),
    (re.compile(r"(?i)(发票号码|发票号|预付款号|费用单号|报销单号|单据号|订单号|流水号)\s*[A-Za-z]*\s*[-—_:：]*\s*[A-Za-z0-9][A-Za-z0-9 _./—-]{3,}"), r"\1=<ID>"),
    (re.compile(r"(?i)(amount|total|price|金额|价税合计|余额)\s*(?:为|是|[:=|：])?\s*[¥￥]?\s*[-+]?\d+(?:\.\d+)?"), r"\1=<AMOUNT>"),
    (re.compile(r"(?i)(date|time|日期|时间)?\s*[:=|：]?\s*\d{4}[-/.年]\d{1,2}[-/.月]\d{1,2}(?:日)?(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?"), lambda match: f"{match.group(1) or 'date'}=<DATE_TIME>"),
    (re.compile(r"(?i)(location|address|city|地区|地址|城市|地点)\s*(?:为|是|[:=|：])?\s*[A-Za-z\u4e00-\u9fff]{2,30}"), r"\1=<LOCATION>"),
    (re.compile(r"https?://[^\s?]+\?[^\s]+"), "<URL_WITH_PARAMS>"),
    (re.compile(r"(?<![\w.-])(?:/[\w .-]+){2,}"), "<FILE_PATH>"),
    (re.compile(r"(?i)\b[A-Z]:\\(?:[^\\\s]+\\)+[^\\\s]*"), "<FILE_PATH>"),
    (re.compile(r"(?<!\d)(?:\d[\s_-]?){5,}(?!\d)"), "<N>"),
]

CATEGORY_RULES = [
    ("form_validation", ("必填", "校验", "验证", "格式", "不能为空")),
    ("invoice_or_document", ("发票", "票据", "单据", "影像")),
    ("permission_or_eligibility", ("权限", "无权", "资格", "不允许", "不可")),
    ("business_rule", ("预算", "日期", "金额", "额度", "规则", "前款")),
    ("network_or_service", ("网络", "超时", "服务异常", "系统异常", "接口", "失败")),
]

OPAQUE_TOKEN = re.compile(r"(?<![<\w])[A-Za-z0-9_./+=-]{24,}(?![>\w])")
SUSPICIOUS_ASSIGNMENT = re.compile(r"(?i)\b(?:credential|auth|bearer|key|secret|token|cookie|password|pwd|session|trace|account|employee|order|tenant|user)\w*\s*[:=]\s*\S+")


def redact_message(message: Any, code: Any = "") -> tuple[str, str, str]:
    raw = str(message or "").strip()
    value = re.sub(
        r"(?i)(?:^|[;|])\s*(?:INFO[2-9]\d*|WARN\d*|ERROR\d*)\s*[:：|-]\s*[^;|]*",
        "",
        raw,
    )
    value = re.sub(r"(?i)^INFO1\s*[:：|-]\s*", "", value)
    value = re.sub(r"\[(?:CUSTOM_[A-Za-z0-9_-]+|[A-Za-z][A-Za-z0-9_-]{2,})\]", "<FIELD>", value)
    for pattern, replacement in SENSITIVE_PATTERNS:
        value = pattern.sub(replacement, value)
    value = re.sub(r"\s+", " ", value)
    if not value:
        value = f"error_code:{code}" if code else "unknown_error"
    state = "safe"
    if SUSPICIOUS_ASSIGNMENT.search(value) or OPAQUE_TOKEN.search(value):
        state = "uncertain"
        value = "unclassified_redacted_error"
    seed = hashlib.sha256(raw.encode("utf-8")).hexdigest() if state != "safe" else value
    return value[:240], state, seed


def canonical_safe_label(message: Any, code: Any = "") -> str:
    return redact_message(message, code)[0]


def category(label: str) -> str:
    lowered = label.lower()
    for name, keywords in CATEGORY_RULES:
        if any(keyword.lower() in lowered for keyword in keywords):
            return name
    return "other"


def signature(label: str, code: Any = "", presentation: Any = "") -> str:
    return "err_" + hashlib.sha256(
        f"{code}|{presentation}|{label}".encode("utf-8")
    ).hexdigest()[:16]


def message_kind(label: str, code: Any = "", explicit_complete: Any = "") -> str:
    """Separate actionable errors from confirmations and ordinary status messages."""
    text = str(label or "").strip().lower()
    if str(code or "").strip() or str(explicit_complete or "").strip().lower() in {"1", "1.0", "true", "是"}:
        return "actionable_error"
    if any(token in text for token in ("恢复成功", "保存成功", "操作成功", "提交成功", "处理成功")):
        return "success_status"
    if any(token in text for token in ("正在", "处理中", "准备中", "报送中", "加载中")):
        return "informational"
    error_tokens = ("不能", "不可", "失败", "错误", "异常", "超时", "无权限", "不足", "缺失", "不能为空", "校验", "验证")
    if any(token in text for token in error_tokens):
        return "actionable_error"
    confirmation_actions = ("删除", "覆盖", "继续", "提交", "撤销", "清空", "离开", "前往", "不同步")
    confirmation_tone = (
        any(token in text for token in ("是否", "要不要", "确认"))
        or "吗" in text
        or text.endswith(("?", "？"))
    )
    if (
        any(token in text for token in ("是否确认", "操作确认", "确认删除"))
        or (confirmation_tone and any(token in text for token in confirmation_actions))
    ):
        return "confirmation"
    if any(token in text for token in ("警告", "提醒", "注意")):
        return "warning"
    return "unknown"


def analyze_rows(
    rows: list[dict[str, Any]],
    task_col: str = "task_instance_id",
    class_col: str = "event_class",
    message_col: str = "error_message",
    code_col: str = "error_code",
    presentation_col: str = "error_presentation",
    step_col: str = "journey_step",
    top_n: int = 20,
) -> dict[str, Any]:
    candidates = [row for row in rows if row.get(class_col) == "error_event"]
    kind_counts: Counter[str] = Counter()
    errors = []
    excluded = []
    for row in candidates:
        label = canonical_safe_label(row.get(message_col), row.get(code_col))
        kind = message_kind(label, row.get(code_col), row.get("error_is_complete"))
        row["_error_message_kind"] = kind
        kind_counts[kind] += 1
        if kind in {"confirmation", "informational", "success_status"}:
            excluded.append(row)
        else:
            errors.append(row)
    patterns: Counter[tuple[str, str, str, str, str]] = Counter()
    by_step: Counter[str] = Counter()
    by_step_types: dict[str, Counter[str]] = defaultdict(Counter)
    tasks: dict[str, set[str]] = defaultdict(set)
    users: dict[str, set[str]] = defaultdict(set)
    enterprises: dict[str, set[str]] = defaultdict(set)
    times: dict[tuple[str, str], list[datetime]] = defaultdict(list)
    for row in errors:
        label, redaction_state, signature_seed = redact_message(row.get(message_col), row.get(code_col))
        code = str(row.get(code_col) or "")
        presentation = str(row.get(presentation_col) or "")
        sig = signature(signature_seed, code, presentation)
        cat = category(label)
        patterns[(sig, label, cat, redaction_state, presentation)] += 1
        step, step_state, _ = redact_message(row.get(step_col) or "UNKNOWN")
        if step_state != "safe":
            step = "unclassified_redacted_step"
        by_step[step] += 1
        by_step_types[step][cat] += 1
        task = str(row.get(task_col) or "")
        if task:
            tasks[sig].add(task)
        if row.get("user_id"):
            users[sig].add(str(row["user_id"]))
        if row.get("enterprise_id"):
            enterprises[sig].add(str(row["enterprise_id"]))
        parsed = parse_time(row.get("event_time"))
        if task and parsed:
            times[(sig, task)].append(parsed)
    top_patterns = []
    for (sig, label, cat, redaction_state, presentation), count in patterns.most_common(top_n):
        max_burst = 0
        for task in tasks[sig]:
            ordered = sorted(times.get((sig, task), []))
            left = 0
            for right, current in enumerate(ordered):
                while left <= right and (current - ordered[left]).total_seconds() > 60:
                    left += 1
                max_burst = max(max_burst, right - left + 1)
        affected = len(tasks[sig])
        top_patterns.append({
            "error_signature": sig,
            "canonical_safe_label": label,
            "category": cat,
            "presentation": presentation,
            "event_count": count,
            "affected_task_count": affected,
            "affected_user_count": len(users[sig]),
            "affected_enterprise_count": len(enterprises[sig]),
            "events_per_affected_task": count / affected if affected else None,
            "max_events_in_60_seconds_same_task": max_burst,
            "message_kind": next(
                (
                    row.get("_error_message_kind")
                    for row in errors
                    if signature(
                        redact_message(row.get(message_col), row.get(code_col))[2],
                        str(row.get(code_col) or ""),
                        str(row.get(presentation_col) or ""),
                    ) == sig
                ),
                "unknown",
            ),
            "share_of_error_events": count / len(errors) if errors else None,
            "redaction_state": redaction_state,
        })
    return {
        "status": "completed",
        "observed_task_count": len({str(row.get(task_col)) for row in rows if row.get(task_col)}),
        "candidate_error_event_count": len(candidates),
        "error_event_count": len(errors),
        "excluded_non_error_event_count": len(excluded),
        "message_kind_distribution": dict(kind_counts),
        "affected_task_count": len({str(row.get(task_col)) for row in errors if row.get(task_col)}),
        "unique_error_pattern_count": len(patterns),
        "top_error_patterns": top_patterns,
        "error_category_distribution": dict(Counter(category(canonical_safe_label(row.get(message_col), row.get(code_col))) for row in errors)),
        "error_by_step": [
            {
                "step": step,
                "error_event_count": count,
                "share": count / len(errors) if errors else None,
                "error_types": [
                    {"type": kind, "event_count": type_count}
                    for kind, type_count in by_step_types[step].most_common()
                ],
            }
            for step, count in by_step.most_common()
        ],
        "privacy": {
            "formal_output": "canonical_safe_label_only",
            "raw_error_retained": False,
            "redacted_parameters": ["credential", "token", "cookie", "api_key", "email", "phone", "identity_number", "payment_card", "ip", "uuid", "business_ids", "amount", "date_time", "location", "url_query", "file_path", "long_numbers"],
            "fallback_rule": "retain readable message text only after known sensitive parameter classes are redacted",
        },
        "reliability": {
            "sample_size": len({str(row.get(task_col)) for row in rows if row.get(task_col)}),
            "error_event_count": len(errors),
            "affected_task_count": len({str(row.get(task_col)) for row in errors if row.get(task_col)}),
            "uncertain_redaction_pattern_count": sum(item["redaction_state"] != "safe" for item in top_patterns),
            "inference_performed": False,
        },
        "limitations": (
            (["uncertain error text was replaced by a generic safe label"] if any(item["redaction_state"] != "safe" for item in top_patterns) else [])
            + (["confirmation, informational, and success-status messages were excluded from actionable error rankings"] if excluded else [])
            + (["unknown message types remain in the analysis and require sampled review"] if kind_counts.get("unknown") else [])
        ),
    }
