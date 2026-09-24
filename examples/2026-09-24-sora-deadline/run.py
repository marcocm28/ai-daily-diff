"""Offline date-level migration guard, not an API availability probe."""
import json
from datetime import date
from pathlib import Path

data = json.loads(Path("fixture.json").read_text())
as_of = date.fromisoformat(data["as_of"])
cutoff = date.fromisoformat(data["shutdown_date"])
remaining = max(0, (cutoff - as_of).days)
print(f"Days until scheduled retirement: {remaining}")
for model in data["sample_jobs"]:
    blocked = as_of >= cutoff and model in data["retired_models"]
    print(f"{'BLOCK' if blocked else 'ALLOW'} {model}")
print("Offline policy only; no endpoint probe.")
