from decimal import Decimal as Dec

from core.basket_io import (COL_BUY, COL_SPOIL, catalog_rows_to_df, df_to_items,
                            empty_basket_df)
from core.catalog import load_catalog
from core.models import TAG_DEMO, TAG_ENTERED


def test_catalog_has_12_demo_products():
    assert 10 <= len(load_catalog()) <= 15


def test_catalog_rows_are_demo_tagged_and_spoilage_is_fraction():
    cat = load_catalog()
    items = df_to_items(catalog_rows_to_df(cat, ["עגבניות"]), cat)
    assert items[0].spoilage == Dec("0.2") and items[0].spoilage_tag == TAG_DEMO


def test_edited_demo_value_becomes_entered():
    cat = load_catalog()
    df = catalog_rows_to_df(cat, ["עגבניות"])
    df.loc[0, COL_SPOIL] = 10.0
    it = df_to_items(df, cat)[0]
    assert it.spoilage_tag == TAG_ENTERED and it.buy_tag == TAG_DEMO


def test_missing_value_becomes_none_not_zero():
    cat = load_catalog()
    df = catalog_rows_to_df(cat, ["לחם"])
    df[COL_BUY] = df[COL_BUY].astype(object)
    df.loc[0, COL_BUY] = None
    assert df_to_items(df, cat)[0].buy_price is None


def test_blank_rows_are_dropped():
    assert df_to_items(empty_basket_df()) == []
