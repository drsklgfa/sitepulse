from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.models import ConditionType


def _decimal(value: str | None) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def evaluate_condition(
    *,
    condition: ConditionType,
    current_value: str,
    previous_value: str | None,
    changed: bool,
    threshold: float | None = None,
    keyword: str | None = None,
) -> bool:
    if previous_value is None and condition != ConditionType.STATUS_NOT_OK:
        return False
    if condition == ConditionType.ANY_CHANGE:
        return changed
    if condition == ConditionType.PRICE_DROP:
        current = _decimal(current_value)
        previous = _decimal(previous_value)
        return current is not None and previous is not None and current < previous
    if condition == ConditionType.PRICE_BELOW:
        current = _decimal(current_value)
        return current is not None and threshold is not None and current < Decimal(str(threshold))
    if condition == ConditionType.CONTAINS:
        return bool(keyword) and keyword.lower() in current_value.lower()
    if condition == ConditionType.NOT_CONTAINS:
        return bool(keyword) and keyword.lower() not in current_value.lower()
    if condition == ConditionType.STATUS_NOT_OK:
        try:
            return int(current_value) >= 400
        except ValueError:
            return True
    return False
