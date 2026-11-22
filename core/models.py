"""מודלים של נתונים: מוצר בסל, תנאי תשלום וסל. כל הסכומים ב-Decimal ללא מע"מ."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

# תוויות רמת ודאות (ליד כל נתון קלט)
TAG_ENTERED = "הוזן"
TAG_ESTIMATE = "הערכה"
TAG_DEMO = "הדגמה"
ALL_TAGS = (TAG_ENTERED, TAG_ESTIMATE, TAG_DEMO)

CASH = "cash"
CREDIT = "credit"


@dataclass
class BasketItem:
    name: str
    buy_price: Optional[Decimal]      # None = חסר
    sell_price: Optional[Decimal]     # None = חסר
    qty: Optional[Decimal]            # יחידות נמכרות
    spoilage: Optional[Decimal]       # 0 <= d < 1 (שבר, לא אחוז)
    buy_tag: str = TAG_ENTERED
    sell_tag: str = TAG_ENTERED
    spoilage_tag: str = TAG_ENTERED


@dataclass
class PaymentTerms:
    method: str = CASH                # cash / credit
    rate: Decimal = Decimal("0")      # r - עמלה יחסית (שבר)
    fixed: Decimal = Decimal("0")     # F - עמלה קבועה לעסקה
    tag: str = TAG_ENTERED


@dataclass
class Basket:
    items: List[BasketItem] = field(default_factory=list)
    terms: PaymentTerms = field(default_factory=PaymentTerms)
