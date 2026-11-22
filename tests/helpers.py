from decimal import Decimal as Dec

from core.models import CASH, CREDIT, Basket, BasketItem, PaymentTerms

CREDIT_TERMS = PaymentTerms(CREDIT, Dec("0.015"), Dec("0.50"))


def item(buy, sell, qty=1, d="0", name="מוצר"):
    f = lambda v: None if v is None else Dec(str(v))
    return BasketItem(name, f(buy), f(sell), f(qty), f(d))


def stitch_basket(tomato_spoilage="0.20", terms=CREDIT_TERMS):
    return Basket(
        [
            item("4.20", "6.00", 1, "0.05", "לחם"),
            item("5.10", "6.50", 2, "0", "חלב"),
            item("6.00", "9.00", 2, tomato_spoilage, "עגבניות"),
        ],
        terms,
    )
