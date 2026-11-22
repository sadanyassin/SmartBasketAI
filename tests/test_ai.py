import json
from decimal import Decimal as Dec

import pytest

from ai import llm_client
from ai.fallback import FALLBACK_LABEL, rule_based_explanation
from ai.payload import ALLOWED_KEYS, RESULT_KEYS, build_payload
from core.calculations import compute
from core.models import TAG_DEMO
from core.scenarios import make_alternative

from .helpers import stitch_basket


def _payload():
    base = stitch_basket()
    for it in base.items:
        it.spoilage_tag = TAG_DEMO
    alt = make_alternative(base, spoilage_overrides={2: Dec("0.10")})
    return build_payload(base, alt, compute(base), compute(alt), "פחת עגבניות מ-20% ל-10%")


def test_payload_contains_only_allowed_computed_keys():
    p = _payload()
    assert set(p) == ALLOWED_KEYS
    assert set(p["base"]) == RESULT_KEYS and set(p["alternative"]) == RESULT_KEYS
    assert p["base"]["profit"] == 6.32 and p["alternative"]["profit"] == 7.99
    assert p["delta"]["profit"] == 1.67


def test_payload_lists_estimate_fields_and_is_json_serializable():
    p = _payload()
    assert any("פחת - עגבניות" in f for f in p["estimated_fields"])
    json.dumps(p, ensure_ascii=False)


def test_fallback_is_labeled_not_ai_and_mentions_limits():
    assert "לא AI" in FALLBACK_LABEL
    text = rule_based_explanation(_payload())
    assert "6.32" in text and "7.99" in text and "אומדן" in text


def test_missing_api_key_raises_unavailable(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(llm_client.LLMUnavailable):
        llm_client.explain(_payload())
