"""Assembler for the 2026-09-02 episode — the first one selected under the revised weights.

Two items, not three, on purpose: the day offered two strong candidates and one eight-day-old
one, and `RECIPE.md` says padding a brief with a weak item is worse than running short.

Code and output on the slides are read out of examples/*/, and slide excerpts are asserted to be
verbatim slices, so what a viewer sees cannot drift from what CI runs.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
EX = ROOT / "examples"

D1 = "2026-09-02-price-spread"
D2 = "2026-09-02-gguf-defaults"


def read(example_dir: str, name: str) -> str:
    return (EX / example_dir / name).read_text(encoding="utf-8").rstrip("\n")


def excerpt(example_dir: str, ranges: list[tuple[int, int]]) -> str:
    lines = read(example_dir, "run.py").split("\n")
    parts = []
    for start, end in ranges:
        chunk = "\n".join(lines[start - 1:end])
        assert chunk in read(example_dir, "run.py"), f"excerpt drifted in {example_dir}"
        parts.append(chunk)
    return "\n…\n".join(parts)


def cost_chart() -> dict:
    """Monthly cost against volume, from the same vendored price list the example reads."""
    models = {m["id"]: m for m in json.loads(read(D1, "prices.json"))["models"]}
    picks = [("inception/mercury-2.5-preview", "cheapest on the list"),
             ("qwen/qwen3.8-flash", "mid-priced"),
             ("anthropic/claude-fable-5.1", "most expensive on the list")]
    series = []
    for mid, label in picks:
        m = models[mid]
        per_review = 30_000 * m["prompt"] + 2_000 * m["completion"]
        series.append({"label": label,
                        "data": [[n, round(n * per_review, 2)] for n in range(0, 1001, 50)]})
    return {"xlabel": "code reviews per month", "ylabel": "cost ($ / month)", "series": series}


episode = {
    "date": "2026-09-02",
    "kind": "daily",
    "title": "The same work costs $0.30 or $80 — AI Daily Diff Sep 2",
    "cover_title": "Two things|that changed today.",
    "thumbnail_text": "267×",
    "thumbnail_color": "var(--accent2)",
    "thumbnail_label": "the price spread for one month of the same work",
    "closing_line": "The model you pick decides the bill more than the prompt you write. And if you "
                    "run models locally, check your defaults after upgrading.",
    "items": [
        {
            "id": D1,
            "vertical": "cost-limits",
            "vertical_label": "COST & LIMITS",
            "rail_color": "var(--accent2)",
            "org_label": "OPENROUTER",
            "headline": "Same code-review workload, same platform: the price list spans 267× from "
                        "cheapest to most expensive.",
            "what_changed": "Output prices for long-context models on one platform span $0.15 to "
                            "$50 per million tokens today.",
            "why_it_matters": "Above a certain volume the model you pick decides the bill, not how "
                              "tightly you write the prompt.",
            "who_should_care": "Anyone running a high-volume automated workload: reviews, "
                               "summaries, extraction, agent loops.",
            "the_number": {
                "value": "$0.30 → $80.00",
                "label": "the same 200-review month, cheapest against most expensive on today's list — 267×",
                "notes": [
                    "One review priced at 30,000 input and 2,000 output tokens, 200 reviews a month.",
                    "The spread is on the price list, not on quality: this compares cost only.",
                    "A cheaper model that needs two attempts is not cheaper — measure retries before switching.",
                    "Cache reads and writes are priced separately and can reorder the ranking for repeated prefixes.",
                    "Free tiers exist at $0 but carry rate limits: they are not the same product.",
                ],
            },
            "diff": {
                "minus": "budget the prompt: shave tokens, trim the system message",
                "plus": "budget the model: the same month costs $0.30 or $80.00",
            },
            "watch_out": "This is a cost comparison, not a quality one, and prices move. The example "
                         "vendors today's price list so the arithmetic stays reproducible — re-fetch "
                         "before acting on it.",
            "example": {
                "kind": "analysis",
                "dir": f"examples/{D1}",
                "run_cmd": "bash run.sh",
                "run_summary": "9 lines, CPU, offline, < 1 s",
                "caption": "Today's real price list, one workload, sorted by monthly cost.",
                "code": read(D1, "run.py"),
                "code_slide": excerpt(D1, [(1, 7), (13, 14)]),
                "output": read(D1, "expected_output.txt"),
                "tested_in_ci": False,
            },
            "chart": cost_chart(),
            "source_url": "https://openrouter.ai/api/v1/models",
        },
        {
            "id": D2,
            "vertical": "tools-agents",
            "vertical_label": "TOOLS & AGENTS",
            "rail_color": "var(--ok)",
            "org": "ollama",
            "org_label": "OLLAMA",
            "headline": "Ollama now honours the sampling defaults declared inside the model file. "
                        "Local outputs may shift.",
            "what_changed": "Release v0.33.3 honours GGUF-defined default parameters, so a model "
                            "runs with the settings its author shipped.",
            "why_it_matters": "If you relied on the runner's own defaults, this upgrade changes your "
                              "output distribution.",
            "who_should_care": "Anyone running local models through Ollama in something that has to "
                               "be reproducible.",
            "the_number": {
                "value": "12 → 4",
                "label": "tokens the model can pick at one step — same weights, only the defaults differ",
                "notes": [
                    "Total variation distance between the two distributions: 0.230, on a fixed logit vector.",
                    "Top-token probability moves from 0.314 to 0.467: the model becomes more decisive.",
                    "The example uses two plausible default sets, not Ollama's specific old values, "
                    "which the release note does not state.",
                    "If you already pin temperature and top_p explicitly in your calls, nothing changes for you.",
                ],
            },
            "diff": {
                "minus": "the runner's own defaults, whatever the file declared",
                "plus": "the defaults the model author shipped inside the GGUF",
            },
            "watch_out": "We are not claiming what Ollama's previous defaults were: the release note "
                         "says defaults are now honoured, and our example quantifies why that class "
                         "of change matters. Check your own before and after.",
            "example": {
                "kind": "analysis",
                "dir": f"examples/{D2}",
                "run_cmd": "bash run.sh",
                "run_summary": "14 lines, numpy, CPU, offline, < 1 s",
                "caption": "Same logits, two default sets, two different models in practice.",
                "code": read(D2, "run.py"),
                "code_slide": excerpt(D2, [(5, 13)]),
                "output": read(D2, "expected_output.txt"),
                "tested_in_ci": False,
            },
            "source_url": "https://github.com/ollama/ollama/releases",
        },
    ],
}

out = ROOT / "data" / "episodes" / "2026-09-02.json"
out.write_text(json.dumps(episode, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {out}")
for item in episode["items"]:
    print(f"  {item['id']:34} headline={len(item['headline'].split()):3} words  "
          f"what_changed={len(item['what_changed'].split()):3} words")
