from decimal import Decimal

import pytest

from app.models import ExtractionType
from app.services.extractors import ExtractionError, extract_content, parse_number


def test_parse_brazilian_price() -> None:
    assert parse_number("R$ 2.199,90") == Decimal("2199.90")


def test_parse_us_price() -> None:
    assert parse_number("$1,299.50") == Decimal("1299.50")


def test_extract_text_by_selector() -> None:
    value, raw = extract_content(
        "<html><body><span class='status'> Em estoque </span></body></html>",
        selector=".status",
        extraction_type=ExtractionType.TEXT,
    )
    assert value == "Em estoque"
    assert "status" in raw


def test_missing_selector_raises() -> None:
    with pytest.raises(ExtractionError):
        extract_content("<p>Olá</p>", selector=".missing", extraction_type=ExtractionType.TEXT)
