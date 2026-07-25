from __future__ import annotations

import time
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx

from app.config import get_settings
from app.models import ExtractionType, Monitor
from app.services.extractors import extract_content
from app.services.url_safety import validate_target_url


class ScrapeError(RuntimeError):
    pass


@dataclass(slots=True)
class ScrapeResult:
    value: str
    raw_excerpt: str
    http_status: int
    duration_ms: int
    final_url: str


def _fetch_http(url: str) -> tuple[str, int, str]:
    settings = get_settings()
    current_url = validate_target_url(
        url,
        allow_private_networks=settings.allow_private_networks,
        allowed_private_hosts=settings.allowed_private_hosts,
    )
    headers = {"User-Agent": settings.user_agent, "Accept": "text/html,application/xhtml+xml,application/json"}
    with httpx.Client(timeout=settings.request_timeout_seconds, headers=headers, follow_redirects=False) as client:
        for _ in range(settings.max_redirects + 1):
            with client.stream("GET", current_url) as response:
                if response.status_code in {301, 302, 303, 307, 308}:
                    location = response.headers.get("location")
                    if not location:
                        raise ScrapeError("Redirecionamento sem cabeçalho Location")
                    current_url = urljoin(current_url, location)
                    validate_target_url(
                        current_url,
                        allow_private_networks=settings.allow_private_networks,
                        allowed_private_hosts=settings.allowed_private_hosts,
                    )
                    continue
                chunks: list[bytes] = []
                total = 0
                for chunk in response.iter_bytes():
                    total += len(chunk)
                    if total > settings.max_response_bytes:
                        raise ScrapeError("A resposta ultrapassou o limite de tamanho configurado")
                    chunks.append(chunk)
                content = b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")
                return content, response.status_code, str(response.url)
    raise ScrapeError("A página excedeu o limite de redirecionamentos")


def _fetch_browser(url: str) -> tuple[str, int, str]:
    settings = get_settings()
    validate_target_url(
        url,
        allow_private_networks=settings.allow_private_networks,
        allowed_private_hosts=settings.allowed_private_hosts,
    )
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise ScrapeError("O suporte Playwright não está instalado neste ambiente") from exc

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(user_agent=settings.user_agent)
        response = page.goto(url, wait_until="networkidle", timeout=int(settings.request_timeout_seconds * 1000))
        html = page.content()
        final_url = page.url
        browser.close()
    if len(html.encode("utf-8")) > settings.max_response_bytes:
        raise ScrapeError("A resposta ultrapassou o limite de tamanho configurado")
    return html, response.status if response else 200, final_url


def scrape_monitor(monitor: Monitor) -> ScrapeResult:
    started = time.perf_counter()
    try:
        html, status_code, final_url = _fetch_browser(monitor.url) if monitor.render_js else _fetch_http(monitor.url)
        value, raw = extract_content(
            html,
            selector=monitor.selector,
            extraction_type=monitor.extraction_type,
            attribute_name=monitor.attribute_name,
            http_status=status_code,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return ScrapeResult(value=value, raw_excerpt=raw[:4000], http_status=status_code, duration_ms=duration_ms, final_url=final_url)
    except (httpx.HTTPError, ValueError, RuntimeError) as exc:
        raise ScrapeError(str(exc)) from exc
