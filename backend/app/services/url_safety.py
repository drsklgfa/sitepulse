from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class UnsafeUrlError(ValueError):
    pass


_METADATA_IPS = {"169.254.169.254", "100.100.100.200"}


def _is_unsafe_ip(ip_text: str) -> bool:
    ip = ipaddress.ip_address(ip_text)
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
        or ip_text in _METADATA_IPS
    )


def validate_target_url(
    url: str,
    *,
    allow_private_networks: bool = False,
    allowed_private_hosts: list[str] | None = None,
) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeUrlError("Somente URLs HTTP e HTTPS são permitidas")
    if not parsed.hostname:
        raise UnsafeUrlError("A URL precisa conter um host válido")
    if parsed.username or parsed.password:
        raise UnsafeUrlError("Credenciais embutidas na URL não são permitidas")

    hostname = parsed.hostname.lower().rstrip(".")
    allowed_hosts = {host.lower().rstrip(".") for host in (allowed_private_hosts or [])}
    if hostname in allowed_hosts and allow_private_networks:
        return url

    try:
        addresses = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise UnsafeUrlError("Não foi possível resolver o host informado") from exc

    ips = {item[4][0] for item in addresses}
    if not ips:
        raise UnsafeUrlError("O host não retornou um endereço de rede")
    if not allow_private_networks and any(_is_unsafe_ip(ip) for ip in ips):
        raise UnsafeUrlError("Endereços internos, privados ou reservados não podem ser monitorados")
    if any(ip in _METADATA_IPS for ip in ips):
        raise UnsafeUrlError("O endereço de metadados de infraestrutura é bloqueado")
    return url
