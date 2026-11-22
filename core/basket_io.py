"""המרה בין טבלת העריכה (DataFrame, פחת באחוזים) לבין אובייקט Basket (פחת כשבר)."""
from __future__ import annotations

import math
from decimal import Decimal
from typing import Optional

import pandas as pd

from .calculations import D
from .models import ALL_TAGS, TAG_DEMO, TAG_ENTERED, Basket, BasketItem

COL_NAME = "מוצר"
COL_CAT = "קטגוריה"
COL_BUY = "מחיר קנייה (₪)"
COL_SELL = "מחיר מכירה (₪)"
COL_QTY = "כמות"
COL_SPOIL = "פחת (%)"
COL_BUY_TAG = "ודאות מחיר קנייה"
COL_SELL_TAG = "ודאות מחיר מכירה"
COL_SPOIL_TAG = "ודאות פחת"

COLUMNS = [COL_NAME, COL_CAT, COL_BUY, COL_SELL, COL_QTY, COL_SPOIL,
           COL_BUY_TAG, COL_SELL_TAG, COL_SPOIL_TAG]


def empty_basket_df() -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series(dtype="object") for c in COLUMNS})


def catalog_rows_to_df(catalog: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    """שורות קטלוג -> טבלת סל. כל הערכים מסומנים 'הדגמה'."""
    rows = []
    for name in names:
        r = catalog[catalog["name"] == name].iloc[0]
        rows.append({
            COL_NAME: r["name"], COL_CAT: r["category"],
            COL_BUY: float(r["buy_price"]), COL_SELL: float(r["sell_price"]),
            COL_QTY: 1, COL_SPOIL: float(r["default_spoilage"]) * 100,
            COL_BUY_TAG: TAG_DEMO, COL_SELL_TAG: TAG_DEMO, COL_SPOIL_TAG: TAG_DEMO,
        })
    return pd.DataFrame(rows, columns=COLUMNS)


def _num(v) -> Optional[Decimal]:
    if v is None:
        return None
    try:
        if isinstance(v, float) and math.isnan(v):
            return None
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    try:
        return D(v)
    except Exception:
        return None


def _tag(v, default: str = TAG_ENTERED) -> str:
    return v if v in ALL_TAGS else default


def effective_tag(tag: str, value, catalog_value) -> str:
    """ערך הדגמה שהמשתמש שינה כבר אינו 'הדגמה' - הופך ל'הוזן'."""
    if tag == TAG_DEMO and catalog_value is not None and value is not None:
        if abs(D(value) - D(catalog_value)) > Decimal("0.000001"):
            return TAG_ENTERED
    return tag


def df_to_items(df: pd.DataFrame, catalog: Optional[pd.DataFrame] = None) -> list[BasketItem]:
    items: list[BasketItem] = []
    cat = catalog.set_index("name") if catalog is not None else None
    for _, row in df.iterrows():
        name = row.get(COL_NAME)
        values = [row.get(c) for c in (COL_BUY, COL_SELL, COL_QTY, COL_SPOIL)]
        if (name is None or pd.isna(name) or str(name).strip() == "") and all(_num(v) is None for v in values):
            continue  # שורה ריקה לגמרי
        buy, sell, qty, sp = (_num(v) for v in values)
        spoilage = sp / Decimal(100) if sp is not None else None
        buy_t = _tag(row.get(COL_BUY_TAG))
        sell_t = _tag(row.get(COL_SELL_TAG))
        sp_t = _tag(row.get(COL_SPOIL_TAG))
        if cat is not None and name in cat.index:
            c = cat.loc[name]
            buy_t = effective_tag(buy_t, buy, c["buy_price"])
            sell_t = effective_tag(sell_t, sell, c["sell_price"])
            sp_t = effective_tag(sp_t, spoilage, c["default_spoilage"])
        items.append(BasketItem("" if name is None or pd.isna(name) else str(name).strip(),
                                buy, sell, qty, spoilage, buy_t, sell_t, sp_t))
    return items
