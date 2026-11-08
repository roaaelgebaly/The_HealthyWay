import json
import re
from typing import Type, TypeVar

import groq
from groq import Groq
from pydantic import BaseModel, ValidationError

from src.config import LLM_MODEL, get_secret

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    """Raised for any LLM failure (missing key, rate limit, API error, invalid output)."""


def _client() -> Groq:
    key = get_secret("GROQ_API_KEY")
    if not key:
        raise LLMError("GROQ_API_KEY is not set (add it to the .env file).")
    return Groq(api_key=key, timeout=60.0, max_retries=2)


def generate_text(system: str, user: str, max_tokens: int = 1200, json_mode: bool = False) -> str:
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
    try:
        resp = _client().chat.completions.create(
            model=LLM_MODEL,
            max_tokens=max_tokens,
            temperature=0.4,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            **kwargs,
        )
    except groq.RateLimitError as e:
        raise LLMError("Groq free-tier rate limit reached. Please wait a minute and try again.") from e
    except groq.GroqError as e:
        raise LLMError(f"LLM request failed: {e}") from e
    return (resp.choices[0].message.content or "").strip()


def _extract_json(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model output.")
    return text[start : end + 1]


def generate_structured(system: str, user: str, schema: Type[T], max_tokens: int = 2500) -> T:
    """Ask for JSON matching `schema`, validate with Pydantic, retry once on failure."""
    system_full = (
        f"{system}\n\nReturn ONLY a JSON object that conforms to this JSON Schema. "
        f"No prose, no code fences.\n{json.dumps(schema.model_json_schema())}"
    )
    prompt = user
    last_error: Exception | None = None
    for _ in range(2):
        raw = generate_text(system_full, prompt, max_tokens=max_tokens, json_mode=True)
        try:
            return schema.model_validate(json.loads(_extract_json(raw)))
        except (ValueError, ValidationError) as e:
            last_error = e
            prompt = f"{user}\n\nYour previous reply was invalid ({e}). Return corrected JSON only."
    raise LLMError(f"Model returned invalid structured output: {last_error}")