"""
Agent 4: Qualification & Scoring
Thin wrapper that calls the deterministic scoring engine.
The LLM's job here is minimal — just MEDDPICC signal extraction.
"""

from models.schemas import (
    LeadRecord,
    AccountResearch,
    ContactIntelligence,
    QualificationResult,
)
from scoring.engine import compute_lead_score


def run_qualification_agent(
    lead: LeadRecord,
    research: AccountResearch | None,
    contact: ContactIntelligence | None,
) -> QualificationResult:
    """
    Qualify and score the lead using the deterministic scoring engine.
    No LLM is used here — scoring is pure code.
    """
    return compute_lead_score(lead, research, contact)
