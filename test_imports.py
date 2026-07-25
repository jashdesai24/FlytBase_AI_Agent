"""Quick test to verify all Gemini imports and graph compilation."""
import sys
sys.path.insert(0, ".")

# Test 1: google-genai SDK
from google import genai
print(f"[OK] google-genai imported")

# Test 2: LLM utils
from utils.llm import get_client, call_llm, call_llm_structured, _resolve_model
print(f"[OK] LLM utils imported")
print(f"     Model mapping: gpt-4o -> {_resolve_model('gpt-4o')}")
print(f"     Model mapping: gpt-4o-mini -> {_resolve_model('gpt-4o-mini')}")

# Test 3: All schemas
from models.schemas import LeadRecord, RawLeadInput, QualificationResult
print(f"[OK] Schemas imported")

# Test 4: Scoring engine
from scoring.engine import compute_lead_score
print(f"[OK] Scoring engine imported")

# Test 5: All agents
from agents.intake import run_intake_agent
from agents.research import run_research_agent
from agents.contact import run_contact_agent
from agents.qualification import run_qualification_agent
from agents.case_study import run_case_study_agent
from agents.email_generator import run_email_agent
from agents.handoff import run_handoff_agent
print(f"[OK] All 7 agents imported")

# Test 6: Graph compilation
from graph.workflow import graph
print(f"[OK] LangGraph compiled: {list(graph.nodes.keys())}")

print("\n=== ALL CHECKS PASSED - ready to run with Gemini API ===")
