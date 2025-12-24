from __future__ import annotations
from typing import Dict, Any
from django.urls import reverse
from django.test import Client

def fetch_credit_snapshot(user, payload: Dict[str, Any]) -> Dict[str, Any]:

    c = Client()
    c.force_login(user)
    r = c.post(reverse("banking:ai_credit_score"), data=payload, content_type="application/json")
    if r.status_code != 200:
        return {}
    return r.json()
