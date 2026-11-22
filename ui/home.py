"""דף ראשי: הסבר קצר וכפתור 'בניית סל חדש'."""
import streamlit as st

from core.basket_io import empty_basket_df


def render() -> None:
    st.title("SmartBasket AI")
    st.subheader("סימולציית רווחיות לסל קנייה אחד במכולת")
    st.write(
        "הכלי עוזר להבין מה משפיע על הרווח התרומתי המשוער של קנייה אחת של לקוח: "
        "מחירי קנייה ומכירה, פחת משוער ועמלת אשראי. אפשר לבדוק מה קורה אם משנים מחיר, פחת או אמצעי תשלום, "
        "ולקבל הסבר קצר במילים פשוטות."
    )
    st.info(
        "חשוב לדעת: זה אומדן לצורך סימולציה בלבד. כל המחירים ללא מע\"מ, התוצאה אינה רווח נקי, "
        "והיא לא כוללת שכירות, שכר ומסים. נתונים שאינם מדויקים מסומנים כ\"הערכה\" או \"הדגמה\"."
    )
    if st.button("בניית סל חדש", type="primary"):
        st.session_state["basket_df"] = empty_basket_df()
        st.session_state["editor_ver"] = st.session_state.get("editor_ver", 0) + 1
        st.success("הסל החדש מוכן. עברו ללשונית \"בניית סל\" כדי להוסיף מוצרים.")
