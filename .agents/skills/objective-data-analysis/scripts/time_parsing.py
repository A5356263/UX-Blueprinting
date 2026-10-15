#!/usr/bin/env python3
"""Deterministic timestamp parsing shared by Objective analysis modules."""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any


NUMERIC_TIMESTAMP = re.compile(r"^[+-]?\d+(?:\.\d+)?$")


def _numeric_timestamp(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    else:
        text = str(value or "").strip()
        if not NUMERIC_TIMESTAMP.fullmatch(text):
            return None
        number = float(text)
    if not math.isfinite(number):
        return None
    integer_digits = len(str(abs(int(number))))
    if integer_digits == 13:
        return number / 1000.0
    if integer_digits == 10:
        return number
    return None


def parse_time(value: Any) -> datetime | None:
    """Parse datetime, 10-digit epoch seconds, 13-digit epoch milliseconds, or ISO-8601."""
    if isinstance(value, datetime):
        parsed = value
    else:
        numeric = _numeric_timestamp(value)
        if numeric is not None:
            try:
                return datetime.fromtimestamp(numeric, tz=timezone.utc)
            except (OverflowError, OSError, ValueError):
                return None
        text = str(value or "").strip()
        if not text:
            return None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

