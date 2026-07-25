from app.models import ConditionType
from app.services.change_detection import evaluate_condition


def test_any_change() -> None:
    assert evaluate_condition(
        condition=ConditionType.ANY_CHANGE,
        current_value="novo",
        previous_value="antigo",
        changed=True,
    )


def test_price_drop() -> None:
    assert evaluate_condition(
        condition=ConditionType.PRICE_DROP,
        current_value="899.90",
        previous_value="999.90",
        changed=True,
    )


def test_first_snapshot_does_not_alert() -> None:
    assert not evaluate_condition(
        condition=ConditionType.ANY_CHANGE,
        current_value="primeiro",
        previous_value=None,
        changed=False,
    )
