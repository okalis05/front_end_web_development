from __future__ import annotations
from typing import Any, Dict, Tuple

from .agents import route, AGENTS, AgentResult


def run_multi_agent(text: str, state: Dict[str, Any]) -> AgentResult:
    agent_key = route(text, state)
    agent_fn = AGENTS[agent_key]
    return agent_fn(text, state)
