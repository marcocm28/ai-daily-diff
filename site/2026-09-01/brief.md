# Quantization day: 69% less state memory, and an 85% backdoor — AI Daily Diff Sep 1

2026-09-01

Every claim below links to a primary source. Every example is executed in CI before this video is published; if an example fails, the video does not ship.

## 01 · Qwen's next architecture appears in a preview: half the hidden size, 512 experts, 62% less KV cache.
**Vertical:** MODELS & RELEASES

WHAT CHANGED — Qwen3.8-Flash-Next ships a new model_type, qwen4_exp: a 512-expert MoE with 10 active per token, replacing a dense FFN.
WHY IT MATTERS — Fewer KV heads and 12 full-attention layers change what one GPU can hold, before any kernel work.
THE NUMBER — 24 KiB (KV cache per token, against 64 KiB for Qwen3.8-27B — 62.5% less)

Run it yourself (13 lines, CPU, offline, < 1 s):
  examples/2026-09-01-qwen-flash-next-config/

Caveat: This is a preview checkpoint with an experimental model_type, and the two models are different sizes. The diff shows a direction of travel, not a like-for-like benchmark.

Primary source: https://huggingface.co/Qwen/Qwen3.8-Flash-Next
Tested example: https://github.com/marcocm28/ai-daily-diff/tree/main/examples/2026-09-01-qwen-flash-next-config

## 02 · Those linear-attention layers keep a fixed state in FP32. Quantizing it frees 69% of that memory.
**Vertical:** COST & LIMITS

WHAT CHANGED — DAMP quantizes recurrent states to 9.9 bits per value on average, keeping high-error channels precise instead of quantizing uniformly.
WHY IT MATTERS — Uniform INT8 already hurts reasoning accuracy and INT4 destroys it. Mixed precision is what makes the saving usable.
THE NUMBER — 6.75 → 2.09 GiB (recurrent-state memory at batch 64, computed from the Flash-Next config)

Run it yourself (11 lines, CPU, offline, < 1 s):
  examples/2026-09-01-damp-recurrent-state/

Caveat: The paper measures Qwen3.6-35B and Kimi-Linear-48B, not this config. Our numbers apply its stated bit budget to the Flash-Next config from item 01: a projection, not their measurement.

Primary source: https://arxiv.org/abs/2608.27513
Tested example: https://github.com/marcocm28/ai-daily-diff/tree/main/examples/2026-09-01-damp-recurrent-state

## 03 · A checkpoint can pass every FP16 check and behave differently after INT8. Certification does not survive quantization.
**Vertical:** CLAIMS & RISKS

WHAT CHANGED — A paper formalizes quantization as a many-to-one map, then embeds payloads that stay dormant at FP16 and activate after compression.
WHY IT MATTERS — If you validate the FP16 checkpoint and ship the quantized one, you certified a model you did not deploy.
THE NUMBER — 0% → 85.02% (friend-foe inversion in their backdoored translation model, after quantization)

Run it yourself (17 lines, numpy, CPU, offline, < 1 s):
  examples/2026-09-01-quantization-gap/

Caveat: Our example demonstrates the structural gap — a perturbation orthogonal to the validation input flipping INT8 codes — not the paper's fine-tuning attack. It is not a reproduction of their 85.02%.

Primary source: https://arxiv.org/abs/2608.27512
Tested example: https://github.com/marcocm28/ai-daily-diff/tree/main/examples/2026-09-01-quantization-gap

---
Slides (PDF): https://marcocm28.github.io/ai-daily-diff/2026-09-01/slides.pdf      Cheat sheet (PDF): https://marcocm28.github.io/ai-daily-diff/2026-09-01/cheatsheet.pdf
Episode page: https://marcocm28.github.io/ai-daily-diff/2026-09-01/