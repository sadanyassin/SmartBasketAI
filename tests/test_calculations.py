from decimal import Decimal as Dec

import pytest

from core.calculations import compute, effective_unit_cost, round2
from core.models import CASH, CREDIT, Basket, PaymentTerms
from core.scenarios import compare, make_alternative

from .helpers import CREDIT_TERMS, item, stitch_basket


def r2(x):
    return round2(x)


def test_01_reference_case_from_spec():
    res = compute(Basket([item(6, 9, 2, "0.20")], CREDIT_TERMS))
    assert r2(res.revenue) == Dec("18.00")
    assert r2(res.cost) == Dec("15.00")
    assert r2(res.fee) == Dec("0.77")
    assert r2(res.profit) == Dec("2.23")
    assert r2(res.break_even) == Dec("15.74")


def test_02_stitch_demo_basket():
    res = compute(stitch_basket())
    assert r2(res.revenue) == Dec("37.00")
    assert r2(res.cost) == Dec("29.62")
    assert r2(res.fee) == Dec("1.06")
    assert r2(res.profit) == Dec("6.32")
    assert r2(res.break_even) == Dec("30.58")


def test_03_stitch_alternative_tomato_spoilage_10pct():
    base = stitch_basket()
    alt = make_alternative(base, spoilage_overrides={2: Dec("0.10")})
    res = compute(alt)
    assert r2(res.cost) == Dec("27.95")
    assert r2(res.profit) == Dec("7.99")
    assert r2(res.break_even) == Dec("28.89")
    assert base.items[2].spoilage == Dec("0.20")  # הבסיס לא השתנה
    assert r2(compare(compute(base), res)["profit"]) == Dec("1.67")


def test_04_cash_has_no_fee_and_breakeven_equals_cost():
    res = compute(Basket([item(6, 9, 2, "0.20")], PaymentTerms(CASH, Dec("0.015"), Dec("0.50"))))
    assert res.fee == 0
    assert r2(res.profit) == Dec("3.00")
    assert res.break_even == res.cost == Dec("15")


def test_05_zero_spoilage_effective_cost_equals_buy_price():
    assert effective_unit_cost(Dec("6"), Dec("0")) == Dec("6")


def test_06_fixed_fee_charged_once_per_basket():
    one = compute(Basket([item(1, 2, 1)], CREDIT_TERMS))
    three = compute(Basket([item(1, 2, 1), item(1, 2, 1), item(1, 2, 1)], CREDIT_TERMS))
    # עמלה = R*r + F; הפרש בין 3 מוצרים ל-1 הוא רק החלק היחסי
    assert three.fee - one.fee == (three.revenue - one.revenue) * Dec("0.015")
    assert three.fee == Dec("6") * Dec("0.015") + Dec("0.50")


def test_07_loss_status():
    res = compute(Basket([item(10, 8, 1)], PaymentTerms(CASH)))
    assert res.profit < 0 and res.status == "הפסד"


def test_08_break_even_status():
    res = compute(Basket([item(5, 5, 1)], PaymentTerms(CASH)))
    assert res.profit == 0 and res.status == "איזון"


def test_09_profit_status():
    assert compute(stitch_basket()).status == "רווח"


def test_10_selling_at_breakeven_revenue_gives_zero_profit():
    # בדיקת עקביות: אם ההכנסה = R*, הרווח התרומתי = 0 (הנוסחה הפוכה ל-P)
    res = compute(Basket([item(6, 9, 2, "0.20")], CREDIT_TERMS))
    r_star = res.break_even
    p_at_star = r_star - res.cost - (r_star * CREDIT_TERMS.rate + CREDIT_TERMS.fixed)
    assert abs(p_at_star) < Dec("1e-20")


def test_11_price_change_scenario():
    base = Basket([item(6, 9, 2, "0.20")], CREDIT_TERMS)
    alt = make_alternative(base, price_change_pct=Dec("10"))
    assert r2(compute(alt).revenue) == Dec("19.80")


def test_12_payment_method_scenario():
    base = Basket([item(6, 9, 2, "0.20")], CREDIT_TERMS)
    alt = make_alternative(base, method=CASH)
    assert compute(alt).fee == 0
    assert r2(compare(compute(base), compute(alt))["profit"]) == Dec("0.77")


def test_13_invalid_input_never_computes():
    with pytest.raises(ValueError):
        compute(Basket([item(6, 9, 2, "1")], CREDIT_TERMS))
