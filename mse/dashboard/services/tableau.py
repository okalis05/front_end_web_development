from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
from django.conf import settings


@dataclass(frozen=True)
class TableauEmbed:
    name: str
    url: str
    host: str


def _allowed_hosts() -> set[str]:
    raw = getattr(settings, "TABLEAU_EMBED_ALLOWED_HOSTS", "")
    return {h.strip().lower() for h in raw.split(",") if h.strip()}


def validate_tableau_url(url: str) -> TableauEmbed:
    """
    Enforces:
      - https URL
      - host allowlist
    Returns structured embed info.
    """
    if not url:
        raise ValueError("Missing Tableau view URL (environment variable not set).")

    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("Tableau embed URL must be https.")

    host = (parsed.netloc or "").lower()
    if not host:
        raise ValueError("Invalid Tableau embed URL host.")

    allowed = _allowed_hosts()
    if allowed and host not in allowed:
        raise ValueError(f"Tableau host '{host}' is not allowed by TABLEAU_EMBED_ALLOWED_HOSTS.")

    return TableauEmbed(name="tableau", url=url, host=host)


def get_view(view_key: str) -> TableauEmbed | None:
    views = getattr(settings, "TABLEAU_VIEWS", {})
    url = views.get(view_key, "")
    if not url:
        return None
    return validate_tableau_url(url)
