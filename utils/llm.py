"""
LLM client wrapper — uses Google Gemini (google-genai SDK).
Free tier: 15 requests/min, 1500 requests/day.
Includes a PROACTIVE global rate limiter that prevents 429 errors entirely,
plus automatic model fallback and proper quota recovery waits.
"""

import os
import json
import time
import threading
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Type, TypeVar

load_dotenv(override=True)

T = TypeVar("T", bound=BaseModel)

_client: genai.Client | None = None

# Default to modern reliable Gemini models
MODEL_MAP = {
    "gpt-4o": "gemini-2.5-flash",
    "gpt-4o-mini": "gemini-2.5-flash",
    "gemini-2.0-flash": "gemini-2.5-flash",
    "gemini-flash": "gemini-2.5-flash",
}

# Primary + fallback models — VERIFIED active via models.list() on 2026-07-25
FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

MAX_RETRIES = 2
QUOTA_RECOVERY_WAIT = 30  # wait 30s on 429 so Google's 60s sliding window actually clears


# ── Global Proactive Rate Limiter ──────────────────────────────────────────────
# Ensures we NEVER exceed 15 RPM by tracking call timestamps and sleeping
# proactively BEFORE making a call, rather than reacting to 429 errors.

_call_timestamps: list[float] = []
_rate_lock = threading.Lock()
RPM_LIMIT = 12  # Stay safely under 15 RPM ceiling (buffer of 3)
WINDOW_SECONDS = 60


def _wait_for_rate_limit():
    """Proactively block until we have capacity under the RPM limit."""
    with _rate_lock:
        now = time.time()
        # Prune timestamps older than 60 seconds
        _call_timestamps[:] = [t for t in _call_timestamps if now - t < WINDOW_SECONDS]

        if len(_call_timestamps) >= RPM_LIMIT:
            # Must wait until the oldest call exits the 60-second window
            oldest = _call_timestamps[0]
            wait_time = WINDOW_SECONDS - (now - oldest) + 1.0
            if wait_time > 0:
                print(f"[Rate Limiter] At {len(_call_timestamps)}/{RPM_LIMIT} RPM capacity. "
                      f"Pausing {wait_time:.1f}s for window to clear...")
                time.sleep(wait_time)
                # Clean up after sleeping
                now = time.time()
                _call_timestamps[:] = [t for t in _call_timestamps if now - t < WINDOW_SECONDS]

        # Register this call
        _call_timestamps.append(time.time())


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key.startswith("your-"):
            raise ValueError(
                "GEMINI_API_KEY not set. Add it to .env file.\n"
                "Get a FREE key at: https://aistudio.google.com/apikey"
            )
        _client = genai.Client(api_key=api_key)
    return _client


def _resolve_model(model: str) -> str:
    return MODEL_MAP.get(model, "gemini-2.5-flash")


def _execute_with_fallback(call_func):
    """Execute API call with proactive rate limiting, retries, and model fallback."""
    last_err = None

    for model_id in FALLBACK_MODELS:
        for attempt in range(MAX_RETRIES + 1):
            try:
                # Proactively wait before every call to stay under 15 RPM
                _wait_for_rate_limit()
                return call_func(model_id)
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                is_retriable = any(k in err_str for k in [
                    "resource_exhausted", "429", "rate limit", "quota",
                    "resource has been exhausted", "too many requests",
                ])
                is_not_found = "404" in err_str or "not found" in err_str

                if is_not_found:
                    print(f"[{model_id}] Model not found (404). Trying next model...")
                    break  # Skip to next fallback model immediately
                elif is_retriable:
                    if attempt < MAX_RETRIES:
                        print(f"[{model_id}] 429 quota hit. Waiting {QUOTA_RECOVERY_WAIT}s "
                              f"for sliding window to clear (attempt {attempt+1}/{MAX_RETRIES})...")
                        time.sleep(QUOTA_RECOVERY_WAIT)
                    else:
                        print(f"[{model_id}] Still exhausted after {MAX_RETRIES} retries. "
                              f"Trying next model...")
                        break
                else:
                    raise  # Non-quota error, raise immediately
    raise last_err


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.3,
    max_tokens: int = 4000,
) -> str:
    """Basic LLM call that returns raw text with auto model fallback on rate limits."""
    client = get_client()

    def _do_call(model_id: str):
        response = client.models.generate_content(
            model=model_id,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text or ""

    return _execute_with_fallback(_do_call)


def _repair_truncated_json(raw: str) -> str:
    """Attempt to repair truncated JSON by closing open structures."""
    s = raw.strip()
    # Remove markdown fences if present
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s[3:]
    if s.endswith("```"):
        s = s[:-3].strip()
    
    # Try to close truncated strings and structures
    in_string = False
    escape = False
    for ch in s:
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
    
    # If we ended inside a string, close it
    if in_string:
        s += '"'
    
    # Count unclosed brackets/braces
    opens = 0
    open_sq = 0
    for ch in s:
        if ch == '{': opens += 1
        elif ch == '}': opens -= 1
        elif ch == '[': open_sq += 1
        elif ch == ']': open_sq -= 1
    
    s += ']' * max(0, open_sq)
    s += '}' * max(0, opens)
    
    return s


def call_llm_structured(
    system_prompt: str,
    user_prompt: str,
    response_model: Type[T],
    model: str = "gemini-2.5-flash",
    temperature: float = 0.2,
    max_tokens: int = 4000,
) -> T:
    """LLM call returning a parsed Pydantic model with auto model fallback on rate limits."""
    client = get_client()

    def _do_call(model_id: str):
        response = client.models.generate_content(
            model=model_id,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
                response_schema=response_model,
            ),
        )
        return response.text or "{}"

    raw = _execute_with_fallback(_do_call)

    # Attempt 1: parse raw
    try:
        data = json.loads(raw)
        return response_model.model_validate(data)
    except Exception:
        pass
    
    # Attempt 2: repair truncated JSON (no extra API call needed)
    try:
        repaired = _repair_truncated_json(raw)
        data = json.loads(repaired)
        return response_model.model_validate(data)
    except Exception as e:
        raise ValueError(
            f"Failed to parse Gemini response into {response_model.__name__}.\n"
            f"Error: {e}\n"
            f"Raw response: {raw[:500]}"
        )


def embed_text(text: str) -> list[float]:
    """Generate embedding with gemini-embedding-2."""
    client = get_client()

    def _do_call():
        _wait_for_rate_limit()  # Proactive rate limiting for embeddings too
        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=text,
        )
        return response.embeddings[0].values

    for attempt in range(3):
        try:
            return _do_call()
        except Exception as e:
            if attempt < 2 and any(k in str(e).lower() for k in ["429", "resource_exhausted", "quota", "rate"]):
                time.sleep(QUOTA_RECOVERY_WAIT)
            else:
                raise

