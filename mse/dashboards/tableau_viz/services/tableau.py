from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from django.conf import settings


@dataclass(frozen=True)
class TableauEmbed:
    url: str
    host: str


FORCE_PARAMS = {
    ":embed": "yes",
    ":showVizHome": "no",
    ":toolbar": "no",
}


def _allowed_hosts() -> set[str]:
    raw = getattr(settings, "TABLEAU_EMBED_ALLOWED_HOSTS", "")
    return {h.strip().lower() for h in raw.split(",") if h.strip()}


def _host_allowed(host: str, allowed: set[str]) -> bool:
    if not allowed:
        return True
    host = host.lower()
    if host in allowed:
        return True
    return any(host.endswith("." + a) for a in allowed)


def _normalize_tableau_public_url(url: str) -> str:
    p = urlparse(url.strip())
    q = dict(parse_qsl(p.query, keep_blank_values=True))

    # strip volatile / tracking
    for k in (":language", ":sid", ":redirect", ":display_count", ":origin"):
        q.pop(k, None)

    # force embed behavior
    for k, v in FORCE_PARAMS.items():
        q[k] = v

    return urlunparse(p._replace(query=urlencode(q, doseq=True)))


def _validate(url: str) -> TableauEmbed:
    if not url:
        raise ValueError("Missing Tableau view URL.")
    url = _normalize_tableau_public_url(url)

    p = urlparse(url)
    if p.scheme != "https":
        raise ValueError("Tableau URL must be https.")
    host = (p.netloc or "").lower()
    if not host:
        raise ValueError("Invalid Tableau host.")

    allowed = _allowed_hosts()
    if not _host_allowed(host, allowed):
        raise ValueError(f"Tableau host '{host}' not allowed.")

    return TableauEmbed(url=url, host=host)


def get_embed(*, view_key: str, facility_id: str | None = None) -> TableauEmbed | None:
    views = getattr(settings, "TABLEAU_VIEWS", {}) or {}
    raw = (views.get(view_key) or "").strip()
    if not raw:
        return None

    embed = _validate(raw)

    # drill-through param for hospital profile
    if view_key == "hospital_profile" and facility_id:
        joiner = "&" if "?" in embed.url else "?"
        return TableauEmbed(url=f"{embed.url}{joiner}pFacilityID={facility_id}", host=embed.host)

    return embed
