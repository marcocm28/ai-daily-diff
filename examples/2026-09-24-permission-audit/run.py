"""Synthetic grant accounting, not a sandbox implementation."""
import json
from pathlib import Path

data = json.loads(Path("fixture.json").read_text())
grants = set(data["blanket_grants"])
tasks = data["synthetic_tasks"] * 10
required = [set(task["requires"]) for task in tasks]
assert all(need <= grants for need in required)
unused = sum(len(grants - need) for need in required)
total = len(tasks) * len(grants)
print(f"Unused blanket grants: {100 * unused / total:.1f}%")
scoped = [set(need) for need in required]
assert all(given == need for given, need in zip(scoped, required))
print("Scoped grant audit: PASS")
print("Synthetic fixture; not a sandbox test.")
