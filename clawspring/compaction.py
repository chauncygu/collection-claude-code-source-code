"""Context window management: two-layer compression for long conversations."""
from __future__ import annotations

import providers


# ── Token estimation ──────────────────────────────────────────────────────

def estimate_tokens(messages: list) -> int:
    """Estimate token count by summing content lengths / 3.5.

    Args:
        messages: list of message dicts with "content" field (str or list of dicts)
    Returns:
        approximate token count, int
    """
    total_chars = 0
    for m in messages:
        content = m.get("content", "")
        if isinstance(content, str):
            total_chars += len(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    # Sum all string values in the block
                    for v in block.values():
                        if isinstance(v, str):
                            total_chars += len(v)
        # Also count tool_calls if present
        for tc in m.get("tool_calls", []):
            if isinstance(tc, dict):
                for v in tc.values():
                    if isinstance(v, str):
                        total_chars += len(v)
    return int(total_chars / 3.5)


def get_context_limit(model: str) -> int:
    """Look up context window size for a model.

    Args:
        model: model string (e.g. "claude-opus-4-6", "ollama/llama3.3")
    Returns:
        context limit in tokens
    """
    return providers.get_context_limit(model)


# ── Layer 1: Snip old tool results ────────────────────────────────────────

def snip_old_tool_results(
    messages: list,
    max_chars: int = 2000,
    preserve_last_n_turns: int = 6,
) -> list:
    """Truncate tool-role messages older than preserve_last_n_turns from end.

    For old tool messages whose content exceeds max_chars, keep the first half
    and last quarter, inserting '[... N chars snipped ...]' in between.
    Mutates in place and returns the same list.

    Args:
        messages: list of message dicts (mutated in place)
        max_chars: maximum character length before truncation
        preserve_last_n_turns: number of messages from end to preserve
    Returns:
        the same messages list (mutated)
    """
    cutoff = max(0, len(messages) - preserve_last_n_turns)
    for i in range(cutoff):
        m = messages[i]
        if m.get("role") != "tool":
            continue
        content = m.get("content", "")
        if not isinstance(content, str) or len(content) <= max_chars:
            continue
        first_half = content[: max_chars // 2]
        last_quarter = content[-(max_chars // 4):]
        snipped = len(content) - len(first_half) - len(last_quarter)
        m["content"] = f"{first_half}\n[... {snipped} chars snipped ...]\n{last_quarter}"
    return messages


# ── Layer 2: Auto-compact ─────────────────────────────────────────────────

def find_split_point(messages: list, keep_ratio: float = 0.3) -> int:
    """Find index that splits messages so ~keep_ratio of tokens are in the recent portion.

    Walks backwards from end, accumulating token estimates, and returns the
    index where the recent portion reaches ~keep_ratio of total tokens.

    Args:
        messages: list of message dicts
        keep_ratio: fraction of tokens to keep in the recent portion
    Returns:
        split index (messages[:idx] = old, messages[idx:] = recent)
    """
    total = estimate_tokens(messages)
    target = int(total * keep_ratio)
    running = 0
    for i in range(len(messages) - 1, -1, -1):
        running += estimate_tokens([messages[i]])
        if running >= target:
            return i
    return 0


def compact_messages(messages: list, config: dict) -> list:
    """Compress old messages into a summary via LLM call.

    Splits at find_split_point, summarizes old portion, returns
    [summary_msg, ack_msg, *recent_messages].

    Args:
        messages: full message list
        config: agent config dict (must contain "model")
    Returns:
        new compacted message list
    """
    split = find_split_point(messages)
    if split <= 0:
        return messages

    old = messages[:split]
    recent = messages[split:]

    # Build summary request
    old_text = ""
    for m in old:
        role = m.get("role", "?")
        content = m.get("content", "")
        if isinstance(content, str):
            old_text += f"[{role}]: {content[:500]}\n"
        elif isinstance(content, list):
            old_text += f"[{role}]: (structured content)\n"

    summary_prompt = (
        "Summarize the following conversation history concisely. "
        "Preserve key decisions, file paths, tool results, and context "
        "needed to continue the conversation:\n\n" + old_text
    )

    # Call LLM for summary
    summary_text = ""
    for event in providers.stream(
        model=config["model"],
        system="You are a concise summarizer.",
        messages=[{"role": "user", "content": summary_prompt}],
        tool_schemas=[],
        config=config,
    ):
        if isinstance(event, providers.TextChunk):
            summary_text += event.text

    summary_msg = {
        "role": "user",
        "content": f"[Previous conversation summary]\n{summary_text}",
    }
    ack_msg = {
        "role": "assistant",
        "content": "Understood. I have the context from the previous conversation. Let's continue.",
    }
    return [summary_msg, ack_msg, *recent]


# ── Main entry ────────────────────────────────────────────────────────────

def maybe_compact(state, config: dict) -> bool:
    """Check if context window is getting full and compress if needed.

    Runs snip_old_tool_results first, then auto-compact if still over threshold.

    Args:
        state: AgentState with .messages list
        config: agent config dict (must contain "model")
    Returns:
        True if compaction was performed
    """
    model = config.get("model", "")
    limit = get_context_limit(model)
    threshold = limit * 0.7

    if estimate_tokens(state.messages) <= threshold:
        return False

    # Layer 1: snip old tool results
    snip_old_tool_results(state.messages)

    if estimate_tokens(state.messages) <= threshold:
        return True

    # Layer 2: auto-compact
    state.messages = compact_messages(state.messages, config)
    return True
