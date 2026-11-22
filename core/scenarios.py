"""תרחיש חלופי והשוואה לבסיס. אין כאן נוסחאות חדשות - רק שינוי קלט וחישוב מחדש."""
from __future__ import annotations

import copy
from decimal import Decimal
from typing import Optional

from .calculations import D, BasketResult, compute
from .models import TAG_ESTIMATE, Basket


def make_alternative(
    base: Basket,
    price_change_pct: Decimal = Decimal("0"),
    spoilage_overrides: Optional[dict[int, Decimal]] = None,
    method: Optional[str] = None,
) -> Basket:
    """בונה תרחיש חלופי: שינוי באחוזים בכל מחירי המכירה, פחת חדש למוצרים נבחרים
    (לפי אינדקס בסל) ואמצעי תשלום אחר. הבסיס לא משתנה."""
    alt = copy.deepcopy(base)
    factor = Decimal("1") + D(price_change_pct) / Decimal("100")
    for i, item in enumerate(alt.items):
        if price_change_pct and item.sell_price is not None:
            item.sell_price = item.sell_price * factor
        if spoilage_overrides and i in spoilage_overrides:
            item.spoilage = D(spoilage_overrides[i])
            item.spoilage_tag = TAG_ESTIMATE  # הנחת סימולציה בלבד
    if method:
        alt.terms.method = method
    return alt


def compare(base: BasketResult, alt: BasketResult) -> dict[str, Decimal]:
    """הפרשים (חלופה פחות בסיס) לכל מדד."""
    return {
        "revenue": alt.revenue - base.revenue,
        "cost": alt.cost - base.cost,
        "fee": alt.fee - base.fee,
        "profit": alt.profit - base.profit,
        "break_even": alt.break_even - base.break_even,
    }


def compute_pair(base: Basket, alt: Basket) -> tuple[BasketResult, BasketResult]:
    return compute(base), compute(alt)
