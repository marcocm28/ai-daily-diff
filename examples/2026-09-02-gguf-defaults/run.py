import numpy as np

# One fixed logit vector, so this is deterministic. It stands in for the model's output at a
# single step: nothing here depends on which model, only on the sampling parameters applied.
logits = np.array([4.1, 3.9, 3.4, 2.8, 2.7, 2.1, 1.6, 1.2, 0.9, 0.4, -0.6, -1.8])

def distribution(temperature, top_p):
    p = np.exp((logits - logits.max()) / temperature); p /= p.sum()
    order = np.argsort(-p)
    keep = order[:np.searchsorted(np.cumsum(p[order]), top_p) + 1]
    q = np.zeros_like(p); q[keep] = p[keep]
    return q / q.sum()

for label, temp, top_p in (("generic fallback", 1.0, 1.00), ("declared in the file", 0.6, 0.90)):
    q = distribution(temp, top_p)
    print(f"{label:22} temp={temp:.1f} top_p={top_p:.2f}   "
          f"top token {q.max():.3f}   tokens reachable {int((q > 0).sum())}/{q.size}")

a, b = distribution(1.0, 1.00), distribution(0.6, 0.90)
print(f"\ntotal variation distance between the two: {0.5 * np.abs(a - b).sum():.3f}")
print("same logits, same model weights - only the defaults differ")
