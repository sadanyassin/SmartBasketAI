"""לשונית בניית סל: בחירת מוצרים מהקטלוג, עריכת מחירים/כמויות/פחת ותנאי תשלום."""
from __future__ import annotations

from decimal import Decimal

import pandas as pd
import streamlit as st

from core.basket_io import (COL_BUY, COL_BUY_TAG, COL_CAT, COL_NAME, COL_QTY, COL_SELL,
                            COL_SELL_TAG, COL_SPOIL, COL_SPOIL_TAG, COLUMNS, catalog_rows_to_df,
                            df_to_items, empty_basket_df)
from core.calculations import D
from core.catalog import load_catalog
from core.models import ALL_TAGS, CASH, CREDIT, TAG_DEMO, Basket, PaymentTerms
from core.validation import validate_basket

DEMO_BASKET_NAMES = ["לחם", "חלב", "עגבניות"]
DEMO_QTY = {"לחם": 1, "חלב": 2, "עגבניות": 2}


def _ver() -> int:
    return st.session_state.setdefault("editor_ver", 0)


def _add_rows(new_df: pd.DataFrame) -> None:
    current = st.session_state.get("last_edited_df", st.session_state["basket_df"])
    st.session_state["basket_df"] = pd.concat([current, new_df], ignore_index=True)[COLUMNS]
    st.session_state["editor_ver"] = _ver() + 1  # מאפס את מצב העורך עם הנתונים החדשים


def render() -> tuple[Basket, list[str]]:
    catalog = load_catalog()
    st.session_state.setdefault("basket_df", empty_basket_df())

    st.header("בניית סל")
    st.caption("סל = קנייה אחת של לקוח בקופה, עם אמצעי תשלום אחד. כל המחירים ללא מע\"מ.")

    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        picked = st.multiselect("הוספת מוצרים מקטלוג ההדגמה (12 מוצרים מדומים)", list(catalog["name"]),
                                key=f"pick_{_ver()}")
    with c2:
        st.write("")
        if st.button("הוספה לסל", disabled=not picked):
            _add_rows(catalog_rows_to_df(catalog, picked))
            st.rerun()
    with c3:
        st.write("")
        if st.button("טעינת סל הדגמה"):
            demo = catalog_rows_to_df(catalog, DEMO_BASKET_NAMES)
            demo[COL_QTY] = [DEMO_QTY[n] for n in DEMO_BASKET_NAMES]
            st.session_state["basket_df"] = demo
            st.session_state["editor_ver"] = _ver() + 1
            st.rerun()

    st.markdown("**טבלת הסל** - אפשר לערוך ערכים, להוסיף שורה חדשה בתחתית הטבלה, ולמחוק שורה.")
    edited = st.data_editor(
        st.session_state["basket_df"],
        key=f"editor_{_ver()}",
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        column_config={
            COL_NAME: st.column_config.TextColumn(COL_NAME),
            COL_CAT: st.column_config.TextColumn(COL_CAT),
            COL_BUY: st.column_config.NumberColumn(COL_BUY, format="%.2f", help="חסר מחיר קנייה = לא מחושב רווח"),
            COL_SELL: st.column_config.NumberColumn(COL_SELL, format="%.2f"),
            COL_QTY: st.column_config.NumberColumn(COL_QTY, step=1, format="%d"),
            COL_SPOIL: st.column_config.NumberColumn(COL_SPOIL, format="%.1f",
                                                     help="אומדן תקופתי. ערכי ההדגמה להמחשה בלבד, לא נתוני ענף מאומתים"),
            COL_BUY_TAG: st.column_config.SelectboxColumn(COL_BUY_TAG, options=list(ALL_TAGS)),
            COL_SELL_TAG: st.column_config.SelectboxColumn(COL_SELL_TAG, options=list(ALL_TAGS)),
            COL_SPOIL_TAG: st.column_config.SelectboxColumn(COL_SPOIL_TAG, options=list(ALL_TAGS)),
        },
    )
    st.session_state["last_edited_df"] = edited
    st.caption("ערכי \"הדגמה\" הם נתונים מדומים ולא מחירי שוק. ערך הדגמה ששיניתם הופך אוטומטית ל\"הוזן\". "
               "פחת בקטלוג (למשל 20% לעגבניות) הוא אומדן להמחשה בלבד.")

    st.subheader("תנאי תשלום")
    method_label = st.radio("אמצעי תשלום של העסקה", ["מזומן", "אשראי"], horizontal=True, key="pay_method")
    method = CREDIT if method_label == "אשראי" else CASH
    rate_pct, fixed, terms_tag = 1.5, 0.50, TAG_DEMO
    if method == CREDIT:
        a, b, c = st.columns(3)
        rate_pct = a.number_input("עמלה יחסית (% מסכום העסקה)", min_value=0.0, value=1.5, step=0.1, key="rate_pct")
        fixed = b.number_input("עמלה קבועה לעסקה (₪)", min_value=0.0, value=0.50, step=0.05, key="fixed_fee",
                               help="נגבית פעם אחת לסל כולו, לא לכל מוצר")
        terms_tag = c.selectbox("רמת ודאות של נתוני העמלה", list(ALL_TAGS), index=2, key="terms_tag")
    terms = PaymentTerms(method, D(rate_pct) / Decimal(100), D(fixed), terms_tag)

    basket = Basket(df_to_items(edited, catalog), terms)
    errors = validate_basket(basket)
    if errors:
        st.warning("יש להשלים או לתקן לפני שאפשר לחשב:")
        for e in errors:
            st.markdown(f"- {e}")
    else:
        st.success("הסל תקין. עברו ללשונית \"תוצאות וסימולציה\".")
    return basket, errors
