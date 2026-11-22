"""הסבר מבוסס כללים כשה-AI לא זמין. תמיד מסומן בבירור כ'לא AI'."""
FALLBACK_LABEL = "הסבר מבוסס כללים - לא AI"


def rule_based_explanation(payload: dict) -> str:
    b, a, d = payload["base"], payload["alternative"], payload["delta"]
    parts = []
    if b["revenue"] > 0:
        cost_share = b["cost"] / b["revenue"] * 100
        parts.append(
            f"בתרחיש הבסיס, עלות המוצרים (כולל פחת) היא {b['cost']:.2f} ₪ מתוך הכנסות של "
            f"{b['revenue']:.2f} ₪ ({cost_share:.0f}%), והעמלה {b['fee']:.2f} ₪; "
            f"הרווח התרומתי המשוער הוא {b['profit']:.2f} ₪ ({b['status']})."
        )
    if d["profit"] == 0:
        parts.append("השינוי שנבדק לא שינה את הרווח התרומתי המשוער.")
    else:
        direction = "עלה" if d["profit"] > 0 else "ירד"
        parts.append(
            f"בתרחיש החלופי ({payload['change_tested']}) הרווח התרומתי המשוער {direction} "
            f"ב-{abs(d['profit']):.2f} ₪ ל-{a['profit']:.2f} ₪."
        )
    est = "קיימים נתונים שמסומנים כהערכה או הדגמה" if payload["estimated_fields"] else "כל הנתונים הוזנו"
    parts.append(f"זהו אומדן בלבד ולא רווח נקי; {est}.")
    return " ".join(parts)
