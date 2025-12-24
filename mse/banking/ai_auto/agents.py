from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List
import re


@dataclass
class AgentResult:
    reply: str
    state: Dict[str, Any]
    agent: str
    payload: Dict[str, Any]


def _money(text: str) -> int | None:
    m = re.search(r"\$?\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{3,6})", text or "")
    if not m:
        return None
    try:
        v = int(m.group(1).replace(",", ""))
        if 1900 <= v <= 2100:
            return None
        return v
    except Exception:
        return None


def route(text: str, state: Dict[str, Any]) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["reset", "start over", "new session"]):
        return "reset"
    if any(k in t for k in ["monthly", "payment", "down", "apr", "term", "zip"]):
        return "budget"
    if any(k in t for k in ["inventory", "available", "models", "trims", "catalog"]):
        return "inventory"
    if any(k in t for k in ["recommend", "shortlist", "top 3", "suggest"]):
        return "match"
    return "intake" if "body_style" not in state or "monthly_target" not in state else "match"


def agent_reset(_: str, __: Dict[str, Any]) -> AgentResult:
    return AgentResult(
        reply="Reset complete. Tell me: SUV/sedan/truck/coupe, new/used, and your max monthly payment.",
        state={},
        agent="reset",
        payload={"action": "reset"},
    )


def agent_intake(text: str, state: Dict[str, Any]) -> AgentResult:
    t = (text or "").lower()
    if "suv" in t: state["body_style"] = "SUV"
    if "sedan" in t: state["body_style"] = "Sedan"
    if "truck" in t: state["body_style"] = "Truck"
    if "coupe" in t: state["body_style"] = "Coupe"

    if "new" in t: state["condition"] = "New"
    elif "used" in t or "pre-owned" in t: state["condition"] = "Used"
    elif "either" in t: state["condition"] = "Either"

    m = _money(text)
    if m and m < 5000:
        state["monthly_target"] = m

    missing = []
    if "body_style" not in state: missing.append("body style")
    if "condition" not in state: missing.append("new/used/either")
    if "monthly_target" not in state: missing.append("max monthly")

    if missing:
        return AgentResult(
            reply=f"Quick intake — what’s your {', '.join(missing)}?",
            state=state,
            agent="intake",
            payload={"missing": missing},
        )

    return AgentResult(
        reply="Locked. Add down payment, term (36/48/60/72), and ZIP. Then say “recommend”.",
        state=state,
        agent="intake",
        payload={"captured": {k: state.get(k) for k in ["body_style", "condition", "monthly_target"]}},
    )


def agent_budget(text: str, state: Dict[str, Any]) -> AgentResult:
    t = (text or "").lower()
    m = _money(text)
    if m and m >= 500:
        state["down_payment"] = m

    for term in [36,48,60,72,84]:
        if str(term) in t:
            state["term_months"] = term

    z = re.search(r"\b([0-9]{5})\b", t)
    if z:
        state["zip_code"] = z.group(1)

    monthly = state.get("monthly_target")
    term = state.get("term_months", 60)
    down = state.get("down_payment", 0)
    if monthly:
        # conservative cap
        state["price_cap_est"] = int((monthly * term) * 0.75 + down)

    missing = []
    if "down_payment" not in state: missing.append("down payment")
    if "term_months" not in state: missing.append("term")
    if "zip_code" not in state: missing.append("ZIP")

    if missing:
        return AgentResult(
            reply=f"I still need: {', '.join(missing)}.",
            state=state,
            agent="budget",
            payload={"missing": missing},
        )

    return AgentResult(
        reply=f"Budget finalized. Estimated cap ≈ ${state.get('price_cap_est',0):,}. Say “recommend” for Top 3, or “inventory” for real model catalog.",
        state=state,
        agent="budget",
        payload={"price_cap_est": state.get("price_cap_est")},
    )


def _badge_for_risk(risk_tier: str, est_price: int | None, max_amount: float | None) -> str:
    if not risk_tier:
        return ""
    risk = risk_tier.upper()
    if risk == "HIGH":
        return "Conservative"
    if risk == "LOW":
        # allow stretch if close to max
        if est_price and max_amount and est_price > 0.9 * float(max_amount):
            return "Stretch"
        return "Conservative"
    # MEDIUM
    if est_price and max_amount and est_price > 0.85 * float(max_amount):
        return "Stretch"
    return "Balanced"


def agent_match(_: str, state: Dict[str, Any]) -> AgentResult:
    body = state.get("body_style", "SUV")
    cap = state.get("price_cap_est") or 0
    credit = state.get("credit_snapshot") or {}
    risk_tier = credit.get("risk_tier", "MEDIUM")
    max_amount = credit.get("max_amount", cap) or cap

    # curated picks (still used as fallback if inventory not fetched yet)
    if body == "SUV":
        picks = [
            {"make":"Toyota","model":"RAV4","tier":"Core","why":"Reliability + resale"},
            {"make":"Honda","model":"CR-V","tier":"Core","why":"Comfort + low ownership cost"},
            {"make":"Mazda","model":"CX-5","tier":"Executive","why":"Premium feel under budget"},
        ]
    elif body == "Sedan":
        picks = [
            {"make":"Toyota","model":"Camry","tier":"Core","why":"Efficient + resale"},
            {"make":"Honda","model":"Accord","tier":"Core","why":"Space + tech"},
            {"make":"Lexus","model":"ES","tier":"Executive","why":"Executive comfort (used)"},
        ]
    else:
        picks = [
            {"make":"Toyota","model":"Highlander","tier":"Core","why":"Practical + strong resale"},
            {"make":"Ford","model":"F-150","tier":"Core","why":"Versatility + availability"},
            {"make":"Audi","model":"Q5","tier":"Executive","why":"Luxury crossover (used)"},
        ]

    for p in picks:
        p["target_budget_note"] = f"Target cap ≈ ${cap:,}"
        p["risk_tier"] = risk_tier
        # cheap estimate (for badges). inventory integration overrides later.
        est_price = cap if cap else None
        p["est_price"] = est_price
        p["badge"] = _badge_for_risk(risk_tier, est_price, max_amount)

    state["last_recommendations"] = picks

    return AgentResult(
        reply="Executive shortlist is ready. Open the Shortlist page to review, compare, and export a Buyer Brief.",
        state=state,
        agent="match",
        payload={"recommendations": picks, "risk_tier": risk_tier},
    )


def agent_inventory(_: str, state: Dict[str, Any]) -> AgentResult:
    return AgentResult(
        reply="Inventory catalog is available from the Auto page form (Make/Model/Year). Use it to pull real makes/models/trims and refresh your shortlist.",
        state=state,
        agent="inventory",
        payload={"hint": "use catalog search"},
    )


AGENTS = {
    "reset": agent_reset,
    "intake": agent_intake,
    "budget": agent_budget,
    "match": agent_match,
    "inventory": agent_inventory,
}
