"""
Agent 3: Contact Intelligence
Builds a profile of the individual contact — buying role, persona, communication preferences.
"""

from pathlib import Path
from models.schemas import (
    ContactIntelligence,
    ContactProfile,
    CommunicationPreferences,
    Seniority,
    BuyingRole,
    Department,
    Tone,
)
from utils.llm import call_llm_structured
from pydantic import BaseModel, Field
from typing import Optional


PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "contact.txt"


class ContactExtraction(BaseModel):
    """Internal model for LLM extraction."""
    seniority: str = "Unknown"
    department: str = "Other"
    buying_role: str = "Unknown"
    recommended_tone: str = "consultative"
    recommended_length: str = "medium"
    likely_objections: list[str] = Field(default_factory=list)
    linkedin_headline: Optional[str] = None
    notable_signals: list[str] = Field(default_factory=list)
    research_confidence: float = 0.5


def run_contact_agent(
    first_name: str,
    last_name: str,
    job_title: str,
    company_name: str,
    email: str,
    seniority_hint: Seniority = Seniority.UNKNOWN,
) -> ContactIntelligence:
    """
    Build a contact intelligence profile from available data.
    Uses title-based heuristics + LLM classification.
    """
    system_prompt = """You are a B2B sales intelligence analyst. Your job is to classify a business contact's buying role, communication preferences, and likely objections.

CONTEXT — FLYTBASE:
FlytBase is an enterprise drone autonomy platform. Typical buying committee:
- Economic Buyer: VP/C-Suite who controls budget (VP Operations, CFO, COO)
- Technical Buyer: IT/Engineering leader who evaluates technology (CTO, VP IT, Director Engineering)  
- Champion: Middle management who drives the initiative (Drone Program Manager, Head of Innovation, Operations Director)
- Influencer: Has opinion but not decision power (Safety Manager, Site Manager)
- End User: Will use the product daily (Drone Pilot, Field Operator)
- Gatekeeper: Controls access to decision makers (Procurement, Executive Assistant)

BUYING ROLE CLASSIFICATION RULES:
1. C-Suite + Operations/Security/Safety → Economic Buyer
2. C-Suite + IT/Technology → Technical Buyer  
3. VP/Director + Operations/Innovation/Safety → Champion (most likely to drive drone initiatives)
4. VP + IT/Engineering → Technical Buyer
5. Manager + Operations/Safety/Security → Influencer or Champion
6. Manager + IT → Technical Buyer
7. IC level → End User or Influencer
8. Procurement titles → Gatekeeper

TONE RECOMMENDATION:
- C-Suite / Economic Buyer → executive_brief (concise, ROI-focused, no fluff)
- VP/Director Technical → technical_deep (specs, integrations, API details)
- Champion → consultative (problem-solving, collaborative, show understanding)
- Manager / IC → peer_to_peer (direct, practical, use-case focused)

LIKELY OBJECTIONS (pick the most relevant 2-3):
- Budget/cost concerns
- "We're already using [competitor]"
- "Need to evaluate multiple vendors"  
- "Not a priority right now"
- "Need to get IT/security approval"
- "Our regulatory environment is complex"
- "We need on-premise deployment"
- "How does this integrate with our existing systems?"
- "What about data privacy/security?"
"""

    user_prompt = f"""
Classify this business contact:

Name: {first_name} {last_name}
Title: {job_title}
Company: {company_name}
Email: {email}
Seniority Hint: {seniority_hint.value}

Based on their title, company, and seniority, determine:
1. Their buying role in a drone technology purchase
2. Their department
3. Recommended communication tone
4. Top 2-3 likely objections they might raise
"""

    extraction = call_llm_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=ContactExtraction,
        model="gpt-4o-mini",
        temperature=0.1,
    )

    # Map strings to enums
    seniority_map = {v.value: v for v in Seniority}
    department_map = {v.value: v for v in Department}
    buying_role_map = {v.value: v for v in BuyingRole}
    tone_map = {v.value: v for v in Tone}

    seniority = seniority_map.get(extraction.seniority, seniority_hint)
    department = department_map.get(extraction.department, Department.OTHER)
    buying_role = buying_role_map.get(extraction.buying_role, BuyingRole.UNKNOWN)
    tone = tone_map.get(extraction.recommended_tone, Tone.CONSULTATIVE)

    return ContactIntelligence(
        contact_profile=ContactProfile(
            full_name=f"{first_name} {last_name}",
            verified_title=job_title,
            seniority=seniority,
            department=department,
            linkedin_headline=extraction.linkedin_headline,
        ),
        buying_role=buying_role,
        persona_signals={"notable_signals": extraction.notable_signals},
        communication_preferences=CommunicationPreferences(
            recommended_tone=tone,
            recommended_length=extraction.recommended_length,
            likely_objections=extraction.likely_objections,
        ),
        research_confidence=extraction.research_confidence,
    )
