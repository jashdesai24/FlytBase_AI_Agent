# FlytBase Inbound BDR AI Agent

> **7 Specialized AI Agents · Deterministic Lead Scoring · Real-Time Web Research · Semantic Case Study Matching · Personalized Email Generation · Intelligent AE Handoff**

A production-grade inbound BDR (Business Development Representative) AI system that automatically qualifies leads, researches accounts, generates personalized email sequences, matches case studies, and creates AE handoff briefs — all in under 30 seconds.

## Architecture

```
Inbound Lead → [Agent 1: Intake] → [Agent 2: Research ∥ Agent 3: Contact]
    → [Agent 4: Qualification] → (Qualified?)
        → YES: [Agent 5: Case Study RAG] → [Agent 6: GTM + Email] → [Agent 7: AE Handoff]
        → NO: Auto-Nurture
```

**Key Design Decisions:**
- **Multi-agent DAG** — each agent has a single responsibility and typed contracts
- **Deterministic scoring** — LLM extracts signals, Python code assigns scores (no hallucinated scores)
- **Parallel execution** — Research + Contact agents run simultaneously
- **Semantic RAG** — ChromaDB vector search for case study matching
- **Fail-open** — missing data reduces confidence, doesn't crash the pipeline

## Quick Start

### 1. Install Backend Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Set API Keys

Edit `.env` and add your keys:

```
GEMINI_API_KEY=your-gemini-api-key
TAVILY_API_KEY=tvly-...
```

Get keys at:
- **Gemini**: https://aistudio.google.com/apikey (free tier: 15 req/min)
- **Tavily**: https://tavily.com (free tier: 1000 searches/month)

### 4. Run the App

Start both servers:

```bash
# Terminal 1 — Backend API (port 8000)
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend (port 3000)
cd frontend && npm run dev
```

Open http://localhost:3000 in your browser.

## Demo

1. Click **Launch Console** from the landing page
2. Select a **Quick Demo Scenario** (e.g., "Mining VP" for a high-fit lead)
3. Click **Run Pipeline**
4. Watch the 7 agents execute in real-time with live streaming logs
5. Explore results across tabs: Qualification Breakdown, Research Profile, Emails, AE Handoff

## Project Structure

```
flytbase-bdr-agent/
├── api.py                        # FastAPI server (SSE streaming)
├── frontend/                     # Next.js 16 + TailwindCSS v4
│   └── src/app/
│       ├── page.tsx              # Landing page
│       ├── about/page.tsx        # Architecture & how-to-use
│       └── dashboard/page.tsx    # Main BDR console
├── agents/                       # 7 specialized agents
│   ├── intake.py                 # Lead parsing & normalization
│   ├── research.py               # Account research (Tavily web search)
│   ├── contact.py                # Contact intelligence & buying role
│   ├── qualification.py          # Lead qualification (calls scoring engine)
│   ├── case_study.py             # Case study matching (ChromaDB RAG)
│   ├── email_generator.py        # GTM routing + 3-email sequence
│   └── handoff.py                # AE handoff briefing
├── graph/
│   ├── state.py                  # Shared pipeline state schema
│   └── workflow.py               # LangGraph DAG orchestration
├── knowledge/
│   ├── case_studies.json         # 10 FlytBase case studies
│   ├── product_knowledge.json    # Product features & pricing
│   └── partners.json             # Partner directory
├── models/
│   └── schemas.py                # All Pydantic data contracts
├── scoring/
│   └── engine.py                 # Deterministic lead scoring (no LLM)
└── utils/
    └── llm.py                    # Gemini client wrapper with fallback
```

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | Next.js 16 + TailwindCSS v4 |
| Backend API | FastAPI + Uvicorn (SSE) |
| Agent Orchestration | LangGraph |
| LLM | Google Gemini (Free tier) |
| Embeddings | Gemini Embedding |
| Vector DB | ChromaDB (in-memory) |
| Web Search | Tavily |
| Lead Scoring | Pure Python (deterministic) |

## Cost

Free! Uses Gemini free tier (15 req/min, 1500 req/day) and Tavily free tier (1000 searches/month).
