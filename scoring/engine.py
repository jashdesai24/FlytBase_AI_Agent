"""
Deterministic Lead Scoring Engine

This is pure code — NO LLM involved.
The LLM extracts signals (Agent 4). This engine maps signals to scores.
Why? Because LLMs are bad at consistent numerical scoring. Code is not.
"""

from models.schemas import (
    LeadRecord,
    AccountResearch,
    ContactIntelligence,
    QualificationResult,
    ScoringBreakdown,
    ScoringFactor,
    MEDDPICCSignals,
    Industry,
    Seniority,
    BuyingRole,
    Department,
    DroneUsage,
    LeadGrade,
    Disposition,
)


# ── Industry Scoring ───────────────────────────────────────────────────────────

CORE_INDUSTRIES = {
    Industry.MINING: 8,
    Industry.SECURITY: 8,
    Industry.UTILITIES: 8,
    Industry.ENERGY: 8,
    Industry.CONSTRUCTION: 7,
    Industry.OIL_AND_GAS: 8,
}

ADJACENT_INDUSTRIES = {
    Industry.LOGISTICS: 6,
    Industry.PUBLIC_SAFETY: 6,
    Industry.MARITIME: 6,
}

EMERGING_INDUSTRIES = {
    Industry.AGRICULTURE: 4,
}

# Default for Industry.OTHER = 2


def _score_industry(industry: Industry) -> ScoringFactor:
    if industry in CORE_INDUSTRIES:
        score = CORE_INDUSTRIES[industry]
        return ScoringFactor(value=score, max_value=8, reason=f"Core FlytBase industry: {industry.value}")
    elif industry in ADJACENT_INDUSTRIES:
        score = ADJACENT_INDUSTRIES[industry]
        return ScoringFactor(value=score, max_value=8, reason=f"Adjacent industry with proven use cases: {industry.value}")
    elif industry in EMERGING_INDUSTRIES:
        score = EMERGING_INDUSTRIES[industry]
        return ScoringFactor(value=score, max_value=8, reason=f"Emerging market with growth potential: {industry.value}")
    else:
        return ScoringFactor(value=2, max_value=8, reason=f"Non-core industry: {industry.value}")


def _score_company_size(employee_count: int | None) -> ScoringFactor:
    if employee_count is None:
        return ScoringFactor(value=2, max_value=5, reason="Employee count unknown")
    if employee_count >= 5000:
        return ScoringFactor(value=5, max_value=5, reason=f"Enterprise ({employee_count:,} employees)")
    elif employee_count >= 200:
        return ScoringFactor(value=4, max_value=5, reason=f"Mid-Market ({employee_count:,} employees)")
    elif employee_count >= 50:
        return ScoringFactor(value=3, max_value=5, reason=f"SMB ({employee_count:,} employees)")
    else:
        return ScoringFactor(value=1, max_value=5, reason=f"Startup/Small ({employee_count:,} employees)")


def _score_geography(country: str | None, global_presence: list[str] | None) -> ScoringFactor:
    if not country:
        return ScoringFactor(value=2, max_value=4, reason="Geography unknown")

    country_upper = country.upper()
    tier1 = ["US", "USA", "UNITED STATES", "UK", "UNITED KINGDOM", "AUSTRALIA", "CANADA",
             "GERMANY", "FRANCE", "NETHERLANDS", "SWITZERLAND", "DENMARK", "NORWAY", "SWEDEN"]
    tier2 = ["INDIA", "UAE", "SAUDI ARABIA", "QATAR", "BRAZIL", "MEXICO", "CHILE",
             "SINGAPORE", "JAPAN", "SOUTH KOREA", "ISRAEL"]
    tier3 = ["SOUTH AFRICA", "NIGERIA", "INDONESIA", "THAILAND", "PHILIPPINES", "VIETNAM",
             "COLOMBIA", "PERU", "ARGENTINA"]

    if any(t in country_upper for t in tier1):
        return ScoringFactor(value=4, max_value=4, reason=f"Tier 1 market: {country}")
    elif any(t in country_upper for t in tier2):
        return ScoringFactor(value=3, max_value=4, reason=f"Tier 2 market: {country}")
    elif any(t in country_upper for t in tier3):
        return ScoringFactor(value=2, max_value=4, reason=f"Tier 3 market: {country}")
    else:
        return ScoringFactor(value=1, max_value=4, reason=f"Other market: {country}")


def _score_tech_readiness(drone_usage: DroneUsage) -> ScoringFactor:
    scores = {
        DroneUsage.ACTIVE: (5, "Active drone program — ready for scale"),
        DroneUsage.PILOTING: (4, "Piloting drones — ready for production platform"),
        DroneUsage.EVALUATING: (3, "Evaluating drone solutions — active buyer"),
        DroneUsage.NONE: (1, "No drone usage detected"),
        DroneUsage.UNKNOWN: (2, "Drone usage unknown"),
    }
    score, reason = scores.get(drone_usage, (2, "Unknown"))
    return ScoringFactor(value=score, max_value=5, reason=reason)


def _score_revenue_potential(site_count: int | None) -> ScoringFactor:
    if site_count is None:
        return ScoringFactor(value=1, max_value=3, reason="Site count unknown")
    if site_count >= 10:
        return ScoringFactor(value=3, max_value=3, reason=f"Large multi-site ({site_count} sites)")
    elif site_count >= 3:
        return ScoringFactor(value=2, max_value=3, reason=f"Multi-site ({site_count} sites)")
    else:
        return ScoringFactor(value=1, max_value=3, reason=f"Single/few sites ({site_count})")


def _score_seniority(seniority: Seniority) -> ScoringFactor:
    scores = {
        Seniority.C_SUITE: (8, "C-Suite executive"),
        Seniority.VP: (7, "VP-level leader"),
        Seniority.DIRECTOR: (6, "Director-level"),
        Seniority.MANAGER: (4, "Manager-level"),
        Seniority.IC: (2, "Individual contributor"),
        Seniority.UNKNOWN: (1, "Seniority unknown"),
    }
    score, reason = scores.get(seniority, (1, "Unknown"))
    return ScoringFactor(value=score, max_value=8, reason=reason)


def _score_buying_role(role: BuyingRole) -> ScoringFactor:
    scores = {
        BuyingRole.ECONOMIC_BUYER: (7, "Controls budget — highest value contact"),
        BuyingRole.CHAMPION: (6, "Internal champion — drives initiatives"),
        BuyingRole.TECHNICAL_BUYER: (5, "Technical evaluator"),
        BuyingRole.INFLUENCER: (3, "Influencer — can push but not decide"),
        BuyingRole.END_USER: (2, "End user"),
        BuyingRole.GATEKEEPER: (2, "Gatekeeper — controls access"),
        BuyingRole.UNKNOWN: (1, "Role unknown"),
    }
    score, reason = scores.get(role, (1, "Unknown"))
    return ScoringFactor(value=score, max_value=7, reason=reason)


def _score_department(department: Department) -> ScoringFactor:
    high_relevance = {Department.OPERATIONS, Department.SECURITY, Department.SAFETY}
    medium_relevance = {Department.IT, Department.ENGINEERING, Department.INNOVATION, Department.EXECUTIVE}
    low_relevance = {Department.PROCUREMENT}

    if department in high_relevance:
        return ScoringFactor(value=5, max_value=5, reason=f"High-relevance department: {department.value}")
    elif department in medium_relevance:
        return ScoringFactor(value=4, max_value=5, reason=f"Relevant department: {department.value}")
    elif department in low_relevance:
        return ScoringFactor(value=3, max_value=5, reason=f"Procurement — gatekeeper potential")
    else:
        return ScoringFactor(value=1, max_value=5, reason=f"Low-relevance department: {department.value}")


def _score_form_urgency(form_message: str | None) -> ScoringFactor:
    if not form_message:
        return ScoringFactor(value=1, max_value=8, reason="No form message provided")

    msg_lower = form_message.lower()
    score = 1
    reasons = []

    # High urgency signals
    urgency_keywords = ["rfp", "rfi", "budget", "timeline", "deadline", "asap",
                        "urgent", "this quarter", "this year", "q1", "q2", "q3", "q4",
                        "procurement", "vendor selection", "evaluation"]
    for kw in urgency_keywords:
        if kw in msg_lower:
            score = max(score, 8)
            reasons.append(f"mentions '{kw}'")
            break

    # Medium urgency - specific use case
    use_case_keywords = ["inspection", "patrol", "monitoring", "surveillance",
                         "autonomous", "bvlos", "drone-in-a-box", "fleet",
                         "scale", "multiple sites"]
    if score < 8:
        for kw in use_case_keywords:
            if kw in msg_lower:
                score = max(score, 6)
                reasons.append(f"specific use case: '{kw}'")
                break

    # Low urgency - general interest
    if score <= 1:
        general_keywords = ["interested", "learn more", "information", "demo", "pricing"]
        for kw in general_keywords:
            if kw in msg_lower:
                score = 3
                reasons.append(f"general interest: '{kw}'")
                break

    reason = "; ".join(reasons) if reasons else "Vague or unclear message"
    return ScoringFactor(value=score, max_value=8, reason=reason)


def _score_use_case_clarity(form_message: str | None) -> ScoringFactor:
    if not form_message:
        return ScoringFactor(value=0, max_value=7, reason="No form message")

    msg_lower = form_message.lower()

    # Specific use case + site type = 7
    specific = ["mine site", "solar farm", "pipeline", "perimeter", "warehouse",
                "port", "construction site", "power line", "dam", "rail"]
    for term in specific:
        if term in msg_lower:
            return ScoringFactor(value=7, max_value=7, reason=f"Specific use case + site type: '{term}'")

    # General use case = 4
    general = ["inspection", "monitoring", "surveillance", "patrol", "mapping",
               "survey", "delivery", "emergency"]
    for term in general:
        if term in msg_lower:
            return ScoringFactor(value=4, max_value=7, reason=f"General use case: '{term}'")

    # Just exploring = 2
    exploring = ["exploring", "evaluating", "considering", "looking into"]
    for term in exploring:
        if term in msg_lower:
            return ScoringFactor(value=2, max_value=7, reason=f"Early exploration: '{term}'")

    return ScoringFactor(value=1, max_value=7, reason="No clear use case mentioned")


def _score_content_engagement(page_visited: str | None) -> ScoringFactor:
    if not page_visited:
        return ScoringFactor(value=1, max_value=5, reason="No page data")

    page_lower = page_visited.lower()

    if "pricing" in page_lower:
        return ScoringFactor(value=5, max_value=5, reason="Visited pricing page — high intent")
    elif "case-stud" in page_lower or "customer" in page_lower:
        return ScoringFactor(value=4, max_value=5, reason="Visited case studies — evaluating")
    elif "product" in page_lower or "platform" in page_lower or "feature" in page_lower:
        return ScoringFactor(value=3, max_value=5, reason="Visited product page")
    elif "blog" in page_lower or "resource" in page_lower:
        return ScoringFactor(value=1, max_value=5, reason="Visited blog/resources — early stage")
    else:
        return ScoringFactor(value=2, max_value=5, reason=f"Visited: {page_visited}")


def _score_competitive_mention(form_message: str | None, competitors: list[str] | None) -> ScoringFactor:
    competitors_found = []

    # Check form message
    if form_message:
        msg_lower = form_message.lower()
        known = ["skydio", "dronedeploy", "percepto", "auterion", "dji enterprise",
                 "flightops", "aloft", "pix4d"]
        for comp in known:
            if comp in msg_lower:
                competitors_found.append(comp)

    # Check research competitors
    if competitors:
        competitors_found.extend(competitors)

    competitors_found = list(set(competitors_found))

    if not competitors_found:
        return ScoringFactor(value=0, max_value=5, reason="No competitor mentions")

    # Check if actively evaluating
    if form_message and any(w in form_message.lower() for w in ["evaluating", "comparing", "vs", "versus", "alternative"]):
        return ScoringFactor(value=5, max_value=5, reason=f"Actively evaluating against: {', '.join(competitors_found)}")

    return ScoringFactor(value=3, max_value=5, reason=f"Competitors detected: {', '.join(competitors_found)}")


def _score_pains(pain_hypotheses: list) -> ScoringFactor:
    count = len(pain_hypotheses)
    evidenced = sum(1 for p in pain_hypotheses if p.confidence >= 0.5)

    if evidenced >= 3:
        return ScoringFactor(value=10, max_value=10, reason=f"{evidenced} pains identified with evidence")
    elif evidenced >= 2:
        return ScoringFactor(value=7, max_value=10, reason=f"{evidenced} pains with evidence")
    elif evidenced >= 1:
        return ScoringFactor(value=4, max_value=10, reason=f"{evidenced} pain identified")
    elif count > 0:
        return ScoringFactor(value=2, max_value=10, reason=f"{count} potential pains, low evidence")
    else:
        return ScoringFactor(value=0, max_value=10, reason="No pain points identified")


def _score_pain_urgency(form_message: str | None, pain_hypotheses: list) -> ScoringFactor:
    urgency_signals = ["safety incident", "regulatory", "compliance deadline", "audit",
                       "accident", "fatality", "mandate", "requirement"]

    found = []
    text = (form_message or "").lower()
    for pain in pain_hypotheses:
        text += " " + pain.pain.lower() + " " + pain.evidence.lower()

    for signal in urgency_signals:
        if signal in text:
            found.append(signal)

    if found:
        return ScoringFactor(value=5, max_value=5, reason=f"Urgency signals: {', '.join(found)}")

    efficiency = ["efficiency", "cost reduction", "scale", "automate", "reduce manual"]
    for signal in efficiency:
        if signal in text:
            return ScoringFactor(value=3, max_value=5, reason=f"Efficiency-driven: {signal}")

    return ScoringFactor(value=1, max_value=5, reason="No urgency signals detected")


def _score_pain_fit(pain_hypotheses: list, industry: Industry) -> ScoringFactor:
    flytbase_pains = {
        "manual_inspection", "site_monitoring", "perimeter_security", "safety",
        "scale", "multiple_sites", "remote", "bvlos", "autonomous", "fleet_management",
        "24_7", "surveillance", "patrol", "drone", "inspection"
    }

    matched = 0
    for pain in pain_hypotheses:
        pain_text = pain.pain.lower().replace(" ", "_")
        if any(fp in pain_text for fp in flytbase_pains):
            matched += 1

    if matched >= 2:
        return ScoringFactor(value=5, max_value=5, reason=f"{matched} pains directly addressable by FlytBase")
    elif matched == 1:
        return ScoringFactor(value=3, max_value=5, reason="1 pain addressable by FlytBase")
    elif industry in CORE_INDUSTRIES:
        return ScoringFactor(value=2, max_value=5, reason="Core industry, likely fit even without explicit pain match")
    else:
        return ScoringFactor(value=1, max_value=5, reason="No clear FlytBase pain fit")


def _score_budget_cycle() -> ScoringFactor:
    # At inbound stage, we rarely know budget cycle — default score
    return ScoringFactor(value=2, max_value=4, reason="Budget cycle unknown at inbound stage")


def _score_trigger_events(news: list, pain_hypotheses: list) -> ScoringFactor:
    triggers = ["funding", "expansion", "new hire", "acquisition", "contract",
                "partnership", "growth", "new facility", "new site"]

    found = []
    for item in news:
        headline_lower = item.headline.lower() if item.headline else ""
        for trigger in triggers:
            if trigger in headline_lower:
                found.append(f"{trigger}: {item.headline}")

    if found:
        return ScoringFactor(value=3, max_value=3, reason=f"Trigger events: {'; '.join(found[:2])}")

    return ScoringFactor(value=0, max_value=3, reason="No trigger events detected")


def _score_competitive_eval(form_message: str | None) -> ScoringFactor:
    if not form_message:
        return ScoringFactor(value=0, max_value=3, reason="No form message to evaluate")

    msg_lower = form_message.lower()
    if any(w in msg_lower for w in ["rfp", "rfi", "vendor selection", "shortlist"]):
        return ScoringFactor(value=3, max_value=3, reason="Active RFP/vendor selection")
    elif any(w in msg_lower for w in ["comparing", "evaluating", "alternative", "vs"]):
        return ScoringFactor(value=2, max_value=3, reason="Early-stage comparison")
    return ScoringFactor(value=0, max_value=3, reason="No competitive evaluation signals")


# ── Main Scoring Function ─────────────────────────────────────────────────────

def compute_lead_score(
    lead: LeadRecord,
    research: AccountResearch | None,
    contact: ContactIntelligence | None,
) -> QualificationResult:
    """
    Compute a deterministic lead score from 0-100.
    This function uses NO LLM — it's pure code.
    """

    # Extract signals from available data
    industry = research.company_profile.industry if research else Industry.OTHER
    employee_count = research.company_profile.employee_count if research else None
    country = research.company_profile.hq_location if research else lead.company.country
    global_presence = research.company_profile.global_presence if research else []
    drone_usage = research.drone_relevance.current_drone_usage if research else DroneUsage.UNKNOWN
    site_count = research.drone_relevance.estimated_site_count if research else None
    pains = research.pain_hypotheses if research else []
    news = research.strategic_context.recent_news if research else []
    research_competitors = research.drone_relevance.drone_vendors_detected if research else []

    seniority = contact.contact_profile.seniority if contact else lead.contact.seniority
    buying_role = contact.buying_role if contact else BuyingRole.UNKNOWN
    department = contact.contact_profile.department if contact else Department.OTHER

    form_message = lead.intent_signals.form_message
    page_visited = lead.intent_signals.page_visited

    # Compute all scoring factors
    breakdown = ScoringBreakdown(
        # Company Fit (max 25)
        industry_match=_score_industry(industry),
        company_size=_score_company_size(employee_count),
        geography=_score_geography(country, global_presence),
        technology_readiness=_score_tech_readiness(drone_usage),
        revenue_potential=_score_revenue_potential(site_count),
        # Contact Fit (max 20)
        seniority_score=_score_seniority(seniority),
        buying_role_score=_score_buying_role(buying_role),
        department_relevance=_score_department(department),
        # Intent Strength (max 25)
        form_message_urgency=_score_form_urgency(form_message),
        use_case_clarity=_score_use_case_clarity(form_message),
        content_engagement=_score_content_engagement(page_visited),
        competitive_mention=_score_competitive_mention(form_message, research_competitors),
        # Pain Evidence (max 20)
        identified_pains=_score_pains(pains),
        pain_urgency=_score_pain_urgency(form_message, pains),
        pain_flytbase_fit=_score_pain_fit(pains, industry),
        # Timing (max 10)
        budget_cycle=_score_budget_cycle(),
        trigger_events=_score_trigger_events(news, pains),
        competitive_evaluation=_score_competitive_eval(form_message),
    )

    total = breakdown.total_score

    # Assign grade
    if total >= 75:
        grade = LeadGrade.A
        disposition = Disposition.QUALIFIED_HOT
    elif total >= 55:
        grade = LeadGrade.B
        disposition = Disposition.QUALIFIED_WARM
    elif total >= 40:
        grade = LeadGrade.C
        disposition = Disposition.QUALIFIED_WARM
    elif total >= 15:
        grade = LeadGrade.D
        disposition = Disposition.NURTURE
    else:
        grade = LeadGrade.F
        disposition = Disposition.DISQUALIFY

    # Compute confidence
    confidence = 1.0
    missing = []
    if not research or research.research_confidence < 0.5:
        confidence -= 0.2
        missing.append("Low research confidence")
    if not contact or contact.research_confidence < 0.3:
        confidence -= 0.2
        missing.append("Low contact intelligence confidence")
    if not form_message:
        confidence -= 0.15
        missing.append("No form message")
    if industry == Industry.OTHER:
        confidence -= 0.1
        missing.append("Industry unknown")
    if employee_count is None:
        confidence -= 0.05
        missing.append("Employee count unknown")
    confidence = max(0.0, min(1.0, confidence))

    return QualificationResult(
        total_score=total,
        grade=grade,
        disposition=disposition,
        confidence=round(confidence, 2),
        scoring_breakdown=breakdown,
        meddpicc_signals=MEDDPICCSignals(),  # Populated later if needed
        disqualification_reasons=[] if total >= 15 else ["Score too low for outreach"],
        missing_critical_data=missing,
    )
