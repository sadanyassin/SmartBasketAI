from decimal import Decimal as Dec

from core.models import CREDIT, Basket, PaymentTerms
from core.validation import validate_basket

from .helpers import CREDIT_TERMS, item


def errs(it, terms=CREDIT_TERMS):
    return validate_basket(Basket([it], terms))


def test_valid_basket_has_no_errors():
    assert errs(item(6, 9, 2, "0.2")) == []


def test_spoilage_100pct_rejected():
    assert any("פחת" in e for e in errs(item(6, 9, 2, "1")))


def test_spoilage_negative_rejected():
    assert any("פחת" in e for e in errs(item(6, 9, 2, "-0.1")))


def test_spoilage_missing_rejected():
    assert any("פחת" in e for e in errs(item(6, 9, 2, None)))


def test_quantity_zero_negative_and_fractional_rejected():
    for q in (0, -1, "1.5"):
        assert any("כמות" in e for e in errs(item(6, 9, q))), q


def test_missing_sell_price_must_be_filled():
    assert any("מחיר מכירה" in e for e in errs(item(6, None, 1)))


def test_missing_buy_price_blocks_profit_and_says_so():
    e = errs(item(None, 9, 1))
    assert any("חסר מחיר קנייה" in x and "לא מחושב רווח" in x for x in e)


def test_credit_rate_100pct_or_more_rejected():
    t = PaymentTerms(CREDIT, Dec("1"), Dec("0"))
    assert any("עמלת האשראי" in e for e in errs(item(6, 9, 1), t))


def test_negative_fixed_fee_rejected():
    t = PaymentTerms(CREDIT, Dec("0.01"), Dec("-1"))
    assert any("העמלה הקבועה" in e for e in errs(item(6, 9, 1), t))


def test_empty_basket_rejected():
    assert any("ריק" in e for e in validate_basket(Basket([], CREDIT_TERMS)))
