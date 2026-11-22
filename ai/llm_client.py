"""חיבור לשירות ה-AI. הספק עדיין לא סוכם עם המרצה - כרגע מימוש זמני עם Anthropic SDK.
כדי להחליף ספק מחליפים רק את הפונקציה explain() בקובץ הזה.

מפתח ה-API נקרא ממשתנה סביבה ANTHROPIC_API_KEY או מ-.streamlit/secrets.toml. לא נכתב בקוד.
"""
from __future__ import annotations

import os

from .prompt import SYSTEM_PROMPT, build_user_message

DEFAULT_MODEL = "claude-opus-5-5"


class LLMUnavailable(Exception):
    """שירות ה-AI לא זמין (אין מפתח, אין רשת, שגיאת שירות או סירוב)."""


def explain(payload: dict, api_key: str | None = None) -> str:
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMUnavailable("לא הוגדר מפתח API לשירות ה-AI.")
    try:
        import anthropic
    except ImportError as e:
        raise LLMUnavailable("חבילת anthropic אינה מותקנת.") from e

    model = os.environ.get("SMARTBASKET_LLM_MODEL", DEFAULT_MODEL)
    client = anthropic.Anthropic(api_key=api_key, timeout=60.0)
    try:
        response = client.beta.messages.create(
            model=model,
            max_tokens=8000,
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_message(payload)}],
        )
    except anthropic.AuthenticationError as e:
        raise LLMUnavailable("מפתח ה-API אינו תקין.") from e
    except anthropic.RateLimitError as e:
        raise LLMUnavailable("חריגה ממגבלת הבקשות של השירות. נסו שוב בעוד רגע.") from e
    except anthropic.APIConnectionError as e:
        raise LLMUnavailable("אין חיבור לשירות ה-AI (בדקו חיבור לאינטרנט).") from e
    except anthropic.APIStatusError as e:
        raise LLMUnavailable(f"שירות ה-AI החזיר שגיאה ({e.status_code}).") from e

    if response.stop_reason == "refusal":
        raise LLMUnavailable("המודל סירב להשיב על הבקשה.")
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    if not text:
        raise LLMUnavailable("המודל לא החזיר טקסט.")
    return text
