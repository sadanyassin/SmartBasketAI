"""בניית המידע שנשלח למודל: רק ערכים ש-Python כבר חישב. בלי פרטי לקוחות או פרטים אישיים."""
from __future__ import annotations

from core.calculations import BasketResult, round2
from core.models import TAG_ENTERED, Basket

ALLOWED_KEYS = {"payment_method", "base", "alternative", "delta", "change_tested", "estimated_fields"}
RESULT_KEYS = {"revenue", "cost", "fee", "profit", "break_even", "status"}


def _res(r: BasketResult) -> dict:
    return {
        "revenue": float(round2(r.revenue)),
        "cost": float(round2(r.cost)),
        "fee": float(round2(r.fee)),
        "profit": float(round2(r.profit)),
        "break_even": float(round2(r.break_even)),
        "status": r.status,
    }


def estimated_fields(basket: Basket) -> list[str]:
    """רשימת שדות שאינם 'הוזן' (הערכה/הדגמה)."""
    out = []
    for it in basket.items:
        for label, tag in (("מחיר קנייה", it.buy_tag), ("מחיר מכירה", it.sell_tag), ("פחת", it.spoilage_tag)):
            if tag != TAG_ENTERED:
                out.append(f"{label} - {it.name} ({tag})")
    if basket.terms.method == "credit" and basket.terms.tag != TAG_ENTERED:
        out.append(f"תנאי עמלת אשראי ({basket.terms.tag})")
    return out


def build_payload(base_basket: Basket, alt_basket: Basket, base: BasketResult, alt: BasketResult,
                  change_tested: str) -> dict:
    b, a = _res(base), _res(alt)
    return {
        "payment_method": base_basket.terms.method,
        "base": b,
        "alternative": a,
        "delta": {k: round(a[k] - b[k], 2) for k in ("revenue", "cost", "fee", "profit", "break_even")},
        "change_tested": change_tested,
        "estimated_fields": sorted(set(estimated_fields(base_basket)) | set(estimated_fields(alt_basket))),
    }
