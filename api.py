"""
FastAPI server wrapping the LangGraph workflow.
Streams execution updates via Server-Sent Events (SSE).
"""

import json
import traceback
from enum import Enum
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI(title="FlytBase BDR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SafeEncoder(json.JSONEncoder):
    """Handle enums and other non-serializable types."""
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


@app.post("/api/process-lead")
async def process_lead(request: Request):
    raw_input_data = await request.json()

    initial_state = {
        "raw_input": raw_input_data,
        "lead_record": None,
        "account_research": None,
        "contact_intelligence": None,
        "qualification": None,
        "case_study_matches": None,
        "gtm_and_email": None,
        "handoff_brief": None,
        "current_agent": "",
        "agent_errors": {},
        "execution_log": [],
        "is_qualified": False,
    }

    async def event_generator():
        try:
            # IMMEDIATELY yield start packet so Render flushes stream & UI activates without delay
            yield {
                "event": "update",
                "data": json.dumps({
                    "node": "init",
                    "output": {
                        "execution_log": [
                            "⚡ Connected to FastAPI orchestration engine.",
                            "🚀 Engaging Agent 1: Lead Intake & Normalization..."
                        ]
                    }
                }, cls=SafeEncoder),
            }

            from graph.workflow import graph

            for event in graph.stream(initial_state, stream_mode="updates"):
                for node_name, node_output in event.items():
                    payload = {
                        "node": node_name,
                        "output": node_output,
                    }
                    yield {
                        "event": "update",
                        "data": json.dumps(payload, cls=SafeEncoder),
                    }

            yield {"event": "done", "data": "{}"}

        except Exception as e:
            error_msg = traceback.format_exc()
            print(f"[API ERROR] {error_msg}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e), "traceback": error_msg}),
            }

    return EventSourceResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Critical for Nginx & Render proxies
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
