"""
Agent 1: Lead Intake & Normalization
Parses raw form input into a canonical LeadRecord schema.
"""

import uuid
from pathlib import Path
from models.schemas import (
    RawLeadInput,
    LeadRecord,
    ContactInfo,
    CompanyInfo,
    IntentSignals,
    Seniority,
)
from utils.llm import call_llm_structured
from pydantic import BaseModel, Field
from typing import Optional


# Internal model for LLM extraction (simpler than LeadRecord)
class IntakeExtraction(BaseModel):
    seniority: str = "Unknown"
    department: str = "Other"
    use_case_mentions: list[str] = Field(default_factory=list)
    urgency_signals: list[str] = Field(default_factory=list)
    competitor_mentions: list[str] = Field(default_factory=list)
    site_mentions: list[str] = Field(default_factory=list)
    company_industry_guess: Optional[str] = None
    message_summary: Optional[str] = None


PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "intake.txt"


def run_intake_agent(raw_input: RawLeadInput) -> LeadRecord:
    """
    Parse raw lead input into a structured LeadRecord.
    Uses LLM only for title classification and message parsing.
    """
    # Load system prompt
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    # Build user prompt with the raw data
    user_prompt = f"""
Parse the following lead data:

First Name: {raw_input.first_name}
Last Name: {raw_input.last_name}
Email: {raw_input.email}
Job Title: {raw_input.job_title}
Company: {raw_input.company_name}
Phone: {raw_input.phone or 'Not provided'}
Form Message: {raw_input.message or 'Not provided'}
Page Visited: {raw_input.page_visited or 'Not provided'}

Extract the seniority, department, and any signals from the form message.
"""

    # Call LLM for intelligent extraction
    extraction = call_llm_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=IntakeExtraction,
        model="gpt-4o-mini",
        temperature=0.1,
    )

    # Derive company domain from email
    domain = raw_input.email.split("@")[1] if "@" in raw_input.email else ""

    # Map seniority string to enum
    seniority_map = {
        "C-Suite": Seniority.C_SUITE,
        "VP": Seniority.VP,
        "Director": Seniority.DIRECTOR,
        "Manager": Seniority.MANAGER,
        "IC": Seniority.IC,
    }
    seniority = seniority_map.get(extraction.seniority, Seniority.UNKNOWN)

    # Calculate parse confidence
    filled_fields = sum(
        1
        for v in [
            raw_input.first_name,
            raw_input.last_name,
            raw_input.email,
            raw_input.job_title,
            raw_input.company_name,
            raw_input.message,
        ]
        if v
    )
    parse_confidence = min(filled_fields / 6.0, 1.0)

    # Track missing fields
    missing = []
    if not raw_input.phone:
        missing.append("phone")
    if not raw_input.message:
        missing.append("form_message")
    if not raw_input.page_visited:
        missing.append("page_visited")

    # Build canonical LeadRecord
    return LeadRecord(
        lead_id=str(uuid.uuid4()),
        contact=ContactInfo(
            first_name=raw_input.first_name.strip(),
            last_name=raw_input.last_name.strip(),
            email=raw_input.email.strip().lower(),
            phone=raw_input.phone,
            job_title=raw_input.job_title.strip(),
            seniority=seniority,
        ),
        company=CompanyInfo(
            name=raw_input.company_name.strip(),
            domain=domain,
            industry_raw=extraction.company_industry_guess,
        ),
        intent_signals=IntentSignals(
            form_message=raw_input.message,
            page_visited=raw_input.page_visited,
        ),
        parse_confidence=round(parse_confidence, 2),
        missing_fields=missing,
    )
