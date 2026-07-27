from urllib.parse import urlparse

_BLOCKED_HOSTS = {
    "localhost", "127.0.0.1", "0.0.0.0", "::1",
    "169.254.169.254",  # AWS metadata
    "metadata.google.internal",
}


def is_safe_url(url: str) -> bool:
    """
    Returns True only for http/https URLs pointing to public hosts.
    Blocks private IPs, localhost, and metadata endpoints (SSRF prevention).
    """
    if not url:
        return False
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme not in ("http", "https"):
        return False

    host = (parsed.hostname or "").lower().split(":")[0]

    if host in _BLOCKED_HOSTS:
        return False

    # block RFC-1918 ranges
    import ipaddress
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
    except ValueError:
        pass  # it's a hostname, not an IP — fine

    return True
