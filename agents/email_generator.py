"""
Agent 6: GTM Router + Email Sequence Generator
Decides the go-to-market motion and generates personalized 3-email sequence.
"""

import json
from pathlib import Path
from models.schemas import (
    LeadRecord,
    AccountResearch,
    ContactIntelligence,
    QualificationResult,
    CaseStudyMatches,
    GTMAndEmailResult,
    GTMDecision,
    EmailSequence,
    Email,
    GTMMotion,
    Industry,
    Tone,
)
from utils.llm import call_llm
from pydantic import BaseModel, Field
from typing import Optional

PARTNERS_PATH = Path(__file__).parent.parent / "knowledge" / "partners.json"
PRODUCT_PATH = Path(__file__).parent.parent / "knowledge" / "product_knowledge.json"


def _load_partners() -> list[dict]:
    with open(PARTNERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_product_knowledge() -> dict:
    with open(PRODUCT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _find_partner(industry: str, country: str | None) -> dict | None:
    """Find the best matching partner for this lead."""
    partners = _load_partners()
    country = (country or "").lower()
    industry = industry.lower()

    best = None
    best_score = 0

    for p in partners:
        score = 0
        # Country match
        if any(c.lower() in country for c in p.get("countries", [])):
            score += 3
        # Region match
        if any(country in r.lower() for r in p.get("regions", [])):
            score += 2
        # Industry match
        if industry in [i.lower() for i in p.get("industries", [])]:
            score += 2
        # Tier bonus
        if p.get("tier") == "gold":
            score += 1

        if score > best_score:
            best_score = score
            best = p

    return best if best_score >= 3 else None


def _decide_gtm(
    lead: LeadRecord,
    research: AccountResearch | None,
    qualification: QualificationResult | None,
) -> GTMDecision:
    """
    Deterministic GTM routing decision tree.
    No LLM — pure logic.
    """
    employee_count = research.company_profile.employee_count if research else None
    industry = research.company_profile.industry.value if research else "other"
    country = research.company_profile.hq_location if research else lead.company.country
    total_score = qualification.total_score if qualification else 0

    # Estimate deal size
    site_count = (research.drone_relevance.estimated_site_count or 1) if research else 1
    if employee_count and employee_count >= 5000:
        per_site = 5000
    elif employee_count and employee_count >= 200:
        per_site = 3000
    else:
        per_site = 999
    estimated_deal = site_count * 2 * per_site  # 2 drones per site estimate
    deal_str = f"${estimated_deal:,} ARR"

    # Sales cycle estimate
    if employee_count and employee_count >= 5000:
        cycle = "6-12 months"
    elif employee_count and employee_count >= 200:
        cycle = "3-6 months"
    else:
        cycle = "1-3 months"

    # Find partner
    partner = _find_partner(industry, country)

    # Decision tree
    if employee_count and employee_count >= 5000:
        if estimated_deal >= 100000:
            motion = GTMMotion.ENTERPRISE_PROGRAM
            reasoning = f"Enterprise company ({employee_count:,} employees) with ${estimated_deal:,} estimated deal. Direct enterprise engagement."
        elif partner:
            motion = GTMMotion.PARTNER_LED
            reasoning = f"Enterprise company in {industry} with partner {partner['name']} available in {country}."
        else:
            motion = GTMMotion.DIRECT_AE
            reasoning = f"Enterprise company ({employee_count:,} employees). No partner match. Direct AE engagement."
    elif employee_count and employee_count >= 200:
        if partner:
            motion = GTMMotion.PARTNER_LED
            reasoning = f"Mid-market in {industry}. Partner {partner['name']} available for {country}."
        else:
            motion = GTMMotion.DIRECT_AE
            reasoning = f"Mid-market ({employee_count:,} employees). No partner. Direct AE."
    elif total_score >= 55:
        motion = GTMMotion.DIRECT_AE
        reasoning = f"SMB with strong score ({total_score}). Direct commercial AE."
    else:
        motion = GTMMotion.PRODUCT_LED
        reasoning = f"SMB with moderate score ({total_score}). Route to Pro plan self-serve."

    # Determine region
    region = "Americas"
    if country:
        c = country.lower()
        if any(r in c for r in ["europe", "uk", "germany", "france", "switzerland", "netherlands", "denmark", "norway", "sweden"]):
            region = "EMEA"
        elif any(r in c for r in ["india", "australia", "singapore", "japan", "china", "korea"]):
            region = "APAC"
        elif any(r in c for r in ["uae", "saudi", "qatar", "israel", "south africa"]):
            region = "EMEA"

    return GTMDecision(
        motion=motion,
        reasoning=reasoning,
        assigned_region=region,
        partner_name=partner["name"] if partner else None,
        deal_size_estimate=deal_str,
        sales_cycle_estimate=cycle,
    )


def _generate_email_sequence(
    lead: LeadRecord,
    research: AccountResearch | None,
    contact: ContactIntelligence | None,
    qualification: QualificationResult | None,
    case_studies: CaseStudyMatches | None,
    gtm: GTMDecision,
) -> EmailSequence:
    """Generate a 3-email personalized sequence using LLM."""

    product = _load_product_knowledge()

    # Build context for the LLM
    first_name = lead.contact.first_name
    company = lead.company.name
    title = lead.contact.job_title
    industry = research.company_profile.industry.value if research else "unknown"

    # Tone from contact intelligence
    tone = contact.communication_preferences.recommended_tone.value if contact else "consultative"

    # Build research summary
    research_summary = "No research available."
    if research:
        pains = "; ".join(p.pain for p in research.pain_hypotheses[:3])
        news = "; ".join(n.headline for n in research.strategic_context.recent_news[:2])
        drone_status = research.drone_relevance.current_drone_usage.value
        research_summary = (
            f"Industry: {industry}\n"
            f"Employee count: {research.company_profile.employee_count or 'unknown'}\n"
            f"Drone usage: {drone_status}\n"
            f"Competitors detected: {', '.join(research.drone_relevance.drone_vendors_detected) or 'None'}\n"
            f"Pain points: {pains or 'None identified'}\n"
            f"Recent news: {news or 'None'}\n"
            f"Tech stack: {', '.join(research.strategic_context.technology_stack_signals) or 'Unknown'}"
        )

    # Build case study context
    cs_context = "No matching case studies."
    if case_studies and case_studies.matched_case_studies:
        cs_parts = []
        for cs in case_studies.matched_case_studies[:2]:
            cs_parts.append(
                f"- {cs.customer_name} ({cs.industry}): {cs.key_metric}. "
                f"Hook: {cs.one_line_hook}"
            )
        cs_context = "\n".join(cs_parts)

    # Build competitor context
    competitor_context = ""
    if research and research.drone_relevance.drone_vendors_detected:
        comps = research.drone_relevance.drone_vendors_detected
        comp_data = product.get("competitors", [])
        for c in comp_data:
            if c["name"].lower() in [x.lower() for x in comps]:
                competitor_context += f"\nvs {c['name']}: {c['flytbase_advantage']}"

    system_prompt = f"""You are an elite B2B email copywriter for FlytBase, the leading drone autonomy platform.

FLYTBASE KEY DIFFERENTIATORS:
- Hardware-agnostic (works with DJI, others — no vendor lock-in)
- One-to-many operations (one pilot, multiple drones)
- Enterprise-grade security (ISO 27001, SOC 2)
- Flinks integration suite (Milestone, Genetec, SAP, SCADA)
- 125+ partners worldwide
- Pro plan at $99/month for getting started

COMPETITIVE POSITIONING:
{competitor_context or 'No specific competitor detected.'}

HARD RULES:
1. NEVER use: "I hope this email finds you well", "Just following up", "I wanted to reach out", "touch base", "circle back", "leverage", "synergy", "game-changer"
2. NEVER claim features not listed above
3. NEVER fabricate case study details — use ONLY what's provided
4. ALWAYS use the contact's first name: {first_name}
5. Subject lines: Max 8 words. No clickbait. No ALL CAPS.
6. NO exclamation marks except maximum one per email

TONE: {tone}
- executive_brief: Short sentences. Numbers over adjectives. No small talk.
- technical_deep: Technical specifics. APIs, integrations, architecture.
- consultative: Problem-solving partner. Ask questions. Show understanding.
- peer_to_peer: Casual, direct. Assume competence.
"""

    user_prompt = f"""Write a 3-email sequence for this prospect:

PROSPECT:
Name: {first_name} (Title: {title})
Company: {company}

RESEARCH:
{research_summary}

CASE STUDIES TO USE:
{cs_context}

GTM MOTION: {gtm.motion.value}
{f"Partner: {gtm.partner_name}" if gtm.partner_name else ""}

FORM MESSAGE: {lead.intent_signals.form_message or 'None provided'}

Write exactly 3 emails in this JSON format:
{{
  "emails": [
    {{
      "email_number": 1,
      "subject": "max 8 word subject line",
      "body": "email body, max 120 words",
      "goal": "what this email tries to achieve",
      "personalization_elements": ["list of personalization used"],
      "cta": "the call to action"
    }},
    {{
      "email_number": 2,
      "subject": "...",
      "body": "max 150 words",
      "goal": "...",
      "personalization_elements": [],
      "cta": "..."
    }},
    {{
      "email_number": 3,
      "subject": "...",
      "body": "max 100 words",
      "goal": "...",
      "personalization_elements": [],
      "cta": "..."
    }}
  ]
}}

Email 1: Lead with their pain/situation, not FlytBase features. Soft CTA.
Email 2: Lead with case study proof. Include specific metric. Calendar link CTA.
Email 3: Create gentle urgency with industry trend. Binary yes/no CTA.

Return ONLY the JSON. No markdown fences. No commentary.
"""

    raw = call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model="gpt-4o",
        temperature=0.6,
        max_tokens=3000,
    )

    # Parse the email sequence
    try:
        # Clean potential markdown fences
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
        data = json.loads(cleaned)
        emails_data = data.get("emails", [])
    except (json.JSONDecodeError, KeyError):
        # Fallback: create basic emails
        emails_data = [
            {
                "email_number": 1,
                "subject": f"{company}'s drone operations at scale",
                "body": f"Hi {first_name},\n\nI noticed {company} is exploring drone operations. FlytBase helps companies in {industry} automate and scale their drone programs.\n\nWorth a 15-minute conversation?\n\nBest regards",
                "goal": "Book discovery call",
                "personalization_elements": ["company name", "industry"],
                "cta": "15-minute call",
            }
        ]

    emails = []
    delays = [0, 72, 168]
    for i, e in enumerate(emails_data[:3]):
        emails.append(Email(
            email_number=e.get("email_number", i + 1),
            subject=e.get("subject", f"Email {i+1}"),
            body=e.get("body", ""),
            send_delay_hours=delays[i] if i < len(delays) else 168,
            goal=e.get("goal", ""),
            personalization_elements=e.get("personalization_elements", []),
            cta=e.get("cta", ""),
        ))

    return EmailSequence(emails=emails)


def run_email_agent(
    lead: LeadRecord,
    research: AccountResearch | None,
    contact: ContactIntelligence | None,
    qualification: QualificationResult | None,
    case_studies: CaseStudyMatches | None,
) -> GTMAndEmailResult:
    """
    Main entry point: decide GTM motion + generate email sequence.
    """
    gtm = _decide_gtm(lead, research, qualification)
    emails = _generate_email_sequence(lead, research, contact, qualification, case_studies, gtm)

    return GTMAndEmailResult(
        gtm_decision=gtm,
        email_sequence=emails,
    )
