"""לשונית הסבר AI: הסבר קצר שנוצר על סמך תוצאות ש-Python כבר חישב."""
from __future__ import annotations

import html
import json
import os

import streamlit as st

from ai.fallback import FALLBACK_LABEL, rule_based_explanation
from ai.llm_client import LLMUnavailable, explain


def _api_key() -> str | None:
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY")  # מ-.streamlit/secrets.toml
    except Exception:
        key = None
    return key or os.environ.get("ANTHROPIC_API_KEY")


def _box(text: str, ai: bool) -> None:
    tag = "✨ הסבר שנוצר על ידי AI" if ai else f"⚙ {FALLBACK_LABEL}"
    cls = "sb-ai" if ai else "sb-ai nonai"
    st.markdown(f'<div class="{cls}"><span class="tag">{tag}</span>{html.escape(text)}</div>',
                unsafe_allow_html=True)


def render() -> None:
    st.header("הסבר AI")
    payload = st.session_state.get("scenario_payload")
    if not payload:
        st.info("כדי לקבל הסבר, צריך קודם סל תקין. בנו סל בלשונית \"בניית סל\".")
        return

    st.write("ההסבר מבוסס רק על המספרים שכבר חושבו בלשונית התוצאות. המודל לא מחשב מחדש ולא מוסיף נתונים.")
    with st.expander("מה נשלח לשירות ה-AI?"):
        st.caption("רק ערכים מחושבים ורשימת נתונים מסומנים כהערכה או הדגמה. אין פרטי לקוחות או פרטים אישיים.")
        st.code(json.dumps(payload, ensure_ascii=False, indent=2), language="json")

    key = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    if st.button("הסבר את התוצאה", type="primary"):
        with st.spinner("מכין הסבר..."):
            try:
                st.session_state["ai_result"] = {"key": key, "text": explain(payload, _api_key()), "ai": True}
            except LLMUnavailable as e:
                st.session_state["ai_result"] = {"key": key, "error": str(e),
                                                 "text": rule_based_explanation(payload), "ai": False}

    res = st.session_state.get("ai_result")
    if res and res["key"] != key:
        st.info("התוצאות השתנו מאז ההסבר האחרון. לחצו שוב על \"הסבר את התוצאה\".")
    elif res:
        if not res["ai"]:
            st.warning(f"אין כרגע הסבר של מודל AI: {res['error']} "
                       "מוצג במקומו הסבר מבוסס כללים, שמסומן כ\"לא AI\".")
        _box(res["text"], res["ai"])

    st.caption("זהו אומדן בלבד. ההסבר אינו הבטחת רווח ואינו מתחשב בשינויי ביקוש.")
