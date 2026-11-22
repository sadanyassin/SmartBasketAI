"""לשונית תוצאות וסימולציה: מדדים, תרחיש חלופי, טבלת השוואה וגרף לפני/אחרי."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ai.payload import build_payload
from core.calculations import D, compute, round2
from core.models import CASH, CREDIT, Basket
from core.scenarios import compare, make_alternative
from ui import components as ui


def _pct(x: Optional[Decimal]) -> str:
    return "אין הכנסות" if x is None else f"{round2(x * 100):.2f}%"


def render(basket: Basket, errors: list[str]) -> None:
    st.header("תוצאות וסימולציה")
    if errors:
        st.warning("אי אפשר להציג תוצאות עד שהסל תקין. הפרטים בלשונית \"בניית סל\":")
        for e in errors:
            st.markdown(f"- {e}")
        st.session_state.pop("scenario_payload", None)
        return

    base = compute(basket)

    st.subheader("תרחיש בסיס")
    st.markdown(ui.status_box(base.status), unsafe_allow_html=True)
    st.write("")
    c = st.columns(3)
    c[0].markdown(ui.card("רווח תרומתי משוער", ui.money(base.profit), "אינו רווח נקי"), unsafe_allow_html=True)
    c[1].markdown(ui.card("שיעור רווחיות", _pct(base.margin), "רווח תרומתי חלקי הכנסות"), unsafe_allow_html=True)
    c[2].markdown(ui.card("נקודת איזון להכנסות הסל", ui.money(base.break_even), "באותו הרכב וכמויות"),
                  unsafe_allow_html=True)
    c = st.columns(3)
    c[0].markdown(ui.card("הכנסות הסל", ui.money(base.revenue)), unsafe_allow_html=True)
    c[1].markdown(ui.card("עלות מתואמת לפחת", ui.money(base.cost), "הפחת כלול בעלות, לא נספר פעמיים"),
                  unsafe_allow_html=True)
    fee_sub = "אשראי: אחוז מההכנסות + עמלה קבועה פעם אחת" if basket.terms.method == CREDIT else "מזומן: אין עמלה"
    c[2].markdown(ui.card("עמלת אשראי", ui.money(base.fee), fee_sub), unsafe_allow_html=True)

    with st.expander("פירוט המוצרים ורמת הוודאות של כל נתון"):
        rows = []
        for it in basket.items:
            rows.append({
                "מוצר": it.name,
                "מחיר קנייה": f"{round2(it.buy_price)} ({it.buy_tag})",
                "מחיר מכירה": f"{round2(it.sell_price)} ({it.sell_tag})",
                "כמות": int(it.qty),
                "פחת": f"{round2(it.spoilage * 100)}% ({it.spoilage_tag})",
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    st.subheader("סימולציה: תרחיש חלופי")
    st.caption("שנו מחיר, פחת או אמצעי תשלום וראו מה קורה. זו השוואה סטטית: לא נבדקת השפעה על הביקוש.")
    s1, s2 = st.columns(2)
    price_change = s1.slider("שינוי במחירי המכירה (%)", -30, 30, 0, 1, key="sim_price")
    names = [f"{i + 1}. {it.name}" for i, it in enumerate(basket.items)]
    idx = s2.selectbox("מוצר לשינוי פחת", range(len(names)), format_func=lambda i: names[i], key="sim_item")
    item = basket.items[idx]
    cur_pct = float(round2(item.spoilage * 100))
    new_pct = s2.slider(f"פחת חלופי ל{item.name} (%)", 0.0, 95.0, cur_pct, 1.0,
                        key=f"sim_sp_{idx}_{item.name}_{cur_pct}")
    method_default = 1 if basket.terms.method == CREDIT else 0
    alt_label = st.radio("אמצעי תשלום בתרחיש החלופי", ["מזומן", "אשראי"], index=method_default,
                         horizontal=True, key=f"sim_method_{basket.terms.method}")
    alt_method = CREDIT if alt_label == "אשראי" else CASH

    overrides = {idx: D(new_pct) / Decimal(100)} if abs(new_pct - cur_pct) > 1e-9 else None
    alt_basket = make_alternative(basket, D(price_change), overrides, alt_method)
    alt = compute(alt_basket)

    changes = []
    if price_change:
        changes.append(f"שינוי מחירי מכירה ב-{price_change:+d}%")
    if overrides:
        changes.append(f"פחת {item.name} מ-{cur_pct:g}% ל-{new_pct:g}% (הנחת סימולציה)")
    if alt_method != basket.terms.method:
        changes.append(f"אמצעי תשלום: {'אשראי' if alt_method == CREDIT else 'מזומן'} במקום "
                       f"{'אשראי' if basket.terms.method == CREDIT else 'מזומן'}")
    change_text = "; ".join(changes) if changes else "לא נבדק שינוי (התרחיש החלופי זהה לבסיס)"
    st.write(f"**מה נבדק:** {change_text}")
    st.markdown(ui.status_box(alt.status), unsafe_allow_html=True)

    d = compare(base, alt)
    table = pd.DataFrame({
        "מדד": ["הכנסות", "עלות מתואמת לפחת", "עמלה", "רווח תרומתי משוער", "נקודת איזון להכנסות"],
        "בסיס": [ui.money(x) for x in (base.revenue, base.cost, base.fee, base.profit, base.break_even)],
        "חלופה": [ui.money(x) for x in (alt.revenue, alt.cost, alt.fee, alt.profit, alt.break_even)],
        "הפרש": [ui.signed_money(d[k]) for k in ("revenue", "cost", "fee", "profit", "break_even")],
    })
    st.dataframe(table, hide_index=True, width="stretch")

    labels = ["הכנסות", "עלות מתואמת לפחת", "עמלה", "רווח תרומתי משוער"]
    fig = go.Figure()
    for name, res, color in (("בסיס", base, ui.OUTLINE), ("חלופה", alt, ui.PRIMARY)):
        vals = [float(round2(v)) for v in (res.revenue, res.cost, res.fee, res.profit)]
        fig.add_bar(name=name, x=labels, y=vals, marker_color=color, text=[f"{v:.2f}" for v in vals],
                    textposition="outside")
    fig.update_layout(barmode="group", title="לפני ואחרי (₪)", font=dict(family="Rubik, sans-serif", size=14),
                      plot_bgcolor="#ffffff", paper_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h"),
                      margin=dict(t=60, b=20))
    st.plotly_chart(fig, width="stretch")

    st.session_state["scenario_payload"] = build_payload(basket, alt_basket, base, alt, change_text)
