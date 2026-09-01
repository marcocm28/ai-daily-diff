# examples/2026-08-28-prefix-cache/run.py
# Demonstrates the arithmetic behind prefix-cache reuse: shared request prefixes are billed
# once instead of once per request. Token counts are approximated at ~4 characters/token (a
# standard rule of thumb for English text), so this runs fully offline -- no model download,
# no network access, no dependency beyond the standard library. That makes it runnable in any
# CI runner, which is the point: Gate 2 requires this to reproduce on a clean machine.

def approx_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))

prefix = "You are a helpful assistant. " * 40
requests = [prefix + q for q in ("hi", "why is the sky blue?", "can you say that again?")]

naive = sum(approx_tokens(r) for r in requests)
shared = approx_tokens(prefix) + sum(approx_tokens(r[len(prefix):]) for r in requests)

print(naive, shared, round(1 - shared / naive, 3))
