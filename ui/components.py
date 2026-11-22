"""רכיבי תצוגה משותפים: עיצוב RTL, תגי ודאות, חיווי הפסד/איזון/רווח וכרטיסי מדדים.
הצבעים לפי מערכת העיצוב ב-Stitch (SmartBasket AI)."""
from __future__ import annotations

import html
from decimal import Decimal
from typing import Optional

import streamlit as st

from core.calculations import STATUS_BREAK_EVEN, STATUS_LOSS, STATUS_PROFIT, round2
from core.models import TAG_DEMO, TAG_ENTERED, TAG_ESTIMATE

PRIMARY = "#2c6a53"
LOSS = "#a83836"
AMBER = "#b26a00"
OUTLINE = "#737d77"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;700&display=swap');
html, body, .stApp, [class*="css"] { font-family: 'Rubik', sans-serif; }
.stApp { direction: rtl; background: #f6faf6; color: #2b3530; }
.stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label, .stApp li { text-align: right; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { font-size: 1.05rem; padding: 10px 18px; }
.sb-card { background:#fff; border:1px solid #dbe5de; border-radius:8px; padding:14px 16px; text-align:right; }
.sb-card .lbl { color:#57615c; font-size:0.9rem; }
.sb-card .val { font-size:1.7rem; font-weight:700; margin-top:2px; }
.sb-card .sub { color:#57615c; font-size:0.8rem; }
.sb-status { border-radius:8px; padding:14px 16px; font-size:1.2rem; font-weight:700; text-align:right; }
.sb-chip { display:inline-block; font-size:0.75rem; padding:1px 8px; border-radius:10px; margin-inline-start:6px; }
.chip-entered { background:#57615c; color:#fff; border:1px solid #57615c; }
.chip-estimate { color:#b26a00; border:1px solid #b26a00; background:#fff; }
.chip-demo { color:#737d77; border:1px dashed #737d77; background:#fff; }
.sb-ai { background:#e5f4ec; border:1px solid #b0f0d2; border-radius:8px; padding:16px; text-align:right; font-size:1.1rem; line-height:1.7; }
.sb-ai.nonai { background:#fff8e6; border-color:#e6c36a; }
.sb-ai .tag { font-size:0.8rem; font-weight:700; color:#1c5c46; display:block; margin-bottom:6px; }
.sb-ai.nonai .tag { color:#8a5a00; }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def money(x: Decimal) -> str:
    return f"{round2(x):,.2f} ₪"


def signed_money(x: Decimal) -> str:
    v = round2(x)
    return f"{'+' if v > 0 else ''}{v:,.2f} ₪"


def tag_chip(tag: str) -> str:
    cls = {TAG_ENTERED: "chip-entered", TAG_ESTIMATE: "chip-estimate", TAG_DEMO: "chip-demo"}.get(tag, "chip-demo")
    return f'<span class="sb-chip {cls}">{html.escape(tag)}</span>'


def card(label: str, value: str, sub: str = "", color: Optional[str] = None) -> str:
    style = f' style="color:{color}"' if color else ""
    sub_html = f'<div class="sub">{html.escape(sub)}</div>' if sub else ""
    return (f'<div class="sb-card"><div class="lbl">{html.escape(label)}</div>'
            f'<div class="val"{style}>{html.escape(value)}</div>{sub_html}</div>')


def status_box(status: str) -> str:
    """חיווי עם אייקון וטקסט (לא רק צבע)."""
    icon, color, bg = {
        STATUS_PROFIT: ("✔", PRIMARY, "#e5f4ec"),
        STATUS_BREAK_EVEN: ("●", AMBER, "#fff3d6"),
        STATUS_LOSS: ("▲", LOSS, "#fde8e7"),
    }[status]
    return (f'<div class="sb-status" style="color:{color};background:{bg};border:1px solid {color}">'
            f'{icon} מצב הסל: {status}</div>')
