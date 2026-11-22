"""בדיקות קלט. מחזירות רשימת הודעות שגיאה בעברית (רשימה ריקה = תקין)."""
from __future__ import annotations

from decimal import Decimal

from .models import CREDIT, Basket

ZERO = Decimal("0")
ONE = Decimal("1")


def validate_basket(basket: Basket) -> list[str]:
    errors: list[str] = []
    if not basket.items:
        errors.append("הסל ריק: הוסיפו לפחות מוצר אחד.")

    for idx, it in enumerate(basket.items, start=1):
        name = it.name or f"שורה {idx}"
        if it.buy_price is None:
            errors.append(
                f"{name}: חסר מחיר קנייה, ולכן לא מחושב רווח למוצר. "
                "הזינו מחיר (או אומדן) או הסירו את המוצר."
            )
        elif it.buy_price < ZERO:
            errors.append(f"{name}: מחיר קנייה לא יכול להיות שלילי.")

        if it.sell_price is None:
            errors.append(f"{name}: חסר מחיר מכירה - יש להשלים לפני החישוב.")
        elif it.sell_price < ZERO:
            errors.append(f"{name}: מחיר מכירה לא יכול להיות שלילי.")

        if it.qty is None or it.qty <= ZERO:
            errors.append(f"{name}: הכמות חייבת להיות מספר חיובי.")
        elif it.qty != it.qty.to_integral_value():
            errors.append(f"{name}: הכמות חייבת להיות מספר שלם של יחידות.")

        if it.spoilage is None:
            errors.append(f"{name}: חסר שיעור פחת (0% אם אין פחת).")
        elif not (ZERO <= it.spoilage < ONE):
            errors.append(f"{name}: הפחת חייב להיות בטווח 0% עד פחות מ-100%.")

    t = basket.terms
    if t.method == CREDIT:
        if t.rate is None or not (ZERO <= t.rate < ONE):
            errors.append("עמלת האשראי היחסית חייבת להיות בטווח 0% עד פחות מ-100%.")
        if t.fixed is None or t.fixed < ZERO:
            errors.append("העמלה הקבועה לעסקה לא יכולה להיות שלילית.")
    return errors
