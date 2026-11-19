"""在内存中预处理反馈、基础脱敏并计算样本内 NPS。"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SENSITIVE_PATTERNS = {
    "phone": re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "cn_id": re.compile(r"(?<!\d)\d{17}[0-9Xx](?!\d)"),
    "long_account": re.compile(r"(?<!\d)\d{16,19}(?!\d)"),
    "access_token": re.compile(r"(?i)\b(access[_-]?token|api[_-]?key|authorization)\s*[:=]\s*[^\s,;|]+"),
    "url_secret": re.compile(r"(?i)https?://[^\s]+[?&](token|access_token|key|signature|sig)=[^&\s]+"),
}
TEXT_ALIASES = {
    "customer_voice": ("feedback", "content", "description", "message", "工单内容", "问题描述", "反馈内容", "客户反馈", "用户反馈", "报错信息"),
    "support_restatement": ("客服转述", "问题摘要", "服务摘要", "处理描述"),
    "internal_context": ("处理记录", "跟进记录", "原因分析", "解决方案", "内部备注"),
}


def _fingerprint(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _redact(value: Any) -> tuple[str, list[str]]:
    text = str(value or "")
    risks = []
    replacements = {
        "phone": "[PHONE]",
        "email": "[EMAIL]",
        "cn_id": "[IDENTITY_NUMBER]",
        "long_account": "[ACCOUNT]",
        "access_token": "[CREDENTIAL]",
        "url_secret": "[URL_WITH_SECRET]",
    }
    for risk, pattern in SENSITIVE_PATTERNS.items():
        if pattern.search(text):
            risks.append(risk)
            text = pattern.sub(replacements[risk], text)
    text = re.sub(
        r"(?i)(user_?id|employee_?id|order_?id|ticket_?id)\s*[:=|：]\s*[^\s,;|]+",
        r"\1=[ID]",
        text,
    )
    return re.sub(r"\s+", " ", text).strip(), sorted(set(risks))


def _load_rows(source: dict[str, Any]) -> tuple[list[dict[str, Any]], bytes]:
    if source.get("content_ref"):
        raw = str(source["content_ref"]).encode("utf-8")
        return [{"content": source["content_ref"]}], raw
    path = Path(str(source.get("path_ref") or ""))
    path = path.resolve()
    raw = path.read_bytes()
    fmt = str(source.get("format") or path.suffix.lstrip(".")).lower()
    if fmt in {"csv", "tsv"}:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle, delimiter="\t" if fmt == "tsv" else ",")), raw
    if fmt in {"json", "jsonl"}:
        if fmt == "jsonl":
            return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()], raw
        data = json.loads(raw.decode("utf-8-sig"))
        return data if isinstance(data, list) else data.get("records", data.get("rows", [])), raw
    if fmt == "xlsx":
        try:
            from openpyxl import load_workbook
        except ImportError as exc:
            raise ValueError("XLSX input requires optional openpyxl>=3.1") from exc
        workbook = load_workbook(path, read_only=True, data_only=True)
        rows: list[dict[str, Any]] = []
        selected = source.get("sheets")
        if isinstance(selected, str):
            selected = [selected]
        worksheets = [
            workbook[name] for name in selected
        ] if selected else workbook.worksheets
        for sheet in worksheets:
            iterator = sheet.iter_rows(values_only=True)
            header = next(iterator, None)
            if header is None:
                continue
            fields = [str(value or f"unnamed_{index + 1}") for index, value in enumerate(header)]
            rows.extend(dict(zip(fields, values)) for values in iterator)
        workbook.close()
        return rows, raw
    raise ValueError(f"unsupported subjective input format: {fmt}")


STRUCTURED_LABELS = {
    "场景": ("场景", "问题场景", "descpScene"),
    "问题": ("问题", "问题描述", "descpQuestion"),
    "诉求": ("诉求", "用户诉求", "descpAppeal"),
    "其他风险": ("其他风险", "otherRisks"),
}


def _structured_parts(row: dict[str, Any]) -> list[tuple[str, str]]:
    parts = []
    for label, aliases in STRUCTURED_LABELS.items():
        value = next((row.get(key) for key in aliases if row.get(key) not in (None, "")), None)
        if value is not None:
            parts.append((label, str(value).strip()))
    return parts


def _ordered_text(row: dict[str, Any], fields: list[str]) -> tuple[str, list[dict[str, str]]]:
    values = []
    for field in fields:
        value = row.get(field)
        if value not in (None, ""):
            values.append({"field": field, "value": str(value).strip()})
    structured = _structured_parts(row)
    for label, value in structured:
        if not any(item["value"] == value for item in values):
            values.append({"field": label, "value": value})
    text = "\n".join(f"【{item['field']}】{item['value']}" for item in values)
    return text, values


def _nps_class(score: float) -> str:
    if score >= 9:
        return "promoter"
    if score <= 6:
        return "detractor"
    return "passive"


def _nps_fact(
    responses: list[dict[str, Any]],
    *,
    dimensions: dict[str, str],
    invited_count: int | None,
) -> dict[str, Any]:
    counts = {"promoter": 0, "passive": 0, "detractor": 0}
    for item in responses:
        counts[_nps_class(item["score"])] += 1
    response_count = len(responses)
    nps = (
        (counts["promoter"] - counts["detractor"]) / response_count * 100
        if response_count
        else None
    )
    return {
        "measurement_scope": {
            "grain": "survey_response",
            "dimensions": dimensions,
        },
        "response_count": response_count,
        "promoter_count": counts["promoter"],
        "passive_count": counts["passive"],
        "detractor_count": counts["detractor"],
        "nps": nps,
        "response_rate": {
            "status": "available" if invited_count is not None else "not_evaluable",
            "numerator": response_count,
            "denominator": invited_count,
            "value": (
                response_count / invited_count
                if invited_count not in (None, 0)
                else None
            ),
        },
    }


def analyze_nps_sources(
    source_rows: list[tuple[dict[str, Any], list[dict[str, Any]]]],
) -> dict[str, Any]:
    responses: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    invalid_score_count = 0
    duplicate_response_count = 0
    invited_total = 0
    invitation_known = False
    for source, rows in source_rows:
        bindings = source.get("field_bindings", {})
        score_field = bindings.get("nps_score")
        if not score_field:
            continue
        source_id = str(source.get("source_id") or "")
        response_id_field = bindings.get("response_id")
        invited_flag_field = bindings.get("invited_flag")
        if source.get("invited_count") is not None:
            invited_total += int(source["invited_count"])
            invitation_known = True
        elif invited_flag_field:
            invited_total += sum(
                str(row.get(invited_flag_field) or "").strip().lower()
                in {"1", "1.0", "true", "yes", "y", "是"}
                for row in rows
            )
            invitation_known = True
        for index, row in enumerate(rows, start=1):
            raw_score = row.get(score_field)
            if raw_score in (None, ""):
                continue
            try:
                score = float(raw_score)
            except (TypeError, ValueError):
                invalid_score_count += 1
                continue
            if score < 0 or score > 10:
                invalid_score_count += 1
                continue
            response_id = str(
                row.get(response_id_field) if response_id_field else index
            )
            key = (source_id, response_id)
            if key in seen:
                duplicate_response_count += 1
                continue
            seen.add(key)
            responses.append({
                "score": score,
                "business_board": (
                    str(row.get(bindings.get("business_board")) or "").strip()
                    if bindings.get("business_board")
                    else ""
                ),
                "enterprise_state": (
                    str(row.get(bindings.get("enterprise_state")) or "").strip()
                    if bindings.get("enterprise_state")
                    else ""
                ),
            })
    if not responses:
        return {
            "status": "not_evaluable",
            "reason": "nps_score_input_unavailable",
            "overall": None,
            "slices": [],
            "reliability": {
                "response_count": 0,
                "invalid_score_count": invalid_score_count,
                "duplicate_response_count": duplicate_response_count,
            },
            "limitations": [
                "NPS score field was not bound or contained no valid 0-10 responses"
            ],
        }
    overall = _nps_fact(
        responses,
        dimensions={},
        invited_count=invited_total if invitation_known else None,
    )
    grouped: dict[tuple[tuple[str, str], ...], list[dict[str, Any]]] = {}
    for response in responses:
        available = {
            key: response[key]
            for key in ("business_board", "enterprise_state")
            if response.get(key)
        }
        dimension_sets = [{key: value} for key, value in available.items()]
        if len(available) > 1:
            dimension_sets.append(available)
        for dimensions in dimension_sets:
            key = tuple(sorted(dimensions.items()))
            grouped.setdefault(key, []).append(response)
    return {
        "status": (
            "completed_with_caveats"
            if invalid_score_count or not invitation_known
            else "completed"
        ),
        "overall": overall,
        "slices": [
            _nps_fact(items, dimensions=dict(key), invited_count=None)
            for key, items in sorted(grouped.items())
        ],
        "reliability": {
            "response_count": len(responses),
            "invalid_score_count": invalid_score_count,
            "duplicate_response_count": duplicate_response_count,
            "response_deduplication": "source_id_plus_response_id_or_source_row",
            "inference_performed": False,
        },
        "limitations": (
            []
            if invitation_known
            else [
                "invited population denominator unavailable; response rate is not evaluable"
            ]
        ),
    }


def prepare_input(request: dict[str, Any]) -> dict[str, Any]:
    manifests, prepared = [], []
    nps_source_rows: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    seen: set[str] = set()
    for source in request.get("input_sources", []):
        try:
            rows, raw = _load_rows(source)
            status, failure = "loaded", None
        except Exception as exc:
            rows, raw = [], b""
            status, failure = "unreadable", f"{type(exc).__name__}: {exc}"
        nps_source_rows.append((source, rows))
        bindings = source.get("field_bindings", {})
        source_type = str(source.get("source_type") or "")
        content_role = str(source.get("content_role") or ("internal_context" if source_type == "service_log" else "customer_voice"))
        configured_text_fields = bindings.get(content_role, [])
        if isinstance(configured_text_fields, str):
            configured_text_fields = [configured_text_fields]
        if not configured_text_fields and source_type != "service_log":
            configured_text_fields = list(TEXT_ALIASES.get(content_role, TEXT_ALIASES["customer_voice"]))
        usable_before = len(prepared)
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            raw_text, text_parts = _ordered_text(row, list(configured_text_fields))
            redacted, risks = _redact(raw_text)
            key = _fingerprint(redacted.encode("utf-8"))
            if not redacted or key in seen:
                continue
            seen.add(key)
            prepared.append(
                {
                    "prepared_item_id": f"prepared_{key[:14]}",
                    "source_id": source.get("source_id"),
                    "source_type": source_type,
                    "content_role": content_role,
                    "eligible_for_feedback_analysis": content_role != "internal_context",
                    "source_row": index,
                    "redacted_text": redacted,
                    "privacy_risk_types": risks,
                    "manual_review_required": bool(risks),
                    "channel": (
                        row.get(bindings.get("channel"))
                        if bindings.get("channel")
                        else source.get("channel") or source_type
                    ),
                    "product_location": {
                        "product_module": row.get(bindings.get("product_module")) if bindings.get("product_module") else None,
                        "page": row.get(bindings.get("page")) if bindings.get("page") else None,
                        "function": row.get(bindings.get("function")) if bindings.get("function") else None,
                        "operation_node": row.get(bindings.get("operation_node")) if bindings.get("operation_node") else None,
                        "mapping_basis": "explicit_field",
                        "mapping_confidence": "high",
                    },
                    "text_parts": [
                        {"field": item["field"], "redacted_value": _redact(item["value"])[0]}
                        for item in text_parts
                    ],
                    "segment_fields": {
                        "enterprise_id": row.get(bindings.get("enterprise_id")) if bindings.get("enterprise_id") else None,
                        "enterprise_name": row.get(bindings.get("enterprise_name")) if bindings.get("enterprise_name") else None,
                        **{
                            str(logical): row.get(source_field)
                            for logical, source_field in bindings.get("segment_fields", {}).items()
                        },
                    },
                }
            )
        usable_count = len(prepared) - usable_before
        analyzable_count = sum(
            item["eligible_for_feedback_analysis"]
            for item in prepared[usable_before:]
        )
        manifests.append(
            {
                "source_id": source.get("source_id"),
                "source_type": source_type,
                "content_role": content_role,
                "format": source.get("format"),
                "fingerprint": _fingerprint(raw) if raw else None,
                "row_count": len(rows),
                "usable_item_count": usable_count,
                "read_status": status,
                "analysis_status": (
                    "usable"
                    if analyzable_count
                    else "context_only"
                    if usable_count
                    else "unavailable"
                ),
                "unavailable_reason": (
                    failure
                    if failure
                    else "service_log_requires_explicit_text_field_binding"
                    if source_type == "service_log" and not configured_text_fields
                    else "no_usable_text_in_bound_fields"
                ) if not usable_count else None,
                "failure_reason": failure,
            }
        )
    analysis_item_count = sum(item["eligible_for_feedback_analysis"] for item in prepared)
    context_item_count = len(prepared) - analysis_item_count
    return {
        "project_name": request.get("project_name"),
        "source_mode": request.get("source_mode"),
        "analysis_mode": request.get("analysis_mode"),
        "source_manifest": manifests,
        "prepared_items": prepared,
        "nps_summary": analyze_nps_sources(nps_source_rows),
        "deduplicated_item_count": len(prepared),
        "analysis_item_count": analysis_item_count,
        "context_item_count": context_item_count,
        "raw_text_persisted": False,
        "status": (
            "ready"
            if analysis_item_count and all(item["analysis_status"] != "unavailable" for item in manifests if item["read_status"] == "loaded")
            else "ready_with_caveats"
            if analysis_item_count
            else "not_evaluable"
        ),
    }
