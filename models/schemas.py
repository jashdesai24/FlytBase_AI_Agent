"""
Pydantic models defining typed contracts between all agents.
These schemas ARE the API between agents — if a schema changes, downstream agents must adapt.
"""

from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum
import re


# ── Enums ──────────────────────────────────────────────────────────────────────

class Seniority(str, Enum):
    C_SUITE = "C-Suite"
    VP = "VP"
    DIRECTOR = "Director"
    MANAGER = "Manager"
    IC = "IC"
    UNKNOWN = "Unknown"


class BuyingRole(str, Enum):
    ECONOMIC_BUYER = "Economic Buyer"
    TECHNICAL_BUYER = "Technical Buyer"
    CHAMPION = "Champion"
    INFLUENCER = "Influencer"
    END_USER = "End User"
    GATEKEEPER = "Gatekeeper"
    UNKNOWN = "Unknown"


class Department(str, Enum):
    OPERATIONS = "Operations"
    SECURITY = "Security"
    IT = "IT"
    SAFETY = "Safety"
    INNOVATION = "Innovation"
    ENGINEERING = "Engineering"
    PROCUREMENT = "Procurement"
    EXECUTIVE = "Executive"
    OTHER = "Other"


class Industry(str, Enum):
    MINING = "mining"
    SECURITY = "security"
    UTILITIES = "utilities"
    CONSTRUCTION = "construction"
    LOGISTICS = "logistics"
    PUBLIC_SAFETY = "public_safety"
    ENERGY = "energy"
    AGRICULTURE = "agriculture"
    MARITIME = "maritime"
    OIL_AND_GAS = "oil_and_gas"
    OTHER = "other"


class DroneUsage(str, Enum):
    ACTIVE = "active"
    PILOTING = "piloting"
    EVALUATING = "evaluating"
    NONE = "none"
    UNKNOWN = "unknown"


class LeadGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class Disposition(str, Enum):
    QUALIFIED_HOT = "qualified_hot"
    QUALIFIED_WARM = "qualified_warm"
    NURTURE = "nurture"
    DISQUALIFY = "disqualify"


class GTMMotion(str, Enum):
    DIRECT_AE = "direct_ae"
    PARTNER_LED = "partner_led"
    CHANNEL = "channel"
    ENTERPRISE_PROGRAM = "enterprise_program"
    PRODUCT_LED = "product_led"


class Priority(str, Enum):
    P0_CALL_TODAY = "P0_call_today"
    P1_CALL_THIS_WEEK = "P1_call_this_week"
    P2_SEQUENCE_FIRST = "P2_scheduled_sequence"
    P3_NURTURE = "P3_nurture"


class Tone(str, Enum):
    EXECUTIVE_BRIEF = "executive_brief"
    TECHNICAL_DEEP = "technical_deep"
    CONSULTATIVE = "consultative"
    PEER_TO_PEER = "peer_to_peer"


# ── Agent 1: Lead Intake ───────────────────────────────────────────────────────

class ContactInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    job_title: str
    seniority: Seniority = Seniority.UNKNOWN
    linkedin_url: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v.strip()):
            raise ValueError(f"Invalid email format: {v}")
        return v.strip().lower()


class CompanyInfo(BaseModel):
    name: str
    domain: str
    industry_raw: Optional[str] = None
    employee_count_estimate: Optional[int] = None
    country: Optional[str] = None


class IntentSignals(BaseModel):
    form_message: Optional[str] = None
    page_visited: Optional[str] = None
    content_downloaded: Optional[str] = None
    utm_campaign: Optional[str] = None


class LeadRecord(BaseModel):
    """Output of Agent 1: Lead Intake & Normalization"""
    lead_id: str
    contact: ContactInfo
    company: CompanyInfo
    intent_signals: IntentSignals
    parse_confidence: float = Field(ge=0.0, le=1.0)
    missing_fields: list[str] = Field(default_factory=list)


# ── Agent 2: Account Research ──────────────────────────────────────────────────

class CompanyProfile(BaseModel):
    name: str
    domain: str
    industry: Industry = Industry.OTHER
    sub_industry: Optional[str] = None
    employee_count: Optional[int] = None
    revenue_estimate: Optional[str] = None
    hq_location: Optional[str] = None
    global_presence: list[str] = Field(default_factory=list)
    is_public: bool = False


class DroneRelevance(BaseModel):
    current_drone_usage: DroneUsage = DroneUsage.UNKNOWN
    drone_vendors_detected: list[str] = Field(default_factory=list)
    bvlos_interest_signals: list[str] = Field(default_factory=list)
    site_types: list[str] = Field(default_factory=list)
    estimated_site_count: Optional[int] = None
    regulatory_environment: Optional[str] = None


class NewsItem(BaseModel):
    headline: str
    date: Optional[str] = None
    source: Optional[str] = None
    relevance: Optional[str] = None


class StrategicContext(BaseModel):
    recent_news: list[NewsItem] = Field(default_factory=list)
    key_initiatives: list[str] = Field(default_factory=list)
    technology_stack_signals: list[str] = Field(default_factory=list)
    competitor_landscape: list[str] = Field(default_factory=list)


class PainHypothesis(BaseModel):
    pain: str
    evidence: str
    confidence: float = Field(ge=0.0, le=1.0)
    source_url: Optional[str] = None


class AccountResearch(BaseModel):
    """Output of Agent 2: Account Research"""
    company_profile: CompanyProfile
    drone_relevance: DroneRelevance
    strategic_context: StrategicContext
    pain_hypotheses: list[PainHypothesis] = Field(default_factory=list)
    research_confidence: float = Field(ge=0.0, le=1.0)
    sources_consulted: list[str] = Field(default_factory=list)
    contradictions_detected: list[str] = Field(default_factory=list)


# ── Agent 3: Contact Intelligence ─────────────────────────────────────────────

class ContactProfile(BaseModel):
    full_name: str
    verified_title: str
    seniority: Seniority = Seniority.UNKNOWN
    department: Department = Department.OTHER
    linkedin_headline: Optional[str] = None


class CommunicationPreferences(BaseModel):
    recommended_tone: Tone = Tone.CONSULTATIVE
    recommended_length: str = "medium"  # short | medium | detailed
    likely_objections: list[str] = Field(default_factory=list)


class ContactIntelligence(BaseModel):
    """Output of Agent 3: Contact Intelligence"""
    contact_profile: ContactProfile
    buying_role: BuyingRole = BuyingRole.UNKNOWN
    persona_signals: dict = Field(default_factory=dict)
    communication_preferences: CommunicationPreferences = Field(
        default_factory=CommunicationPreferences
    )
    research_confidence: float = Field(ge=0.0, le=1.0, default=0.5)


# ── Agent 4: Qualification & Scoring ───────────────────────────────────────────

class ScoringFactor(BaseModel):
    value: int
    max_value: int
    reason: str


class ScoringBreakdown(BaseModel):
    # Company Fit (max 25)
    industry_match: ScoringFactor
    company_size: ScoringFactor
    geography: ScoringFactor
    technology_readiness: ScoringFactor
    revenue_potential: ScoringFactor

    # Contact Fit (max 20)
    seniority_score: ScoringFactor
    buying_role_score: ScoringFactor
    department_relevance: ScoringFactor

    # Intent Strength (max 25)
    form_message_urgency: ScoringFactor
    use_case_clarity: ScoringFactor
    content_engagement: ScoringFactor
    competitive_mention: ScoringFactor

    # Pain Evidence (max 20)
    identified_pains: ScoringFactor
    pain_urgency: ScoringFactor
    pain_flytbase_fit: ScoringFactor

    # Timing (max 10)
    budget_cycle: ScoringFactor
    trigger_events: ScoringFactor
    competitive_evaluation: ScoringFactor

    @property
    def company_fit_total(self) -> int:
        return (
            self.industry_match.value
            + self.company_size.value
            + self.geography.value
            + self.technology_readiness.value
            + self.revenue_potential.value
        )

    @property
    def contact_fit_total(self) -> int:
        return (
            self.seniority_score.value
            + self.buying_role_score.value
            + self.department_relevance.value
        )

    @property
    def intent_total(self) -> int:
        return (
            self.form_message_urgency.value
            + self.use_case_clarity.value
            + self.content_engagement.value
            + self.competitive_mention.value
        )

    @property
    def pain_total(self) -> int:
        return (
            self.identified_pains.value
            + self.pain_urgency.value
            + self.pain_flytbase_fit.value
        )

    @property
    def timing_total(self) -> int:
        return (
            self.budget_cycle.value
            + self.trigger_events.value
            + self.competitive_evaluation.value
        )

    @property
    def total_score(self) -> int:
        return (
            self.company_fit_total
            + self.contact_fit_total
            + self.intent_total
            + self.pain_total
            + self.timing_total
        )


class MEDDPICCSignals(BaseModel):
    metrics: Optional[str] = None
    economic_buyer: Optional[str] = None
    decision_criteria: Optional[str] = None
    decision_process: Optional[str] = None
    paper_process: Optional[str] = None
    identify_pain: Optional[str] = None
    champion: Optional[str] = None
    competition: Optional[str] = None


class QualificationResult(BaseModel):
    """Output of Agent 4: Qualification & Scoring"""
    total_score: int = Field(ge=0, le=100)
    grade: LeadGrade
    disposition: Disposition
    confidence: float = Field(ge=0.0, le=1.0)
    scoring_breakdown: ScoringBreakdown
    meddpicc_signals: MEDDPICCSignals = Field(default_factory=MEDDPICCSignals)
    disqualification_reasons: list[str] = Field(default_factory=list)
    missing_critical_data: list[str] = Field(default_factory=list)


# ── Agent 5: Case Study Matching ───────────────────────────────────────────────

class CaseStudyMatch(BaseModel):
    case_study_id: str
    title: str
    customer_name: str
    industry: str
    use_case: str
    key_metric: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    match_reasons: list[str] = Field(default_factory=list)
    one_line_hook: str = ""


class CaseStudyMatches(BaseModel):
    """Output of Agent 5: Case Study Matching"""
    matched_case_studies: list[CaseStudyMatch] = Field(default_factory=list)
    match_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    no_match_fallback: Optional[str] = None


# ── Agent 6: GTM Router + Email Sequence ───────────────────────────────────────

class GTMDecision(BaseModel):
    motion: GTMMotion
    reasoning: str
    assigned_region: Optional[str] = None
    partner_name: Optional[str] = None
    deal_size_estimate: Optional[str] = None
    sales_cycle_estimate: Optional[str] = None


class Email(BaseModel):
    email_number: int
    subject: str
    body: str
    send_delay_hours: int = 0
    goal: str
    personalization_elements: list[str] = Field(default_factory=list)
    cta: str = ""


class EmailSequence(BaseModel):
    emails: list[Email] = Field(default_factory=list)


class GTMAndEmailResult(BaseModel):
    """Output of Agent 6: GTM Router + Email Sequence"""
    gtm_decision: GTMDecision
    email_sequence: EmailSequence


# ── Agent 7: AE Handoff ───────────────────────────────────────────────────────

class CompanySnapshot(BaseModel):
    what_they_do: str
    why_they_need_flytbase: str
    key_risks: list[str] = Field(default_factory=list)


class ContactSnapshot(BaseModel):
    who_they_are: str
    buying_role: str
    how_to_approach: str


class BuyingCommitteeMember(BaseModel):
    role: str
    likely_title: str
    identified: bool = False
    name: Optional[str] = None


class DealIntelligence(BaseModel):
    estimated_deal_size: Optional[str] = None
    estimated_sales_cycle: Optional[str] = None
    competition: list[str] = Field(default_factory=list)
    buying_committee: list[BuyingCommitteeMember] = Field(default_factory=list)
    champion_potential: str = "unknown"


class RecommendedAction(BaseModel):
    action: str
    priority: int = Field(ge=1, le=5)
    deadline: str = ""


class ObjectionHandler(BaseModel):
    objection: str
    response: str


class ConfidenceAssessment(BaseModel):
    overall: float = Field(ge=0.0, le=1.0)
    data_gaps: list[str] = Field(default_factory=list)
    assumptions_made: list[str] = Field(default_factory=list)


class HandoffBrief(BaseModel):
    """Output of Agent 7: AE Handoff & Briefing"""
    priority: Priority
    one_line_summary: str
    lead_score: int
    lead_grade: LeadGrade
    company_snapshot: CompanySnapshot
    contact_snapshot: ContactSnapshot
    deal_intelligence: DealIntelligence
    recommended_actions: list[RecommendedAction] = Field(default_factory=list)
    talking_points: list[str] = Field(default_factory=list)
    objection_handlers: list[ObjectionHandler] = Field(default_factory=list)
    case_studies_to_reference: list[str] = Field(default_factory=list)
    confidence_assessment: ConfidenceAssessment = Field(
        default_factory=lambda: ConfidenceAssessment(overall=0.5)
    )


# ── Raw Lead Input (from UI form) ─────────────────────────────────────────────

class RawLeadInput(BaseModel):
    """What the user enters in the Streamlit form"""
    first_name: str
    last_name: str
    email: str
    job_title: str
    company_name: str
    phone: Optional[str] = None
    message: Optional[str] = None
    page_visited: Optional[str] = None
