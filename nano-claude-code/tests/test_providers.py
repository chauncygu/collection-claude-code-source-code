"""Tests for providers.py — MiniMax provider registration, detection, and cost."""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from providers import (
    PROVIDERS,
    COSTS,
    _PREFIXES,
    detect_provider,
    bare_model,
    get_api_key,
    calc_cost,
)


# ── MiniMax provider registration ─────────────────────────────────────────

class TestMinimaxRegistration:
    def test_minimax_in_providers(self):
        assert "minimax" in PROVIDERS

    def test_minimax_type_is_openai_compat(self):
        assert PROVIDERS["minimax"]["type"] == "openai"

    def test_minimax_base_url(self):
        assert PROVIDERS["minimax"]["base_url"] == "https://api.minimax.io/v1"

    def test_minimax_api_key_env(self):
        assert PROVIDERS["minimax"]["api_key_env"] == "MINIMAX_API_KEY"

    def test_minimax_models_present(self):
        models = PROVIDERS["minimax"]["models"]
        assert "MiniMax-M2.7" in models
        assert "MiniMax-M2.7-highspeed" in models

    def test_minimax_context_limit(self):
        assert PROVIDERS["minimax"]["context_limit"] > 0


# ── Auto-detection ─────────────────────────────────────────────────────────

class TestDetectProvider:
    def test_detect_minimax_m27(self):
        assert detect_provider("MiniMax-M2.7") == "minimax"

    def test_detect_minimax_highspeed(self):
        assert detect_provider("MiniMax-M2.7-highspeed") == "minimax"

    def test_detect_minimax_case_insensitive(self):
        assert detect_provider("minimax-m2.7") == "minimax"

    def test_explicit_provider_prefix(self):
        assert detect_provider("minimax/MiniMax-M2.7") == "minimax"

    def test_bare_model_strips_prefix(self):
        assert bare_model("minimax/MiniMax-M2.7") == "MiniMax-M2.7"
        assert bare_model("MiniMax-M2.7") == "MiniMax-M2.7"

    def test_other_providers_unaffected(self):
        assert detect_provider("claude-opus-4-6") == "anthropic"
        assert detect_provider("gpt-4o") == "openai"
        assert detect_provider("deepseek-chat") == "deepseek"


# ── Cost calculation ────────────────────────────────────────────────────────

class TestMinimaxCosts:
    def test_minimax_m27_cost_in_costs(self):
        assert "MiniMax-M2.7" in COSTS

    def test_minimax_highspeed_cost_in_costs(self):
        assert "MiniMax-M2.7-highspeed" in COSTS

    def test_minimax_cost_nonzero(self):
        ic, oc = COSTS["MiniMax-M2.7"]
        assert ic > 0
        assert oc > 0

    def test_calc_cost_minimax_m27(self):
        cost = calc_cost("MiniMax-M2.7", 1_000_000, 1_000_000)
        assert cost > 0

    def test_calc_cost_minimax_with_provider_prefix(self):
        cost = calc_cost("minimax/MiniMax-M2.7", 1_000_000, 1_000_000)
        assert cost > 0

    def test_calc_cost_zero_tokens(self):
        assert calc_cost("MiniMax-M2.7", 0, 0) == 0.0


# ── API key resolution ──────────────────────────────────────────────────────

class TestGetApiKey:
    def test_get_api_key_from_config(self):
        config = {"minimax_api_key": "test-key-123"}
        key = get_api_key("minimax", config)
        assert key == "test-key-123"

    def test_get_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("MINIMAX_API_KEY", "env-key-456")
        key = get_api_key("minimax", {})
        assert key == "env-key-456"

    def test_get_api_key_empty_when_not_set(self, monkeypatch):
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        key = get_api_key("minimax", {})
        assert key == ""

    def test_config_key_takes_precedence_over_env(self, monkeypatch):
        monkeypatch.setenv("MINIMAX_API_KEY", "env-key")
        config = {"minimax_api_key": "config-key"}
        key = get_api_key("minimax", config)
        assert key == "config-key"


# ── Prefix list sanity ──────────────────────────────────────────────────────

class TestPrefixes:
    def test_minimax_prefix_in_list(self):
        prefixes = [p for p, _ in _PREFIXES]
        assert "minimax-" in prefixes

    def test_minimax_prefix_maps_to_minimax(self):
        mapping = {p: n for p, n in _PREFIXES}
        assert mapping["minimax-"] == "minimax"
