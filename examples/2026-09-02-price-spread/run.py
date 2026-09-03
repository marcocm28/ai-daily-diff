import json, pathlib
M = json.loads((pathlib.Path(__file__).parent / "prices.json").read_text())["models"]

IN_TOK, OUT_TOK, PER_MONTH = 30_000, 2_000, 200      # one code review, and how many a month

def monthly(m):
    return (IN_TOK * m["prompt"] + OUT_TOK * m["completion"]) * PER_MONTH

rows = sorted(M, key=monthly)
for m in rows:
    print(f"{m['id']:42} {m['context']//1000:>5}k ctx   ${monthly(m):8.2f} / month")

lo, hi = monthly(rows[0]), monthly(rows[-1])
print(f"\nsame workload, same platform: ${lo:.2f} vs ${hi:.2f} per month  ->  {hi/lo:.0f}x")
