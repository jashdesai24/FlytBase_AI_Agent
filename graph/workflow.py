"""
LangGraph Workflow — Orchestrates all 7 agents into a DAG.
Supports parallel execution of Research + Contact agents.
"""

from langgraph.graph import StateGraph, START, END
from graph.state import BDRAgentState
from models.schemas import RawLeadInput, Disposition

from agents.intake import run_intake_agent
from agents.research import run_research_agent
from agents.contact import run_contact_agent
from agents.qualification import run_qualification_agent
from agents.case_study import run_case_study_agent
from agents.email_generator import run_email_agent
from agents.handoff import run_handoff_agent

import time


# ── Node Functions ─────────────────────────────────────────────────────────────
# IMPORTANT: execution_log uses an `operator.add` reducer, so each node must
# return ONLY the new entries (a list with the delta), NOT the accumulated list.
# Similarly agent_errors uses a merge-dict reducer — return only new keys.

def intake_node(state: dict) -> dict:
    """Agent 1: Parse and normalize the raw lead input."""
    raw = RawLeadInput.model_validate(state["raw_input"])
    start = time.time()

    try:
        lead_record = run_intake_agent(raw)
        elapsed = round(time.time() - start, 2)
        return {
            "lead_record": lead_record.model_dump(),
            "current_agent": "intake",
            "execution_log": [f"Intake Agent completed in {elapsed}s"],
        }
    except Exception as e:
        return {
            "current_agent": "intake",
            "agent_errors": {"intake": str(e)},
            "execution_log": [f"Intake Agent failed: {str(e)[:100]}"],
        }


def research_node(state: dict) -> dict:
    """Agent 2: Deep-dive research on the company."""
    lead = state.get("lead_record")
    if not lead:
        return {
            "current_agent": "research",
            "execution_log": ["Research skipped: no lead record"],
        }

    start = time.time()
    try:
        company_name = lead["company"]["name"]
        company_domain = lead["company"]["domain"]

        research = run_research_agent(company_name, company_domain)
        elapsed = round(time.time() - start, 2)
        return {
            "account_research": research.model_dump(),
            "current_agent": "research",
            "execution_log": [f"Research Agent completed in {elapsed}s"],
        }
    except Exception as e:
        return {
            "current_agent": "research",
            "agent_errors": {"research": str(e)},
            "execution_log": [f"Research Agent failed: {str(e)[:100]}"],
        }


def contact_node(state: dict) -> dict:
    """Agent 3: Contact intelligence."""
    lead = state.get("lead_record")
    if not lead:
        return {
            "current_agent": "contact",
            "execution_log": ["Contact skipped: no lead record"],
        }

    start = time.time()
    try:
        from models.schemas import Seniority
        contact = lead["contact"]
        seniority = Seniority(contact.get("seniority", "Unknown"))

        intelligence = run_contact_agent(
            first_name=contact["first_name"],
            last_name=contact["last_name"],
            job_title=contact["job_title"],
            company_name=lead["company"]["name"],
            email=contact["email"],
            seniority_hint=seniority,
        )
        elapsed = round(time.time() - start, 2)
        return {
            "contact_intelligence": intelligence.model_dump(),
            "current_agent": "contact",
            "execution_log": [f"Contact Agent completed in {elapsed}s"],
        }
    except Exception as e:
        return {
            "current_agent": "contact",
            "agent_errors": {"contact": str(e)},
            "execution_log": [f"Contact Agent failed: {str(e)[:100]}"],
        }


def qualification_node(state: dict) -> dict:
    """Agent 4: Score and qualify the lead."""
    start = time.time()
    try:
        from models.schemas import LeadRecord, AccountResearch, ContactIntelligence

        lead = LeadRecord.model_validate(state["lead_record"]) if state.get("lead_record") else None
        research = AccountResearch.model_validate(state["account_research"]) if state.get("account_research") else None
        contact = ContactIntelligence.model_validate(state["contact_intelligence"]) if state.get("contact_intelligence") else None

        if not lead:
            return {
                "current_agent": "qualification",
                "execution_log": ["Qualification skipped: no lead record"],
            }

        result = run_qualification_agent(lead, research, contact)
        is_qualified = result.total_score >= 40
        elapsed = round(time.time() - start, 2)

        return {
            "qualification": result.model_dump(),
            "is_qualified": is_qualified,
            "current_agent": "qualification",
            "execution_log": [
                f"Qualification Agent completed in {elapsed}s -- Score: {result.total_score}, Grade: {result.grade.value}, {'QUALIFIED' if is_qualified else 'NOT QUALIFIED'}"
            ],
        }
    except Exception as e:
        return {
            "current_agent": "qualification",
            "agent_errors": {"qualification": str(e)},
            "execution_log": [f"Qualification Agent failed: {str(e)[:100]}"],
        }


def should_continue(state: dict) -> str:
    """Decision node: route to case study matching or end."""
    if state.get("is_qualified", False):
        return "case_study"
    else:
        return "end_disqualified"


def case_study_node(state: dict) -> dict:
    """Agent 5: Match case studies."""
    start = time.time()
    try:
        from models.schemas import AccountResearch, QualificationResult

        research = AccountResearch.model_validate(state["account_research"]) if state.get("account_research") else None
        qualification = QualificationResult.model_validate(state["qualification"]) if state.get("qualification") else None

        matches = run_case_study_agent(research, qualification)
        elapsed = round(time.time() - start, 2)
        matched_count = len(matches.matched_case_studies)
        return {
            "case_study_matches": matches.model_dump(),
            "current_agent": "case_study",
            "execution_log": [
                f"Case Study Agent completed in {elapsed}s -- {matched_count} matches found"
            ],
        }
    except Exception as e:
        return {
            "current_agent": "case_study",
            "agent_errors": {"case_study": str(e)},
            "execution_log": [f"Case Study Agent failed: {str(e)[:100]}"],
        }


def email_node(state: dict) -> dict:
    """Agent 6: GTM routing + email sequence generation."""
    start = time.time()
    try:
        from models.schemas import LeadRecord, AccountResearch, ContactIntelligence, QualificationResult, CaseStudyMatches

        lead = LeadRecord.model_validate(state["lead_record"])
        research = AccountResearch.model_validate(state["account_research"]) if state.get("account_research") else None
        contact = ContactIntelligence.model_validate(state["contact_intelligence"]) if state.get("contact_intelligence") else None
        qualification = QualificationResult.model_validate(state["qualification"]) if state.get("qualification") else None
        case_studies = CaseStudyMatches.model_validate(state["case_study_matches"]) if state.get("case_study_matches") else None

        result = run_email_agent(lead, research, contact, qualification, case_studies)
        elapsed = round(time.time() - start, 2)
        return {
            "gtm_and_email": result.model_dump(),
            "current_agent": "email",
            "execution_log": [
                f"Email Agent completed in {elapsed}s -- GTM: {result.gtm_decision.motion.value}, {len(result.email_sequence.emails)} emails generated"
            ],
        }
    except Exception as e:
        return {
            "current_agent": "email",
            "agent_errors": {"email": str(e)},
            "execution_log": [f"Email Agent failed: {str(e)[:100]}"],
        }


def handoff_node(state: dict) -> dict:
    """Agent 7: Generate AE handoff briefing."""
    start = time.time()
    try:
        from models.schemas import (
            LeadRecord, AccountResearch, ContactIntelligence,
            QualificationResult, CaseStudyMatches, GTMAndEmailResult,
        )

        lead = LeadRecord.model_validate(state["lead_record"])
        research = AccountResearch.model_validate(state["account_research"]) if state.get("account_research") else None
        contact = ContactIntelligence.model_validate(state["contact_intelligence"]) if state.get("contact_intelligence") else None
        qualification = QualificationResult.model_validate(state["qualification"]) if state.get("qualification") else None
        case_studies = CaseStudyMatches.model_validate(state["case_study_matches"]) if state.get("case_study_matches") else None
        gtm_email = GTMAndEmailResult.model_validate(state["gtm_and_email"]) if state.get("gtm_and_email") else None

        brief = run_handoff_agent(lead, research, contact, qualification, case_studies, gtm_email)
        elapsed = round(time.time() - start, 2)
        return {
            "handoff_brief": brief.model_dump(),
            "current_agent": "handoff",
            "execution_log": [
                f"Handoff Agent completed in {elapsed}s -- Priority: {brief.priority.value}"
            ],
        }
    except Exception as e:
        return {
            "current_agent": "handoff",
            "agent_errors": {"handoff": str(e)},
            "execution_log": [f"Handoff Agent failed: {str(e)[:100]}"],
        }


def end_disqualified_node(state: dict) -> dict:
    """Terminal node for disqualified leads."""
    score = state.get("qualification", {}).get("total_score", 0)
    grade = state.get("qualification", {}).get("grade", "F")
    return {
        "current_agent": "complete_disqualified",
        "execution_log": [
            f"Lead disqualified -- Score: {score}, Grade: {grade}. Routed to nurture."
        ],
    }


# ── Build the Graph ────────────────────────────────────────────────────────────

def build_workflow():
    """
    Build and compile the LangGraph workflow.

    Architecture:
        Intake → [Research ∥ Contact] → Qualification → (qualified?)
            → Case Study → Email → Handoff → END
            → End Disqualified → END
    """
    workflow = StateGraph(BDRAgentState)

    # Add all nodes
    workflow.add_node("intake", intake_node)
    workflow.add_node("research", research_node)
    workflow.add_node("contact", contact_node)
    workflow.add_node("qualification", qualification_node)
    workflow.add_node("case_study", case_study_node)
    workflow.add_node("email", email_node)
    workflow.add_node("handoff", handoff_node)
    workflow.add_node("end_disqualified", end_disqualified_node)

    # Define edges
    workflow.add_edge(START, "intake")

    # After intake, run research and contact in parallel
    workflow.add_edge("intake", "research")
    workflow.add_edge("intake", "contact")

    # Both feed into qualification
    workflow.add_edge("research", "qualification")
    workflow.add_edge("contact", "qualification")

    # Conditional routing after qualification
    workflow.add_conditional_edges(
        "qualification",
        should_continue,
        {
            "case_study": "case_study",
            "end_disqualified": "end_disqualified",
        },
    )

    # Sequential: case_study → email → handoff → END
    workflow.add_edge("case_study", "email")
    workflow.add_edge("email", "handoff")
    workflow.add_edge("handoff", END)
    workflow.add_edge("end_disqualified", END)

    return workflow.compile()


# Pre-compiled graph
graph = build_workflow()
