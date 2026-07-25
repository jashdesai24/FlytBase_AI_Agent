"""
Agent 2: Account Research
Deep-dives into the prospect's company using web search.
Produces structured firmographic, technographic, and pain point analysis.
"""

import os
from pathlib import Path
from tavily import TavilyClient
from models.schemas import (
    AccountResearch,
    CompanyProfile,
    DroneRelevance,
    StrategicContext,
    NewsItem,
    PainHypothesis,
    Industry,
    DroneUsage,
)
from utils.llm import call_llm_structured
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "research.txt"


class NewsExtraction(BaseModel):
    """Typed model for a news item extracted by LLM."""
    headline: str = ""
    date: Optional[str] = None
    source: Optional[str] = None
    relevance: Optional[str] = None


class PainExtraction(BaseModel):
    """Typed model for a pain hypothesis extracted by LLM."""
    pain: str = "Unknown pain"
    evidence: str = "No evidence provided"
    confidence: float = 0.5
    source_url: Optional[str] = None


class ResearchExtraction(BaseModel):
    """Internal model for LLM to fill from search results."""
    industry: str = "other"
    sub_industry: Optional[str] = None
    employee_count: Optional[int] = None
    revenue_estimate: Optional[str] = None
    hq_location: Optional[str] = None
    global_presence: list[str] = Field(default_factory=list)
    is_public: bool = False

    current_drone_usage: str = "unknown"
    drone_vendors_detected: list[str] = Field(default_factory=list)
    bvlos_interest_signals: list[str] = Field(default_factory=list)
    site_types: list[str] = Field(default_factory=list)
    estimated_site_count: Optional[int] = None

    recent_news: list[NewsExtraction] = Field(default_factory=list)
    key_initiatives: list[str] = Field(default_factory=list)
    technology_stack_signals: list[str] = Field(default_factory=list)
    competitor_landscape: list[str] = Field(default_factory=list)

    pain_hypotheses: list[PainExtraction] = Field(default_factory=list)
    research_confidence: float = 0.5
    sources_consulted: list[str] = Field(default_factory=list)
    contradictions_detected: list[str] = Field(default_factory=list)


def _search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """Run a Tavily search and return results."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or api_key.startswith("your-"):
        return [{"title": "Search unavailable", "content": "Tavily API key not configured", "url": ""}]

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=max_results, include_raw_content=False)
        return response.get("results", [])
    except Exception as e:
        return [{"title": "Search error", "content": str(e), "url": ""}]


def run_research_agent(company_name: str, company_domain: str) -> AccountResearch:
    """
    Research a company using web search and produce structured output.
    Runs 3 targeted searches to maximize signal quality while controlling cost.
    """
    # Run 3 targeted searches
    searches = [
        f"{company_name} company overview employees industry revenue",
        f"{company_name} drone UAV BVLOS autonomous operations technology",
        f"{company_name} recent news 2024 2025 strategy digital transformation",
    ]

    # Try Tavily, fall back to LLM-only research if unavailable
    all_results = []
    tavily_available = True

    try:
        for query in searches:
            results = _search_tavily(query, max_results=4)
            # Check if search actually returned useful results
            if results and results[0].get("title") not in ("Search unavailable", "Search error"):
                all_results.extend(results)
            else:
                tavily_available = False
                break
    except Exception:
        tavily_available = False

    if tavily_available and all_results:
        search_context = "\n\n".join(
            f"SOURCE: {r.get('url', 'N/A')}\nTITLE: {r.get('title', 'N/A')}\nCONTENT: {r.get('content', 'No content')}"
            for r in all_results
            if r.get("content")
        )
        research_mode = "web search"
    else:
        search_context = "(No web search available — use your training knowledge about this company.)"
        research_mode = "LLM knowledge only"

    # Load system prompt
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    user_prompt = f"""
Research this company:
Company Name: {company_name}
Company Domain: {company_domain}

Here are the search results to analyze:

{search_context}

Based on these search results, produce a comprehensive company research profile.
Remember: cite sources for every claim. Say "No information found" if data is missing.

CRITICAL: Keep all string values SHORT and CONCISE (1-2 sentences max). Do NOT write long paragraphs.
For lists, use 3-5 items maximum. For pain hypotheses, limit to top 3.
"""

    # Call LLM for structured extraction
    extraction = call_llm_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=ResearchExtraction,
        model="gpt-4o",  # Use stronger model for research synthesis
        temperature=0.2,
        max_tokens=8000,
    )

    # Map to canonical schema
    industry_map = {v.value: v for v in Industry}
    industry = industry_map.get(extraction.industry.lower(), Industry.OTHER)

    drone_usage_map = {v.value: v for v in DroneUsage}
    drone_usage = drone_usage_map.get(extraction.current_drone_usage.lower(), DroneUsage.UNKNOWN)

    # Build pain hypotheses
    pains = []
    for p in extraction.pain_hypotheses:
        pains.append(PainHypothesis(
            pain=p.pain,
            evidence=p.evidence,
            confidence=float(p.confidence),
            source_url=p.source_url,
        ))

    # Build news items
    news_items = []
    for n in extraction.recent_news:
        news_items.append(NewsItem(
            headline=n.headline,
            date=n.date,
            source=n.source,
            relevance=n.relevance,
        ))

    # Collect all source URLs
    sources = list(set(
        r.get("url", "") for r in all_results if r.get("url")
    ))

    return AccountResearch(
        company_profile=CompanyProfile(
            name=company_name,
            domain=company_domain,
            industry=industry,
            sub_industry=extraction.sub_industry,
            employee_count=extraction.employee_count,
            revenue_estimate=extraction.revenue_estimate,
            hq_location=extraction.hq_location,
            global_presence=extraction.global_presence,
            is_public=extraction.is_public,
        ),
        drone_relevance=DroneRelevance(
            current_drone_usage=drone_usage,
            drone_vendors_detected=extraction.drone_vendors_detected,
            bvlos_interest_signals=extraction.bvlos_interest_signals,
            site_types=extraction.site_types,
            estimated_site_count=extraction.estimated_site_count,
        ),
        strategic_context=StrategicContext(
            recent_news=news_items,
            key_initiatives=extraction.key_initiatives,
            technology_stack_signals=extraction.technology_stack_signals,
            competitor_landscape=extraction.competitor_landscape,
        ),
        pain_hypotheses=pains,
        research_confidence=extraction.research_confidence,
        sources_consulted=sources,
        contradictions_detected=extraction.contradictions_detected,
    )
