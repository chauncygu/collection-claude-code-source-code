"""Focused tests for provider registry metadata and pricing."""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from providers import (  # noqa: E402
    MODEL_METADATA,
    PROVIDERS,
    calc_cost,
    detect_provider,
    get_api_key,
)


def test_minimax_registry_and_detection():
    provider = PROVIDERS["minimax"]
    assert provider["type"] == "openai"
    assert provider["base_url"] == "https://api.minimax.io/v1"
    assert provider["models"] == ["MiniMax-M3", "MiniMax-M2.7"]
    assert detect_provider("MiniMax-M3") == "minimax"
    assert detect_provider("MiniMax-M2.7") == "minimax"


def test_minimax_api_key_lookup(monkeypatch):
    monkeypatch.setenv("MINIMAX_API_KEY", "test-key")
    assert get_api_key("minimax", {}) == "test-key"
    assert get_api_key("minimax", {"minimax_api_key": "config-key"}) == "config-key"


def test_minimax_model_capabilities():
    assert MODEL_METADATA["MiniMax-M3"]["input_modalities"] == [
        "text", "image", "video",
    ]
    assert MODEL_METADATA["MiniMax-M3"]["thinking"] == ["adaptive", "disabled"]
    assert MODEL_METADATA["MiniMax-M2.7"]["input_modalities"] == ["text"]
    assert MODEL_METADATA["MiniMax-M2.7"]["thinking"] == ["always_on"]


def test_minimax_m3_standard_pricing_tiers():
    lower = calc_cost("MiniMax-M3", 512000, 1000000)
    upper = calc_cost("MiniMax-M3", 512001, 1000000)
    assert lower == pytest.approx(0.512 * 0.3 + 1.2)
    assert upper == pytest.approx(0.512001 * 0.6 + 2.4)


def test_minimax_m3_priority_pricing_tiers():
    lower = calc_cost("MiniMax-M3", 512000, 1000000, service_tier="priority")
    upper = calc_cost("MiniMax-M3", 512001, 1000000, service_tier="priority")
    assert lower == pytest.approx(0.512 * 0.45 + 1.8)
    assert upper == pytest.approx(0.512001 * 0.9 + 3.6)


def test_minimax_cache_pricing_metadata():
    m3_tiers = MODEL_METADATA["MiniMax-M3"]["pricing_tiers"]
    m27_standard = MODEL_METADATA["MiniMax-M2.7"]["pricing_tiers"][0]
    assert [tier["cache_read"] for tier in m3_tiers] == [0.06, 0.12, 0.09, 0.18]
    assert all(tier["cache_write"] is None for tier in m3_tiers)
    assert m27_standard["cache_read"] == 0.06
    assert m27_standard["cache_write"] == 0.375
    assert calc_cost("MiniMax-M2.7", 1000000, 1000000) == pytest.approx(1.5)
