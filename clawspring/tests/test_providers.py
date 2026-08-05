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
    assert provider["anthropic_base_url"] == "https://api.minimax.io/anthropic"
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


def test_minimax_regional_endpoints():
    assert PROVIDERS["minimax"]["regional_endpoints"] == [
        {
            "region": "global_en",
            "openai_base_url": "https://api.minimax.io/v1",
            "anthropic_base_url": "https://api.minimax.io/anthropic",
            "docs_root": "https://platform.minimax.io/docs",
        },
        {
            "region": "cn_zh",
            "openai_base_url": "https://api.minimaxi.com/v1",
            "anthropic_base_url": "https://api.minimaxi.com/anthropic",
            "docs_root": "https://platform.minimaxi.com/docs",
        },
    ]


def test_minimax_cache_pricing_metadata():
    m3_pricing = MODEL_METADATA["MiniMax-M3"]["pricing"]
    m27_pricing = MODEL_METADATA["MiniMax-M2.7"]["pricing"]
    assert m3_pricing == {
        "input": 0.6,
        "output": 2.4,
        "cache_read": 0.12,
        "cache_write": None,
    }
    assert m27_pricing == {
        "input": 0.3,
        "output": 1.2,
        "cache_read": 0.06,
        "cache_write": 0.375,
    }
    assert calc_cost("MiniMax-M3", 1000000, 1000000) == pytest.approx(3.0)
    assert calc_cost("MiniMax-M2.7", 1000000, 1000000) == pytest.approx(1.5)
