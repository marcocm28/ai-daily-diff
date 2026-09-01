# examples/

One folder per item, named `YYYY-MM-DD-slug/` (matching the episode date and the item's `id` in
`data/episodes/YYYY-MM-DD.json`). Each folder has exactly two required files:

- **`run.sh`** — runs the example. Must finish in well under 60 seconds, CPU-only, no network
  access assumed at run time (fetch anything needed once, or vendor small fixtures).
- **`expected_output.txt`** — the exact stdout `run.sh` must reproduce. `src/schema.py
  verify_example()` runs `run.sh` and diffs its stdout against this file — a mismatch fails
  Gate 2, and `.github/workflows/test.yml` re-runs the same check on a clean GitHub-hosted
  runner before anything publishes.

Optional: a folder-local `requirements.txt` if the example needs a package beyond the repo
root's `requirements.txt`.

See `prompts/example.md` for how to pick the right kind of example per vertical.

`2026-08-28-prefix-cache/` below is a worked example, carried over from the original proof of
concept, so the pattern is concrete rather than just described.
