import hashlib
import ipaddress
import json
import socket
from typing import Any
from urllib.parse import urlparse

SENSITIVE_KEYS = {"authorization", "api_key", "token", "password", "secret"}


def action_fingerprint(action_type: str, arguments: dict[str, Any]) -> str:
    canonical = json.dumps(
        {"type": action_type, "arguments": arguments}, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: ("[REDACTED]" if k.lower() in SENSITIVE_KEYS else redact(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def validate_public_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only public HTTP(S) URLs are allowed")
    if parsed.hostname in {"localhost", "metadata.google.internal"}:
        raise ValueError("Private hosts are blocked")
    try:
        for result in socket.getaddrinfo(parsed.hostname, None):
            ip = ipaddress.ip_address(result[4][0])
            if not ip.is_global:
                raise ValueError("Private network targets are blocked")
    except socket.gaierror as exc:
        raise ValueError("Host could not be resolved") from exc
    return url
