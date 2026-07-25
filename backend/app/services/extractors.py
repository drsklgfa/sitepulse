from __future__ import annotations

import hashlib
import re
from decimal import Decimal, InvalidOperation

from bs4 import BeautifulSoup

from app.models import ExtractionType


class ExtractionError(ValueError):
    pass


def normalize_text(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split()).strip()


def parse_number(value: str) -> Decimal:
    cleaned = re.sub(r"[^0-9,.-]", "", value)
    if not cleaned:
        raise ExtractionError("Nenhum número foi encontrado no conteúdo")

    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        tail = cleaned.rsplit(",", 1)[-1]
        cleaned = cleaned.replace(".", "")
        cleaned = cleaned.replace(",", "." if len(tail) <= 2 else "")
    elif cleaned.count(".") > 1:
        parts = cleaned.split(".")
        cleaned = "".join(parts[:-1]) + "." + parts[-1]

    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise ExtractionError("O valor numérico não pôde ser interpretado") from exc


def canonical_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f")


def extract_content(
    html: str,
    *,
    selector: str | None,
    extraction_type: ExtractionType,
    attribute_name: str | None = None,
    http_status: int = 200,
) -> tuple[str, str]:
    if extraction_type == ExtractionType.STATUS:
        value = str(http_status)
        return value, value

    soup = BeautifulSoup(html, "html.parser")
    element = soup.select_one(selector) if selector else soup.body or soup
    if element is None:
        raise ExtractionError(f"O seletor CSS não encontrou elementos: {selector}")

    raw = str(element)[:10_000]
    if extraction_type == ExtractionType.HTML:
        value = normalize_text(str(element))
    elif extraction_type == ExtractionType.ATTRIBUTE:
        if not attribute_name:
            raise ExtractionError("Informe o nome do atributo que será extraído")
        attr = element.get(attribute_name)
        if attr is None:
            raise ExtractionError(f"O atributo '{attribute_name}' não foi encontrado")
        value = normalize_text(" ".join(attr) if isinstance(attr, list) else str(attr))
    else:
        value = normalize_text(element.get_text(" ", strip=True))
        if extraction_type in {ExtractionType.PRICE, ExtractionType.NUMBER}:
            value = canonical_decimal(parse_number(value))

    if not value:
        raise ExtractionError("O conteúdo extraído está vazio")
    return value, raw


def content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
