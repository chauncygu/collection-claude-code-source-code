"""Tests for compaction.py — token estimation, context limits, snipping, split point."""
from __future__ import annotations

import sys
import os

# Ensure project root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from compaction import estimate_tokens, get_context_limit, snip_old_tool_results, find_split_point


# ── estimate_tokens ───────────────────────────────────────────────────────

class TestEstimateTokens:
    def test_simple_messages(self):
        msgs = [
            {"role": "user", "content": "Hello world"},          # 11 chars
            {"role": "assistant", "content": "Hi there!"},       # 9 chars
        ]
        result = estimate_tokens(msgs)
        # (11 + 9) / 3.5 = 5.71 -> 5
        assert result == int(20 / 3.5)

    def test_empty_messages(self):
        assert estimate_tokens([]) == 0

    def test_empty_content(self):
        msgs = [{"role": "user", "content": ""}]
        assert estimate_tokens(msgs) == 0

    def test_tool_result_messages(self):
        msgs = [
            {"role": "tool", "tool_call_id": "abc", "name": "Read", "content": "x" * 350},
        ]
        result = estimate_tokens(msgs)
        assert result == int(350 / 3.5)

    def test_structured_content(self):
        """Content that is a list of dicts (e.g. Anthropic tool_result blocks)."""
        msgs = [
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "id1", "content": "A" * 70},
                ],
            },
        ]
        result = estimate_tokens(msgs)
        # "tool_result" (11) + "id1" (3) + "A"*70 (70) = 84  -> 84/3.5 = 24
        assert result == int(84 / 3.5)

    def test_with_tool_calls(self):
        msgs = [
            {
                "role": "assistant",
                "content": "ok",
                "tool_calls": [
                    {"id": "c1", "name": "Bash", "input": {"command": "ls"}},
                ],
            },
        ]
        result = estimate_tokens(msgs)
        # content "ok" (2) + tool_calls string values: "c1" (2) + "Bash" (4) = 8
        assert result == int(8 / 3.5)


# ── get_context_limit ─────────────────────────────────────────────────────

class TestGetContextLimit:
    def test_anthropic(self):
        assert get_context_limit("claude-opus-4-6") == 200000

    def test_gemini(self):
        assert get_context_limit("gemini-2.0-flash") == 1000000

    def test_deepseek(self):
        assert get_context_limit("deepseek-chat") == 64000

    def test_openai(self):
        assert get_context_limit("gpt-4o") == 128000

    def test_qwen(self):
        assert get_context_limit("qwen-max") == 1000000

    def test_unknown_model_fallback(self):
        # Unknown models fall back to openai provider which has 128000
        assert get_context_limit("some-random-model-xyz") == 128000

    def test_explicit_provider_prefix(self):
        assert get_context_limit("ollama/llama3.3") == 128000

    def test_minimax_models_use_model_specific_limits(self):
        assert get_context_limit("MiniMax-M3") == 1000000
        assert get_context_limit("MiniMax-M2.7") == 204800

    def test_minimax_limit_is_independent_of_adapter_prefix(self):
        assert get_context_limit("custom/MiniMax-M3") == 1000000
        assert get_context_limit("anthropic/MiniMax-M2.7") == 204800


# ── snip_old_tool_results ─────────────────────────────────────────────────

class TestSnipOldToolResults:
    def test_old_tool_results_get_truncated(self):
        long_content = "A" * 5000
        msgs = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "let me check", "tool_calls": []},
            {"role": "tool", "tool_call_id": "t1", "name": "Read", "content": long_content},
            {"role": "user", "content": "thanks"},
            {"role": "assistant", "content": "you're welcome"},
            {"role": "user", "content": "bye"},
            {"role": "assistant", "content": "goodbye"},
            {"role": "user", "content": "wait"},
            {"role": "assistant", "content": "yes?"},
            {"role": "user", "content": "never mind"},
        ]
        result = snip_old_tool_results(msgs, max_chars=2000, preserve_last_n_turns=6)
        assert result is msgs  # mutated in place
        tool_msg = msgs[2]
        assert len(tool_msg["content"]) < 5000
        assert "snipped" in tool_msg["content"]

    def test_recent_tool_results_preserved(self):
        long_content = "B" * 5000
        msgs = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "ok", "tool_calls": []},
            {"role": "tool", "tool_call_id": "t1", "name": "Read", "content": long_content},
        ]
        # All 3 messages are within preserve_last_n_turns=6
        result = snip_old_tool_results(msgs, max_chars=2000, preserve_last_n_turns=6)
        assert msgs[2]["content"] == long_content  # not truncated

    def test_short_tool_results_not_touched(self):
        msgs = [
            {"role": "tool", "tool_call_id": "t1", "name": "Bash", "content": "short"},
            {"role": "user", "content": "a"},
            {"role": "user", "content": "b"},
            {"role": "user", "content": "c"},
            {"role": "user", "content": "d"},
            {"role": "user", "content": "e"},
            {"role": "user", "content": "f"},
        ]
        snip_old_tool_results(msgs, max_chars=2000, preserve_last_n_turns=6)
        assert msgs[0]["content"] == "short"

    def test_non_tool_messages_untouched(self):
        msgs = [
            {"role": "user", "content": "X" * 5000},
            {"role": "user", "content": "a"},
            {"role": "user", "content": "b"},
            {"role": "user", "content": "c"},
            {"role": "user", "content": "d"},
            {"role": "user", "content": "e"},
            {"role": "user", "content": "f"},
        ]
        snip_old_tool_results(msgs, max_chars=2000, preserve_last_n_turns=6)
        assert msgs[0]["content"] == "X" * 5000


# ── find_split_point ──────────────────────────────────────────────────────

class TestFindSplitPoint:
    def test_returns_reasonable_index(self):
        msgs = [
            {"role": "user", "content": "A" * 1000},
            {"role": "assistant", "content": "B" * 1000},
            {"role": "user", "content": "C" * 1000},
            {"role": "assistant", "content": "D" * 1000},
            {"role": "user", "content": "E" * 1000},
        ]
        idx = find_split_point(msgs, keep_ratio=0.3)
        # With equal-size messages and keep_ratio=0.3, split should be around index 3-4
        assert 2 <= idx <= 4

    def test_single_message(self):
        msgs = [{"role": "user", "content": "hello"}]
        idx = find_split_point(msgs, keep_ratio=0.3)
        assert idx == 0

    def test_empty_messages(self):
        idx = find_split_point([], keep_ratio=0.3)
        assert idx == 0

    def test_split_preserves_recent(self):
        # Recent portion should contain ~30% of tokens
        msgs = [{"role": "user", "content": "X" * 100} for _ in range(10)]
        idx = find_split_point(msgs, keep_ratio=0.3)
        total = estimate_tokens(msgs)
        recent = estimate_tokens(msgs[idx:])
        # Recent should be roughly 30% of total (allow some tolerance)
        assert recent >= total * 0.2
        assert recent <= total * 0.5
