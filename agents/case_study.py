"""
Agent 5: Case Study Matching
Semantic search over FlytBase case studies using ChromaDB.
Retrieves the most relevant case studies and generates personalized hooks.
"""

import json
from pathlib import Path
from typing import Optional
from models.schemas import (
    AccountResearch,
    QualificationResult,
    CaseStudyMatches,
    CaseStudyMatch,
    Industry,
)
from utils.llm import call_llm

# Lazy-loaded ChromaDB
_collection = None
_case_studies_data = None

CASE_STUDIES_PATH = Path(__file__).parent.parent / "knowledge" / "case_studies.json"


def _load_case_studies() -> list[dict]:
    """Load raw case study data."""
    global _case_studies_data
    if _case_studies_data is None:
        with open(CASE_STUDIES_PATH, "r", encoding="utf-8") as f:
            _case_studies_data = json.load(f)
    return _case_studies_data


def _get_collection():
    """Initialize ChromaDB collection with case study embeddings."""
    global _collection
    if _collection is not None:
        return _collection

    import chromadb
    from chromadb.utils import embedding_functions
    import os

    # Use ChromaDB's zero-latency local default embedding function to prevent exhausting
    # Google's free-tier API quota (15 RPM) during vector index initialization
    ef = embedding_functions.DefaultEmbeddingFunction()


    client = chromadb.Client()

    # Check if collection exists
    try:
        _collection = client.get_collection("case_studies", embedding_function=ef)
        return _collection
    except Exception:
        pass

    # Create and populate
    _collection = client.create_collection(
        name="case_studies",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    case_studies = _load_case_studies()

    documents = []
    metadatas = []
    ids = []

    for cs in case_studies:
        # Create rich document text for embedding
        doc_text = (
            f"Industry: {cs['industry']}. "
            f"Company: {cs['customer_name']}. "
            f"Use cases: {', '.join(cs['use_case'])}. "
            f"Pain points addressed: {', '.join(cs['pain_addressed'])}. "
            f"Summary: {cs['summary']}"
        )
        documents.append(doc_text)

        metadatas.append({
            "industry": cs["industry"],
            "geography": cs["geography"],
            "company_size": cs["company_size"],
            "title": cs["title"],
            "customer_name": cs["customer_name"],
        })

        ids.append(cs["id"])

    _collection.add(documents=documents, metadatas=metadatas, ids=ids)
    return _collection


def _generate_hook(case_study: dict, prospect_industry: str, prospect_company: str) -> str:
    """Generate a one-line personalized hook connecting case study to prospect."""
    prompt = f"""Write ONE sentence connecting this case study to the prospect's situation.

Case Study: {case_study['customer_name']} ({case_study['industry']}) - {case_study['summary'][:200]}
Key Metric: {json.dumps(case_study.get('key_metrics', {}))}

Prospect: {prospect_company} in {prospect_industry}

Rules:
- One sentence only, max 30 words
- Mention the specific metric from the case study
- Reference the prospect's industry
- Be specific, not generic
- Do NOT start with "Like" or "Similar to"
"""
    return call_llm(
        system_prompt="You write concise, compelling one-line sales hooks.",
        user_prompt=prompt,
        model="gpt-4o-mini",
        temperature=0.5,
        max_tokens=100,
    ).strip().strip('"')


def run_case_study_agent(
    research: AccountResearch | None,
    qualification: QualificationResult | None,
) -> CaseStudyMatches:
    """
    Find the most relevant case studies for this prospect.
    Uses semantic search + metadata filtering + LLM hook generation.
    """
    if not research:
        return CaseStudyMatches(
            matched_case_studies=[],
            match_confidence=0.0,
            no_match_fallback="generic_value_prop",
        )

    industry = research.company_profile.industry.value
    company_name = research.company_profile.name

    # Build search query from prospect profile
    pain_text = "; ".join(p.pain for p in research.pain_hypotheses[:3])
    site_text = ", ".join(research.drone_relevance.site_types[:3])
    use_case_text = research.drone_relevance.current_drone_usage.value

    query = (
        f"Industry: {industry}. "
        f"Pain points: {pain_text}. "
        f"Site types: {site_text}. "
        f"Drone maturity: {use_case_text}. "
        f"Company size: {research.company_profile.employee_count or 'unknown'} employees."
    )

    # Search ChromaDB
    collection = _get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=5,
        include=["documents", "metadatas", "distances"],
    )

    if not results or not results["ids"] or not results["ids"][0]:
        return CaseStudyMatches(
            matched_case_studies=[],
            match_confidence=0.0,
            no_match_fallback="generic_value_prop",
        )

    # Load full case study data for matched IDs
    all_cs = {cs["id"]: cs for cs in _load_case_studies()}
    matched = []

    for i, cs_id in enumerate(results["ids"][0][:3]):  # Top 3
        cs_data = all_cs.get(cs_id)
        if not cs_data:
            continue

        # Compute relevance score (ChromaDB returns distances, convert to similarity)
        distance = results["distances"][0][i] if results["distances"] else 1.0
        similarity = max(0.0, 1.0 - distance)  # cosine distance → similarity

        # Metadata boost
        if cs_data["industry"] == industry:
            similarity = min(1.0, similarity + 0.15)
        if cs_data.get("geography") == (research.company_profile.hq_location or ""):
            similarity = min(1.0, similarity + 0.10)

        # Determine match reasons
        match_reasons = []
        if cs_data["industry"] == industry:
            match_reasons.append("Same industry")
        if any(uc in cs_data.get("use_case", []) for uc in ["autonomous_inspection", "site_monitoring"]):
            match_reasons.append("Similar use case")
        if cs_data.get("company_size") == "enterprise" and (research.company_profile.employee_count or 0) >= 5000:
            match_reasons.append("Similar company size")
        if not match_reasons:
            match_reasons.append("Related technology application")

        # Generate personalized hook
        hook = _generate_hook(cs_data, industry, company_name)

        # Build key metric string
        metrics = cs_data.get("key_metrics", {})
        metric_str = "; ".join(f"{k}: {v}" for k, v in list(metrics.items())[:2])

        matched.append(CaseStudyMatch(
            case_study_id=cs_id,
            title=cs_data["title"],
            customer_name=cs_data["customer_name"],
            industry=cs_data["industry"],
            use_case=", ".join(cs_data.get("use_case", [])),
            key_metric=metric_str,
            relevance_score=round(similarity, 2),
            match_reasons=match_reasons,
            one_line_hook=hook,
        ))

    # Sort by relevance
    matched.sort(key=lambda x: x.relevance_score, reverse=True)

    confidence = matched[0].relevance_score if matched else 0.0

    return CaseStudyMatches(
        matched_case_studies=matched,
        match_confidence=round(confidence, 2),
        no_match_fallback="generic_value_prop" if not matched else None,
    )
