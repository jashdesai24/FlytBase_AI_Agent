"""
LLM client wrapper — uses Google Gemini (google-genai SDK).
Free tier: 15 requests/min, 1500 requests/day.
Includes automatic model fallback across 2026 models and exponential backoff for rate limits.
"""

import os
import json
import time
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

# Fallback sequence using distinct active quota tiers (Flash, Flash-Lite, Pro)
FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite-001",  # distinct high-concurrency token pool
    "gemini-2.5-pro",             # distinct Pro tier token pool
]

MAX_RETRIES = 1
INITIAL_BACKOFF = 2  # short 2-second pause before instantly trying next quota tier


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
    """Execute API call with model fallback if quota is exhausted or rate limited."""
    last_err = None
    
    # First try the requested call, then try fallback models
    models_to_try = FALLBACK_MODELS
    
    for model_id in models_to_try:
        for attempt in range(MAX_RETRIES + 1):
            try:
                return call_func(model_id)
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                is_quota_exhausted = any(k in err_str for k in [
                    "resource_exhausted", "429", "rate limit", "quota",
                    "resource has been exhausted", "too many requests", "404", "not found"
                ])
                if is_quota_exhausted:
                    if "404" in err_str or "not found" in err_str:
                        print(f"[{model_id}] Model not found (404). Switching immediately to fallback model...")
                        break
                    if attempt < MAX_RETRIES:
                        wait = min(15, INITIAL_BACKOFF * (2 ** attempt))
                        print(f"[{model_id} rate limit/quota] Waiting {wait}s before retry ({attempt+1}/{MAX_RETRIES})...")
                        time.sleep(wait)
                    else:
                        print(f"[{model_id}] Quota exhausted after retries. Switching to next fallback model...")
                        break  # Break out of attempts loop to switch to next fallback model
                else:
                    raise
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
    
    # Attempt 2: repair truncated JSON
    try:
        repaired = _repair_truncated_json(raw)
        data = json.loads(repaired)
        return response_model.model_validate(data)
    except Exception:
        pass
    
    # Attempt 3: retry the LLM call with higher token limit
    try:
        def _retry_call(model_id: str):
            response = client.models.generate_content(
                model=model_id,
                contents=user_prompt + "\n\nIMPORTANT: Keep your response concise. Use short strings. Do not write long paragraphs.",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    max_output_tokens=min(max_tokens * 2, 16000),
                    response_mime_type="application/json",
                    response_schema=response_model,
                ),
            )
            return response.text or "{}"
        
        raw2 = _execute_with_fallback(_retry_call)
        data = json.loads(raw2)
        return response_model.model_validate(data)
    except Exception as e:
        # Try repairing the retry response too
        try:
            repaired2 = _repair_truncated_json(raw2)
            data = json.loads(repaired2)
            return response_model.model_validate(data)
        except Exception:
            raise ValueError(
                f"Failed to parse Gemini response into {response_model.__name__}.\n"
                f"Error: {e}\n"
                f"Raw response: {raw[:500]}"
            )


def embed_text(text: str) -> list[float]:
    """Generate embedding with gemini-embedding-2."""
    client = get_client()

    def _do_call():
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
                time.sleep(3)
            else:
                raise
