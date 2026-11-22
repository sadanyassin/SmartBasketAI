"""טעינת קטלוג ההדגמה (מוצרים מדומים, לא מחירי שוק)."""
from pathlib import Path

import pandas as pd

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "demo_catalog.csv"


def load_catalog(path: Path = CATALOG_PATH) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")
