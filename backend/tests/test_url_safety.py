import socket

import pytest

from app.services.url_safety import UnsafeUrlError, validate_target_url


def test_rejects_non_http_scheme() -> None:
    with pytest.raises(UnsafeUrlError):
        validate_target_url("file:///etc/passwd")


def test_blocks_private_ip(monkeypatch) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: [(2, 1, 6, "", ("127.0.0.1", 80))])
    with pytest.raises(UnsafeUrlError):
        validate_target_url("http://example.test")


def test_allows_explicit_demo_host() -> None:
    assert (
        validate_target_url(
            "http://demo-target:8080/product",
            allow_private_networks=True,
            allowed_private_hosts=["demo-target"],
        )
        == "http://demo-target:8080/product"
    )
