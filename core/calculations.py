"""חישובי רווחיות לסל אחד (עסקה אחת). הנוסחאות לפי אפיון v2.0, ללא שינוי.

כל החישוב ב-Decimal בדיוק מלא; עיגול לשתי ספרות נעשה רק בתצוגה (round2).
הפחת נכנס רק דרך העלות האפקטיבית C/(1-d) - אין שורת פחת נפרדת.
העמלה הקבועה F נגבית פעם אחת לסל.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from .models import CREDIT, Basket, BasketItem, PaymentTerms
from .validation import validate_basket

ZERO = Decimal("0")
ONE = Decimal("1")
CENT = Decimal("0.01")

STATUS_LOSS = "הפסד"
STATUS_BREAK_EVEN = "איזון"
STATUS_PROFIT = "רווח"


def D(x) -> Decimal:
    """המרה בטוחה ל-Decimal (דרך מחרוזת, כדי לא לגרור שגיאות float)."""
    return x if isinstance(x, Decimal) else Decimal(str(x))


def round2(x: Decimal) -> Decimal:
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def effective_unit_cost(buy_price: Decimal, spoilage: Decimal) -> Decimal:
    if not (ZERO <= spoilage < ONE):
        raise ValueError("פחת חייב להיות בטווח 0 עד פחות מ-100%")
    return buy_price / (ONE - spoilage)


def revenue(items: list[BasketItem]) -> Decimal:
    return sum((i.sell_price * i.qty for i in items), ZERO)


def basket_cost(items: list[BasketItem]) -> Decimal:
    return sum((effective_unit_cost(i.buy_price, i.spoilage) * i.qty for i in items), ZERO)


def fee(rev: Decimal, terms: PaymentTerms) -> Decimal:
    if terms.method == CREDIT:
        return rev * terms.rate + terms.fixed
    return ZERO


def contribution(rev: Decimal, cost: Decimal, fee_amount: Decimal) -> Decimal:
    return rev - cost - fee_amount


def break_even(cost: Decimal, terms: PaymentTerms) -> Decimal:
    if terms.method == CREDIT:
        if terms.rate >= ONE:
            raise ValueError("עמלה יחסית חייבת להיות קטנה מ-100%")
        return (cost + terms.fixed) / (ONE - terms.rate)
    return cost


def margin_pct(profit: Decimal, rev: Decimal) -> Optional[Decimal]:
    """שיעור רווחיות = P / R (שבר). None אם אין הכנסות."""
    return profit / rev if rev > ZERO else None


def status(profit: Decimal) -> str:
    p = round2(profit)
    if p < ZERO:
        return STATUS_LOSS
    if p == ZERO:
        return STATUS_BREAK_EVEN
    return STATUS_PROFIT


@dataclass
class BasketResult:
    revenue: Decimal
    cost: Decimal
    fee: Decimal
    profit: Decimal
    break_even: Decimal
    margin: Optional[Decimal]
    status: str


def compute(basket: Basket) -> BasketResult:
    """מחשב סל. קלט לא תקין לעולם לא עובר בשקט: נזרקת ValueError עם ההודעות."""
    errors = validate_basket(basket)
    if errors:
        raise ValueError("\n".join(errors))
    r = revenue(basket.items)
    k = basket_cost(basket.items)
    f = fee(r, basket.terms)
    p = contribution(r, k, f)
    return BasketResult(r, k, f, p, break_even(k, basket.terms), margin_pct(p, r), status(p))
