# Prompt — designing the runnable example (Gate 2)

> Editorial update 25 September 2026: read `prompts/editorial.md` first. Its novelty,
> practical-value and honest-evidence gates supersede conflicting editorial preferences
> below. Existing schema and CI requirements still apply.

Every item needs an example under `examples/YYYY-MM-DD-slug/` with a `run.sh` and an
`expected_output.txt`. CI re-runs `run.sh` on a clean machine and diffs the output; a mismatch
fails the build and the video does not publish. This is what "TESTED IN CI ✓" actually means —
it is CI's claim, never the author's.

## Pick the right kind, per vertical (`PROJECT_INSTRUCTIONS.md` §5)
- **Models & Releases:** inspect a config/tokenizer from the HF Hub, reimplement the
  mechanism at toy scale in numpy, or diff the new config against the predecessor's.
- **Tools & Agents:** most real results need a live model call, which Gate 2 forbids (no
  paid keys in CI). Only when it teaches the actual mechanism, use a **deterministic stub** — a fake LLM driven by a script — that
  demonstrates the control loop, context packing, retry logic, or token/cost accounting. Where a
  real small model fits in CI, use it. **State on the slide when the example is a stub** —
  honesty about what is demonstrated is part of the product.
- **Media Generation:** never run a generative model in CI. Analyze instead: compute
  VRAM from the model card, reimplement the noise schedule in numpy, compute latent size from
  resolution, or diff license terms programmatically. Say plainly that the executable artifact
  here is the math/inspection, not generation.
- **Claims & Risks:** load a slice of a dataset from HF, compute n-gram overlap with a
  benchmark, measure cross-seed variance, or show a metric change under a different prompt
  format. This is the vertical where the channel can be unambiguously best — it requires exactly
  what slop content skips: actually running things.
- **Cost & Limits:** token/cost arithmetic, KV-cache size from a formula,
  quantization math, batching math. CPU-friendly by default.

## Hard requirements
- CPU-only, no GPU dependency, unless the CI runner is confirmed to have one (it does not, by
  default — do not assume it).
- Runs in well under 60 seconds — nobody executes an example that takes longer, and the video
  segment budget assumes it (`PROJECT_INSTRUCTIONS.md` §8.3).
- Pin dependencies in a `requirements.txt` inside the example folder if it needs anything beyond
  the repo root's `requirements.txt`.
- `expected_output.txt` and the episode's `example.output` must both match captured stdout
  (only leading/trailing whitespace is ignored; no partial or regex matching is supported) —
  ambiguous "close enough" checks defeat the point of Gate 2.
- Use `"${PYTHON:-python3}" run.py` in run.sh. The verifier supplies its Python executable
  on Windows and Linux; Git for Windows supplies Bash when it is missing from PATH.
- Never infer real-world model performance from a deterministic stub. Record the limits
  and the measurement design from `prompts/research.md`.

## Standing corrections
Reject arbitrary fixture percentages, trivial countdowns and arithmetic unrelated to
a meaningful task. Configuration inspection may qualify; do not imply it tests live behaviour.
