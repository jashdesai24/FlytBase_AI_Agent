"""
LangGraph state definition — the shared state object that flows through the entire pipeline.
Each agent reads from and writes to specific fields in this state.
"""

import operator
from typing import Optional, TypedDict, Any, Annotated


class BDRAgentState(TypedDict, total=False):
    """
    The complete state object for the BDR agent pipeline.

    Each agent reads specific fields and writes to its output field.
    The orchestrator passes this state between agents.

    Fields are Optional because agents populate them progressively —
    early agents write their outputs; later agents read them.

    execution_log and agent_errors use Annotated reducers so that
    parallel nodes (research + contact) can both write without conflict.
    """

    # ── Input ──────────────────────────────────────────────────────────
    raw_input: Optional[Any]

    # ── Agent Outputs (populated progressively) ────────────────────────
    lead_record: Optional[Any]
    account_research: Optional[Any]
    contact_intelligence: Optional[Any]
    qualification: Optional[Any]
    case_study_matches: Optional[Any]
    gtm_and_email: Optional[Any]
    handoff_brief: Optional[Any]

    # ── Pipeline Metadata ──────────────────────────────────────────────
    # All fields written by parallel nodes need reducers.
    # "last writer wins" for scalar fields:
    current_agent: Annotated[str, lambda a, b: b]
    agent_errors: Annotated[dict, lambda a, b: {**a, **b}]
    execution_log: Annotated[list, operator.add]
    is_qualified: Annotated[bool, lambda a, b: b]
