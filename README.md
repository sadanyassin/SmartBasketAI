# SmartBasket AI

סימולטור רווחיות לסל קנייה אחד (עסקה אחת) במכולת שכונתית. ממשק בעברית, Python + Streamlit.
התוצאה היא **רווח תרומתי משוער** ולא רווח נקי. כל המחירים ללא מע"מ.

## התקנה (פעם אחת)
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## הרצה
```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```
הדפדפן ייפתח בכתובת http://localhost:8501 (אם לא, פתחו אותה ידנית).

## בדיקות
```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## הגדרת מפתח API להסבר ה-AI (בטוח)
1. העתיקו את `.streamlit/secrets.toml.example` לקובץ חדש בשם `.streamlit/secrets.toml`.
2. הדביקו בו את המפתח שלכן. הקובץ הזה כבר מוחרג ב-`.gitignore`, ולכן לא יעלה ל-GitHub.
3. לעולם אל תכתבו מפתח בקוד, בצ'אט או בהודעת commit.
בלי מפתח האפליקציה עובדת, וההסבר יוצג כהסבר מבוסס כללים שמסומן "לא AI".

## מבנה
`core/` חישובים ובדיקות קלט · `ai/` רכיב ההסבר · `ui/` לשוניות · `data/` קטלוג הדגמה · `tests/` בדיקות
