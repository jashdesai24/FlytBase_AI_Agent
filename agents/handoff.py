"""
Agent 7: AE Handoff & Briefing Generator
Synthesizes all upstream outputs into a concise, actionable briefing for the AE.
"""

import json
from models.schemas import (
    LeadRecord,
    AccountResearch,
    ContactIntelligence,
    QualificationResult,
    CaseStudyMatches,
    GTMAndEmailResult,
    HandoffBrief,
    CompanySnapshot,
    ContactSnapshot,
    DealIntelligence,
    BuyingCommitteeMember,
    RecommendedAction,
    ObjectionHandler,
    ConfidenceAssessment,
    Priority,
    LeadGrade,
)
from utils.llm import call_llm
from pydantic import BaseModel, Field


def _determine_priority(qualification: QualificationResult | None, contact: ContactIntelligence | None) -> Priority:
    """Deterministic priority assignment."""
    if not qualification:
        return Priority.P3_NURTURE

    grade = qualification.grade
    buying_role = contact.buying_role.value if contact else "Unknown"
    score = qualification.total_score

    high_value_roles = ["Economic Buyer", "Champion"]

    if grade == LeadGrade.A and buying_role in high_value_roles:
        return Priority.P0_CALL_TODAY
    elif grade == LeadGrade.A:
        return Priority.P1_CALL_THIS_WEEK
    elif grade == LeadGrade.B and buying_role in high_value_roles:
        return Priority.P1_CALL_THIS_WEEK
    elif grade == LeadGrade.B:
        return Priority.P2_SEQUENCE_FIRST
    elif grade == LeadGrade.C:
        return Priority.P2_SEQUENCE_FIRST
    else:
        return Priority.P3_NURTURE


def run_handoff_agent(
    lead: LeadRecord,
    research: AccountResearch | None,
    contact: ContactIntelligence | None,
    qualification: QualificationResult | None,
    case_studies: CaseStudyMatches | None,
    gtm_email: GTMAndEmailResult | None,
) -> HandoffBrief:
    """
    Generate the AE handoff briefing document.
    Uses LLM for synthesis of talking points and objection handlers.
    """
    priority = _determine_priority(qualification, contact)
    score = qualification.total_score if qualification else 0
    grade = qualification.grade if qualification else LeadGrade.D

    # Build one-line summary
    industry = research.company_profile.industry.value if research else "unknown"
    emp_count = research.company_profile.employee_count if research else None
    emp_str = f"{emp_count:,} employees" if emp_count else "size unknown"
    company = lead.company.name
    name = f"{lead.contact.first_name} {lead.contact.last_name}"
    title = lead.contact.job_title

    # Key signal from form message
    key_signal = ""
    if lead.intent_signals.form_message:
        key_signal = lead.intent_signals.form_message[:80]
    elif research and research.pain_hypotheses:
        key_signal = research.pain_hypotheses[0].pain

    one_line = f"{name}, {title} at {company} — {industry}, {emp_str}"
    if key_signal:
        one_line += f", \"{key_signal}\""

    # Company snapshot
    what_they_do = f"{company} is a {industry} company"
    if research:
        if research.company_profile.hq_location:
            what_they_do += f" headquartered in {research.company_profile.hq_location}"
        what_they_do += f" with approximately {emp_str}."
        if research.strategic_context.key_initiatives:
            what_they_do += f" Key initiatives: {', '.join(research.strategic_context.key_initiatives[:3])}."
    else:
        what_they_do += "."

    why_flytbase = "FlytBase can help with "
    if research and research.pain_hypotheses:
        pains = [p.pain for p in research.pain_hypotheses[:3]]
        why_flytbase += ", ".join(pains) + "."
    else:
        why_flytbase += f"automating drone operations in the {industry} sector."

    risks = []
    if research and research.drone_relevance.drone_vendors_detected:
        risks.append(f"Existing vendor relationship: {', '.join(research.drone_relevance.drone_vendors_detected)}")
    if not research or research.research_confidence < 0.5:
        risks.append("Limited research data — high uncertainty")
    if qualification and qualification.confidence < 0.5:
        risks.append("Low qualification confidence — verify in discovery call")

    # Contact snapshot
    role_str = contact.buying_role.value if contact else "Unknown"
    who = f"{name} is {title} at {company}. Likely buying role: {role_str}."
    approach = "Use a consultative approach."
    if contact:
        approach = f"Recommended tone: {contact.communication_preferences.recommended_tone.value}. "
        approach += f"Recommended length: {contact.communication_preferences.recommended_length}."

    # Deal intelligence
    deal_size = gtm_email.gtm_decision.deal_size_estimate if gtm_email else "Unknown"
    cycle = gtm_email.gtm_decision.sales_cycle_estimate if gtm_email else "Unknown"
    competition = research.drone_relevance.drone_vendors_detected if research else []

    buying_committee = [
        BuyingCommitteeMember(role="Economic Buyer", likely_title="VP/SVP Operations", identified=False),
        BuyingCommitteeMember(role="Technical Buyer", likely_title="IT Director / Drone Program Manager", identified=False),
        BuyingCommitteeMember(role="Champion", likely_title=title, identified=True, name=name),
        BuyingCommitteeMember(role="End User", likely_title="Site Manager / Drone Operator", identified=False),
    ]

    # Generate talking points and objection handlers via LLM
    context = {
        "prospect_name": lead.contact.first_name,
        "company": company,
        "industry": industry,
        "title": title,
        "pains": [p.pain for p in research.pain_hypotheses[:3]] if research else [],
        "drone_status": research.drone_relevance.current_drone_usage.value if research else "unknown",
        "competitors": competition,
        "case_studies": [cs.one_line_hook for cs in case_studies.matched_case_studies[:2]] if case_studies else [],
        "form_message": lead.intent_signals.form_message or "",
    }

    llm_prompt = f"""Generate talking points and objection handlers for a sales call.

Context:
{json.dumps(context, indent=2)}

Return JSON:
{{
  "talking_points": ["5 talking points the AE can say verbatim on a call"],
  "objection_handlers": [
    {{"objection": "likely objection", "response": "how to handle it"}},
    {{"objection": "...", "response": "..."}}
  ],
  "recommended_actions": [
    {{"action": "what to do", "priority": 1, "deadline": "when"}}
  ]
}}

Rules:
- Talking points should be in second person ("You mentioned...", "I noticed...")
- Objection handlers should be specific to THIS prospect
- Actions should be concrete and time-bound
- Return ONLY JSON, no markdown
"""

    raw = call_llm(
        system_prompt="You are a sales strategist preparing an AE for a discovery call. Be specific and practical.",
        user_prompt=llm_prompt,
        model="gpt-4o-mini",
        temperature=0.4,
        max_tokens=2000,
    )

    # Parse LLM output
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
        llm_data = json.loads(cleaned)
    except (json.JSONDecodeError, KeyError):
        llm_data = {
            "talking_points": [f"I noticed {company} is in {industry} — how are you currently handling drone operations?"],
            "objection_handlers": [{"objection": "Not a priority", "response": "Understood — many of our customers started with a small pilot. Would it help to see how companies like yours got started?"}],
            "recommended_actions": [{"action": f"Call {lead.contact.first_name}", "priority": 1, "deadline": "Today"}],
        }

    talking_points = llm_data.get("talking_points", [])

    objection_handlers = [
        ObjectionHandler(objection=o["objection"], response=o["response"])
        for o in llm_data.get("objection_handlers", [])[:4]
    ]

    actions = [
        RecommendedAction(
            action=a["action"],
            priority=a.get("priority", 3),
            deadline=a.get("deadline", "This week"),
        )
        for a in llm_data.get("recommended_actions", [])[:5]
    ]

    # Confidence assessment
    data_gaps = []
    assumptions = []
    if not research or research.research_confidence < 0.5:
        data_gaps.append("Limited company research available")
    if not contact or contact.research_confidence < 0.3:
        data_gaps.append("Contact intelligence is limited to title-based heuristics")
    if not case_studies or not case_studies.matched_case_studies:
        data_gaps.append("No matching case studies found")
    if not lead.intent_signals.form_message:
        data_gaps.append("No form message — intent unclear")

    assumptions.append(f"Assumed {name} is a {role_str} based on title analysis")
    if research and research.drone_relevance.estimated_site_count:
        assumptions.append(f"Estimated {research.drone_relevance.estimated_site_count} sites based on company size")

    overall_confidence = qualification.confidence if qualification else 0.3

    cs_refs = [cs.title for cs in case_studies.matched_case_studies[:3]] if case_studies else []

    return HandoffBrief(
        priority=priority,
        one_line_summary=one_line,
        lead_score=score,
        lead_grade=grade,
        company_snapshot=CompanySnapshot(
            what_they_do=what_they_do,
            why_they_need_flytbase=why_flytbase,
            key_risks=risks,
        ),
        contact_snapshot=ContactSnapshot(
            who_they_are=who,
            buying_role=role_str,
            how_to_approach=approach,
        ),
        deal_intelligence=DealIntelligence(
            estimated_deal_size=deal_size,
            estimated_sales_cycle=cycle,
            competition=competition,
            buying_committee=buying_committee,
            champion_potential="high" if role_str in ["Champion", "Economic Buyer"] else "medium",
        ),
        recommended_actions=actions,
        talking_points=talking_points,
        objection_handlers=objection_handlers,
        case_studies_to_reference=cs_refs,
        confidence_assessment=ConfidenceAssessment(
            overall=overall_confidence,
            data_gaps=data_gaps,
            assumptions_made=assumptions,
        ),
    )
