from pathlib import Path

import pytest

from pipeline.common.cost import PriceMissing, PriceTable, UsageTotals

REPO = Path(__file__).resolve().parents[1]


def test_price_table_loads_and_names_its_source():
    table = PriceTable.load()
    assert table.read_on
    assert "claude-opus-5-5" in table.models


def test_opus_cost_arithmetic():
    table = PriceTable.load()
    cost = table.cost_usd("claude-opus-5-5", {"input_tokens": 1_000_000, "output_tokens": 100_000, "cache_read_input_tokens": 2_000_000})
    # 1M*4 + 0.1M*20 + 2M*0.20 = 4 + 2 + 0.4
    assert cost == pytest.approx(6.4)


def test_null_price_is_loud_not_zero():
    table = PriceTable.load()
    if table.models["claude-opus-5-5"].get("cache_write_5m") is not None:
        pytest.skip("cache_write_5m has been verified; nothing to test")
    with pytest.raises(PriceMissing):
        table.cost_usd("claude-opus-5-5", {"cache_creation_input_tokens": 10})


def test_unknown_model_is_loud():
    table = PriceTable.load()
    with pytest.raises(PriceMissing):
        table.cost_usd("claude-opus-4-9", {"input_tokens": 1})


def test_usage_totals_and_cache_hit_rate():
    totals = UsageTotals("claude-opus-5-5")
    totals.add({"input_tokens": 1000, "output_tokens": 100})
    totals.add({"input_tokens": 1000, "cache_read_input_tokens": 3000, "output_tokens": 100})
    assert totals.n_requests == 2
    assert totals.usage["input_tokens"] == 2000
    assert totals.cache_hit_rate() == pytest.approx(3000 / 5000)
    assert totals.cost_usd == pytest.approx((2000 * 4 + 200 * 20 + 3000 * 0.2) / 1e6)


def test_haiku_long_prompt_warns():
    table = PriceTable.load()
    with pytest.warns(UserWarning):
        table.cost_usd("claude-haiku-5-5", {"input_tokens": 200_000})
