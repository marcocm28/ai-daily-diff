"""Fixed-token cost arithmetic; no model quality or API calls."""
import json
from decimal import Decimal
from pathlib import Path

data = json.loads(Path("prices.json").read_text())
tokens = data["synthetic_tokens"]
costs = {}
for model, rates in data["usd_per_million"].items():
    cost = sum(Decimal(rates[k]) * tokens[k] for k in tokens)
    costs[model] = cost / Decimal(1_000_000)
    print(f"{model}: ${costs[model]:.4f}")
ratio = costs["gpt-6-sol"] / costs["gpt-6-luna"]
print(f"Sol / Luna fixed-token cost: {ratio:.1f}x")
print("Price arithmetic only; quality untested.")
